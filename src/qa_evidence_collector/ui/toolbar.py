from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QMessageBox,
)
from PySide6.QtCore import Qt, QPoint, QTimer, Signal, QThread
from PySide6.QtGui import QColor

from qa_evidence_collector.config.settings import Settings
from qa_evidence_collector.core.session_manager import SessionManager
from qa_evidence_collector.core.hotkey_manager import HotkeyManager
from qa_evidence_collector.services.screenshot_service import ScreenshotService
from qa_evidence_collector.services.report_service import ReportService
from qa_evidence_collector.ui.new_session_dialog import NewSessionDialog
from qa_evidence_collector.ui.note_dialog import NoteDialog
from qa_evidence_collector.ui.step_list_view import StepListView
from qa_evidence_collector.ui.settings_dialog import SettingsDialog
from qa_evidence_collector.ui.annotation_editor import AnnotationEditor
from qa_evidence_collector.ui.test_result_dialog import TestResultDialog
from qa_evidence_collector.ui.issue_key_dialog import IssueKeyDialog
from qa_evidence_collector.services.storage_service import StorageService
from qa_evidence_collector.services.jira_service import JiraService


class _JiraUploadThread(QThread):
    upload_done = Signal(bool, str)   # (success, issue_url_or_error)
    comment_done = Signal(bool, str)

    def __init__(self, settings, issue_key: str, file_path: str, comment: str) -> None:
        super().__init__()
        self._settings = settings
        self._issue_key = issue_key
        self._file_path = file_path
        self._comment = comment

    def run(self) -> None:
        svc = JiraService()
        ok, result = svc.upload_attachment(
            self._settings.jira_url,
            self._settings.jira_email,
            self._settings.jira_api_token,
            self._issue_key,
            self._file_path,
        )
        self.upload_done.emit(ok, result)
        if ok and self._comment:
            svc.post_comment(
                self._settings.jira_url,
                self._settings.jira_email,
                self._settings.jira_api_token,
                self._issue_key,
                self._comment,
            )


