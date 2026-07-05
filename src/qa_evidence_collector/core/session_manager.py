from __future__ import annotations

from datetime import datetime
from pathlib import Path

from qa_evidence_collector.core.step import Step


class SessionManager:
    def __init__(self) -> None:
        self.session_name: str = ""
        self.test_case_id: str = ""
        self.test_objective: str = ""
        self.status: str = "NOT SET"
        self.created_at: datetime | None = None
        self.steps: list[Step] = []
        self._active: bool = False

    # ------------------------------------------------------------------
    # Session lifecycle
    # ------------------------------------------------------------------

    def start(self, name: str, test_case_id: str = "", test_objective: str = "") -> None:
        self.session_name = name.strip() or "Untitled Session"
        self.test_case_id = test_case_id.strip()
        self.test_objective = test_objective.strip()
        self.status = "NOT SET"
        self.created_at = datetime.now()
        self.steps = []
        self._active = True

    def stop(self) -> None:
        self._active = False

    @property
    def is_active(self) -> bool:
        return self._active

    # ------------------------------------------------------------------
    # Step management
    # ------------------------------------------------------------------

    def add_step(self, screenshot_path: str, note: str = "") -> Step:
        step = Step(
            step_number=len(self.steps) + 1,
            screenshot_path=screenshot_path,
            note=note,
        )
        self.steps.append(step)
        return step

    def delete_step(self, index: int) -> None:
        if 0 <= index < len(self.steps):
            self.steps.pop(index)
            self._renumber()

    def move_step(self, from_index: int, to_index: int) -> None:
        if from_index == to_index:
            return
        step = self.steps.pop(from_index)
        self.steps.insert(to_index, step)
        self._renumber()

    def update_note(self, index: int, note: str) -> None:
        if 0 <= index < len(self.steps):
            self.steps[index].note = note

    def _renumber(self) -> None:
        for i, step in enumerate(self.steps):
            step.step_number = i + 1

    # ------------------------------------------------------------------
    # Serialisation (used by storage_service)
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        return {
            "session_name": self.session_name,
            "test_case_id": self.test_case_id,
            "test_objective": self.test_objective,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "active": self._active,
            "steps": [s.to_dict() for s in self.steps],
        }

    def load_dict(self, data: dict) -> None:
        self.session_name = data.get("session_name", "")
        self.test_case_id = data.get("test_case_id", "")
        self.test_objective = data.get("test_objective", "")
        self.status = data.get("status", "NOT SET")
        created = data.get("created_at")
        self.created_at = datetime.fromisoformat(created) if created else None
        self._active = data.get("active", False)
        self.steps = [Step.from_dict(s) for s in data.get("steps", [])]
