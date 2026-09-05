"""Tests for dashboard defaults."""

from qrobot_dashboard.config import Config


def test_default_config_points_to_packaged_assets() -> None:
    """Default assets are read from the dashboard package."""
    assert Config.DASH_TITLE == "Quantum-robot Dashboard"
    assert Config.DASH_DEBUG is False
    assert Config.DASH_AUTORELOAD is False
    assert Config.DASH_ASSETS_DIR.name == "assets"
    assert Config.DASH_ASSETS_DIR.is_dir()
