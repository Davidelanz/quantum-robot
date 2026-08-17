"""Run a bug-like qBrain in a live two-dimensional ecosystem.

An interactive chessboard shows two blue prey robots, one red predator, and a
self-contained brown BugRobot whose sensors, qUnits, and actuators communicate
through Redis. No ROS, CoppeliaSim, or physical hardware is needed.

Reference: D. Lanza, "Quantum-like Modeling of Cognitive Architectures for Robotics",
Zenodo, 2020, https://doi.org/10.5281/zenodo.22068511.
"""

import argparse
from pathlib import Path
from time import monotonic, sleep

from redis.exceptions import ConnectionError

from qrobot_qunits import RedisConfig, redis_utils
from qrobot_simulator.bug_world import BugRobot, BugWorld, BugWorldLiveView

DEFAULT_DURATION = 0.0
DEFAULT_FPS = 10.0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--duration", type=float, default=DEFAULT_DURATION, help="Seconds; 0 runs until closed."
    )
    parser.add_argument("--fps", type=float, default=DEFAULT_FPS, help="World refresh rate.")
    parser.add_argument("--no-show", action="store_true")
    parser.add_argument("--save-world", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.duration < 0 or args.fps <= 0 or (args.no_show and args.duration == 0):
        raise ValueError("use positive --fps/--duration; headless runs need a duration")
    config = RedisConfig()
    try:
        redis_utils.get_redis(config).ping()
    except ConnectionError as exc:
        raise RuntimeError("Redis must be running on localhost:6379") from exc

    bug = BugRobot(config)
    world = BugWorld.demo(bug)
    view = BugWorldLiveView(world.board, not args.no_show)
    bug.perceive(world.readings)
    frame_period = 1 / args.fps
    started = monotonic()
    next_frame = started
    try:
        bug.start_brain()
        while (args.duration == 0 or monotonic() - started < args.duration) and (
            args.no_show or view.is_open
        ):
            now = monotonic()
            if now < next_frame:
                sleep(next_frame - now)
            bug.perceive(world.readings)
            world.step(bug.actuator_values(), frame_period)
            view.update(world)
            next_frame = max(next_frame + frame_period, monotonic())
    except KeyboardInterrupt:
        pass
    finally:
        if args.save_world:
            print("saved", view.save(args.save_world))
        bug.stop_brain()
        view.close()


if __name__ == "__main__":
    main()
