"""Benchmark qBrain process scaling and Redis communication.

Run the same command on each commit being compared. The benchmark reports
construction cost separately from Redis connectivity and connected-output read
scaling::

    poetry run python scripts/benchmark_qbrain_performance.py
"""

from __future__ import annotations

import argparse
import multiprocessing
from collections.abc import Callable, Iterable
from statistics import median, pstdev
from time import perf_counter, sleep
from typing import Any
from uuid import uuid4

from redis import Redis

from qrobot.bursts import ZeroBurst
from qrobot.models import AngularModel
from qrobot_qunits import ActuatorUnit, QUnit, RedisConfig, SensorialUnit
from qrobot_qunits.redis import get_redis, redis_status
from qrobot_qunits.redis.protocol import RedisAttribute, build_redis_key
from qrobot_simulator.bug_world.robots.bug_robot import BugRobot

try:
    from qrobot_qunits.redis import read_outputs as _read_outputs
except ImportError:
    _read_outputs = None

SECTIONS = (
    "connectivity",
    "status",
    "inputs",
    "output",
    "worker",
    "construction",
    "simulation",
    "scheduling",
)


class RedisOutput:
    """Minimal unit interface for measuring simulation-side output collection."""

    def __init__(self, unit_id: str, config: RedisConfig) -> None:
        self.id = unit_id
        self._config = config

    def get_burst_output(self) -> float | None:
        """Read a qUnit-compatible output."""
        return self._value()

    def get_activation(self) -> float | None:
        """Read an actuator-compatible output."""
        return self._value()

    def _value(self) -> float | None:
        value = get_redis(self._config).get(build_redis_key(self.id, RedisAttribute.OUTPUT))
        return None if value is None else float(value)


class SchedulingProbe(SensorialUnit):
    """Record task starts while exercising the real BaseUnit worker loop."""

    def __init__(self, period: float, task_time: float, iterations: int) -> None:
        super().__init__("benchmark_scheduler", period)
        self.task_time = task_time
        self.iterations = iterations
        self.starts: list[float] = []

    def _unit_task(self) -> None:
        self.starts.append(perf_counter())
        sleep(self.task_time)
        if len(self.starts) == self.iterations:
            self._stop_event.set()


def _shutdown_managers(units: Iterable[Any]) -> None:
    """Stop every manager created for a synthetic brain."""
    managers = {
        id(manager): manager
        for unit in units
        if (manager := getattr(unit, "_multiproc_manager", None)) is not None
    }
    for manager in managers.values():
        manager.shutdown()


