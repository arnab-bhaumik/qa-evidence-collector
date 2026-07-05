import re

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QTextEdit,
    QPushButton, QHBoxLayout, QLabel, QDialogButtonBox, QFrame,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class IssueKeyDialog(QDialog):
    def __init__(self, report_path: str, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Upload to Jira")
        self.setMinimumWidth(420)
        self.setWindowFlags(
            self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint
        )
        self._report_path = report_path
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        # Header
        title = QLabel("Upload Report to Jira")
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(title)

        subtitle = QLabel(f"File: <b>{self._report_path.split('/')[-1].split(chr(92))[-1]}</b>")
        subtitle.setStyleSheet("font-size: 11px; color: #7f8c8d;")
        subtitle.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(subtitle)

        # Divider
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("color: #dee2e6;")
        layout.addWidget(line)

        # Form
        form = QFormLayout()
        form.setSpacing(10)

        self.issue_key_input = QLineEdit()
        self.issue_key_input.setFixedHeight(32)
        self.issue_key_input.setPlaceholderText("e.g. QA-123")
        self._key_error = QLabel()
        self._key_error.setStyleSheet("color: #e74c3c; font-size: 11px;")
        self._key_error.hide()
        form.addRow("Issue Key:", self.issue_key_input)
        form.addRow("", self._key_error)

        self.comment_input = QTextEdit()
        self.comment_input.setFixedHeight(80)
        self.comment_input.setPlaceholderText(
            "Optional: add a comment to the Jira issue activity feed…"
        )
        form.addRow("Comment:", self.comment_input)

        layout.addLayout(form)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedHeight(32)
        cancel_btn.clicked.connect(self.reject)

        self.upload_btn = QPushButton("Upload")
        self.upload_btn.setFixedHeight(32)
        self.upload_btn.setStyleSheet(
            """
            QPushButton {
                background: #2980b9;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                padding: 0 20px;
            }
            QPushButton:hover { background: #2471a3; }
            QPushButton:disabled { background: #bdc3c7; color: #7f8c8d; }
            """
        )
        self.upload_btn.clicked.connect(self._on_upload)

        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(self.upload_btn)
        layout.addLayout(btn_row)

        self.issue_key_input.setFocus()

    def _on_upload(self) -> None:
        key = self.issue_key_input.text().strip().upper()
        if not re.match(r'^[A-Z]+-\d+$', key):
            self._key_error.setText("Invalid format — use PROJECT-NUMBER, e.g. QA-123")
            self._key_error.show()
            self.issue_key_input.setFocus()
            return
        self._key_error.hide()
        self.issue_key_input.setText(key)
        self.accept()

    def issue_key(self) -> str:
        return self.issue_key_input.text().strip().upper()

    def comment(self) -> str:
        return self.comment_input.toPlainText().strip()
