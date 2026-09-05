"""Tests for dashboard page components."""

from dash.development.base_component import Component

from qrobot_dashboard.layout import (
    DEFAULT_REFRESH_SECONDS,
    MAX_REFRESH_SECONDS,
    MIN_REFRESH_SECONDS,
    NETWORK_GRAPH_ID,
    REFRESH_INTERVAL_ID,
    REFRESH_LABEL_ID,
    REFRESH_SLIDER_ID,
    build_controls,
    build_layout,
    build_network_panel,
)


def component_ids(component: Component) -> set[str]:
    """Collect component IDs from a Dash component tree."""
    ids = {component.id} if getattr(component, "id", None) else set()
    children = getattr(component, "children", None)
    descendants = children if isinstance(children, list) else [children]
    return ids | {
        component_id
        for child in descendants
        if isinstance(child, Component)
        for component_id in component_ids(child)
    }


def test_build_controls_contains_refresh_inputs() -> None:
    """The control panel contains both parts of the refresh control."""
    controls = build_controls()
    assert component_ids(controls) == {REFRESH_SLIDER_ID, REFRESH_LABEL_ID}
    slider = controls.children[1].children[0]
    assert (slider.min, slider.max, slider.step) == (
        MIN_REFRESH_SECONDS,
        MAX_REFRESH_SECONDS,
        0.5,
    )
    assert slider.marks == {0.5: "0.5", 1: "1", 2: "2", 5: "5", 10: "10 s"}
    assert slider.updatemode == "mouseup"


def test_build_network_panel_contains_graph() -> None:
    """The network panel exposes the callback graph target."""
    assert component_ids(build_network_panel()) == {NETWORK_GRAPH_ID}


def test_build_layout_contains_callback_targets_and_safe_interval() -> None:
    """A fresh layout starts at one second and includes every callback target."""
    layout = build_layout()
    assert component_ids(layout) == {
        REFRESH_SLIDER_ID,
        REFRESH_LABEL_ID,
        REFRESH_INTERVAL_ID,
        NETWORK_GRAPH_ID,
    }
    interval = next(
        child for child in layout.children if getattr(child, "id", None) == REFRESH_INTERVAL_ID
    )
    assert interval.interval == DEFAULT_REFRESH_SECONDS * 1000