def build_synthetic_brain(unit_count: int) -> list[Any]:
    """Build an equally divided sensor, qUnit, and actuator network."""
    layer_size = max(1, unit_count // 3)
    sensors = [SensorialUnit(f"bench_sensor_{index}", 1.0) for index in range(layer_size)]
    qunits = [
        QUnit(
            f"bench_qunit_{index}",
            AngularModel(n=1, tau=1),
            ZeroBurst(),
            1.0,
            in_qunits={0: sensors[index % len(sensors)].id},
        )
        for index in range(layer_size)
    ]
    actuators = [
        ActuatorUnit(
            f"bench_actuator_{index}",
            [qunits[index % len(qunits)].id],
            1.0,
        )
        for index in range(layer_size)
    ]
    return [*sensors, *qunits, *actuators]


def measure_brain_construction(unit_count: int) -> tuple[float, int, int]:
    """Return construction time, actual unit count, and new child processes."""
    children_before = {process.pid for process in multiprocessing.active_children()}
    started_at = perf_counter()
    units = build_synthetic_brain(unit_count)
    elapsed = perf_counter() - started_at
    children_after = {
        process.pid
        for process in multiprocessing.active_children()
        if process.pid not in children_before
    }
    try:
        return elapsed, len(units), len(children_after)
    finally:
        _shutdown_managers(units)


def measure_calls(operation: Callable[[], object], runs: int) -> list[float]:
    """Measure individual operation durations in milliseconds."""
    samples = []
    for _ in range(runs):
        started_at = perf_counter()
        operation()
        samples.append((perf_counter() - started_at) * 1_000)
    return samples


def read_connected_outputs(client: Redis, unit_ids: list[str]) -> list[object]:
    """Use the package's batched reader, or its historical sequential behavior."""
    if _read_outputs is not None:
        return _read_outputs(client, unit_ids)
    return [client.get(build_redis_key(unit_id, RedisAttribute.OUTPUT)) for unit_id in unit_ids]


def print_samples(label: str, samples: list[float], unit: str = "ms") -> None:
    """Print median, range, and population standard deviation."""
    print(
        f"{label}: median={median(samples):.3f} {unit}, "
        f"range={min(samples):.3f}-{max(samples):.3f} {unit}, "
        f"stddev={pstdev(samples):.3f} {unit}"
    )


def benchmark_construction(sizes: list[int], runs: int) -> None:
    """Report how process count and construction time scale with brain size."""
    print("\nBrain construction and process scaling")
    for requested_size in sizes:
        samples = [measure_brain_construction(requested_size) for _ in range(runs)]
        elapsed = [sample[0] * 1_000 for sample in samples]
        actual_sizes = {sample[1] for sample in samples}
        child_counts = {sample[2] for sample in samples}
        print_samples(f"requested={requested_size}, actual={actual_sizes.pop()}", elapsed)
        print(f"  manager processes: {min(child_counts)}-{max(child_counts)}")


def benchmark_connectivity(
    config: RedisConfig,
    client: Redis,
    runs: int,
) -> None:
    """Report new-connection and existing-client Redis latency."""

    def connect_and_ping() -> None:
        fresh_client = get_redis(config)
        try:
            fresh_client.ping()
        finally:
            fresh_client.close()

    print("\nRedis connectivity")
    print_samples("connect + PING", measure_calls(connect_and_ping, runs))
    client.ping()
    print_samples("PING on existing client", measure_calls(client.ping, runs))


def benchmark_status(client: Redis, sizes: list[int], runs: int) -> None:
    """Report full-database status collection scaling."""
    print("\nRedis status scaling")
    prefix = f"qrobot-benchmark-status-{uuid4().hex}"
    keys = [f"{prefix}-{index}" for index in range(max(sizes))]
    client.mset(dict.fromkeys(keys, "0.5"))
    try:
        for size in sizes:
            disabled = keys[size:]
            if disabled:
                client.delete(*disabled)
            samples = measure_calls(lambda: redis_status(client_config(client)), runs)
            print_samples(f"keys={size}", samples)
            if disabled:
                client.mset(dict.fromkeys(disabled, "0.5"))
    finally:
        client.delete(*keys)


def client_config(client: Redis) -> RedisConfig:
    """Recover benchmark connection settings from a Redis client."""
    options = client.connection_pool.connection_kwargs
    return RedisConfig(str(options["host"]), int(options["port"]), int(options["db"]))


def benchmark_inputs(client: Redis, sizes: list[int], runs: int) -> None:
    """Report connected-output read scaling through the available package API."""

    prefix = f"qrobot-benchmark-input-{uuid4().hex}"
    unit_ids = [f"{prefix}-{index}" for index in range(max(sizes))]
    keys = [f"{unit_id} output" for unit_id in unit_ids]
    client.mset(dict.fromkeys(keys, "0.5"))
    try:
        print("\nConnected-input read scaling")
        for size in sizes:
            samples = measure_calls(
                lambda size=size: read_connected_outputs(client, unit_ids[:size]), runs
            )
            print_samples(f"fan-in={size}", samples)
    finally:
        client.delete(*keys)


def benchmark_single_output(client: Redis, background_keys: int, runs: int) -> None:
    """Measure one qUnit output lookup with unrelated Redis state present."""
    unit = QUnit("benchmark_output", AngularModel(n=1, tau=1), ZeroBurst(), 1.0)
    unit.redis_config = client_config(client)
    output_key = build_redis_key(unit.id, RedisAttribute.OUTPUT)
    prefix = f"qrobot-benchmark-background-{uuid4().hex}"
    keys = [f"{prefix}-{index}" for index in range(background_keys)]
    client.mset({**dict.fromkeys(keys, "0.5"), output_key: "0.5"})
    try:
        print("\nSingle-output lookup")
        print_samples(
            f"background-keys={background_keys}",
            measure_calls(unit.get_burst_output, runs),
        )
    finally:
        client.delete(*keys, output_key)
        _shutdown_managers([unit])


def benchmark_worker_cycle(client: Redis, runs: int) -> None:
    """Measure repeated sensor publication using worker-equivalent client state."""
    sensor = SensorialUnit("benchmark_worker", 1.0, redis_config=client_config(client))
    if hasattr(sensor, "_worker_redis"):
        sensor._worker_redis = client
    try:
        print("\nSensor worker cycle")
        print_samples("read + publish", measure_calls(sensor._unit_task, runs))
    finally:
        client.delete(build_redis_key(sensor.id, RedisAttribute.OUTPUT))
        _shutdown_managers([sensor])


def benchmark_simulation_outputs(client: Redis, runs: int) -> None:
    """Measure collection of the Bug brain outputs used by each simulation frame."""
    config = client_config(client)
    robot = BugRobot(redis_config=config, connect_brain=False)
    prefix = f"qrobot-benchmark-simulation-{uuid4().hex}"
    qunits = {f"qunit-{index}": RedisOutput(f"{prefix}-q-{index}", config) for index in range(7)}
    actuators = {
        f"actuator-{index}": RedisOutput(f"{prefix}-a-{index}", config) for index in range(5)
    }
    robot.qunits = qunits  # type: ignore[assignment]
    robot.actuators = actuators  # type: ignore[assignment]
    keys = [
        build_redis_key(unit.id, RedisAttribute.OUTPUT)
        for unit in (*qunits.values(), *actuators.values())
    ]
    client.mset(dict.fromkeys(keys, "0.5"))
    try:
        print("\nSimulation output collection")
        print_samples(
            "7 qUnits + 5 actuators",
            measure_calls(lambda: (robot.qunint_values(), robot.actuator_values()), runs),
        )
    finally:
        client.delete(*keys)


def benchmark_scheduling(runs: int) -> None:
    """Measure start-to-start interval and accumulated scheduler drift."""
    period = 0.02
    task_time = 0.008
    iterations = 20
    intervals: list[float] = []
    drift: list[float] = []
    for _ in range(runs):
        probe = SchedulingProbe(period, task_time, iterations)
        try:
            probe._loop()
            intervals.extend(
                (current - previous) * 1_000
                for previous, current in zip(probe.starts, probe.starts[1:])
            )
            actual_duration = probe.starts[-1] - probe.starts[0]
            expected_duration = (iterations - 1) * period
            drift.append((actual_duration - expected_duration) * 1_000)
        finally:
            _shutdown_managers([probe])

    print("\nWorker scheduling")
    print(f"period={period * 1_000:.0f} ms, task={task_time * 1_000:.0f} ms")
    print_samples("start interval", intervals)
    print_samples("accumulated drift", drift)


def _positive_int(value: str) -> int:
    """Parse a strictly positive command-line integer."""
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("value must be positive")
    return parsed


def main() -> None:
    """Parse options and run the process and Redis benchmarks."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="localhost", help="Redis host")
    parser.add_argument("--port", type=_positive_int, default=6379, help="Redis port")
    parser.add_argument("--database", type=int, default=14, help="Redis database")
    parser.add_argument("--runs", type=_positive_int, default=7, help="Samples per measurement")
    parser.add_argument(
        "--brain-sizes",
        type=_positive_int,
        nargs="+",
        default=[6, 12, 24],
        help="Approximate total unit counts",
    )
    parser.add_argument(
        "--fan-ins",
        type=_positive_int,
        nargs="+",
        default=[1, 8, 32, 128, 512],
        help="Connected outputs per batched Redis read",
    )
    parser.add_argument(
        "--sections",
        choices=SECTIONS,
        nargs="+",
        default=list(SECTIONS),
        help="Benchmark sections to run",
    )
    parser.add_argument(
        "--skip-construction",
        action="store_true",
        help="Run only Redis connectivity and read scaling",
    )
    parser.add_argument(
        "--skip-redis",
        action="store_true",
        help="Run only brain construction and process scaling",
    )
    args = parser.parse_args()
    if args.skip_construction and args.skip_redis:
        parser.error("the benchmark cannot skip both sections")

    sections = set(args.sections)
    if not args.skip_construction and "construction" in sections:
        benchmark_construction(args.brain_sizes, args.runs)
    if "scheduling" in sections:
        benchmark_scheduling(args.runs)
    if args.skip_redis:
        return

    config = RedisConfig(args.host, args.port, args.database)
    client = get_redis(config)
    try:
        if "connectivity" in sections:
            benchmark_connectivity(config, client, args.runs)
        if "status" in sections:
            benchmark_status(client, args.fan_ins, args.runs)
        if "inputs" in sections:
            benchmark_inputs(client, args.fan_ins, args.runs)
        if "output" in sections:
            benchmark_single_output(client, max(args.fan_ins), args.runs)
        if "worker" in sections:
            benchmark_worker_cycle(client, args.runs)
        if "simulation" in sections:
            benchmark_simulation_outputs(client, args.runs)
    finally:
        client.close()


if __name__ == "__main__":
    main()
