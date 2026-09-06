"""Benchmark qBrain behavior from construction to Redis-backed execution.

The benchmark answers three questions using public package behavior:

* Is Redis responsive from a fresh and an existing connection?
* How does reading connected outputs scale with the number of connections?
* How do construction, startup, observation, and shutdown scale for complete
  sensor -> qUnit -> actuator networks?

Run the same command from each revision being compared::

    poetry run python scripts/benchmark_qbrain_performance.py
"""

from __future__ import annotations

import argparse
import gc
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from statistics import median, pstdev
from time import perf_counter, sleep
from typing import Any
from uuid import uuid4

from redis import Redis

from qrobot.bursts import ZeroBurst
from qrobot.models import AngularModel
from qrobot_qunits import ActuatorUnit, QUnit, RedisConfig, SensorialUnit
from qrobot_qunits import redis as redis_api
from qrobot_qunits.redis import get_redis
from qrobot_qunits.redis.protocol import RedisAttribute, build_redis_key

_read_outputs: Callable[[Redis, Iterable[str]], list[str | None]] | None = getattr(
    redis_api, "read_outputs", None
)


@dataclass(frozen=True)
class Measurement:
    """Summarize repeated timings measured in milliseconds."""

    median_ms: float
    minimum_ms: float
    maximum_ms: float
    deviation_ms: float

    @classmethod
    def from_samples(cls, samples: list[float]) -> Measurement:
        """Build a measurement from a non-empty collection of samples."""
        return cls(median(samples), min(samples), max(samples), pstdev(samples))


@dataclass(frozen=True)
class Brain:
    """Hold the units in a synthetic layered qBrain."""

    sensors: tuple[SensorialUnit, ...]
    qunits: tuple[QUnit, ...]
    actuators: tuple[ActuatorUnit, ...]

    @property
    def units(self) -> tuple[SensorialUnit | QUnit | ActuatorUnit, ...]:
        """Return every unit in signal-flow order."""
        return (*self.sensors, *self.qunits, *self.actuators)


def measure(operation: Callable[[], object], runs: int) -> Measurement:
    """Measure repeated operation durations in milliseconds."""
    samples = []
    for _ in range(runs):
        started_at = perf_counter()
        operation()
        samples.append((perf_counter() - started_at) * 1_000)
    return Measurement.from_samples(samples)


def print_measurement(label: str, result: Measurement) -> None:
    """Print one consistently formatted benchmark result."""
    print(
        f"{label:<30} median {result.median_ms:9.3f} ms  "
        f"range {result.minimum_ms:9.3f}-{result.maximum_ms:9.3f} ms  "
        f"sd {result.deviation_ms:8.3f} ms"
    )


def client_config(client: Redis) -> RedisConfig:
    """Recover benchmark connection settings from a Redis client."""
    options = client.connection_pool.connection_kwargs
    return RedisConfig(str(options["host"]), int(options["port"]), int(options["db"]))


def read_outputs(client: Redis, unit_ids: Iterable[str]) -> list[str | None]:
    """Read outputs with the package API available in the tested revision."""
    ids = list(unit_ids)
    if _read_outputs is not None:
        return _read_outputs(client, ids)
    values = [client.get(build_redis_key(unit_id, RedisAttribute.OUTPUT)) for unit_id in ids]
    return [None if value is None else str(value) for value in values]


def read_normalized_outputs(client: Redis, unit_ids: Iterable[str]) -> list[float]:
    """Read outputs and verify that every unit published a normalized value."""
    values = read_outputs(client, unit_ids)
    normalized = []
    for value in values:
        if value is None:
            raise RuntimeError("an expected qBrain output is missing")
        normalized.append(float(value))
    if any(not 0.0 <= value <= 1.0 for value in normalized):
        raise RuntimeError("a qBrain output is outside the normalized range")
    return normalized


def output_keys(units: Iterable[Any]) -> list[str]:
    """Return Redis output keys for units exposing an identifier."""
    return [build_redis_key(unit.id, RedisAttribute.OUTPUT) for unit in units]


def build_brain(unit_count: int, config: RedisConfig, period: float) -> Brain:
    """Build independent three-layer chains totaling ``unit_count`` units."""
    chain_count = unit_count // 3
    prefix = f"benchmark-{uuid4().hex[:8]}"
    sensors = tuple(
        SensorialUnit(f"{prefix}-sensor-{index}", period, redis_config=config)
        for index in range(chain_count)
    )
    qunits = tuple(
        QUnit(
            f"{prefix}-qunit-{index}",
            AngularModel(n=1, tau=1),
            ZeroBurst(),
            period,
            in_qunits={0: sensor.id},
            redis_config=config,
        )
        for index, sensor in enumerate(sensors)
    )
    actuators = tuple(
        ActuatorUnit(
            f"{prefix}-actuator-{index}",
            [qunit.id],
            period,
            redis_config=config,
        )
        for index, qunit in enumerate(qunits)
    )
    return Brain(sensors, qunits, actuators)


def stop_brain(brain: Brain) -> None:
    """Stop a brain in reverse signal-flow order."""
    for unit in reversed(brain.units):
        unit.stop()


def release_managers(units: Iterable[Any]) -> None:
    """Release multiprocessing managers left by the tested revision."""
    managers = {
        id(manager): manager
        for unit in units
        if (manager := getattr(unit, "_multiproc_manager", None)) is not None
    }
    for manager in managers.values():
        manager.shutdown()


