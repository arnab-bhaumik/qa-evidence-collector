from __future__ import annotations

import math
from pathlib import Path

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsItem,
    QWidget, QButtonGroup, QSizePolicy, QFrame,
)
from PySide6.QtGui import (
    QPixmap, QColor, QIcon, QPainter, QPen, QBrush,
    QPolygonF, QPainterPath, QImage,
)
from PySide6.QtCore import Qt, QSize, QPointF, QRectF, QLineF


_ICONS_DIR = Path(__file__).parent.parent / "resources" / "icons"

ARROW_COLOR   = QColor("#FF3B30")   # red
ARROW_WIDTH   = 3
ARROWHEAD_SIZE = 14


# ==================================================================
# Arrow Graphics Item
# ==================================================================

class ArrowItem(QGraphicsItem):
    def __init__(self, start: QPointF, end: QPointF) -> None:
        super().__init__()
        self._start = start
        self._end   = end
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)

    def update_end(self, end: QPointF) -> None:
        self.prepareGeometryChange()
        self._end = end

    def boundingRect(self) -> QRectF:
        extra = ARROWHEAD_SIZE + ARROW_WIDTH
        return QRectF(self._start, self._end).normalized().adjusted(
            -extra, -extra, extra, extra
        )

    def paint(self, painter: QPainter, option, widget=None) -> None:
        if self._start == self._end:
            return

        pen = QPen(ARROW_COLOR, ARROW_WIDTH, Qt.PenStyle.SolidLine,
                   Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(QBrush(ARROW_COLOR))
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Shaft
        line = QLineF(self._start, self._end)
        painter.drawLine(line)

        # Arrowhead
        angle = math.atan2(line.dy(), line.dx())
        head_size = ARROWHEAD_SIZE

        p1 = self._end - QPointF(
            math.cos(angle - math.pi / 6) * head_size,
            math.sin(angle - math.pi / 6) * head_size,
        )
        p2 = self._end - QPointF(
            math.cos(angle + math.pi / 6) * head_size,
            math.sin(angle + math.pi / 6) * head_size,
        )

        head = QPolygonF([self._end, p1, p2])
        painter.drawPolygon(head)


# ==================================================================
# Annotation Canvas
# ==================================================================

class AnnotationCanvas(QGraphicsView):
    def __init__(self, pixmap: QPixmap) -> None:
        super().__init__()
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)

        self._pixmap_item = QGraphicsPixmapItem(pixmap)
        self._scene.addItem(self._pixmap_item)
        self._scene.setSceneRect(self._pixmap_item.boundingRect())

        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setStyleSheet("background: #1a1a1a; border: none;")
        self.fitInView(self._pixmap_item, Qt.AspectRatioMode.KeepAspectRatio)

        self._current_tool: str = "arrow"
        self._drawing: bool = False
        self._current_item: ArrowItem | None = None
        self._annotation_items: list[QGraphicsItem] = []

    # ------------------------------------------------------------------
    # Tool switching
    # ------------------------------------------------------------------

    def set_tool(self, tool: str) -> None:
        self._current_tool = tool
        cursors = {
            "arrow":     Qt.CursorShape.CrossCursor,
            "text":      Qt.CursorShape.IBeamCursor,
            "highlight": Qt.CursorShape.CrossCursor,
            "blur":      Qt.CursorShape.CrossCursor,
        }
        self.setCursor(cursors.get(tool, Qt.CursorShape.ArrowCursor))

    # ------------------------------------------------------------------
    # Undo / Clear
    # ------------------------------------------------------------------

    def undo(self) -> None:
        if self._annotation_items:
            item = self._annotation_items.pop()
            self._scene.removeItem(item)

    def clear_all(self) -> None:
        for item in self._annotation_items:
            self._scene.removeItem(item)
        self._annotation_items.clear()

    # ------------------------------------------------------------------
    # Mouse events — arrow drawing
    # ------------------------------------------------------------------

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton and self._current_tool == "arrow":
            scene_pos = self.mapToScene(event.position().toPoint())
            self._drawing = True
            self._current_item = ArrowItem(scene_pos, scene_pos)
            self._scene.addItem(self._current_item)
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:
        if self._drawing and self._current_item:
            scene_pos = self.mapToScene(event.position().toPoint())
            self._current_item.update_end(scene_pos)
            self._scene.update()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        if self._drawing and self._current_item:
            scene_pos = self.mapToScene(event.position().toPoint())
            self._current_item.update_end(scene_pos)
            self._annotation_items.append(self._current_item)
            self._current_item = None
            self._drawing = False
            self._scene.update()
        else:
            super().mouseReleaseEvent(event)

    # ------------------------------------------------------------------
    # Flatten to image
    # ------------------------------------------------------------------

    def render_to_pixmap(self) -> QPixmap:
        rect = self._scene.sceneRect()
        image = QImage(
            int(rect.width()), int(rect.height()), QImage.Format.Format_ARGB32
        )
        image.fill(Qt.GlobalColor.transparent)
        painter = QPainter(image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        self._scene.render(painter, source=rect)
        painter.end()
        return QPixmap.fromImage(image)

    # ------------------------------------------------------------------

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self.fitInView(self._pixmap_item, Qt.AspectRatioMode.KeepAspectRatio)


# ==================================================================
# Helper factories
# ==================================================================

def _tool_btn(icon_name: str, tooltip: str, checkable: bool = True) -> QPushButton:
    btn = QPushButton()
    icon_path = _ICONS_DIR / icon_name
    if icon_path.exists():
        btn.setIcon(QIcon(str(icon_path)))
        btn.setIconSize(QSize(22, 22))
    else:
        btn.setText(tooltip[0])
    btn.setToolTip(tooltip)
    btn.setCheckable(checkable)
    btn.setFixedSize(44, 44)
    btn.setStyleSheet(
        """
        QPushButton {
            background: #2d2d2d;
            border: 2px solid transparent;
            border-radius: 10px;
            color: #cccccc;
        }
        QPushButton:hover {
            background: #3a3a3a;
            border: 2px solid #555555;
        }
        QPushButton:checked {
            background: #1a73e8;
            border: 2px solid #4a9eff;
        }
        QPushButton:pressed {
            background: #1558b0;
        }
        """
    )
    return btn


def _action_btn(label: str, color: str) -> QPushButton:
    btn = QPushButton(label)
    btn.setFixedHeight(40)
    btn.setMinimumWidth(100)
    btn.setStyleSheet(
        f"""
        QPushButton {{
            background: {color};
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 13px;
            font-weight: bold;
            padding: 0 18px;
        }}
        QPushButton:hover {{ background: {color}cc; }}
        QPushButton:pressed {{ background: {color}99; }}
        """
    )
    return btn


# ==================================================================
# Annotation Editor Dialog
# ==================================================================

class AnnotationEditor(QDialog):
    def __init__(self, screenshot_path: str, step_number: int, parent=None) -> None:
        super().__init__(parent)
        self._screenshot_path = screenshot_path
        self._step_number = step_number
        self._annotated_path: str = screenshot_path

        self.setWindowTitle(f"Annotate — Step {step_number}")
        self.setMinimumSize(1000, 680)
        self.setWindowFlags(
            Qt.WindowType.Window | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setStyleSheet("QDialog { background: #1e1e1e; }")
        self._build_ui()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_tool_panel())

        centre = QVBoxLayout()
        centre.setContentsMargins(0, 0, 0, 0)
        centre.setSpacing(0)
        centre.addWidget(self._build_info_bar())

        pixmap = QPixmap(self._screenshot_path)
        self._canvas = AnnotationCanvas(pixmap)
        self._canvas.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        centre.addWidget(self._canvas, stretch=1)
        centre.addWidget(self._build_action_bar())
        root.addLayout(centre, stretch=1)

    def _build_tool_panel(self) -> QWidget:
        panel = QWidget()
        panel.setFixedWidth(72)
        panel.setStyleSheet("background: #252525; border-right: 1px solid #333333;")

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 16, 12, 16)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        lbl = QLabel("TOOLS")
        lbl.setStyleSheet("color: #666666; font-size: 9px; font-weight: bold; letter-spacing: 1px;")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl)
        layout.addSpacing(4)

        self._btn_arrow     = _tool_btn("arrow_tool.svg",     "Arrow  (A)")
        self._btn_text      = _tool_btn("text_tool.svg",      "Text  (T)")
        self._btn_highlight = _tool_btn("highlight_tool.svg", "Highlight  (H)")
        self._btn_blur      = _tool_btn("blur_tool.svg",      "Blur  (B)")

        self._tool_group = QButtonGroup(self)
        self._tool_group.setExclusive(True)
        for btn in (self._btn_arrow, self._btn_text, self._btn_highlight, self._btn_blur):
            self._tool_group.addButton(btn)
            layout.addWidget(btn)

        self._btn_arrow.setChecked(True)
        self._tool_group.buttonClicked.connect(self._on_tool_selected)

        layout.addStretch()

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("color: #333333;")
        layout.addWidget(line)
        layout.addSpacing(4)

        self._btn_undo = _tool_btn("undo.svg", "Undo  (Ctrl+Z)", checkable=False)
        layout.addWidget(self._btn_undo)
        self._btn_undo.clicked.connect(lambda: self._canvas.undo())

        self._btn_clear = _tool_btn("clear.svg", "Clear All", checkable=False)
        layout.addWidget(self._btn_clear)
        self._btn_clear.clicked.connect(lambda: self._canvas.clear_all())

        return panel

    def _build_info_bar(self) -> QWidget:
        bar = QWidget()
        bar.setFixedHeight(40)
        bar.setStyleSheet("background: #252525; border-bottom: 1px solid #333333;")

        layout = QHBoxLayout(bar)
        layout.setContentsMargins(16, 0, 16, 0)

        lbl = QLabel(f"Step {self._step_number}  ·  Draw arrows on your screenshot")
        lbl.setStyleSheet("color: #aaaaaa; font-size: 12px;")
        layout.addWidget(lbl)
        layout.addStretch()

        hint = QLabel("Click & drag to draw arrow  ·  Ctrl+Z to undo")
        hint.setStyleSheet("color: #555555; font-size: 11px;")
        layout.addWidget(hint)

        return bar

    def _build_action_bar(self) -> QWidget:
        bar = QWidget()
        bar.setFixedHeight(64)
        bar.setStyleSheet("background: #252525; border-top: 1px solid #333333;")

        layout = QHBoxLayout(bar)
        layout.setContentsMargins(20, 12, 20, 12)
        layout.setSpacing(12)
        layout.addStretch()

        self._btn_skip = _action_btn("Skip Annotation", "#444444")
        self._btn_skip.setToolTip("Use screenshot without annotation")
        self._btn_skip.clicked.connect(self.reject)

        self._btn_done = _action_btn("Done  ✓", "#1a73e8")
        self._btn_done.setToolTip("Save annotations and continue")
        self._btn_done.clicked.connect(self._on_done)

        layout.addWidget(self._btn_skip)
        layout.addWidget(self._btn_done)

        return bar

    # ------------------------------------------------------------------
    # Handlers
    # ------------------------------------------------------------------

    def _on_tool_selected(self, btn: QPushButton) -> None:
        tool_map = {
            self._btn_arrow:     "arrow",
            self._btn_text:      "text",
            self._btn_highlight: "highlight",
            self._btn_blur:      "blur",
        }
        self._canvas.set_tool(tool_map.get(btn, "arrow"))

    def _on_done(self) -> None:
        if not self._canvas._annotation_items:
            # Nothing drawn — use original
            self.accept()
            return

        pixmap = self._canvas.render_to_pixmap()
        out_path = Path(self._screenshot_path).with_stem(
            Path(self._screenshot_path).stem + "_annotated"
        )
        pixmap.save(str(out_path), "PNG")
        self._annotated_path = str(out_path)
        self.accept()

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key.Key_Z and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self._canvas.undo()
        else:
            super().keyPressEvent(event)

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def annotated_path(self) -> str:
        return self._annotated_path
