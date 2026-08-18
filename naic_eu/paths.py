"""Pad-hulp voor lokale package (P:/Jules/Apps/NAIC)."""

from __future__ import annotations

import os
from pathlib import Path

# Projectroot = map waarin pyproject.toml, schema.sql en config/ staan
PROJECT_ROOT = Path(
    os.environ.get("NAIC_APP_DIR", Path(__file__).resolve().parent.parent)
)

SCHEMA_PATH = PROJECT_ROOT / "schema.sql"
CONFIG_DIR = PROJECT_ROOT / "config"
UNIVERSE_PATH = CONFIG_DIR / "universes.yaml"
DEFAULT_DATA_DIR = Path(os.environ.get("NAIC_DATA_DIR", PROJECT_ROOT / "data"))
DEFAULT_DB_PATH = Path(os.environ.get("NAIC_DB_PATH", DEFAULT_DATA_DIR / "naic_eu.db"))
DEFAULT_LOG_DIR = Path(os.environ.get("NAIC_LOG_DIR", PROJECT_ROOT / "logs"))
