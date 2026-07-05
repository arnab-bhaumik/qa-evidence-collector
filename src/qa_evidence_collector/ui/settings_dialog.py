from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton,
    QHBoxLayout, QLabel, QCheckBox, QFileDialog, QGroupBox,
    QDialogButtonBox,
)
from PySide6.QtCore import Qt, QThread, Signal

from qa_evidence_collector.config.settings import Settings
from qa_evidence_collector.services.jira_service import JiraService


class _TestConnectionThread(QThread):
    result_ready = Signal(bool, str)

    def __init__(self, url: str, email: str, token: str) -> None:
        super().__init__()
        self._url = url
        self._email = email
        self._token = token

    def run(self) -> None:
        ok, msg = JiraService().test_connection(self._url, self._email, self._token)
        self.result_ready.emit(ok, msg)


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

        self.save_to_folder_cb = QCheckBox("Save report to folder")
        self.upload_to_jira_cb = QCheckBox("Upload report to Jira")
        output_form.addRow(self.save_to_folder_cb)
        output_form.addRow(self.upload_to_jira_cb)

        output_hint = QLabel("At least one option must be selected.")
        output_hint.setStyleSheet("color: #6c757d; font-size: 11px;")
        output_form.addRow(output_hint)

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

        self.jira_token_input = QLineEdit()
        self.jira_token_input.setFixedHeight(30)
        self.jira_token_input.setPlaceholderText("Paste your Atlassian API token")
        self.jira_token_input.setEchoMode(QLineEdit.EchoMode.Password)
        jira_form.addRow("API Token:", self.jira_token_input)

        token_hint = QLabel(
            "Generate your token at "
            "<a href='https://id.atlassian.com/manage-profile/security/api-tokens'>"
            "id.atlassian.com</a>"
        )
        token_hint.setStyleSheet("color: #6c757d; font-size: 11px;")
        token_hint.setTextFormat(Qt.TextFormat.RichText)
        token_hint.setOpenExternalLinks(True)
        jira_form.addRow(token_hint)

        # Test Connection button + inline status
        test_conn_row = QHBoxLayout()
        self.test_conn_btn = QPushButton("Test Connection")
        self.test_conn_btn.setFixedHeight(30)
        self.test_conn_btn.clicked.connect(self._test_connection)
        self._conn_status = QLabel()
        self._conn_status.setStyleSheet("font-size: 11px;")
        test_conn_row.addWidget(self.test_conn_btn)
        test_conn_row.addSpacing(10)
        test_conn_row.addWidget(self._conn_status, 1)
        jira_form.addRow(test_conn_row)

        layout.addWidget(jira_group)

        # --- Global Save / Cancel ---
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

        self.save_to_folder_cb.setChecked(self._settings.output_save_to_folder)
        self.upload_to_jira_cb.setChecked(self._settings.output_upload_to_jira)

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

    def _test_connection(self) -> None:
        url   = self.jira_url_input.text().strip()
        email = self.jira_email_input.text().strip()
        token = self.jira_token_input.text().strip()

        self.test_conn_btn.setEnabled(False)
        self.test_conn_btn.setText("Testing…")
        self._conn_status.setText("")

        self._conn_thread = _TestConnectionThread(url, email, token)
        self._conn_thread.result_ready.connect(self._on_connection_result)
        self._conn_thread.start()

    def _on_connection_result(self, success: bool, message: str) -> None:
        self.test_conn_btn.setEnabled(True)
        self.test_conn_btn.setText("Test Connection")
        color = "#27ae60" if success else "#e74c3c"
        self._conn_status.setStyleSheet(f"font-size: 11px; color: {color};")
        self._conn_status.setText(message)

    def _save(self) -> None:
        save_to_folder = self.save_to_folder_cb.isChecked()
        upload_to_jira = self.upload_to_jira_cb.isChecked()
        if not save_to_folder and not upload_to_jira:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self, "Output Options",
                "Please select at least one output option:\n"
                "Save to folder or Upload to Jira."
            )
            return

        self._settings.output_dir = self.dir_input.text().strip()
        self._settings.capture_hotkey = self.hotkey_input.text().strip()
        self._settings.hotkey_enabled = self.hotkey_enabled_cb.isChecked()
        self._settings.output_save_to_folder = save_to_folder
        self._settings.output_upload_to_jira = upload_to_jira

        self._settings.jira_url = self.jira_url_input.text().strip()
        self._settings.jira_project_key = self.jira_project_input.text().strip()
        self._settings.jira_email = self.jira_email_input.text().strip()
        self._settings.jira_api_token = self.jira_token_input.text().strip()

        self._settings.save()
        self.accept()
