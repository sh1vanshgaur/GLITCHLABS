from __future__ import annotations

import json
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any


class StateStore:
    def __init__(self, file_path: Path) -> None:
        self.file_path = file_path
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> dict[str, Any]:
        if not self.file_path.exists():
            return {"lobbies": [], "sessions": []}

        try:
            return json.loads(self.file_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {"lobbies": [], "sessions": []}

    def save(self, payload: dict[str, Any]) -> None:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        with NamedTemporaryFile("w", delete=False, dir=self.file_path.parent, encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=True, indent=2)
            temp_path = Path(handle.name)
        temp_path.replace(self.file_path)