def wait_until_ready(client: Redis, brain: Brain, timeout: float) -> None:
    """Wait until every layer has published an output or raise on timeout."""
    keys = output_keys(brain.units)
    deadline = perf_counter() + timeout
    while perf_counter() < deadline:
        if all(value is not None for value in client.mget(keys)):
            return
        sleep(min(brain.sensors[0].sampling_period / 4, 0.01))
    missing = [key for key, value in zip(keys, client.mget(keys), strict=True) if value is None]
    raise TimeoutError(f"qBrain did not publish {len(missing)} outputs within {timeout:g} seconds")


def benchmark_redis(config: RedisConfig, client: Redis, runs: int) -> None:
    """Measure fresh and reused Redis connections."""

    def fresh_ping() -> None:
        fresh_client = get_redis(config)
        try:
            fresh_client.ping()
        finally:
            fresh_client.close()

    print("\nRedis round trips")
    print_measurement("fresh connection + PING", measure(fresh_ping, runs))
    print_measurement("existing connection PING", measure(client.ping, runs))


def benchmark_output_reads(client: Redis, fan_ins: list[int], runs: int) -> None:
    """Measure reading complete output snapshots at increasing fan-in."""
    prefix = f"benchmark-output-{uuid4().hex}"
    unit_ids = [f"{prefix}-{index}" for index in range(max(fan_ins))]
    keys = [build_redis_key(unit_id, RedisAttribute.OUTPUT) for unit_id in unit_ids]
    client.mset(dict.fromkeys(keys, "0.5"))
    try:
        print("\nConnected output snapshots")
        for fan_in in fan_ins:
            result = measure(lambda: read_normalized_outputs(client, unit_ids[:fan_in]), runs)
            print_measurement(f"outputs {fan_in}", result)
    finally:
        client.delete(*keys)


def benchmark_lifecycle(
    config: RedisConfig,
    client: Redis,
    sizes: list[int],
    runs: int,
    period: float,
    timeout: float,
) -> None:
    """Measure complete qBrain construction and Redis-backed lifecycle scaling."""
    print("\nComplete qBrain lifecycle")
    for size in sizes:
        samples: dict[str, list[float]] = {
            name: [] for name in ("construct", "ready", "observe", "shutdown")
        }
        for _ in range(runs):
            started_at = perf_counter()
            brain = build_brain(size, config, period)
            samples["construct"].append((perf_counter() - started_at) * 1_000)
            stopped = False
            try:
                started_at = perf_counter()
                for unit in brain.units:
                    unit.start()
                wait_until_ready(client, brain, timeout)
                samples["ready"].append((perf_counter() - started_at) * 1_000)

                actuator_ids = [unit.id for unit in brain.actuators]
                result = measure(
                    lambda: read_normalized_outputs(client, actuator_ids),
                    1,
                )
                samples["observe"].append(result.median_ms)

                started_at = perf_counter()
                stop_brain(brain)
                stopped = True
                samples["shutdown"].append((perf_counter() - started_at) * 1_000)
            finally:
                if not stopped:
                    stop_brain(brain)
                release_managers(brain.units)
                del brain
                gc.collect()

        print(f"\n{size} units ({size // 3} independent chains)")
        for name in ("construct", "ready", "observe", "shutdown"):
            print_measurement(name, Measurement.from_samples(samples[name]))


def positive_int(value: str) -> int:
    """Parse a strictly positive command-line integer."""
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("value must be positive")
    return parsed


def positive_float(value: str) -> float:
    """Parse a strictly positive command-line float."""
    parsed = float(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("value must be positive")
    return parsed


def brain_size(value: str) -> int:
    """Parse a positive unit count made of complete three-unit chains."""
    parsed = positive_int(value)
    if parsed % 3:
        raise argparse.ArgumentTypeError("brain size must be divisible by three")
    return parsed


def main() -> None:
    """Parse options, verify Redis, and run the benchmark suite."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="localhost", help="Redis host")
    parser.add_argument("--port", type=positive_int, default=6379, help="Redis port")
    parser.add_argument("--database", type=int, default=14, help="Redis database")
    parser.add_argument("--runs", type=positive_int, default=5, help="Samples per result")
    parser.add_argument(
        "--brain-sizes",
        type=brain_size,
        nargs="+",
        default=[3, 12, 24],
        help="Total units; each value must be divisible by three",
    )
    parser.add_argument(
        "--fan-ins",
        type=positive_int,
        nargs="+",
        default=[1, 8, 32, 128],
        help="Output values per Redis snapshot",
    )
    parser.add_argument(
        "--period",
        type=positive_float,
        default=0.02,
        help="Worker sampling period in seconds",
    )
    parser.add_argument(
        "--timeout",
        type=positive_float,
        default=10.0,
        help="Maximum seconds for a brain to publish all outputs",
    )
    args = parser.parse_args()

    config = RedisConfig(args.host, args.port, args.database)
    client = get_redis(config)
    try:
        client.ping()
        benchmark_redis(config, client, args.runs)
        benchmark_output_reads(client, args.fan_ins, args.runs)
        benchmark_lifecycle(
            config,
            client,
            args.brain_sizes,
            args.runs,
            args.period,
            args.timeout,
        )
    finally:
        client.close()


if __name__ == "__main__":
    main()
