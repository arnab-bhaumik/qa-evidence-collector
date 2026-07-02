from pathlib import Path

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QWidget, QFrame, QMessageBox, QTextEdit,
    QDialogButtonBox, QLineEdit, QFormLayout,
)
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import Qt

_ICONS_DIR = Path(__file__).parent.parent / "resources" / "icons"

from qa_evidence_collector.core.session_manager import SessionManager


class EditNoteDialog(QDialog):
    def __init__(self, step_number: int, current_note: str, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(f"Edit Step {step_number}")
        self.setMinimumWidth(420)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        layout.addWidget(QLabel(f"<b>Step {step_number}</b> — edit note:"))

        self.note_input = QTextEdit()
        self.note_input.setPlainText(current_note)
        self.note_input.setFixedHeight(100)
        layout.addWidget(self.note_input)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.note_input.setFocus()

    def note(self) -> str:
        return self.note_input.toPlainText().strip()


class StepCard(QFrame):
    def __init__(self, step, index: int, parent_view: "StepListView") -> None:
        super().__init__()
        self._index = index
        self._parent_view = parent_view
        self._step = step

        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet(
            "QFrame { background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 6px; }"
        )

        row = QHBoxLayout(self)
        row.setContentsMargins(10, 8, 10, 8)
        row.setSpacing(12)

        # Thumbnail
        thumb = QLabel()
        thumb.setFixedSize(120, 75)
        thumb.setAlignment(Qt.AlignmentFlag.AlignCenter)
        thumb.setStyleSheet("border: 1px solid #ced4da; background: #e9ecef;")
        pixmap = QPixmap(step.screenshot_path)
        if not pixmap.isNull():
            thumb.setPixmap(
                pixmap.scaled(120, 75, Qt.AspectRatioMode.KeepAspectRatio,
                              Qt.TransformationMode.SmoothTransformation)
            )
        else:
            thumb.setText("No image")
        row.addWidget(thumb)

        # Info
        info = QVBoxLayout()
        info.setSpacing(4)

        step_label = QLabel(f"<b>Step {step.step_number}</b>")
        step_label.setStyleSheet("font-size: 13px;")
        info.addWidget(step_label)

        self.note_label = QLabel(step.note if step.note else "<i>No note added</i>")
        self.note_label.setWordWrap(True)
        self.note_label.setStyleSheet("font-size: 12px; color: #495057;")
        info.addWidget(self.note_label)

        ts_label = QLabel(step.timestamp.strftime("%Y-%m-%d %H:%M:%S"))
        ts_label.setStyleSheet("font-size: 11px; color: #6c757d;")
        info.addWidget(ts_label)

        row.addLayout(info, stretch=1)

        # Action buttons
        actions = QVBoxLayout()
        actions.setSpacing(4)

        btn_up = QPushButton("▲")
        btn_up.setFixedSize(28, 28)
        btn_up.setToolTip("Move up")
        btn_up.clicked.connect(self._move_up)

        btn_down = QPushButton("▼")
        btn_down.setFixedSize(28, 28)
        btn_down.setToolTip("Move down")
        btn_down.clicked.connect(self._move_down)

        btn_edit = QPushButton()
        btn_edit.setIcon(QIcon(str(_ICONS_DIR / "edit.svg")))
        btn_edit.setFixedSize(28, 28)
        btn_edit.setToolTip("Edit note")
        btn_edit.clicked.connect(self._edit_note)

        btn_delete = QPushButton()
        btn_delete.setIcon(QIcon(str(_ICONS_DIR / "delete.svg")))
        btn_delete.setFixedSize(28, 28)
        btn_delete.setToolTip("Delete step")
        btn_delete.clicked.connect(self._delete)

        for btn in (btn_up, btn_down, btn_edit, btn_delete):
            btn.setStyleSheet(
                "QPushButton { border: 1px solid #ced4da; border-radius: 4px; background: white; }"
                "QPushButton:hover { background: #e9ecef; }"
            )
            actions.addWidget(btn)

        btn_delete.setStyleSheet(
            "QPushButton { border: 1px solid #ced4da; border-radius: 4px; background: white; color: #dc3545; }"
            "QPushButton:hover { background: #e9ecef; }"
        )

        row.addLayout(actions)

    def _move_up(self) -> None:
        self._parent_view.move_step(self._index, self._index - 1)

    def _move_down(self) -> None:
        self._parent_view.move_step(self._index, self._index + 1)

    def _edit_note(self) -> None:
        dialog = EditNoteDialog(self._step.step_number, self._step.note, self)
        if dialog.exec():
            new_note = dialog.note()
            self._parent_view.update_note(self._index, new_note)

    def _delete(self) -> None:
        self._parent_view.delete_step(self._index)


class EditSessionDialog(QDialog):
    def __init__(self, session: SessionManager, parent=None) -> None:
        super().__init__(parent)
        self._session = session
        self.setWindowTitle("Edit Session Info")
        self.setMinimumWidth(420)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        form = QFormLayout()
        form.setSpacing(10)

        self.tc_id_input = QLineEdit(session.test_case_id)
        self.tc_id_input.setFixedHeight(32)
        form.addRow("Test Case ID:", self.tc_id_input)

        self.objective_input = QLineEdit(session.test_objective)
        self.objective_input.setFixedHeight(32)
        form.addRow("Test Objective:", self.objective_input)

        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def test_case_id(self) -> str:
        return self.tc_id_input.text().strip()

    def test_objective(self) -> str:
        return self.objective_input.text().strip()


class StepListView(QDialog):
    def __init__(self, session: SessionManager, parent=None) -> None:
        super().__init__(parent)
        self._session = session
        self.setWindowTitle(f"Steps — {session.session_name}")
        self.setMinimumSize(620, 480)
        self.setWindowFlags(
            self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint
        )
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        # Session info header
        session_frame = QFrame()
        session_frame.setStyleSheet(
            "QFrame { background: #eaf2fb; border: 1px solid #aed6f1; border-radius: 6px; }"
        )
        session_layout = QHBoxLayout(session_frame)
        session_layout.setContentsMargins(12, 8, 12, 8)

        info_layout = QVBoxLayout()
        info_layout.setSpacing(3)

        self._tc_id_label = QLabel()
        self._tc_id_label.setStyleSheet("font-size: 12px; font-weight: bold; color: #1a5276;")
        info_layout.addWidget(self._tc_id_label)

        self._objective_label = QLabel()
        self._objective_label.setStyleSheet("font-size: 12px; color: #2c3e50;")
        info_layout.addWidget(self._objective_label)

        session_layout.addLayout(info_layout, stretch=1)

        edit_session_btn = QPushButton()
        edit_session_btn.setIcon(QIcon(str(_ICONS_DIR / "edit.svg")))
        edit_session_btn.setFixedSize(30, 30)
        edit_session_btn.setToolTip("Edit Test Case ID and Objective")
        edit_session_btn.setStyleSheet(
            "QPushButton { border: 1px solid #aed6f1; border-radius: 4px; background: white; }"
            "QPushButton:hover { background: #d6eaf8; }"
        )
        edit_session_btn.clicked.connect(self._edit_session_info)
        session_layout.addWidget(edit_session_btn)

        layout.addWidget(session_frame)

        # Step count header
        self._header = QLabel()
        self._header.setStyleSheet("font-size: 13px; padding: 2px 0;")
        layout.addWidget(self._header)

        self._scroll_area = QScrollArea()
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        layout.addWidget(self._scroll_area, stretch=1)

        self._refresh_cards()

        close_btn = QPushButton("Close")
        close_btn.setFixedHeight(34)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

    def _edit_session_info(self) -> None:
        dialog = EditSessionDialog(self._session, self)
        if dialog.exec():
            self._session.test_case_id = dialog.test_case_id()
            self._session.test_objective = dialog.test_objective()
            tc = self._session.test_case_id
            obj = self._session.test_objective
            self._session.session_name = f"{tc} — {obj}" if tc and obj else tc or obj or "Untitled Session"
            self.setWindowTitle(f"Steps — {self._session.session_name}")
            self._refresh_cards()

    def _refresh_cards(self) -> None:
        self._tc_id_label.setText(f"Test Case ID: {self._session.test_case_id or '—'}")
        self._objective_label.setText(f"Test Objective: {self._session.test_objective or '—'}")
        self._header.setText(
            f"<b>{self._session.session_name}</b> &nbsp;·&nbsp; "
            f"{len(self._session.steps)} step(s)"
        )

        container = QWidget()
        vbox = QVBoxLayout(container)
        vbox.setSpacing(8)
        vbox.setContentsMargins(4, 4, 4, 4)

        for i, step in enumerate(self._session.steps):
            vbox.addWidget(StepCard(step, i, self))

        vbox.addStretch()
        self._scroll_area.setWidget(container)

    def move_step(self, from_index: int, to_index: int) -> None:
        if to_index < 0 or to_index >= len(self._session.steps):
            return
        self._session.move_step(from_index, to_index)
        self._refresh_cards()

    def update_note(self, index: int, note: str) -> None:
        self._session.update_note(index, note)
        self._refresh_cards()

    def delete_step(self, index: int) -> None:
        reply = QMessageBox.question(
            self, "Delete Step",
            f"Delete Step {index + 1}? This cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            from pathlib import Path
            path = self._session.steps[index].screenshot_path
            self._session.delete_step(index)
            Path(path).unlink(missing_ok=True)
            self._refresh_cards()
