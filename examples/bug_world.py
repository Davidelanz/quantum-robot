"""Run a bug-like qBrain in a live two-dimensional ecosystem.

Warning: ``qrobot_simulator`` is experimental. This example implements the
predator/prey research scenario with simplified two-dimensional kinematics and
sensing; its simulator interfaces may change between minor releases.

An interactive chessboard shows two blue prey robots, one red predator, and a
self-contained brown bug controlled by either a classical brain or a qBrain.
Matplotlib renders the world, while Redis carries signals between the
independently scheduled units when the quantum controller is selected.

Reference: D. Lanza, "Quantum-like Modeling of Cognitive Architectures for Robotics",
Zenodo, 2020, https://doi.org/10.5281/zenodo.22068511.
"""

import argparse
from pathlib import Path
from time import monotonic, sleep

from redis.exceptions import ConnectionError

from qrobot_qunits import RedisConfig
from qrobot_qunits.redis import get_redis
from qrobot_simulator.bug_world import BugWorld, BugWorldLiveView, ClassicalBug, QuantumBug
from qrobot_simulator.bug_world.robots.base_bug import BaseBug

DEFAULT_DURATION = 0.0
DEFAULT_FPS = 10.0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--duration", type=float, default=DEFAULT_DURATION, help="Seconds; 0 runs until closed."
    )
    parser.add_argument("--fps", type=float, default=DEFAULT_FPS, help="World refresh rate.")
    parser.add_argument(
        "--controller",
        choices=("quantum", "classical"),
        default="quantum",
        help="Brain used by the controlled bug.",
    )
    parser.add_argument("--no-show", action="store_true")
    parser.add_argument("--save-world", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.duration < 0 or args.fps <= 0 or (args.no_show and args.duration == 0):
        raise ValueError("use positive --fps/--duration; headless runs need a duration")
    if args.controller == "quantum":
        redis_config = RedisConfig()
        try:
            get_redis(redis_config).ping()
        except ConnectionError as exc:
            raise RuntimeError("Redis must be running on localhost:6379") from exc
        bug: BaseBug = QuantumBug(redis_config)
    else:
        bug = ClassicalBug()
    world = BugWorld.demo(bug)
    view = (
        BugWorldLiveView(world.board, interactive=not args.no_show)
        if not args.no_show or args.save_world
        else None
    )
    frame_period = 1 / args.fps
    started = monotonic()
    next_frame = started
    try:
        bug.start(world.readings)
        while (args.duration == 0 or monotonic() - started < args.duration) and (
            view is None or view.is_open
        ):
            now = monotonic()
            if now < next_frame:
                sleep(next_frame - now)
            world.step(bug.command(world.readings, frame_period), frame_period)
            if view is not None:
                view.update(world)
            next_frame = max(next_frame + frame_period, monotonic())
    except KeyboardInterrupt:
        pass
    finally:
        if args.save_world and view is not None:
            print("saved", view.save(args.save_world))
        bug.stop()
        if view is not None:
            view.close()


if __name__ == "__main__":
    main()
