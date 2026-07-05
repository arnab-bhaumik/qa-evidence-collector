from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QPushButton,
    QHBoxLayout, QLabel, QCheckBox, QFileDialog,
    QFrame, QScrollArea, QWidget,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from qa_evidence_collector.config.settings import Settings


# ---------------------------------------------------------------------------
# Shared style helpers
# ---------------------------------------------------------------------------

_CARD_STYLE = """
QFrame#sectionCard {{
    background: #252836;
    border: 1px solid #383b50;
    border-radius: 10px;
}}
"""

_INPUT_STYLE = """
QLineEdit {{
    background: #1a1c2a;
    color: #e0e4f0;
    border: 1px solid #383b50;
    border-radius: 6px;
    padding: 0 10px;
    font-size: 12px;
    height: 34px;
}}
QLineEdit:focus {{
    border: 1px solid #4a9eff;
    background: #1e2138;
}}
QLineEdit:disabled {{
    color: #4a4d60;
    background: #1a1c2a;
}}
"""

_BTN_PRIMARY = """
QPushButton {{
    background: {color};
    color: white;
    border: none;
    border-radius: 6px;
    font-size: 12px;
    font-weight: bold;
    padding: 0 18px;
    height: 32px;
    min-width: 80px;
}}
QPushButton:hover {{ background: {hover}; }}
QPushButton:pressed {{ background: {hover}; padding-top: 1px; }}
"""

_BTN_SECONDARY = """
QPushButton {
    background: transparent;
    color: #8890aa;
    border: 1px solid #383b50;
    border-radius: 6px;
    font-size: 12px;
    padding: 0 18px;
    height: 32px;
    min-width: 70px;
}
QPushButton:hover {
    background: #2e3145;
    color: #c8d0e0;
    border: 1px solid #4a9eff;
}
"""


def _make_card(accent_color: str, title: str) -> tuple[QFrame, QVBoxLayout]:
    card = QFrame()
    card.setObjectName("sectionCard")
    card.setStyleSheet(_CARD_STYLE)
    layout = QVBoxLayout(card)
    layout.setContentsMargins(18, 14, 18, 16)
    layout.setSpacing(12)

    # Title row with accent bar
    title_row = QHBoxLayout()
    title_row.setSpacing(8)

    accent_bar = QFrame()
    accent_bar.setFixedSize(3, 16)
    accent_bar.setStyleSheet(
        f"background: {accent_color}; border-radius: 2px;"
    )
    title_row.addWidget(accent_bar)

    title_lbl = QLabel(title)
    title_lbl.setStyleSheet(
        f"color: {accent_color}; font-size: 12px; font-weight: bold;"
    )
    title_row.addWidget(title_lbl)
    title_row.addStretch()
    layout.addLayout(title_row)

    # Divider
    line = QFrame()
    line.setFrameShape(QFrame.Shape.HLine)
    line.setStyleSheet("color: #303348; margin: 0;")
    layout.addWidget(line)

    return card, layout


def _input_row(label: str, widget: QWidget, label_width: int = 100) -> QHBoxLayout:
    row = QHBoxLayout()
    row.setSpacing(12)
    lbl = QLabel(label)
    lbl.setFixedWidth(label_width)
    lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
    lbl.setStyleSheet("color: #8890aa; font-size: 12px;")
    row.addWidget(lbl)
    row.addWidget(widget, 1)
    return row


def _make_input(placeholder: str = "", password: bool = False) -> QLineEdit:
    inp = QLineEdit()
    inp.setPlaceholderText(placeholder)
    inp.setFixedHeight(34)
    if password:
        inp.setEchoMode(QLineEdit.EchoMode.Password)
    inp.setStyleSheet(_INPUT_STYLE)
    return inp


def _save_btn(color: str, hover: str, label: str = "Save") -> QPushButton:
    btn = QPushButton(label)
    btn.setStyleSheet(
        _BTN_PRIMARY.format(color=color, hover=hover)
    )
    return btn


def _cancel_btn() -> QPushButton:
    btn = QPushButton("Cancel")
    btn.setStyleSheet(_BTN_SECONDARY)
    return btn


# ---------------------------------------------------------------------------
# SettingsDialog
# ---------------------------------------------------------------------------

