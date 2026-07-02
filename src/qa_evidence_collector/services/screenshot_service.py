from pathlib import Path
from datetime import datetime

import mss
import mss.tools


class ScreenshotService:
    def __init__(self, output_dir: str | Path = "") -> None:
        self.output_dir = Path(output_dir) if output_dir else Path.home() / "QAEvidence"

    def set_output_dir(self, path: str | Path) -> None:
        self.output_dir = Path(path)

    def capture_fullscreen(self, session_name: str, step_number: int) -> str:
        folder = self._ensure_session_folder(session_name)
        filename = f"step_{step_number:03d}_{datetime.now().strftime('%H%M%S')}.png"
        filepath = folder / filename

        with mss.mss() as sct:
            monitor = sct.monitors[0]  # all monitors combined
            screenshot = sct.grab(monitor)
            mss.tools.to_png(screenshot.rgb, screenshot.size, output=str(filepath))

        return str(filepath)

    def session_folder(self, session_name: str) -> Path:
        safe_name = "".join(c if c.isalnum() or c in " _-" else "_" for c in session_name)
        return self.output_dir / safe_name.strip()

    def _ensure_session_folder(self, session_name: str) -> Path:
        folder = self.session_folder(session_name)
        folder.mkdir(parents=True, exist_ok=True)
        return folder
