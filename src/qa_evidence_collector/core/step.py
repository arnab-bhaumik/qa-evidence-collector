from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Step:
    step_number: int
    screenshot_path: str
    note: str = ""
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            "step_number": self.step_number,
            "screenshot_path": self.screenshot_path,
            "note": self.note,
            "timestamp": self.timestamp.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Step":
        return cls(
            step_number=data["step_number"],
            screenshot_path=data["screenshot_path"],
            note=data.get("note", ""),
            timestamp=datetime.fromisoformat(data["timestamp"]),
        )
