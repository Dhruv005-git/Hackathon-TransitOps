"""
app/config.py

Purpose:
    Centralized configuration for the entire TransitOps application.
    All settings live here — no magic strings scattered across modules.

Reason:
    Single source of truth for database path, secret key, app name, theme,
    and debug mode. Reads from .env so settings can change without touching code.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Resolve project root (parent of app/)
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env from project root
load_dotenv(BASE_DIR / ".env")

# --- Application Settings ---
APP_NAME: str = os.getenv("APP_NAME", "TransitOps")
DEBUG: bool = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")
SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production")
THEME: str = os.getenv("THEME", "dark")

# --- Database Settings ---
DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///data/transitops.db")

# For SQLite, resolve relative paths against BASE_DIR
if DATABASE_URL.startswith("sqlite:///") and not Path(DATABASE_URL.replace("sqlite:///", "")).is_absolute():
    _relative_path = DATABASE_URL.replace("sqlite:///", "")
    DATABASE_PATH: Path = BASE_DIR / _relative_path
    DATABASE_URL = f"sqlite:///{DATABASE_PATH}"
else:
    DATABASE_PATH = Path(DATABASE_URL.replace("sqlite:///", ""))

# Ensure data directory exists
DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
