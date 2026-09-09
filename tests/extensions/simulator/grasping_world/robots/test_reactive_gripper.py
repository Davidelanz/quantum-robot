"""How current proximity and touch readings control the reactive gripper."""

from qrobot_simulator.grasping_world.robots.reactive_gripper import ReactiveGripper


def test_reactive_gripper_closes_immediately_when_the_ball_is_near() -> None:
    """One near reading is sufficient because this robot has no memory."""
    gripper = ReactiveGripper()

    assert gripper.command({"proximity": 1.0, "touch": 1.0}, 0.1) == 1.0


def test_reactive_gripper_holds_a_touched_ball_and_opens_when_empty() -> None:
    """Current contact closes the jaws and an empty reading opens them."""
    gripper = ReactiveGripper()
    gripper.command({"proximity": 1.0, "touch": 1.0}, 0.1)

    assert gripper.command({"proximity": 0.0, "touch": 0.0}, 0.1) == 1.0
    assert gripper.command({"proximity": 0.0, "touch": 1.0}, 0.1) == 0.0
