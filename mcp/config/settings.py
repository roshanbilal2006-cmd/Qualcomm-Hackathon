"""
Centralized application configuration.
All environment-driven settings are defined here. No other module
should read environment variables directly - always go through
get_settings().
"""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

# Anchor all package-relative paths to the mcp/ package directory itself,
# not to the process's current working directory. This file lives at
# mcp/config/settings.py, so its parent's parent is the mcp/ package root.
PACKAGE_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    # --- Mode switches: control which adapters the factory builds ---
    sensor_mode: Literal["demo", "live"] = "demo"
    rera_mode: Literal["mock", "live"] = "mock"

    # --- Arduino / serial configuration (used only in live sensor mode) ---
    arduino_port: str = "/dev/ttyUSB0"
    arduino_baud_rate: int = 9600
    arduino_read_timeout_seconds: float = 2.0

    # --- Mock RERA dataset location (used only in mock RERA mode) ---
    mock_rera_data_path: str = str(PACKAGE_ROOT / "data" / "mock_rera.json")

    # --- Live RERA configuration (reserved for future use) ---
    live_rera_base_url: str | None = None
    live_rera_api_key: str | None = None

    # --- Logging ---
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=str(PACKAGE_ROOT / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    """
    Returns a cached Settings instance so the whole application
    shares one consistent configuration snapshot per process.
    """
    return Settings()