class SettingsDialog(QDialog):
    def __init__(self, settings: Settings, parent=None) -> None:
        super().__init__(parent)
        self._settings = settings
        self.setWindowTitle("Settings")
        self.setMinimumWidth(500)
        self.setWindowFlags(
            self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setStyleSheet(
            """
            QDialog { background: #1a1c2a; }
            QScrollArea { background: transparent; border: none; }
            QWidget#scrollContent { background: transparent; }
            QCheckBox {
                color: #c8d0e0;
                font-size: 12px;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border-radius: 4px;
                border: 2px solid #4a4d60;
                background: #1a1c2a;
            }
            QCheckBox::indicator:hover {
                border: 2px solid #4a9eff;
            }
            QCheckBox::indicator:checked {
                background: #4a9eff;
                border: 2px solid #4a9eff;
                image: none;
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
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        content = QWidget()
        content.setObjectName("scrollContent")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(2, 2, 6, 2)
        content_layout.setSpacing(12)

        # ---- Output Folder card ----
        output_card, output_inner = _make_card("#4a9eff", "Output Folder")

        dir_row = QHBoxLayout()
        dir_row.setSpacing(8)
        self.dir_input = _make_input("e.g. C:\\Users\\You\\QAEvidence")
        browse_btn = QPushButton("Browse…")
        browse_btn.setStyleSheet(_BTN_SECONDARY)
        browse_btn.setFixedWidth(80)
        browse_btn.clicked.connect(self._browse_dir)
        dir_row.addWidget(self.dir_input, 1)
        dir_row.addWidget(browse_btn)

        dir_widget = QWidget()
        dir_widget.setStyleSheet("background: transparent;")
        dir_widget.setLayout(dir_row)
        output_inner.addLayout(_input_row("Save location:", dir_widget))

        # Save button for Output card
        output_btn_row = QHBoxLayout()
        output_btn_row.addStretch()
        output_save_btn = _save_btn("#4a9eff", "#3a8eef", "Save")
        output_save_btn.clicked.connect(self._save_output)
        output_btn_row.addWidget(output_save_btn)
        output_inner.addLayout(output_btn_row)

        self._output_status = self._status_label()
        output_inner.addWidget(self._output_status)
        content_layout.addWidget(output_card)

        # ---- Global Hotkey card ----
        hotkey_card, hotkey_inner = _make_card("#a78bfa", "Global Hotkey")

        self.hotkey_enabled_cb = QCheckBox("Enable global capture hotkey")
        hotkey_inner.addWidget(self.hotkey_enabled_cb)

        self.hotkey_input = _make_input("<ctrl>+<shift>+s")
        hotkey_inner.addLayout(_input_row("Combination:", self.hotkey_input))

        hint = QLabel("Format: <b>&lt;ctrl&gt;+&lt;shift&gt;+s</b>  |  Use pynput key names")
        hint.setStyleSheet("color: #505368; font-size: 11px;")
        hint.setTextFormat(Qt.TextFormat.RichText)
        hotkey_inner.addWidget(hint)

        self.hotkey_enabled_cb.toggled.connect(self.hotkey_input.setEnabled)

        # Save button for Hotkey card
        hotkey_btn_row = QHBoxLayout()
        hotkey_btn_row.addStretch()
        hotkey_save_btn = _save_btn("#a78bfa", "#9370eb", "Save")
        hotkey_save_btn.clicked.connect(self._save_hotkey)
        hotkey_btn_row.addWidget(hotkey_save_btn)
        hotkey_inner.addLayout(hotkey_btn_row)

        self._hotkey_status = self._status_label()
        hotkey_inner.addWidget(self._hotkey_status)
        content_layout.addWidget(hotkey_card)

        # ---- Jira Configuration card ----
        jira_card, jira_inner = _make_card("#36b37e", "Jira Configuration")

        self.jira_url_input    = _make_input("https://yourcompany.atlassian.net")
        self.jira_project_input = _make_input("e.g.  QA")
        self.jira_email_input  = _make_input("your-email@company.com")

        # Token row with Show/Hide
        token_row_layout = QHBoxLayout()
        token_row_layout.setSpacing(6)
        self.jira_token_input = _make_input("Paste your Atlassian API token", password=True)
        self._token_visible = False
        self.toggle_token_btn = QPushButton("Show")
        self.toggle_token_btn.setStyleSheet(_BTN_SECONDARY)
        self.toggle_token_btn.setFixedWidth(54)
        self.toggle_token_btn.clicked.connect(self._toggle_token)
        token_row_layout.addWidget(self.jira_token_input, 1)
        token_row_layout.addWidget(self.toggle_token_btn)

        token_widget = QWidget()
        token_widget.setStyleSheet("background: transparent;")
        token_widget.setLayout(token_row_layout)

        jira_inner.addLayout(_input_row("Jira URL:",     self.jira_url_input))
        jira_inner.addLayout(_input_row("Project Key:",  self.jira_project_input))
        jira_inner.addLayout(_input_row("Email:",        self.jira_email_input))
        jira_inner.addLayout(_input_row("API Token:",    token_widget))

        token_hint = QLabel(
            "Get your token at "
            "<a href='https://id.atlassian.com/manage-profile/security/api-tokens' "
            "style='color:#4a9eff;'>id.atlassian.com</a>"
        )
        token_hint.setStyleSheet("color: #505368; font-size: 11px;")
        token_hint.setTextFormat(Qt.TextFormat.RichText)
        token_hint.setOpenExternalLinks(True)
        jira_inner.addWidget(token_hint)

        # Save / Cancel buttons for Jira card
        jira_btn_row = QHBoxLayout()
        jira_btn_row.addStretch()
        jira_cancel_btn = _cancel_btn()
        jira_cancel_btn.clicked.connect(self._cancel_jira)
        jira_save_btn = _save_btn("#36b37e", "#2a9e6a", "Save")
        jira_save_btn.clicked.connect(self._save_jira)
        jira_btn_row.addWidget(jira_cancel_btn)
        jira_btn_row.addSpacing(6)
        jira_btn_row.addWidget(jira_save_btn)
        jira_inner.addLayout(jira_btn_row)

        self._jira_status = self._status_label()
        jira_inner.addWidget(self._jira_status)
        content_layout.addWidget(jira_card)

        content_layout.addStretch()
        scroll.setWidget(content)
        root.addWidget(scroll)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _status_label(self) -> QLabel:
        lbl = QLabel()
        lbl.setFixedHeight(18)
        lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        lbl.setStyleSheet("font-size: 11px;")
        lbl.hide()
        return lbl

    def _show_status(self, label: QLabel, success: bool, message: str) -> None:
        color = "#36b37e" if success else "#e74c3c"
        label.setStyleSheet(f"font-size: 11px; color: {color};")
        label.setText(message)
        label.show()

    def _toggle_token(self) -> None:
        self._token_visible = not self._token_visible
        self.jira_token_input.setEchoMode(
            QLineEdit.EchoMode.Normal if self._token_visible
            else QLineEdit.EchoMode.Password
        )
        self.toggle_token_btn.setText("Hide" if self._token_visible else "Show")

    # ------------------------------------------------------------------
    # Load values
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

    # ------------------------------------------------------------------
    # Per-card save handlers
    # ------------------------------------------------------------------

    def _browse_dir(self) -> None:
        folder = QFileDialog.getExistingDirectory(
            self, "Select Output Folder", self.dir_input.text()
        )
        if folder:
            self.dir_input.setText(folder)

    def _save_output(self) -> None:
        val = self.dir_input.text().strip()
        if not val:
            self._show_status(self._output_status, False, "Save location cannot be empty.")
            return
        self._settings.output_dir = val
        self._settings.save()
        self._show_status(self._output_status, True, "Saved successfully.")

    def _save_hotkey(self) -> None:
        self._settings.capture_hotkey = self.hotkey_input.text().strip()
        self._settings.hotkey_enabled = self.hotkey_enabled_cb.isChecked()
        self._settings.save()
        self._show_status(self._hotkey_status, True, "Saved successfully.")

    def _save_jira(self) -> None:
        url = self.jira_url_input.text().strip()
        email = self.jira_email_input.text().strip()
        token = self.jira_token_input.text().strip()

        if url and not url.startswith("http"):
            self._show_status(self._jira_status, False, "Jira URL must start with https://")
            return

        self._settings.jira_url = url
        self._settings.jira_project_key = self.jira_project_input.text().strip()
        self._settings.jira_email = email
        self._settings.jira_api_token = token
        self._settings.save()
        self._show_status(self._jira_status, True, "Jira configuration saved.")

    def _cancel_jira(self) -> None:
        self.jira_url_input.setText(self._settings.jira_url)
        self.jira_project_input.setText(self._settings.jira_project_key)
        self.jira_email_input.setText(self._settings.jira_email)
        self.jira_token_input.setText(self._settings.jira_api_token)
        self._jira_status.hide()
