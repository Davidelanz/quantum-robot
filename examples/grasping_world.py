"""Run a classical or quantum gripper in the two-dimensional grasping world.

Warning: ``qrobot_simulator`` is experimental. This example implements the
object-grasping research scenario with simplified two-dimensional kinematics,
sensing, and contact rules; its simulator interfaces may change between minor
releases.

A blue ball wanders between near and far destinations in front of a stationary
brown gripper. The classical version applies a deterministic timed policy; the
quantum version feeds independently timed qUnits and a Redis-connected actuator.

Reference: D. Lanza, "Quantum-like Modeling of Cognitive Architectures for Robotics",
Zenodo, 2020, https://doi.org/10.5281/zenodo.22068511.
"""

import argparse
from pathlib import Path
from time import monotonic, sleep

from redis.exceptions import ConnectionError

from qrobot_qunits import RedisConfig
from qrobot_qunits.redis import get_redis
from qrobot_simulator.grasping_world import (
    ClassicalGripper,
    GraspingWorld,
    GraspingWorldLiveView,
    QuantumGripper,
)
from qrobot_simulator.grasping_world.robots.base_gripper import BaseGripper

DEFAULT_DURATION = 0.0
DEFAULT_SPEED = 2.0
DEFAULT_FPS = 15.0
MAX_SIMULATION_SPEED = 10.0
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
        "--gripper",
        choices=("classical", "quantum"),
        default="quantum",
        help="Controller used by the stationary gripper.",
    )
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
        help=f"Simulation/real-time ratio in (0, {MAX_SIMULATION_SPEED:g}].",
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
        or not 0 < args.speed <= MAX_SIMULATION_SPEED
        or args.fps <= 0
        or (args.no_show and args.duration == 0)
    ):
        raise ValueError("use positive --fps/--speed; headless runs need a positive duration")


# qBrain startup and simulation loop


def wait_for_brain(
    gripper: BaseGripper,
    world: GraspingWorld,
    view: GraspingWorldLiveView | None,
    speed: float,
    frame_period: float,
) -> None:
    """Wait until both perceptual qUnits complete their first window.

    :param gripper: Quantum gripper providing the perceptual qUnit signals.
    :param world: Current simulation state displayed during warm-up.
    :param view: Live view refreshed while the qUnits collect samples.
    :param speed: Simulation-time to wall-clock-time ratio.
    :param frame_period: Wall-clock delay between view updates.
    :raises RuntimeError: If the qUnits do not publish before the deadline.
    """
    # The slower touch qUnit needs five simulated seconds of samples. Extra
    # wall-clock allowance covers process startup on slower computers.
    warmup_deadline = monotonic() + max(MIN_WARMUP_SECONDS, WARMUP_ALLOWANCE / speed)
    while not gripper.brain.ready:
        if monotonic() >= warmup_deadline:
            raise RuntimeError("qUnits did not publish during warm-up")
        if view is not None:
            view.update(world, gripper.diagnostics(), phase="WARMING UP")
        sleep(min(frame_period, MAX_WARMUP_SLEEP))


def run_simulation(
    gripper: BaseGripper,
    world: GraspingWorld,
    view: GraspingWorldLiveView | None,
    duration: float,
    speed: float,
    frame_period: float,
    headless: bool,
) -> None:
    """Run the sensor-brain-actuator loop until time or the window ends.

    :param gripper: Gripper that receives readings and supplies actuator commands.
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
        headless or (view is not None and view.is_open)
    ):
        now = monotonic()
        if now < next_frame:
            sleep(next_frame - now)

        # Each brain translates the same readings and simulated time into the
        # normalized action consumed by the physical world.
        simulated_dt = frame_period * speed
        activation = gripper.command(world.readings, simulated_dt)

        # Physics and rendering consume the selected controller through the
        # same normalized actuator interface.
        world.step(activation, simulated_dt)
        if view is not None:
            view.update(world, gripper.diagnostics())
        next_frame = max(next_frame + frame_period, monotonic())


# Application entry point


def main() -> None:
    """Build, warm up, run, and reliably shut down the live demonstration.

    :raises RuntimeError: If Redis is unavailable or qBrain warm-up fails.
    """
    args = parse_args()
    validate_args(args)
    # Only the quantum implementation depends on Redis-backed worker processes.
    if args.gripper == "quantum":
        redis_config = RedisConfig()
        try:
            get_redis(redis_config).ping()
        except ConnectionError as exc:
            raise RuntimeError("Redis must be running on localhost:6379") from exc
        gripper: BaseGripper = QuantumGripper(redis_config, args.speed)
    else:
        gripper = ClassicalGripper()

    world = GraspingWorld.demo(gripper, seed=args.seed)
    # A headless run constructs no Matplotlib objects unless a final rendered
    # frame was explicitly requested.
    view = (
        GraspingWorldLiveView(world.arena, interactive=not args.no_show)
        if not args.no_show or args.save_world
        else None
    )
    frame_period = 1 / args.fps
    try:
        gripper.brain.start(world.readings)
        wait_for_brain(gripper, world, view, args.speed, frame_period)
        run_simulation(
            gripper,
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
        if args.save_world and view is not None:
            print("saved", view.save(args.save_world))
        gripper.stop()
        if view is not None:
            view.close()


if __name__ == "__main__":
    main()
