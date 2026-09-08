"""Mappings from normalized bug activations to body commands."""

from ..robots.config import BaseBugConfig

Activations = dict[str, float]


def motion_commands(
    activations: Activations,
    config: BaseBugConfig,
) -> tuple[float, float, bool]:
    """Combine opposing activations into speed, turn, and bite commands."""
    forward = activations.get("forward", 0.0)
    backward = activations.get("backward", 0.0)
    left = activations.get("rotate_left", 0.0)
    right = activations.get("rotate_right", 0.0)
    biting = activations.get("bite", 0.0) > config.bite_activation_threshold
    speed = config.forward_gain * forward - config.backward_gain * backward
    turn = config.rotation_gain * (left - right)
    return speed, turn, biting


def behavior_label(speed: float, turn: float, forward: float, biting: bool) -> str:
    """Translate effective body commands into a concise display label."""
    if biting:
        return "BITE"
    if speed > 0 and turn:
        return "FWD LEFT" if turn > 0 else "FWD RIGHT"
    if speed < 0 or (turn and not forward):
        return "BACK LEFT" if turn > 0 else "BACK RIGHT"
    if speed > 0:
        return "FORWARD"
    if turn:
        return "TURN LEFT" if turn > 0 else "TURN RIGHT"
    return ""
