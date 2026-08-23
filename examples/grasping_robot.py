"""Run the object-grasping qBrain in a live two-dimensional world.

A blue ball wanders between near and far destinations in front of a stationary
brown robot whose distance and touch interfaces feed independently timed qUnits
and a Redis-connected gripper actuator. No ROS, LEGO hardware, or physics
engine is required.

Reference: D. Lanza, "Quantum-like Modeling of Cognitive Architectures for Robotics",
Zenodo, 2020, https://doi.org/10.5281/zenodo.22068511.
"""

import argparse
from pathlib import Path
from time import monotonic, sleep

from redis.exceptions import ConnectionError

from qrobot_qunits import RedisConfig, redis_utils
from qrobot_simulator.grasping_robot import (
    GraspingRobot,
    GraspingWorld,
    GraspingWorldLiveView,
)
from qrobot_simulator.grasping_robot.robots.config import GRIPPER_ROBOT_CONFIG

DEFAULT_DURATION = 0.0
DEFAULT_SPEED = 2.0
DEFAULT_FPS = 15.0
MIN_WARMUP_SECONDS = 5.0
WARMUP_ALLOWANCE = 12.0
MAX_WARMUP_SLEEP = 0.05


# Command-line interface


def parse_args() -> argparse.Namespace:
    """Parse simulation duration, speed, frame rate, and display options.

    :returns: Parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--duration",
        type=float,
        default=DEFAULT_DURATION,
        help="Simulated seconds; 0 runs until the window is closed.",
    )
    parser.add_argument(
        "--speed",
        type=float,
        default=DEFAULT_SPEED,
        help=(
            "Simulation/real-time ratio in " f"(0, {GRIPPER_ROBOT_CONFIG.max_simulation_speed:g}]."
        ),
    )
    parser.add_argument("--fps", type=float, default=DEFAULT_FPS)
    parser.add_argument("--seed", type=int, help="Seed for reproducible random ball movement.")
    parser.add_argument("--no-show", action="store_true")
    parser.add_argument("--save-world", type=Path)
    return parser.parse_args()


def validate_args(args: argparse.Namespace) -> None:
    """Validate timing and display arguments.

    :param args: Parsed command-line arguments.
    :raises ValueError: If timing values are invalid or an endless headless run
        is requested.
    """
    if (
        args.duration < 0
        or not 0 < args.speed <= GRIPPER_ROBOT_CONFIG.max_simulation_speed
        or args.fps <= 0
        or (args.no_show and args.duration == 0)
    ):
        raise ValueError("use positive --fps/--speed; headless runs need a positive duration")


# qBrain startup and simulation loop


def wait_for_brain(
    robot: GraspingRobot,
    world: GraspingWorld,
    view: GraspingWorldLiveView,
    speed: float,
    frame_period: float,
) -> None:
    """Wait until both perceptual qUnits complete their first window.

    :param robot: Robot providing the perceptual qUnit signals.
    :param world: Current simulation state displayed during warm-up.
    :param view: Live view refreshed while the qUnits collect samples.
    :param speed: Simulation-time to wall-clock-time ratio.
    :param frame_period: Wall-clock delay between view updates.
    :raises RuntimeError: If the qUnits do not publish before the deadline.
    """
    # The slower touch qUnit needs five simulated seconds of samples. Extra
    # wall-clock allowance covers process startup on slower computers.
    warmup_deadline = monotonic() + max(MIN_WARMUP_SECONDS, WARMUP_ALLOWANCE / speed)
    while any(
        signal is None
        for signal in (
            robot.signals().proximity_burst,
            robot.signals().empty_gripper_burst,
        )
    ):
        if monotonic() >= warmup_deadline:
            raise RuntimeError("qUnits did not publish during warm-up")
        view.update(world, robot.signals(), phase="WARMING UP")
        sleep(min(frame_period, MAX_WARMUP_SLEEP))


def run_simulation(
    robot: GraspingRobot,
    world: GraspingWorld,
    view: GraspingWorldLiveView,
    duration: float,
    speed: float,
    frame_period: float,
    headless: bool,
) -> None:
    """Run the sensor-brain-actuator loop until time or the window ends.

    :param robot: Robot that receives readings and supplies actuator commands.
    :param world: Physical simulation advanced by each actuator command.
    :param view: Live view refreshed after each world step.
    :param duration: Simulated run duration, or zero for an unlimited run.
    :param speed: Simulation-time to wall-clock-time ratio.
    :param frame_period: Wall-clock duration of one rendered frame.
    :param headless: Continue without checking whether a GUI window is open.
    """
    started = monotonic()
    next_frame = started
    while (duration == 0 or (monotonic() - started) * speed < duration) and (
        headless or view.is_open
    ):
        now = monotonic()
        if now < next_frame:
            sleep(next_frame - now)

        # Each frame publishes the previous physical reading, applies the
        # newest brain command, then draws the resulting world state.
        robot.perceive(world.readings)
        world.step(robot.actuator_value(), frame_period * speed)
        view.update(world, robot.signals())
        next_frame = max(next_frame + frame_period, monotonic())


# Application entry point


def main() -> None:
    """Build, warm up, run, and reliably shut down the live demonstration.

    :raises RuntimeError: If Redis is unavailable or qBrain warm-up fails.
    """
    args = parse_args()
    validate_args(args)
    redis_config = RedisConfig()
    try:
        redis_utils.get_redis(redis_config).ping()
    except ConnectionError as exc:
        raise RuntimeError("Redis must be running on localhost:6379") from exc

    robot = GraspingRobot(redis_config, args.speed)
    world = GraspingWorld.demo(robot, seed=args.seed)
    view = GraspingWorldLiveView(world.arena, interactive=not args.no_show)
    robot.perceive(world.readings)
    frame_period = 1 / args.fps
    try:
        robot.start_brain()
        wait_for_brain(robot, world, view, args.speed, frame_period)
        run_simulation(
            robot,
            world,
            view,
            args.duration,
            args.speed,
            frame_period,
            args.no_show,
        )
    except KeyboardInterrupt:
        pass
    finally:
        if args.save_world:
            print("saved", view.save(args.save_world))
        robot.stop_brain()
        view.close()


if __name__ == "__main__":
    main()
