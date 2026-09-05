"""Default configuration for the dashboard application."""

from pathlib import Path


class Config:
    """Settings used by the Flask server and its mounted Dash application."""

    DASH_TITLE = "Quantum-robot Dashboard"
    DASH_DEBUG = False
    DASH_AUTORELOAD = False
    DASH_ASSETS_DIR = Path(__file__).parent / "assets"
