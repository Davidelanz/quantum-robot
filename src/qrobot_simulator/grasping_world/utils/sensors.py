"""Mappings from physical state to normalized sensor readings."""


def proximity_reading(distance: float, near: float, far: float) -> float:
    """Map distance to a normalized nearby-object signal.

    :param distance: Object distance in centimetres.
    :param near: Distance producing a full response.
    :param far: Distance producing a zero response.
    :returns: Proximity in the closed interval ``[0, 1]``.
    """
    if far <= near:
        raise ValueError("far must be greater than near")
    return min(1.0, max(0.0, (far - distance) / (far - near)))


def touch_reading(pressed: bool) -> float:
    """Map the touch switch to the model's empty-gripper signal."""
    return 0.0 if pressed else 1.0
