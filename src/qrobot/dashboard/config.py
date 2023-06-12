"""
Configuration used by the create_app function.

Note: keep it free of inner-project import statements to help prevent circular imports.
"""
from pathlib import Path


class Config:
    """Configuration object for the Dashboard."""

    # User configurations
    DASH_TITLE = "Quantum-robot Dashboard"
    DASH_DEBUG = False
    DASH_AUTORELOAD = False
    DASH_ASSETS_DIR = Path(__file__).parent.joinpath("assets")

    # Flask configurations (https://flask.palletsprojects.com/en/latest/config/)
    # (...)
