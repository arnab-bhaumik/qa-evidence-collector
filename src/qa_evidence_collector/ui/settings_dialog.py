from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton,
    QHBoxLayout, QLabel, QCheckBox, QFileDialog, QDialogButtonBox,
    QFrame, QScrollArea, QWidget,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from qa_evidence_collector.config.settings import Settings


# ---------------------------------------------------------------------------
# Helper — styled card section
# ---------------------------------------------------------------------------

def _make_section(title: str, accent: str = "#4a9eff") -> tuple[QFrame, QVBoxLayout]:
    card = QFrame()
    card.setObjectName("sectionCard")
    card.setStyleSheet(
        f"""
        QFrame#sectionCard {{
            background: #2a2d3e;
            border: 1px solid #3a3d50;
            border-radius: 10px;
            padding: 4px;
        }}
        """
    )
    inner = QVBoxLayout(card)
    inner.setContentsMargins(16, 12, 16, 14)
    inner.setSpacing(10)

    header = QLabel(title)
    header.setStyleSheet(
        f"font-size: 12px; font-weight: bold; color: {accent}; "
        f"padding-bottom: 4px; border-bottom: 1px solid #3a3d50;"
    )
    inner.addWidget(header)

    return card, inner


def _styled_input(placeholder: str = "", password: bool = False) -> QLineEdit:
    inp = QLineEdit()
    inp.setFixedHeight(34)
    inp.setPlaceholderText(placeholder)
    if password:
        inp.setEchoMode(QLineEdit.EchoMode.Password)
    inp.setStyleSheet(
        """
        QLineEdit {
            background: #1e2030;
            color: #e0e0e0;
            border: 1px solid #3a3d50;
            border-radius: 6px;
            padding: 0 10px;
            font-size: 12px;
        }
        QLineEdit:focus {
            border: 1px solid #4a9eff;
        }
        QLineEdit:disabled {
            color: #555;
            background: #1a1c2a;
        }
        """
    )
    return inp


def _form_row(label_text: str, widget) -> QHBoxLayout:
    row = QHBoxLayout()
    row.setSpacing(12)
    lbl = QLabel(label_text)
    lbl.setFixedWidth(110)
    lbl.setStyleSheet("color: #a0a8c0; font-size: 12px;")
    lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
    row.addWidget(lbl)
    row.addWidget(widget, 1)
    return row


# ---------------------------------------------------------------------------
# SettingsDialog
# ---------------------------------------------------------------------------

