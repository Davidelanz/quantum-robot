"""Redis key protocol shared by qUnits and their consumers.

Keys use ``<unit-id> <attribute>``. This module is dependency-free so core
``qrobot`` remains Redis-ignorant while optional integrations share one grammar.
"""

from dataclasses import dataclass
from enum import StrEnum


class RedisAttribute(StrEnum):
    """Attributes published for a Redis-connected unit."""

    CLASS = "class"
    INPUT = "input"
    IN_QUNITS = "in_qunits"
    OUTPUT = "output"
    QUERY = "query"
    STATE = "state"


@dataclass(frozen=True)
class RedisKey:
    """Parsed qUnit Redis key.

    Parameters
    ----------
    unit_id : str
        Unit identifier portion of the key.
    attribute : RedisAttribute
        Published attribute represented by the key.
    """

    unit_id: str
    attribute: RedisAttribute


def build_redis_key(unit_id: str, attribute: RedisAttribute | str) -> str:
    """Build a validated ``<unit-id> <attribute>`` Redis key.

    Parameters
    ----------
    unit_id : str
        Non-empty unit identifier without surrounding whitespace.
    attribute : RedisAttribute or str
        Protocol attribute name or enum member.

    Returns
    -------
    str
        Redis key formed by joining the unit ID and attribute with one space.

    Raises
    ------
    TypeError
        If ``unit_id`` is not a string.
    ValueError
        If the unit ID is malformed or the attribute is unknown.
    """
    if not isinstance(unit_id, str):
        raise TypeError("unit_id must be a string")
    if not unit_id or unit_id != unit_id.strip():
        raise ValueError("unit_id must be non-empty and have no surrounding whitespace")
    try:
        protocol_attribute = RedisAttribute(attribute)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"unknown Redis attribute: {attribute!r}") from exc
    return f"{unit_id} {protocol_attribute.value}"


def parse_redis_key(key: str) -> RedisKey | None:
    """Parse a protocol key, returning ``None`` for malformed or unknown keys.

    Parameters
    ----------
    key : str
        Candidate Redis key.

    Returns
    -------
    RedisKey or None
        Parsed unit ID and attribute, or ``None`` when the key is outside the
        protocol.
    """
    if not isinstance(key, str):
        return None
    unit_id, separator, attribute = key.rpartition(" ")
    if not separator or not unit_id or unit_id != unit_id.strip():
        return None
    try:
        protocol_attribute = RedisAttribute(attribute)
    except ValueError:
        return None
    return RedisKey(unit_id, protocol_attribute)
