from __future__ import annotations

import math
from pathlib import Path

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsItem,
    QGraphicsTextItem, QWidget, QButtonGroup, QSizePolicy, QFrame,
    QInputDialog, QApplication,
)
from PySide6.QtGui import (
    QPixmap, QColor, QIcon, QPainter, QPen, QBrush,
    QPolygonF, QPainterPath, QImage, QFont,
)
from PySide6.QtCore import Qt, QSize, QPointF, QRectF, QLineF


_ICONS_DIR = Path(__file__).parent.parent / "resources" / "icons"

ARROW_COLOR    = QColor("#FF3B30")   # red
ARROW_WIDTH    = 3
ARROWHEAD_SIZE = 14

TEXT_FONT_SIZE = 16
TEXT_PADDING   = 10
TEXT_MAX_WIDTH = 320

HIGHLIGHT_COLOR  = QColor(255, 235, 59, 100)   # yellow, semi-transparent fill
HIGHLIGHT_BORDER = QColor(255, 193, 7, 220)     # amber border
HIGHLIGHT_WIDTH  = 2


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
# Text Graphics Item
# ==================================================================

def _is_dark_at(pixmap: QPixmap, pos: QPointF) -> bool:
    """Sample a small region around pos and return True if it is predominantly dark."""
    img = pixmap.toImage()
    x, y = int(pos.x()), int(pos.y())
    samples, total = 0, 0
    for dx in range(-20, 21, 10):
        for dy in range(-20, 21, 10):
            sx, sy = x + dx, y + dy
            if 0 <= sx < img.width() and 0 <= sy < img.height():
                c = img.pixelColor(sx, sy)
                total += 1
                if c.lightness() < 128:
                    samples += 1
    return (samples / total) > 0.5 if total else True