class SettingsDialog(QDialog):
    def __init__(self, settings: Settings, parent=None) -> None:
        super().__init__(parent)
        self._settings = settings
        self.setWindowTitle("Settings")
        self.setMinimumWidth(520)
        self.setMinimumHeight(560)
        self.setWindowFlags(
            self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setStyleSheet(
            """
            QDialog {
                background: #1e2030;
            }
            QLabel {
                color: #c8d0e0;
            }
            QCheckBox {
                color: #c8d0e0;
                font-size: 12px;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 16px; height: 16px;
                border-radius: 4px;
                border: 1px solid #3a3d50;
                background: #1e2030;
            }
            QCheckBox::indicator:checked {
                background: #4a9eff;
                border: 1px solid #4a9eff;
            }
            QPushButton#actionBtn {
                background: #4a9eff;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 12px;
                font-weight: bold;
                padding: 0 16px;
                height: 34px;
            }
            QPushButton#actionBtn:hover {
                background: #3a8eef;
            }
            QPushButton#secondaryBtn {
                background: #2a2d3e;
                color: #c8d0e0;
                border: 1px solid #3a3d50;
                border-radius: 6px;
                font-size: 12px;
                padding: 0 14px;
                height: 34px;
            }
            QPushButton#secondaryBtn:hover {
                background: #353850;
                border: 1px solid #4a9eff;
            }
            QDialogButtonBox QPushButton {
                min-width: 90px;
                height: 34px;
                border-radius: 6px;
                font-size: 12px;
                font-weight: bold;
            }
            """
        )
        self._build_ui()
        self._load_values()

    # ------------------------------------------------------------------
    # Build UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        # Scrollable content area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; }")

        content = QWidget()
        content.setStyleSheet("background: transparent;")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 4, 0)
        content_layout.setSpacing(12)

        # --- Output section ---
        output_card, output_inner = _make_section("Output Folder", "#4a9eff")

        dir_row = QHBoxLayout()
        dir_row.setSpacing(8)
        self.dir_input = _styled_input("e.g. C:\\Users\\You\\QAEvidence")
        dir_row.addWidget(self.dir_input, 1)
        browse_btn = QPushButton("Browse…")
        browse_btn.setObjectName("secondaryBtn")
        browse_btn.setFixedWidth(80)
        browse_btn.clicked.connect(self._browse_dir)
        dir_row.addWidget(browse_btn)

        output_inner.addLayout(_form_row("Save location:", self._wrap(dir_row)))
        content_layout.addWidget(output_card)

        # --- Hotkey section ---
        hotkey_card, hotkey_inner = _make_section("Global Hotkey", "#a78bfa")

        self.hotkey_enabled_cb = QCheckBox("Enable global capture hotkey  (Ctrl+Shift+S by default)")
        hotkey_inner.addWidget(self.hotkey_enabled_cb)

        self.hotkey_input = _styled_input("e.g. <ctrl>+<shift>+s")
        hotkey_inner.addLayout(_form_row("Combination:", self.hotkey_input))

        hint = QLabel("Use pynput format — example: <b>&lt;ctrl&gt;+&lt;shift&gt;+s</b>")
        hint.setStyleSheet("color: #606880; font-size: 11px;")
        hint.setTextFormat(Qt.TextFormat.RichText)
        hotkey_inner.addWidget(hint)

        self.hotkey_enabled_cb.toggled.connect(self.hotkey_input.setEnabled)
        content_layout.addWidget(hotkey_card)

        # --- Jira Configuration section ---
        jira_card, jira_inner = _make_section("Jira Configuration", "#36b37e")

        self.jira_url_input = _styled_input("https://yourcompany.atlassian.net")
        self.jira_project_input = _styled_input("e.g. QA")
        self.jira_email_input = _styled_input("your-email@company.com")

        # API Token row with show/hide toggle
        token_row = QHBoxLayout()
        token_row.setSpacing(6)
        self.jira_token_input = _styled_input("Paste your Atlassian API token", password=True)
        self._token_visible = False
        self.toggle_token_btn = QPushButton("Show")
        self.toggle_token_btn.setObjectName("secondaryBtn")
        self.toggle_token_btn.setFixedWidth(54)
        self.toggle_token_btn.clicked.connect(self._toggle_token_visibility)
        token_row.addWidget(self.jira_token_input, 1)
        token_row.addWidget(self.toggle_token_btn)

        jira_inner.addLayout(_form_row("Jira URL:", self.jira_url_input))
        jira_inner.addLayout(_form_row("Project Key:", self.jira_project_input))
        jira_inner.addLayout(_form_row("Email:", self.jira_email_input))
        jira_inner.addLayout(_form_row("API Token:", self._wrap(token_row)))

        token_hint = QLabel(
            "Generate your API token at "
            "<a href='https://id.atlassian.com/manage-profile/security/api-tokens' "
            "style='color:#4a9eff;'>id.atlassian.com</a>"
        )
        token_hint.setStyleSheet("color: #606880; font-size: 11px;")
        token_hint.setTextFormat(Qt.TextFormat.RichText)
        token_hint.setOpenExternalLinks(True)
        jira_inner.addWidget(token_hint)

        content_layout.addWidget(jira_card)
        content_layout.addStretch()

        scroll.setWidget(content)
        root.addWidget(scroll, 1)

        # --- Dialog buttons ---
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        btn_row.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("secondaryBtn")
        cancel_btn.clicked.connect(self.reject)

        save_btn = QPushButton("Save Settings")
        save_btn.setObjectName("actionBtn")
        save_btn.clicked.connect(self._save)

        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(save_btn)
        root.addLayout(btn_row)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _wrap(self, layout) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        w.setLayout(layout)
        return w

    def _toggle_token_visibility(self) -> None:
        self._token_visible = not self._token_visible
        if self._token_visible:
            self.jira_token_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.toggle_token_btn.setText("Hide")
        else:
            self.jira_token_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.toggle_token_btn.setText("Show")

    # ------------------------------------------------------------------
    # Load / Save
    # ------------------------------------------------------------------

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
