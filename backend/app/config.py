from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_STATE_FILE = ROOT_DIR / "runtime" / "state.json"

# Load .env from the backend/ directory (where ROOT_DIR points to)
_env_path = ROOT_DIR / ".env"
load_dotenv(dotenv_path=_env_path)

print(f"[CONFIG] Loaded .env from: {_env_path} (exists: {_env_path.exists()})")
print(f"[CONFIG] HF_TOKEN set: {bool(os.getenv('HF_TOKEN'))}")


def allowed_origins() -> list[str]:
    raw_value = os.getenv("GLITCHLABS_ALLOWED_ORIGINS", "http://127.0.0.1:5173,http://localhost:5173")
    return [origin.strip() for origin in raw_value.split(",") if origin.strip()]


def state_file_path() -> Path:
    raw_value = os.getenv("GLITCHLABS_STATE_FILE")
    if not raw_value:
        return DEFAULT_STATE_FILE
    return Path(raw_value).expanduser().resolve()


def hf_api_key() -> str | None:
    return os.getenv("HF_TOKEN")


def use_llm_generation() -> bool:
    """Enable LLM generation if an API key is available."""
    return bool(hf_api_key())