class TextItem(QGraphicsItem):
    def __init__(self, pos: QPointF, text: str, dark_bg: bool = True) -> None:
        super().__init__()
        self._text    = text
        self._font    = QFont("Segoe UI", TEXT_FONT_SIZE, QFont.Weight.Bold)
        self._dark_bg = dark_bg
        self.setPos(pos)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setCursor(Qt.CursorShape.SizeAllCursor)
        self._update_colors()
        self._recalc()

    def set_text(self, text: str) -> None:
        self.prepareGeometryChange()
        self._text = text
        self._recalc()
        self.update()

    def _update_colors(self) -> None:
        if self._dark_bg:
            self._bg_color   = QColor(0, 0, 0, 210)
            self._text_color = QColor("#FFFFFF")
        else:
            self._bg_color   = QColor(255, 255, 255, 230)
            self._text_color = QColor("#000000")

    def _recalc(self) -> None:
        from PySide6.QtGui import QFontMetrics
        fm = QFontMetrics(self._font)
        inner_w = TEXT_MAX_WIDTH - TEXT_PADDING * 2
        # Wrap text into lines
        words = self._text.split()
        lines, current = [], ""
        for word in words:
            test = (current + " " + word).strip()
            if fm.horizontalAdvance(test) <= inner_w:
                current = test
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        self._lines    = lines or [""]
        self._line_h   = fm.height()
        self._line_gap = 3
        total_h = len(self._lines) * self._line_h + (len(self._lines) - 1) * self._line_gap
        max_w   = max(fm.horizontalAdvance(l) for l in self._lines)
        self._inner_w  = max_w
        self._inner_h  = total_h
        self._box_w    = self._inner_w + TEXT_PADDING * 2
        self._box_h    = self._inner_h + TEXT_PADDING * 2

    def boundingRect(self) -> QRectF:
        return QRectF(0, 0, self._box_w, self._box_h)

    def paint(self, painter: QPainter, option, widget=None) -> None:
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setFont(self._font)

        bg_rect = QRectF(0, 0, self._box_w, self._box_h)

        # Background
        painter.setBrush(QBrush(self._bg_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(bg_rect, 8, 8)

        # Each line centred
        painter.setPen(QPen(self._text_color))
        for i, line in enumerate(self._lines):
            y = TEXT_PADDING + i * (self._line_h + self._line_gap)
            line_rect = QRectF(TEXT_PADDING, y, self._inner_w, self._line_h)
            painter.drawText(line_rect, Qt.AlignmentFlag.AlignCenter, line)

    def mouseDoubleClickEvent(self, event) -> None:
        self.scene().views()[0].window()._prompt_text_edit(self)


# ==================================================================
# Highlight Graphics Item
# ==================================================================

_HIGHLIGHT_PRESETS = [
    (QColor(255, 235, 59, 100),  QColor(255, 193, 7, 220)),    # yellow
    (QColor(76, 175, 80, 100),   QColor(56, 142, 60, 220)),     # green
    (QColor(33, 150, 243, 100),  QColor(21, 101, 192, 220)),    # blue
    (QColor(244, 67, 54, 100),   QColor(183, 28, 28, 220)),     # red
    (QColor(156, 39, 176, 100),  QColor(106, 27, 154, 220)),    # purple
]


_HANDLE_SIZE = 8
_HANDLES = ["tl", "tm", "tr", "ml", "mr", "bl", "bm", "br"]


class HighlightItem(QGraphicsItem):
    def __init__(self, start: QPointF) -> None:
        super().__init__()
        self._r            = QRectF(start, start)
        self._color_index  = 0
        self._fill, self._border = _HIGHLIGHT_PRESETS[0]
        self._resize_handle: str | None = None
        self._resize_start: QPointF | None = None
        self._rect_at_start: QRectF | None = None
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setAcceptHoverEvents(True)

    # ------------------------------------------------------------------
    # Geometry helpers
    # ------------------------------------------------------------------

    def update_end(self, end: QPointF) -> None:
        self.prepareGeometryChange()
        self._r = QRectF(self._r.topLeft(), end).normalized()

    def _handle_rects(self) -> dict[str, QRectF]:
        r = self._r
        s = _HANDLE_SIZE / 2
        mx, my = r.center().x(), r.center().y()
        return {
            "tl": QRectF(r.left()  - s, r.top()    - s, _HANDLE_SIZE, _HANDLE_SIZE),
            "tm": QRectF(mx        - s, r.top()    - s, _HANDLE_SIZE, _HANDLE_SIZE),
            "tr": QRectF(r.right() - s, r.top()    - s, _HANDLE_SIZE, _HANDLE_SIZE),
            "ml": QRectF(r.left()  - s, my         - s, _HANDLE_SIZE, _HANDLE_SIZE),
            "mr": QRectF(r.right() - s, my         - s, _HANDLE_SIZE, _HANDLE_SIZE),
            "bl": QRectF(r.left()  - s, r.bottom() - s, _HANDLE_SIZE, _HANDLE_SIZE),
            "bm": QRectF(mx        - s, r.bottom() - s, _HANDLE_SIZE, _HANDLE_SIZE),
            "br": QRectF(r.right() - s, r.bottom() - s, _HANDLE_SIZE, _HANDLE_SIZE),
        }

    def _handle_at(self, pos: QPointF) -> str | None:
        for name, rect in self._handle_rects().items():
            if rect.contains(pos):
                return name
        return None

    def _cursor_for_handle(self, handle: str) -> Qt.CursorShape:
        diag1 = {"tl", "br"}
        diag2 = {"tr", "bl"}
        horiz = {"ml", "mr"}
        if handle in diag1:
            return Qt.CursorShape.SizeFDiagCursor
        if handle in diag2:
            return Qt.CursorShape.SizeBDiagCursor
        if handle in horiz:
            return Qt.CursorShape.SizeHorCursor
        return Qt.CursorShape.SizeVerCursor

    def boundingRect(self) -> QRectF:
        return self._r.adjusted(-_HANDLE_SIZE, -_HANDLE_SIZE,
                                 _HANDLE_SIZE,  _HANDLE_SIZE)

    # ------------------------------------------------------------------
    # Paint
    # ------------------------------------------------------------------

    def paint(self, painter: QPainter, option, widget=None) -> None:
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        if self._r.width() < 2 or self._r.height() < 2:
            return

        # Fill + border
        painter.setBrush(QBrush(self._fill))
        painter.setPen(QPen(self._border, HIGHLIGHT_WIDTH,
                            Qt.PenStyle.SolidLine,
                            Qt.PenCapStyle.RoundCap,
                            Qt.PenJoinStyle.RoundJoin))
        painter.drawRoundedRect(self._r, 4, 4)

        # Draw handles when selected
        if self.isSelected():
            painter.setBrush(QBrush(QColor("#ffffff")))
            painter.setPen(QPen(QColor("#1a73e8"), 1.5))
            for rect in self._handle_rects().values():
                painter.drawRect(rect)

    # ------------------------------------------------------------------
    # Mouse events — resize
    # ------------------------------------------------------------------

    def hoverMoveEvent(self, event) -> None:
        handle = self._handle_at(event.pos())
        if handle:
            self.setCursor(self._cursor_for_handle(handle))
        elif self._r.contains(event.pos()):
            self.setCursor(Qt.CursorShape.SizeAllCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
        super().hoverMoveEvent(event)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            handle = self._handle_at(event.pos())
            if handle:
                self._resize_handle    = handle
                self._resize_start     = event.scenePos()
                self._rect_at_start    = QRectF(self._r)
                event.accept()
                return
        # Move the whole box
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:
        if self._resize_handle and self._resize_start and self._rect_at_start:
            delta = event.scenePos() - self._resize_start
            r     = QRectF(self._rect_at_start)
            h     = self._resize_handle
            if "l" in h: r.setLeft(r.left()     + delta.x())
            if "r" in h: r.setRight(r.right()   + delta.x())
            if "t" in h: r.setTop(r.top()       + delta.y())
            if "b" in h: r.setBottom(r.bottom() + delta.y())
            self.prepareGeometryChange()
            self._r = r.normalized()
            self.update()
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        self._resize_handle = None
        self._resize_start  = None
        self._rect_at_start = None
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event) -> None:
        self._color_index = (self._color_index + 1) % len(_HIGHLIGHT_PRESETS)
        self._fill, self._border = _HIGHLIGHT_PRESETS[self._color_index]
        self.update()


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

        self.setRenderHints(
            QPainter.RenderHint.Antialiasing |
            QPainter.RenderHint.SmoothPixmapTransform
        )
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setStyleSheet("background: #1a1a1a; border: none;")
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)

        self._zoom_level: float = 1.0
        self._current_tool: str = "arrow"
        self._drawing: bool = False
        self._current_item: ArrowItem | HighlightItem | None = None
        self._annotation_items: list[QGraphicsItem] = []
        self._pending_text_pos: QPointF | None = None

    # ------------------------------------------------------------------
    # Tool switching
    # ------------------------------------------------------------------

    def set_tool(self, tool: str) -> None:
        self._current_tool = tool
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
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

    def add_text_item(self, pos: QPointF, text: str) -> None:
        dark = _is_dark_at(self._pixmap_item.pixmap(), pos)
        item = TextItem(pos, text, dark_bg=not dark)
        self._scene.addItem(item)
        self._annotation_items.append(item)
        self._scene.update()

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton and self._current_tool == "arrow":
            scene_pos = self.mapToScene(event.position().toPoint())
            self._drawing = True
            self._current_item = ArrowItem(scene_pos, scene_pos)
            self._scene.addItem(self._current_item)
        elif event.button() == Qt.MouseButton.LeftButton and self._current_tool == "highlight":
            scene_pos = self.mapToScene(event.position().toPoint())
            hit = self._scene.itemAt(scene_pos, self.transform())
            if hit and isinstance(hit, HighlightItem):
                super().mousePressEvent(event)
            else:
                self._drawing = True
                self._current_item = HighlightItem(scene_pos)
                self._current_item.setSelected(True)
                self._scene.addItem(self._current_item)
        elif event.button() == Qt.MouseButton.LeftButton and self._current_tool == "text":
            scene_pos = self.mapToScene(event.position().toPoint())
            hit = self._scene.itemAt(scene_pos, self.transform())
            if hit and isinstance(hit, TextItem):
                super().mousePressEvent(event)  # let the item handle drag
            else:
                self._pending_text_pos = scene_pos
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
        elif self._current_tool == "text" and self._pending_text_pos is not None:
            pos = self._pending_text_pos
            self._pending_text_pos = None
            self.window()._prompt_text_input(pos)
        else:
            super().mouseReleaseEvent(event)

    # ------------------------------------------------------------------
    # Zoom support
    # ------------------------------------------------------------------

    def wheelEvent(self, event) -> None:
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            factor = 1.15 if event.angleDelta().y() > 0 else 1 / 1.15
            new_zoom = self._zoom_level * factor
            if 0.1 <= new_zoom <= 5.0:
                self._zoom_level = new_zoom
                self.scale(factor, factor)
                self.window()._update_zoom_label(self._zoom_level)
        else:
            super().wheelEvent(event)

    def zoom_fit(self) -> None:
        self.resetTransform()
        self._zoom_level = 1.0
        self.fitInView(self._pixmap_item, Qt.AspectRatioMode.KeepAspectRatio)
        vw = self.viewport().width()
        vh = self.viewport().height()
        iw = self._pixmap_item.pixmap().width()
        ih = self._pixmap_item.pixmap().height()
        self._zoom_level = min(vw / iw, vh / ih)
        self.window()._update_zoom_label(self._zoom_level)

    def zoom_100(self) -> None:
        self.resetTransform()
        self._zoom_level = 1.0
        self.window()._update_zoom_label(self._zoom_level)

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self.zoom_fit()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)

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

        self._hint_label = QLabel("Click & drag to draw arrow  ·  Ctrl+Z to undo")
        self._hint_label.setStyleSheet("color: #555555; font-size: 11px;")
        layout.addWidget(self._hint_label)

        layout.addSpacing(16)

        btn_fit = QPushButton("Fit")
        btn_fit.setFixedHeight(24)
        btn_fit.setFixedWidth(36)
        btn_fit.setStyleSheet(
            "QPushButton { background:#333; color:#aaa; border:1px solid #555;"
            "border-radius:4px; font-size:11px; }"
            "QPushButton:hover { background:#444; }"
        )
        btn_fit.setToolTip("Fit to window")
        btn_fit.clicked.connect(lambda: self._canvas.zoom_fit())
        layout.addWidget(btn_fit)

        btn_100 = QPushButton("100%")
        btn_100.setFixedHeight(24)
        btn_100.setFixedWidth(42)
        btn_100.setStyleSheet(
            "QPushButton { background:#333; color:#aaa; border:1px solid #555;"
            "border-radius:4px; font-size:11px; }"
            "QPushButton:hover { background:#444; }"
        )
        btn_100.setToolTip("Actual size")
        btn_100.clicked.connect(lambda: self._canvas.zoom_100())
        layout.addWidget(btn_100)

        self._zoom_label = QLabel("100%")
        self._zoom_label.setStyleSheet("color: #666666; font-size: 11px; min-width: 38px;")
        self._zoom_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._zoom_label)

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
        tool = tool_map.get(btn, "arrow")
        self._canvas.set_tool(tool)
        hints = {
            "arrow":     "Click & drag to draw arrow  ·  Ctrl+Z to undo",
            "text":      "Click on the screenshot to place a text label  ·  Ctrl+Z to undo",
            "highlight": "Click & drag to highlight an area  ·  Ctrl+Z to undo",
            "blur":      "Click & drag to blur sensitive data  ·  Ctrl+Z to undo",
        }
        self._hint_label.setText(hints.get(tool, ""))

    def _update_zoom_label(self, zoom: float) -> None:
        self._zoom_label.setText(f"{int(zoom * 100)}%")

    def _prompt_text_input(self, pos: QPointF) -> None:
        text, ok = QInputDialog.getText(
            self, "Add Text Label", "Enter label text:",
        )
        if ok and text.strip():
            self._canvas.add_text_item(pos, text.strip())

    def _prompt_text_edit(self, item: "TextItem") -> None:
        text, ok = QInputDialog.getText(
            self, "Edit Text Label", "Edit label text:", text=item._text,
        )
        if ok and text.strip():
            item.set_text(text.strip())

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
        elif event.key() == Qt.Key.Key_0 and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self._canvas.zoom_fit()
        elif event.key() == Qt.Key.Key_1 and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self._canvas.zoom_100()
        else:
            super().keyPressEvent(event)

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def annotated_path(self) -> str:
        return self._annotated_path
