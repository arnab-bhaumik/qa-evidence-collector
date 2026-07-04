from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class TestResultDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Test Result")
        self.setFixedSize(380, 220)
        self.setWindowFlags(
            self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setStyleSheet("QDialog { background: #f8f9fa; }")
        self._result: str = "NOT SET"
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        # Title
        title = QLabel("What is the test result?")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 15px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(title)

        subtitle = QLabel("Select the outcome before generating the report.")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("font-size: 12px; color: #7f8c8d;")
        layout.addWidget(subtitle)

        # Divider
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("color: #dee2e6;")
        layout.addWidget(line)

        # Pass / Fail buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(16)

        self._btn_pass = self._make_result_btn("✅  PASSED", "#27ae60", "#1e8449")
        self._btn_fail = self._make_result_btn("❌  FAILED", "#e74c3c", "#c0392b")

        self._btn_pass.clicked.connect(lambda: self._select("PASSED"))
        self._btn_fail.clicked.connect(lambda: self._select("FAILED"))

        btn_row.addWidget(self._btn_pass)
        btn_row.addWidget(self._btn_fail)
        layout.addLayout(btn_row)

    def _make_result_btn(self, label: str, color: str, hover: str) -> QPushButton:
        btn = QPushButton(label)
        btn.setFixedHeight(56)
        font = QFont("Segoe UI", 13, QFont.Weight.Bold)
        btn.setFont(font)
        btn.setStyleSheet(
            f"""
            QPushButton {{
                background: {color};
                color: white;
                border: none;
                border-radius: 10px;
            }}
            QPushButton:hover {{
                background: {hover};
            }}
            QPushButton:pressed {{
                background: {hover};
                padding-top: 2px;
            }}
            """
        )
        return btn

    def _select(self, result: str) -> None:
        self._result = result
        self.accept()

    def result_status(self) -> str:
        return self._result
