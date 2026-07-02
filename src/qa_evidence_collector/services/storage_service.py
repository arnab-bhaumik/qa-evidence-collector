from __future__ import annotations

import json
from pathlib import Path

from qa_evidence_collector.core.session_manager import SessionManager

_AUTOSAVE_FILE = Path.home() / ".qa_evidence_collector" / "autosave.json"


class StorageService:
    def save(self, session: SessionManager) -> None:
        _AUTOSAVE_FILE.parent.mkdir(parents=True, exist_ok=True)
        _AUTOSAVE_FILE.write_text(
            json.dumps(session.to_dict(), indent=2), encoding="utf-8"
        )

    def load(self, session: SessionManager) -> bool:
        if not _AUTOSAVE_FILE.exists():
            return False
        try:
            data = json.loads(_AUTOSAVE_FILE.read_text(encoding="utf-8"))
            session.load_dict(data)
            return True
        except Exception:
            return False

    def clear(self) -> None:
        if _AUTOSAVE_FILE.exists():
            _AUTOSAVE_FILE.unlink()

    def has_saved_session(self) -> bool:
        return _AUTOSAVE_FILE.exists()
