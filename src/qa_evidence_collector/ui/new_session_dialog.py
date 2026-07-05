from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit,
    QDialogButtonBox, QTextEdit,
)
from PySide6.QtCore import Qt


class NewSessionDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("New Session")
        self.setMinimumWidth(420)
        self.setWindowFlags(
            self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint
        )

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        form = QFormLayout()
        form.setSpacing(10)

        self.tc_id_input = QLineEdit()
        self.tc_id_input.setPlaceholderText("e.g. TC-042")
        self.tc_id_input.setFixedHeight(32)
        form.addRow("Test Case ID:", self.tc_id_input)

        self.objective_input = QTextEdit()
        self.objective_input.setPlaceholderText("e.g. Verify user can log in with valid credentials")
        self.objective_input.setFixedHeight(80)
        self.objective_input.setAcceptRichText(False)
        form.addRow("Test Objective:", self.objective_input)

        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.tc_id_input.setFocus()

    def session_name(self) -> str:
        tc_id = self.tc_id_input.text().strip()
        objective = self.objective_input.toPlainText().strip()
        if tc_id and objective:
            return f"{tc_id} — {objective}"
        return tc_id or objective or "Untitled Session"

    def test_case_id(self) -> str:
        return self.tc_id_input.text().strip()

    def test_objective(self) -> str:
        return self.objective_input.toPlainText().strip()
