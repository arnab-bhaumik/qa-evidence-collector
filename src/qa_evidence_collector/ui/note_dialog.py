from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QDialogButtonBox, QFrame,
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt


class NoteDialog(QDialog):
    def __init__(self, step_number: int, screenshot_path: str, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(f"Step {step_number} — Add Note")
        self.setMinimumWidth(520)
        self.setWindowFlags(
            self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint
        )

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Thumbnail preview
        thumb = QLabel()
        thumb.setAlignment(Qt.AlignmentFlag.AlignCenter)
        thumb.setFrameShape(QFrame.Shape.StyledPanel)
        thumb.setFixedHeight(180)
        pixmap = QPixmap(screenshot_path)
        if not pixmap.isNull():
            thumb.setPixmap(
                pixmap.scaled(480, 180, Qt.AspectRatioMode.KeepAspectRatio,
                              Qt.TransformationMode.SmoothTransformation)
            )
        else:
            thumb.setText("Screenshot preview unavailable")
        layout.addWidget(thumb)

        layout.addWidget(QLabel(f"<b>Step {step_number}</b> — describe what this step does:"))

        self.note_input = QTextEdit()
        self.note_input.setPlaceholderText("e.g. Clicked the Login button and verified redirect to dashboard")
        self.note_input.setFixedHeight(80)
        layout.addWidget(self.note_input)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Discard
        )
        buttons.accepted.connect(self.accept)
        buttons.button(QDialogButtonBox.StandardButton.Discard).clicked.connect(self.reject)
        layout.addWidget(buttons)

        self.note_input.setFocus()

    def note(self) -> str:
        return self.note_input.toPlainText().strip()