class FloatingToolbar(QWidget):
    _hotkey_triggered = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._settings = Settings()
        self._session = SessionManager()
        self._screenshot_svc = ScreenshotService(self._settings.output_dir)
        self._report_svc = ReportService()
        self._storage_svc = StorageService()
        self._hotkey_mgr = HotkeyManager()
        self._hotkey_triggered.connect(self._on_capture_step)
        self._last_annotation_colour = QColor("#FF3B30")
        self._last_report_path: str = ""
        self._apply_hotkey()

        self._drag_pos: QPoint | None = None

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self.setFixedHeight(64)
        self.setMinimumWidth(520)

        self._build_ui()
        self._apply_style()
        QTimer.singleShot(200, self._check_resume_session)

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Title bar (drag handle)
        title_bar = QWidget()
        title_bar.setObjectName("titleBar")
        title_bar.setFixedHeight(20)
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(8, 0, 8, 0)

        title_label = QLabel("QA Evidence Collector")
        title_label.setObjectName("titleLabel")
        title_layout.addWidget(title_label)
        title_layout.addStretch()

        close_btn = QPushButton("✕")
        close_btn.setObjectName("closeBtn")
        close_btn.setFixedSize(16, 16)
        close_btn.clicked.connect(self.close)
        title_layout.addWidget(close_btn)

        root.addWidget(title_bar)

        # Button row
        btn_row = QWidget()
        btn_row.setObjectName("btnRow")
        btn_layout = QHBoxLayout(btn_row)
        btn_layout.setContentsMargins(8, 4, 8, 4)
        btn_layout.setSpacing(6)

        self.btn_new = self._make_button("New Session", "#27ae60")
        self.btn_capture = self._make_button("Capture Step", "#2980b9")
        self.btn_capture.setEnabled(False)
        self.btn_steps = self._make_button("View Steps", "#8e44ad")
        self.btn_steps.setEnabled(False)
        self.btn_report = self._make_button("Generate Report", "#e67e22")
        self.btn_report.setEnabled(False)
        self.btn_upload_jira = self._make_button("Upload to Jira", "#1565c0")
        self.btn_upload_jira.setEnabled(False)
        self.btn_upload_jira.setVisible(False)
        self.btn_settings = self._make_button("Settings", "#7f8c8d")

        for btn in (
            self.btn_new,
            self.btn_capture,
            self.btn_steps,
            self.btn_report,
            self.btn_upload_jira,
            self.btn_settings,
        ):
            btn_layout.addWidget(btn)

        root.addWidget(btn_row)

        # Connections
        self.btn_new.clicked.connect(self._on_new_session)
        self.btn_capture.clicked.connect(self._on_capture_step)
        self.btn_steps.clicked.connect(self._on_view_steps)
        self.btn_report.clicked.connect(self._on_generate_report)
        self.btn_upload_jira.clicked.connect(self._on_upload_to_jira)
        self.btn_settings.clicked.connect(self._on_settings)

    def _make_button(self, label: str, color: str) -> QPushButton:
        btn = QPushButton(label)
        btn.setFixedHeight(32)
        btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 0 10px;
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {color}CC;
            }}
            QPushButton:disabled {{
                background-color: #bdc3c7;
                color: #7f8c8d;
            }}
            """
        )
        return btn

    def _apply_style(self) -> None:
        self.setStyleSheet(
            """
            FloatingToolbar {
                background-color: #2c3e50;
                border: 1px solid #1a252f;
                border-radius: 6px;
            }
            QWidget#titleBar {
                background-color: #1a252f;
                border-radius: 6px;
            }
            QLabel#titleLabel {
                color: #ecf0f1;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton#closeBtn {
                background: transparent;
                color: #95a5a6;
                border: none;
                font-size: 11px;
                padding: 0;
            }
            QPushButton#closeBtn:hover {
                color: #e74c3c;
            }
            QWidget#btnRow {
                background-color: #2c3e50;
            }
            """
        )

    # ------------------------------------------------------------------
    # Button handlers
    # ------------------------------------------------------------------

    def _check_resume_session(self) -> None:
        if not self._storage_svc.has_saved_session():
            return
        reply = QMessageBox.question(
            self,
            "Resume Session",
            "A previous session was found. Do you want to resume it?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._storage_svc.load(self._session)
            self._update_button_states()
            self._apply_hotkey()
            self.setWindowTitle(f"QA Evidence Collector — {self._session.session_name}")
        else:
            self._storage_svc.clear()

    def _on_new_session(self) -> None:
        if self._session.is_active and self._session.steps:
            reply = QMessageBox.question(
                self, "New Session",
                "Starting a new session will end the current one. Continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.No:
                return

        dialog = NewSessionDialog(self)
        if dialog.exec():
            name = dialog.session_name() or "Untitled Session"
            self._session.start(name, dialog.test_case_id(), dialog.test_objective())
            self._storage_svc.clear()
            self._update_button_states()
            self._apply_hotkey()
            self.setWindowTitle(f"QA Evidence Collector — {name}")

    def _on_capture_step(self) -> None:
        # Hide toolbar so it doesn't appear in the screenshot
        self.hide()
        QTimer.singleShot(300, self._do_capture)

    def _do_capture(self) -> None:
        try:
            next_number = len(self._session.steps) + 1
            path = self._screenshot_svc.capture_fullscreen(
                self._session.session_name, next_number,
                self._session.test_case_id,
            )
        except Exception as exc:
            self.show()
            QMessageBox.critical(self, "Capture Failed", str(exc))
            return

        self.show()

        # Annotation step — pass last used colour, read it back after
        annotator = AnnotationEditor(path, next_number, self._last_annotation_colour, self)
        if annotator.exec():
            final_path = annotator.annotated_path()
        else:
            final_path = path  # skip annotation, use original
        self._last_annotation_colour = annotator.selected_colour()

        # Note step
        dialog = NoteDialog(next_number, final_path, self)
        if dialog.exec():
            self._session.add_step(final_path, dialog.note())
            self._storage_svc.save(self._session)
        else:
            from pathlib import Path
            Path(final_path).unlink(missing_ok=True)

        self._update_button_states()

    def _on_generate_report(self) -> None:
        if not self._session.steps:
            QMessageBox.warning(self, "No Steps", "Capture at least one step before generating a report.")
            return

        # Ask for Pass / Fail before generating
        result_dialog = TestResultDialog(self)
        if not result_dialog.exec():
            return
        self._session.status = result_dialog.result_status()

        output_dir = self._screenshot_svc.session_folder(
            self._session.session_name, self._session.test_case_id
        )
        try:
            path = self._report_svc.generate(self._session, output_dir)
        except Exception as exc:
            QMessageBox.critical(self, "Report Failed", str(exc))
            return

        self._last_report_path = path
        self._storage_svc.clear()
        self._update_button_states()

        if self._settings.output_save_to_folder:
            result = QMessageBox.information(
                self,
                "Report Generated",
                f"Report saved to:\n{path}\n\nOpen it now?",
                QMessageBox.StandardButton.Open | QMessageBox.StandardButton.Close,
            )
            if result == QMessageBox.StandardButton.Open:
                import os
                os.startfile(path)

    def _on_upload_to_jira(self) -> None:
        if not self._last_report_path:
            QMessageBox.warning(self, "No Report", "Generate a report first before uploading to Jira.")
            return

        dialog = IssueKeyDialog(self._last_report_path, self)
        if not dialog.exec():
            return

        issue_key = dialog.issue_key()
        comment   = dialog.comment()

        # Disable button, show uploading state
        self.btn_upload_jira.setEnabled(False)
        self.btn_upload_jira.setText("Uploading…")

        self._upload_thread = _JiraUploadThread(
            self._settings, issue_key, self._last_report_path, comment
        )
        self._upload_thread.upload_done.connect(
            lambda ok, result: self._on_upload_done(ok, result, issue_key)
        )
        self._upload_thread.start()

    def _on_upload_done(self, success: bool, result: str, issue_key: str) -> None:
        self.btn_upload_jira.setEnabled(True)
        self.btn_upload_jira.setText("Upload to Jira")

        if success:
            issue_url = result
            msg = QMessageBox(self)
            msg.setWindowTitle("Uploaded Successfully")
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setText(
                f"Report uploaded to <b>{issue_key}</b> successfully.\n\n"
                f"<a href='{issue_url}'>{issue_url}</a>"
            )
            msg.setTextFormat(Qt.TextFormat.RichText)
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.exec()
        else:
            QMessageBox.critical(self, "Upload Failed", result)

    def _on_view_steps(self) -> None:
        dialog = StepListView(self._session, self)
        dialog.exec()
        self._storage_svc.save(self._session)
        self._update_button_states()

    def _on_settings(self) -> None:
        dialog = SettingsDialog(self._settings, self)
        if dialog.exec():
            self._screenshot_svc.set_output_dir(self._settings.output_dir)
            self._apply_hotkey()
            self._update_button_states()

    def _apply_hotkey(self) -> None:
        self._hotkey_mgr.unregister()
        if self._settings.hotkey_enabled and self._session.is_active:
            try:
                self._hotkey_mgr.register(
                    self._settings.capture_hotkey,
                    self._trigger_capture_from_hotkey,
                )
            except Exception:
                pass

    def _trigger_capture_from_hotkey(self) -> None:
        if self._session.is_active:
            self._hotkey_triggered.emit()

    def _update_button_states(self) -> None:
        active = self._session.is_active
        self.btn_capture.setEnabled(active)
        self.btn_steps.setEnabled(active and len(self._session.steps) > 0)
        self.btn_report.setEnabled(active and len(self._session.steps) > 0)

        show_jira = (
            self._settings.jira_configured
            and self._settings.output_upload_to_jira
        )
        self.btn_upload_jira.setVisible(show_jira)
        self.btn_upload_jira.setEnabled(show_jira and bool(self._last_report_path))
        target_width = 640 if show_jira else 520
        self.setMinimumWidth(target_width)
        self.resize(target_width, self.height())

    # ------------------------------------------------------------------
    # Drag to move
    # ------------------------------------------------------------------

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event) -> None:
        if self._drag_pos and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, event) -> None:
        self._drag_pos = None

    def closeEvent(self, event) -> None:
        self._hotkey_mgr.unregister()
        super().closeEvent(event)
