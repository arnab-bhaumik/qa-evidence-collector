from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton,
    QHBoxLayout, QLabel, QCheckBox, QFileDialog, QDialogButtonBox,
    QGroupBox,
)
from PySide6.QtCore import Qt

from qa_evidence_collector.config.settings import Settings


class SettingsDialog(QDialog):
    def __init__(self, settings: Settings, parent=None) -> None:
        super().__init__(parent)
        self._settings = settings
        self.setWindowTitle("Settings")
        self.setMinimumWidth(480)
        self.setWindowFlags(
            self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint
        )
        self._build_ui()
        self._load_values()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(14)

        # --- Output folder ---
        output_group = QGroupBox("Output")
        output_form = QFormLayout(output_group)

        dir_row = QHBoxLayout()
        self.dir_input = QLineEdit()
        self.dir_input.setFixedHeight(30)
        dir_row.addWidget(self.dir_input)

        browse_btn = QPushButton("Browse…")
        browse_btn.setFixedHeight(30)
        browse_btn.clicked.connect(self._browse_dir)
        dir_row.addWidget(browse_btn)

        output_form.addRow("Save location:", dir_row)
        layout.addWidget(output_group)

        # --- Hotkey ---
        hotkey_group = QGroupBox("Global Hotkey")
        hotkey_form = QFormLayout(hotkey_group)

        self.hotkey_enabled_cb = QCheckBox("Enable global capture hotkey")
        hotkey_form.addRow(self.hotkey_enabled_cb)

        self.hotkey_input = QLineEdit()
        self.hotkey_input.setFixedHeight(30)
        self.hotkey_input.setPlaceholderText("e.g. <ctrl>+<shift>+s")
        hotkey_form.addRow("Hotkey combination:", self.hotkey_input)

        hint = QLabel(
            "Use pynput format: &lt;ctrl&gt;, &lt;shift&gt;, &lt;alt&gt; + a letter.<br>"
            "Example: <b>&lt;ctrl&gt;+&lt;shift&gt;+s</b>"
        )
        hint.setStyleSheet("color: #6c757d; font-size: 11px;")
        hint.setTextFormat(Qt.TextFormat.RichText)
        hotkey_form.addRow(hint)

        self.hotkey_enabled_cb.toggled.connect(self.hotkey_input.setEnabled)
        layout.addWidget(hotkey_group)

        # --- Jira Configuration ---
        jira_group = QGroupBox("Jira Configuration")
        jira_form = QFormLayout(jira_group)

        self.jira_url_input = QLineEdit()
        self.jira_url_input.setFixedHeight(30)
        self.jira_url_input.setPlaceholderText("https://yourcompany.atlassian.net")
        jira_form.addRow("Jira URL:", self.jira_url_input)

        self.jira_project_input = QLineEdit()
        self.jira_project_input.setFixedHeight(30)
        self.jira_project_input.setPlaceholderText("e.g. QA")
        jira_form.addRow("Project Key:", self.jira_project_input)

        self.jira_email_input = QLineEdit()
        self.jira_email_input.setFixedHeight(30)
        self.jira_email_input.setPlaceholderText("your-email@company.com")
        jira_form.addRow("Email:", self.jira_email_input)

        # API Token with Show/Hide toggle
        token_row = QHBoxLayout()
        self.jira_token_input = QLineEdit()
        self.jira_token_input.setFixedHeight(30)
        self.jira_token_input.setPlaceholderText("Paste your Atlassian API token")
        self.jira_token_input.setEchoMode(QLineEdit.EchoMode.Password)
        self._token_visible = False
        self.toggle_token_btn = QPushButton("Show")
        self.toggle_token_btn.setFixedSize(50, 30)
        self.toggle_token_btn.clicked.connect(self._toggle_token)
        token_row.addWidget(self.jira_token_input)
        token_row.addWidget(self.toggle_token_btn)
        jira_form.addRow("API Token:", token_row)

        token_hint = QLabel(
            "Generate your token at "
            "<a href='https://id.atlassian.com/manage-profile/security/api-tokens'>"
            "id.atlassian.com</a>"
        )
        token_hint.setStyleSheet("color: #6c757d; font-size: 11px;")
        token_hint.setTextFormat(Qt.TextFormat.RichText)
        token_hint.setOpenExternalLinks(True)
        jira_form.addRow(token_hint)

        layout.addWidget(jira_group)

        # --- Buttons ---
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _load_values(self) -> None:
        self.dir_input.setText(self._settings.output_dir)
        self.hotkey_input.setText(self._settings.capture_hotkey)
        self.hotkey_enabled_cb.setChecked(self._settings.hotkey_enabled)
        self.hotkey_input.setEnabled(self._settings.hotkey_enabled)

        self.jira_url_input.setText(self._settings.jira_url)
        self.jira_project_input.setText(self._settings.jira_project_key)
        self.jira_email_input.setText(self._settings.jira_email)
        self.jira_token_input.setText(self._settings.jira_api_token)

    def _browse_dir(self) -> None:
        folder = QFileDialog.getExistingDirectory(
            self, "Select Output Folder", self.dir_input.text()
        )
        if folder:
            self.dir_input.setText(folder)

    def _toggle_token(self) -> None:
        self._token_visible = not self._token_visible
        self.jira_token_input.setEchoMode(
            QLineEdit.EchoMode.Normal if self._token_visible
            else QLineEdit.EchoMode.Password
        )
        self.toggle_token_btn.setText("Hide" if self._token_visible else "Show")

    def _save(self) -> None:
        self._settings.output_dir = self.dir_input.text().strip()
        self._settings.capture_hotkey = self.hotkey_input.text().strip()
        self._settings.hotkey_enabled = self.hotkey_enabled_cb.isChecked()

        self._settings.jira_url = self.jira_url_input.text().strip()
        self._settings.jira_project_key = self.jira_project_input.text().strip()
        self._settings.jira_email = self.jira_email_input.text().strip()
        self._settings.jira_api_token = self.jira_token_input.text().strip()

        self._settings.save()
        self.accept()
