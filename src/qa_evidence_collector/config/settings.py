from __future__ import annotations

import json
from pathlib import Path


_DEFAULT_SETTINGS = {
    "output_dir": str(Path.home() / "QAEvidence"),
    "capture_hotkey": "<ctrl>+<shift>+s",
    "hotkey_enabled": True,
}

_SETTINGS_FILE = Path.home() / ".qa_evidence_collector" / "settings.json"


class Settings:
    def __init__(self) -> None:
        self._data: dict = dict(_DEFAULT_SETTINGS)
        self.load()

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def output_dir(self) -> str:
        return self._data["output_dir"]

    @output_dir.setter
    def output_dir(self, value: str) -> None:
        self._data["output_dir"] = value

    @property
    def capture_hotkey(self) -> str:
        return self._data["capture_hotkey"]

    @capture_hotkey.setter
    def capture_hotkey(self, value: str) -> None:
        self._data["capture_hotkey"] = value

    @property
    def hotkey_enabled(self) -> bool:
        return self._data["hotkey_enabled"]

    @hotkey_enabled.setter
    def hotkey_enabled(self, value: bool) -> None:
        self._data["hotkey_enabled"] = value

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def load(self) -> None:
        if _SETTINGS_FILE.exists():
            try:
                saved = json.loads(_SETTINGS_FILE.read_text(encoding="utf-8"))
                self._data.update(saved)
            except Exception:
                pass

    def save(self) -> None:
        _SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
        _SETTINGS_FILE.write_text(
            json.dumps(self._data, indent=2), encoding="utf-8"
        )
