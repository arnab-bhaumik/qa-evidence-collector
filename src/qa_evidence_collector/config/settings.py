from __future__ import annotations

import json
from pathlib import Path


_DEFAULT_SETTINGS = {
    "output_dir": str(Path.home() / "QAEvidence"),
    "capture_hotkey": "<ctrl>+<shift>+s",
    "hotkey_enabled": True,
    "jira_url": "",
    "jira_project_key": "",
    "jira_email": "",
    "jira_api_token": "",
}

_SETTINGS_FILE = Path.home() / ".qa_evidence_collector" / "settings.json"


class Settings:
    def __init__(self) -> None:
        self._data: dict = dict(_DEFAULT_SETTINGS)
        self.load()

    # ------------------------------------------------------------------
    # Properties — General
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
    # Properties — Jira
    # ------------------------------------------------------------------

    @property
    def jira_url(self) -> str:
        return self._data.get("jira_url", "")

    @jira_url.setter
    def jira_url(self, value: str) -> None:
        self._data["jira_url"] = value.rstrip("/")

    @property
    def jira_project_key(self) -> str:
        return self._data.get("jira_project_key", "")

    @jira_project_key.setter
    def jira_project_key(self, value: str) -> None:
        self._data["jira_project_key"] = value.upper().strip()

    @property
    def jira_email(self) -> str:
        return self._data.get("jira_email", "")

    @jira_email.setter
    def jira_email(self, value: str) -> None:
        self._data["jira_email"] = value.strip()

    @property
    def jira_api_token(self) -> str:
        return self._data.get("jira_api_token", "")

    @jira_api_token.setter
    def jira_api_token(self, value: str) -> None:
        self._data["jira_api_token"] = value.strip()

    @property
    def jira_configured(self) -> bool:
        return bool(self.jira_url and self.jira_email and self.jira_api_token)

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
