from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QWidget, QFrame, QSizePolicy, QMessageBox,
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

from qa_evidence_collector.core.session_manager import SessionManager


class StepCard(QFrame):
    def __init__(self, step, index: int, parent_view: "StepListView") -> None:
        super().__init__()
        self._index = index
        self._parent_view = parent_view

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

        note_label = QLabel(step.note if step.note else "<i>No note added</i>")
        note_label.setWordWrap(True)
        note_label.setStyleSheet("font-size: 12px; color: #495057;")
        info.addWidget(note_label)

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

        btn_delete = QPushButton("🗑")
        btn_delete.setFixedSize(28, 28)
        btn_delete.setToolTip("Delete step")
        btn_delete.setStyleSheet("color: #dc3545;")
        btn_delete.clicked.connect(self._delete)

        for btn in (btn_up, btn_down, btn_delete):
            btn.setStyleSheet(
                btn.styleSheet() +
                "QPushButton { border: 1px solid #ced4da; border-radius: 4px; background: white; }"
                "QPushButton:hover { background: #e9ecef; }"
            )
            actions.addWidget(btn)

        row.addLayout(actions)

    def _move_up(self) -> None:
        self._parent_view.move_step(self._index, self._index - 1)

    def _move_down(self) -> None:
        self._parent_view.move_step(self._index, self._index + 1)

    def _delete(self) -> None:
        self._parent_view.delete_step(self._index)


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

        # Header
        header = QLabel(
            f"<b>{self._session.session_name}</b> &nbsp;·&nbsp; "
            f"{len(self._session.steps)} step(s)"
        )
        header.setStyleSheet("font-size: 14px; padding: 4px 0;")
        layout.addWidget(header)

        # Scrollable step list
        self._scroll_area = QScrollArea()
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        layout.addWidget(self._scroll_area, stretch=1)

        self._refresh_cards()

        # Close button
        close_btn = QPushButton("Close")
        close_btn.setFixedHeight(34)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

    def _refresh_cards(self) -> None:
        container = QWidget()
        vbox = QVBoxLayout(container)
        vbox.setSpacing(8)
        vbox.setContentsMargins(4, 4, 4, 4)

        for i, step in enumerate(self._session.steps):
            vbox.addWidget(StepCard(step, i, self))

        vbox.addStretch()
        self._scroll_area.setWidget(container)

        # Update header count
        if hasattr(self, "_header"):
            self._header.setText(
                f"<b>{self._session.session_name}</b> &nbsp;·&nbsp; "
                f"{len(self._session.steps)} step(s)"
            )

    def move_step(self, from_index: int, to_index: int) -> None:
        if to_index < 0 or to_index >= len(self._session.steps):
            return
        self._session.move_step(from_index, to_index)
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
