from __future__ import annotations

import os
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_STATE_FILE = ROOT_DIR / "runtime" / "state.json"


def allowed_origins() -> list[str]:
    raw_value = os.getenv("GLITCHLABS_ALLOWED_ORIGINS", "http://127.0.0.1:5173,http://localhost:5173")
    return [origin.strip() for origin in raw_value.split(",") if origin.strip()]


def state_file_path() -> Path:
    raw_value = os.getenv("GLITCHLABS_STATE_FILE")
    if not raw_value:
        return DEFAULT_STATE_FILE
    return Path(raw_value).expanduser().resolve()
