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
        self.setMinimumWidth(460)
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
        self._settings.save()
        self.accept()
