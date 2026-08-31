import sys
import os
import json
import time
import platform
from pathlib import Path
from datetime import datetime

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QTabWidget, QPushButton, QLabel, QLineEdit,
    QComboBox, QCheckBox, QSpinBox, QProgressBar, QTextEdit,
    QFileDialog, QListWidget, QListWidgetItem, QGroupBox,
    QFrame, QSplitter, QScrollArea, QMessageBox, QSlider,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QToolButton, QSizePolicy, QMenu, QStatusBar
)
from PyQt6.QtCore import (
    Qt, QThread, pyqtSignal, QTimer, QSize, QPropertyAnimation,
    QEasingCurve, QParallelAnimationGroup, QPoint, QEvent
)
from PyQt6.QtGui import (
    QFont, QColor, QPalette, QIcon, QBrush, QPainter,
    QLinearGradient, QPixmap, QDragEnterEvent, QDropEvent,
    QAction, QCursor
)

from engines.copy_engine import CopyEngine, CopyOptions
from engines.archive_engine import ArchiveEngine, ArchiveOptions
from engines.split_engine import SplitEngine, SplitOptions, MergeOptions

STYLESHEET = """
QMainWindow {
    background-color: #0d1117;
}
QWidget {
    background-color: #0d1117;
    color: #c9d1d9;
    font-family: 'Segoe UI', 'SF Pro Display', 'Ubuntu', sans-serif;
    font-size: 13px;
}
QTabWidget::pane {
    border: 1px solid #21262d;
    border-radius: 8px;
    background-color: #161b22;
    top: -1px;
}
QTabBar::tab {
    background-color: #21262d;
    color: #8b949e;
    padding: 10px 24px;
    margin-right: 2px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    border: 1px solid #21262d;
    font-weight: bold;
    font-size: 13px;
    min-width: 100px;
}
QTabBar::tab:selected {
    background-color: #161b22;
    color: #58a6ff;
    border-bottom-color: #161b22;
}
QTabBar::tab:hover:!selected {
    background-color: #30363d;
    color: #c9d1d9;
}
QPushButton {
    background-color: #21262d;
    color: #c9d1d9;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: bold;
    font-size: 13px;
    min-height: 20px;
}
QPushButton:hover {
    background-color: #30363d;
    border-color: #58a6ff;
    color: #58a6ff;
}
QPushButton:pressed {
    background-color: #1a2030;
}
QPushButton#primaryBtn {
    background-color: #238636;
    border-color: #2ea043;
    color: #ffffff;
    font-size: 14px;
    padding: 10px 28px;
}
QPushButton#primaryBtn:hover {
    background-color: #2ea043;
    border-color: #3fb950;
}
QPushButton#dangerBtn {
    background-color: #da3633;
    border-color: #f85149;
    color: #ffffff;
}
QPushButton#dangerBtn:hover {
    background-color: #f85149;
}
QPushButton#accentBtn {
    background-color: #1f6feb;
    border-color: #388bfd;
    color: #ffffff;
}
QPushButton#accentBtn:hover {
    background-color: #388bfd;
}
QPushButton#winBtn {
    background-color: transparent;
    border: none;
    border-radius: 6px;
    color: #8b949e;
    font-size: 15px;
    padding: 0;
    font-weight: normal;
    min-height: 0;
}
QPushButton#winBtn:hover {
    background-color: #30363d;
    color: #f0f6fc;
}
QPushButton#closeBtn {
    background-color: transparent;
    border: none;
    border-radius: 6px;
    color: #8b949e;
    font-size: 14px;
    padding: 0;
    font-weight: normal;
    min-height: 0;
}
QPushButton#closeBtn:hover {
    background-color: #da3633;
    color: #ffffff;
}
QLineEdit {
    background-color: #0d1117;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 8px 12px;
    color: #c9d1d9;
    font-size: 13px;
    selection-background-color: #1f6feb;
}
QLineEdit:focus {
    border-color: #58a6ff;
}
QLineEdit:read-only {
    background-color: #161b22;
    color: #8b949e;
}
QComboBox {
    background-color: #0d1117;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 8px 12px;
    color: #c9d1d9;
    font-size: 13px;
    min-width: 100px;
}
QComboBox:hover {
    border-color: #58a6ff;
}
QComboBox::drop-down {
    border: none;
    width: 30px;
}
QComboBox QAbstractItemView {
    background-color: #161b22;
    border: 1px solid #30363d;
    color: #c9d1d9;
    selection-background-color: #1f6feb;
    border-radius: 6px;
    padding: 4px;
}
QCheckBox {
    spacing: 8px;
    color: #c9d1d9;
    font-size: 13px;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 2px solid #30363d;
    background-color: #0d1117;
}
QCheckBox::indicator:checked {
    background-color: #238636;
    border-color: #2ea043;
}
QCheckBox::indicator:hover {
    border-color: #58a6ff;
}
QSpinBox {
    background-color: #0d1117;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 6px 8px;
    color: #c9d1d9;
    font-size: 13px;
}
QSpinBox:focus {
    border-color: #58a6ff;
}
QProgressBar {
    border: 1px solid #30363d;
    border-radius: 6px;
    background-color: #0d1117;
    text-align: center;
    color: #ffffff;
    font-weight: bold;
    font-size: 12px;
    min-height: 24px;
}
QProgressBar::chunk {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #238636, stop:0.5 #2ea043, stop:1 #3fb950);
    border-radius: 5px;
}
QGroupBox {
    border: 1px solid #21262d;
    border-radius: 8px;
    margin-top: 16px;
    padding: 16px 12px 12px 12px;
    font-weight: bold;
    color: #58a6ff;
    font-size: 13px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 16px;
    padding: 0 8px;
}
QTextEdit {
    background-color: #0d1117;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 8px;
    color: #c9d1d9;
    font-family: 'Cascadia Code', 'JetBrains Mono', 'Fira Code', monospace;
    font-size: 12px;
}
QListWidget {
    background-color: #0d1117;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 4px;
    color: #c9d1d9;
    font-size: 13px;
}
QListWidget::item {
    padding: 6px 8px;
    border-radius: 4px;
    margin: 1px 0;
}
QListWidget::item:selected {
    background-color: #1f6feb33;
    color: #58a6ff;
}
QListWidget::item:hover {
    background-color: #21262d;
}
QTableWidget {
    background-color: #0d1117;
    border: 1px solid #30363d;
    border-radius: 6px;
    gridline-color: #21262d;
    color: #c9d1d9;
    font-size: 12px;
    selection-background-color: #1f6feb33;
}
QTableWidget::item {
    padding: 6px;
}
QHeaderView::section {
    background-color: #161b22;
    color: #8b949e;
    border: 1px solid #21262d;
    padding: 8px;
    font-weight: bold;
    font-size: 12px;
}
QScrollBar:vertical {
    background-color: #0d1117;
    width: 8px;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background-color: #30363d;
    border-radius: 4px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background-color: #484f58;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
QScrollBar:horizontal {
    background-color: #0d1117;
    height: 8px;
    border-radius: 4px;
}
QScrollBar::handle:horizontal {
    background-color: #30363d;
    border-radius: 4px;
    min-width: 30px;
}
QFrame#separator {
    background-color: #21262d;
    max-height: 1px;
}
QFrame#card {
    background-color: #161b22;
    border: 1px solid #21262d;
    border-radius: 10px;
    padding: 16px;
}
QStatusBar {
    background-color: #0d1117;
    border-top: 1px solid #21262d;
    color: #8b949e;
    font-size: 12px;
}
QMenu {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 4px;
    color: #c9d1d9;
}
QMenu::item {
    padding: 8px 24px;
    border-radius: 4px;
}
QMenu::item:selected {
    background-color: #1f6feb33;
    color: #58a6ff;
}
QSlider::groove:horizontal {
    border: none;
    height: 6px;
    background-color: #21262d;
    border-radius: 3px;
}
QSlider::handle:horizontal {
    background-color: #58a6ff;
    width: 16px;
    height: 16px;
    margin: -5px 0;
    border-radius: 8px;
}
QSlider::handle:horizontal:hover {
    background-color: #79c0ff;
}
QSlider::sub-page:horizontal {
    background-color: #238636;
    border-radius: 3px;
}
"""


class CopyWorker(QThread):
    progress = pyqtSignal(int, int, str)
    file_start = pyqtSignal(str, str)
    file_complete = pyqtSignal(str, str, bool)
    error = pyqtSignal(str, str)
    complete = pyqtSignal(object)
    log = pyqtSignal(str)

    def __init__(self, options: CopyOptions):
        super().__init__()
        self.options = options
        self.engine = CopyEngine()

    def run(self):
        self.options.on_progress = self._on_progress
        self.options.on_file_start = self._on_file_start
        self.options.on_file_complete = self._on_file_complete
        self.options.on_error = self._on_error
        self.options.on_complete = self._on_complete
        self.engine.execute(self.options)

    def _on_progress(self, current, total, filepath):
        pct = int(current / total * 100) if total > 0 else 0
        self.progress.emit(pct, total, os.path.basename(filepath))

    def _on_file_start(self, src, dst):
        self.file_start.emit(src, dst)
        self.log.emit(f"COPY: {os.path.basename(src)}")

    def _on_file_complete(self, src, dst, success):
        status = "OK" if success else "FAILED"
        self.file_complete.emit(src, dst, success)
        self.log.emit(f"[{status}] {os.path.basename(src)}")

    def _on_error(self, filepath, msg):
        self.error.emit(filepath, msg)
        self.log.emit(f"[ERROR] {filepath}: {msg}")

    def _on_complete(self, stats):
        self.complete.emit(stats)
        self.log.emit(f"COMPLETE: {stats.copied_files}/{stats.total_files} files, "
                      f"{stats.failed_files} failed, {stats.skipped_files} skipped")

    def stop(self):
        self.engine.stop()


class ArchiveWorker(QThread):
    progress = pyqtSignal(int, int, str)
    complete = pyqtSignal(str, int)
    error = pyqtSignal(str, str)
    log = pyqtSignal(str)

    def __init__(self, options: ArchiveOptions):
        super().__init__()
        self.options = options
        self.engine = ArchiveEngine()

    def run(self):
        self.options.on_progress = self._on_progress
        self.options.on_complete = self._on_complete
        self.options.on_error = self._on_error
        self.engine.execute(self.options)

    def _on_progress(self, current, total, filepath):
        pct = int(current / total * 100) if total > 0 else 0
        self.progress.emit(pct, total, os.path.basename(filepath))
        self.log.emit(f"ARCHIVE: {os.path.basename(filepath)} [{current}/{total}]")

    def _on_complete(self, path, size):
        self.complete.emit(path, size)
        self.log.emit(f"ARCHIVE COMPLETE: {path} ({self._format_size(size)})")

    def _on_error(self, path, msg):
        self.error.emit(path, msg)
        self.log.emit(f"[ERROR] {path}: {msg}")

    @staticmethod
    def _format_size(size):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} PB"

    def stop(self):
        self.engine.stop()


class SplitWorker(QThread):
    progress = pyqtSignal(int, int, str)
    complete = pyqtSignal(object)
    error = pyqtSignal(str, str)
    log = pyqtSignal(str)

    def __init__(self, options, mode='split'):
        super().__init__()
        self.options = options
        self.mode = mode
        self.engine = SplitEngine()

    def run(self):
        self.options.on_progress = self._on_progress
        self.options.on_complete = self._on_complete
        self.options.on_error = self._on_error

        if self.mode == 'split':
            self.engine.split(self.options)
        else:
            self.engine.merge(self.options)

    def _on_progress(self, current, total, filepath):
        pct = int(current / total * 100) if total > 0 else 0
        self.progress.emit(pct, total, os.path.basename(filepath))
        self.log.emit(f"{'SPLIT' if self.mode == 'split' else 'MERGE'}: {os.path.basename(filepath)} [{current}/{total}]")

    def _on_complete(self, *args):
        self.complete.emit(args)
        self.log.emit("SPLIT/MERGE COMPLETE")

    def _on_error(self, path, msg):
        self.error.emit(path, msg)
        self.log.emit(f"[ERROR] {path}: {msg}")

    def stop(self):
        self.engine.stop()


class ModernCard(QFrame):
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(12)
        self.layout.setContentsMargins(16, 16, 16, 16)
        if title:
            label = QLabel(title)
            label.setStyleSheet("color: #58a6ff; font-weight: bold; font-size: 14px; border: none;")
            self.layout.addWidget(label)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SwiftCopy - Ultra-Fast File Transfer Suite")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setMinimumSize(1000, 700)
        self.resize(1280, 860)
        self.current_worker = None
        self.copy_history = []
        self._drag_pos = None
        self._drag_active = False
        self._title_frame = None
        self._resize_edges = None
        self._resize_start_global = None
        self._resize_start_geom = None
        self._is_maximized = False
        self._normal_geometry = None
        self._init_ui()
        self._cursor_timer = QTimer(self)
        self._cursor_timer.timeout.connect(self._update_edge_cursor)
        self._cursor_timer.start(50)
        self.statusBar().showMessage(
            "Ready | System: " + platform.system() + " | Tool: " + CopyEngine().get_system_copy_tool() +
            "  |  © 2026 ChainIT | newan0805"
        )

    RESIZE_MARGIN = 8
    TITLE_BAR_HEIGHT = 52

    def _update_edge_cursor(self):
        if self._resize_edges or not self.isActiveWindow() or self._is_maximized:
            return
        gpos = self.mapFromGlobal(self.cursor().pos())
        if not (0 <= gpos.x() < self.width() and 0 <= gpos.y() < self.height()):
            self.unsetCursor()
            return
        edges = self._hit_test(gpos)
        cursor = self._corner_for_resize(edges)
        if cursor:
            self.setCursor(cursor)
        else:
            self.unsetCursor()

    def _hit_test(self, pos) -> int:
        if self._is_maximized:
            return 0
        x, y = pos.x(), pos.y()
        rw, rh = self.width(), self.height()
        m = self.RESIZE_MARGIN
        top = y <= m
        bottom = y >= rh - m
        left = x <= m
        right = x >= rw - m

        if top and left:
            return Qt.Edge.TopEdge | Qt.Edge.LeftEdge
        if top and right:
            return Qt.Edge.TopEdge | Qt.Edge.RightEdge
        if bottom and left:
            return Qt.Edge.BottomEdge | Qt.Edge.LeftEdge
        if bottom and right:
            return Qt.Edge.BottomEdge | Qt.Edge.RightEdge
        if top:
            return Qt.Edge.TopEdge
        if bottom:
            return Qt.Edge.BottomEdge
        if left:
            return Qt.Edge.LeftEdge
        if right:
            return Qt.Edge.RightEdge
        return 0

    @staticmethod
    def _corner_for_resize(edges) -> str:
        mapping = (
            (Qt.Edge.TopEdge | Qt.Edge.LeftEdge, Qt.CursorShape.SizeFDiagCursor),
            (Qt.Edge.TopEdge | Qt.Edge.RightEdge, Qt.CursorShape.SizeBDiagCursor),
            (Qt.Edge.BottomEdge | Qt.Edge.LeftEdge, Qt.CursorShape.SizeBDiagCursor),
            (Qt.Edge.BottomEdge | Qt.Edge.RightEdge, Qt.CursorShape.SizeFDiagCursor),
            (Qt.Edge.TopEdge | Qt.Edge.BottomEdge, Qt.CursorShape.SizeVerCursor),
            (Qt.Edge.LeftEdge | Qt.Edge.RightEdge, Qt.CursorShape.SizeHorCursor),
        )
        for e, c in mapping:
            if edges and (edges & e) == e:
                return c
        if edges == Qt.Edge.TopEdge or edges == Qt.Edge.BottomEdge:
            return Qt.CursorShape.SizeVerCursor
        if edges == Qt.Edge.LeftEdge or edges == Qt.Edge.RightEdge:
            return Qt.CursorShape.SizeHorCursor
        return None

    def mousePressEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton:
            return super().mousePressEvent(event)
        pos = event.position().toPoint()
        edges = self._hit_test(pos)
        if edges and not self._drag_active:
            self._resize_edges = edges
            self._resize_start_global = event.globalPosition().toPoint()
            self._resize_start_geom = self.geometry()
            event.accept()
            return
        self._resize_edges = None
        if self._on_title_bar(event.globalPosition().toPoint()):
            self._drag_pos = event.globalPosition().toPoint()
            self._drag_active = True
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        pos = event.position().toPoint()
        if self._resize_edges:
            start = self._resize_start_global
            geom = self._resize_start_geom
            cur = event.globalPosition().toPoint()
            dx = cur.x() - start.x()
            dy = cur.y() - start.y()
            x, y, w, h = geom.x(), geom.y(), geom.width(), geom.height()
            edges = self._resize_edges
            min_w, min_h = self.minimumWidth(), self.minimumHeight()

            if edges & Qt.Edge.LeftEdge:
                nw = w - dx
                if nw >= min_w:
                    x = geom.x() + dx
                    w = nw
            if edges & Qt.Edge.RightEdge:
                if w + dx >= min_w:
                    w = w + dx
            if edges & Qt.Edge.TopEdge:
                nh = h - dy
                if nh >= min_h:
                    y = geom.y() + dy
                    h = nh
            if edges & Qt.Edge.BottomEdge:
                if h + dy >= min_h:
                    h = h + dy

            self.setGeometry(x, y, w, h)
            event.accept()
            return

        if self._drag_active and event.buttons() & Qt.MouseButton.LeftButton:
            delta = event.globalPosition().toPoint() - self._drag_pos
            self.move(self.pos() + delta)
            self._drag_pos = event.globalPosition().toPoint()
            event.accept()
            return

        if self._is_maximized or self._hit_test(pos):
            return super().mouseMoveEvent(event)

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
        self._drag_active = False
        self._resize_edges = None
        self.unsetCursor()
        super().mouseReleaseEvent(event)

    def _on_title_bar(self, global_point) -> bool:
        if not self._title_frame:
            return False
        local = self._title_frame.mapFromGlobal(global_point)
        return self._title_frame.rect().contains(local)

    def eventFilter(self, obj, event):
        if self._title_frame and obj is self._title_frame:
            if event.type() == QEvent.Type.MouseButtonDblClick and event.button() == Qt.MouseButton.LeftButton:
                self._toggle_maximize()
                return True
            if event.type() == QEvent.Type.MouseButtonPress and event.button() == Qt.MouseButton.LeftButton:
                if self._is_maximized:
                    return super().eventFilter(obj, event)
                if self.windowHandle() is not None and hasattr(self.windowHandle(), 'startSystemMove'):
                    try:
                        if self.windowHandle().startSystemMove():
                            return True
                    except Exception:
                        pass
                self._drag_pos = event.globalPosition().toPoint()
                self._drag_active = True
                return True
            if (self._drag_active and event.type() == QEvent.Type.MouseMove):
                delta = event.globalPosition().toPoint() - self._drag_pos
                self.move(self.pos() + delta)
                self._drag_pos = event.globalPosition().toPoint()
                return True
            if (self._drag_active and event.type() == QEvent.Type.MouseButtonRelease):
                self._drag_pos = None
                self._drag_active = False
                self.unsetCursor()
                return True
        return super().eventFilter(obj, event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and event.position().toPoint().y() <= self.TITLE_BAR_HEIGHT:
            self._toggle_maximize()
        else:
            super().mouseDoubleClickEvent(event)

    def _toggle_maximize(self):
        if self._is_maximized:
            if self._normal_geometry:
                self.setGeometry(self._normal_geometry)
                self._normal_geometry = None
            self._is_maximized = False
        else:
            self._normal_geometry = self.geometry()
            self.showMaximized()
            self._is_maximized = True

    def _minimize(self):
        self.showMinimized()

    def _close(self):
        self.close()

    def closeEvent(self, event):
        self._cursor_timer.stop()
        if self.current_worker:
            try:
                self.current_worker.stop()
            except Exception:
                pass
        super().closeEvent(event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, '_header_subtitle'):
            narrow = self.width() < 760
            self._header_subtitle.setVisible(not narrow)
            if hasattr(self, '_title_icon'):
                self._title_icon.setVisible(not narrow)

    def _init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        header = self._create_header()
        main_layout.addWidget(header)

        content_wrap = QWidget()
        content_wrap.setObjectName("contentWrap")
        content_layout = QVBoxLayout(content_wrap)
        content_layout.setContentsMargins(12, 12, 12, 12)
        content_layout.setSpacing(12)

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.addTab(self._create_copy_tab(), "  Copy  ")
        self.tabs.addTab(self._create_archive_tab(), "  Archive  ")
        self.tabs.addTab(self._create_split_tab(), "  Split / Merge  ")
        self.tabs.addTab(self._create_settings_tab(), "  Settings  ")
        self.tabs.addTab(self._create_history_tab(), "  History  ")
        content_layout.addWidget(self.tabs, 1)

        footer = QFrame()
        footer.setObjectName("card")
        footer.setStyleSheet(
            "QFrame#card { background-color: #161b22; border: 1px solid #21262d;"
            " border-radius: 8px; padding: 6px 12px; }"
        )
        footer.setFixedHeight(34)
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(12, 4, 12, 4)
        copy_label = QLabel("© 2026 ChainIT | Author: newan0805")
        copy_label.setStyleSheet(
            "color: #8b949e; font-size: 12px; border: none;"
            "font-weight: bold; color: #58a6ff;"
        )
        footer_layout.addWidget(copy_label)

        sites_label = QLabel(
            "<a style='color:#58a6ff; text-decoration:none;' "
            "href='https://chainit.vercel.app'>chainit.vercel.app</a>"
            "&nbsp;&nbsp;|&nbsp;&nbsp;"
            "<a style='color:#58a6ff; text-decoration:none;' "
            "href='https://newan0805.vercel.app'>newan0805.vercel.app</a>"
        )
        sites_label.setOpenExternalLinks(True)
        sites_label.setTextFormat(Qt.TextFormat.RichText)
        sites_label.setStyleSheet("border: none; font-size: 12px;")
        # footer_layout.addWidget(sites_label)

        footer_layout.addStretch()
        about_btn = QPushButton("About")
        about_btn.setFixedSize(70, 26)
        about_btn.clicked.connect(self._show_about)
        # footer_layout.addWidget(about_btn)

        # content_layout.addWidget(footer)
        main_layout.addWidget(content_wrap, 1)

    def _create_header(self):
        header = QFrame()
        header.setFixedHeight(52)
        header.setObjectName("titleBar")
        header.setStyleSheet("""
            QFrame#titleBar {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #161b22, stop:0.5 #1c2128, stop:1 #161b22);
                border-bottom: 1px solid #21262d;
                border-radius: 0;
            }
        """)
        self._title_frame = header
        layout = QHBoxLayout(header)
        layout.setContentsMargins(16, 6, 8, 6)
        layout.setSpacing(8)

        icon_label = QLabel(">>")
        icon_label.setStyleSheet("color: #3fb950; font-size: 20px; font-weight: bold; border: none;")
        layout.addWidget(icon_label)

        title = QLabel("SwiftCopy")
        title.setStyleSheet("color: #f0f6fc; font-size: 18px; font-weight: bold; border: none;")
        layout.addWidget(title)

        self._header_subtitle = QLabel("Ultra-Fast File Transfer Suite")
        self._header_subtitle.setStyleSheet("color: #8b949e; font-size: 12px; border: none;")
        layout.addWidget(self._header_subtitle)

        self._title_icon = icon_label

        for w in (header, icon_label, title, self._header_subtitle):
            w.installEventFilter(self)
            w.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, w is not header)

        layout.addStretch()

        about_btn = QPushButton("About")
        about_btn.setObjectName("winBtn")
        about_btn.setFixedSize(64, 30)
        about_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        about_btn.clicked.connect(self._show_about)
        layout.addWidget(about_btn)

        min_btn = QPushButton("—")
        min_btn.setObjectName("winBtn")
        min_btn.setFixedSize(40, 30)
        min_btn.setToolTip("Minimize")
        min_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        min_btn.clicked.connect(self._minimize)
        layout.addWidget(min_btn)

        max_btn = QPushButton("□")
        max_btn.setObjectName("winBtn")
        max_btn.setFixedSize(40, 30)
        max_btn.setToolTip("Maximize / Restore")
        max_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        max_btn.clicked.connect(self._toggle_maximize)
        layout.addWidget(max_btn)

        close_btn = QPushButton("✕")
        close_btn.setObjectName("closeBtn")
        close_btn.setFixedSize(40, 30)
        close_btn.setToolTip("Close")
        close_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        close_btn.clicked.connect(self._close)
        layout.addWidget(close_btn)

        return header

    def _show_about(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("About SwiftCopy")
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setText(
            "<h3>SwiftCopy</h3>"
            "<p><b>Ultra-Fast File Transfer Suite</b></p>"
            "<p>Bulk file copying, archiving, splitting &amp; merging.</p>"
            "<hr>"
            "<p><b>&copy; 2026 ChainIT</b><br>"
            "All rights reserved.</p>"
            "<p><b>Author:</b> newan0805</p>"
            "<p><b>ChainIT:</b> <a href='https://chainit.vercel.app'>chainit.vercel.app</a><br>"
            "<b>Author site:</b> <a href='https://newan0805.vercel.app'>newan0805.vercel.app</a></p>"
            # "<p>Built with Python + PyQt6</p>"
        )
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.exec()

    def _create_browse_row(self, label_text, placeholder, file_mode=False):
        row = QHBoxLayout()
        row.setSpacing(8)
        lbl = QLabel(label_text)
        lbl.setFixedWidth(120)
        lbl.setStyleSheet("color: #8b949e; font-weight: bold;")
        entry = QLineEdit()
        entry.setPlaceholderText(placeholder)
        entry.setMinimumHeight(36)
        row.addWidget(lbl)
        row.addWidget(entry, 1)

        btn = QPushButton("Browse")
        btn.setFixedWidth(90)
        btn.setMinimumHeight(36)
        if file_mode:
            btn.clicked.connect(lambda: self._browse_file(entry))
        else:
            btn.clicked.connect(lambda: self._browse_folder(entry))
        row.addWidget(btn)
        return row, entry

    def _browse_folder(self, entry):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            entry.setText(folder)

    def _browse_file(self, entry):
        folder = QFileDialog.getOpenFileName(self, "Select File")
        if folder and folder[0]:
            entry.setText(folder[0])

    def _create_copy_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)

        src_row, self.copy_source = self._create_browse_row("Source:", "Path to file or folder...")
        layout.addLayout(src_row)

        dst_row, self.copy_dest = self._create_browse_row("Destination:", "Destination path...")
        layout.addLayout(dst_row)

        options_card = ModernCard("Copy Options")
        grid = QGridLayout()
        grid.setSpacing(10)
        for col in range(4):
            grid.setColumnStretch(col, 1)

        self.copy_recursive = QCheckBox("Recursive")
        self.copy_recursive.setChecked(True)
        grid.addWidget(self.copy_recursive, 0, 0)

        self.copy_overwrite = QCheckBox("Overwrite")
        self.copy_overwrite.setChecked(True)
        grid.addWidget(self.copy_overwrite, 0, 1)

        self.copy_verify = QCheckBox("Verify (hash)")
        self.copy_verify.setChecked(True)
        grid.addWidget(self.copy_verify, 0, 2)

        self.copy_preserve = QCheckBox("Preserve attrs")
        self.copy_preserve.setChecked(True)
        grid.addWidget(self.copy_preserve, 0, 3)

        self.copy_symlinks = QCheckBox("Follow symlinks")
        self.copy_symlinks.setChecked(True)
        grid.addWidget(self.copy_symlinks, 1, 0)

        self.copy_skip_hidden = QCheckBox("Skip hidden")
        grid.addWidget(self.copy_skip_hidden, 1, 1)

        self.copy_dry_run = QCheckBox("Dry run")
        grid.addWidget(self.copy_dry_run, 1, 2)

        self.copy_resume = QCheckBox("Resume support")
        self.copy_resume.setChecked(True)
        grid.addWidget(self.copy_resume, 1, 3)

        self.copy_include_parent = QCheckBox("Include parent folder")
        self.copy_include_parent.setChecked(True)
        self.copy_include_parent.setToolTip(
            "Copy the selected folder WITH its parent folder into the destination.\n"
            "Example: /music/Album -> /dest/Album/...  (not just /dest/... contents)"
        )
        self.copy_include_parent.setStyleSheet(
            "QCheckBox { color: #58a6ff; font-weight: bold; }"
        )
        grid.addWidget(self.copy_include_parent, 2, 0, 1, 2)

        workers_row = QHBoxLayout()
        workers_row.addWidget(QLabel("Workers:"))
        self.copy_workers = QSpinBox()
        self.copy_workers.setRange(1, 32)
        self.copy_workers.setValue(4)
        workers_row.addWidget(self.copy_workers)

        workers_row.addWidget(QLabel("Buffer:"))
        self.copy_buffer = QComboBox()
        self.copy_buffer.addItems(["1 MB", "4 MB", "8 MB", "16 MB", "32 MB", "64 MB"])
        self.copy_buffer.setCurrentIndex(2)
        workers_row.addWidget(self.copy_buffer)

        workers_row.addWidget(QLabel("Speed limit:"))
        self.copy_speed = QSpinBox()
        self.copy_speed.setRange(0, 99999)
        self.copy_speed.setSuffix(" MB/s")
        self.copy_speed.setSpecialValueText("Unlimited")
        workers_row.addWidget(self.copy_speed)
        workers_row.addStretch()

        grid.addLayout(workers_row, 3, 0, 1, 4)
        options_card.layout.addLayout(grid)

        filters_card = ModernCard("Filters")
        filter_grid = QGridLayout()
        filter_grid.setSpacing(8)

        filter_grid.addWidget(QLabel("Exclude patterns:"), 0, 0)
        self.copy_exclude_patterns = QLineEdit()
        self.copy_exclude_patterns.setPlaceholderText("*.tmp, *.log, .git/*")
        filter_grid.addWidget(self.copy_exclude_patterns, 0, 1)

        filter_grid.addWidget(QLabel("Include only:"), 0, 2)
        self.copy_include_patterns = QLineEdit()
        self.copy_include_patterns.setPlaceholderText("*.py, *.js")
        filter_grid.addWidget(self.copy_include_patterns, 0, 3)

        filter_grid.addWidget(QLabel("Min size:"), 1, 0)
        self.copy_min_size = QSpinBox()
        self.copy_min_size.setRange(0, 999999)
        self.copy_min_size.setSuffix(" KB")
        self.copy_min_size.setSpecialValueText("No min")
        filter_grid.addWidget(self.copy_min_size, 1, 1)

        filter_grid.addWidget(QLabel("Max size:"), 1, 2)
        self.copy_max_size = QSpinBox()
        self.copy_max_size.setRange(0, 999999999)
        self.copy_max_size.setSuffix(" KB")
        self.copy_max_size.setSpecialValueText("No max")
        filter_grid.addWidget(self.copy_max_size, 1, 3)

        filters_card.layout.addLayout(filter_grid)

        action_row = QHBoxLayout()
        action_row.setSpacing(12)
        self.copy_start_btn = QPushButton("  Start Copy  ")
        self.copy_start_btn.setObjectName("primaryBtn")
        self.copy_start_btn.setMinimumHeight(42)
        self.copy_start_btn.setMinimumWidth(160)
        self.copy_start_btn.clicked.connect(self._start_copy)
        action_row.addWidget(self.copy_start_btn)

        self.copy_pause_btn = QPushButton("Pause")
        self.copy_pause_btn.setMinimumHeight(42)
        self.copy_pause_btn.setMinimumWidth(100)
        self.copy_pause_btn.setEnabled(False)
        self.copy_pause_btn.clicked.connect(self._pause_copy)
        action_row.addWidget(self.copy_pause_btn)

        self.copy_stop_btn = QPushButton("Stop")
        self.copy_stop_btn.setObjectName("dangerBtn")
        self.copy_stop_btn.setMinimumHeight(42)
        self.copy_stop_btn.setMinimumWidth(100)
        self.copy_stop_btn.setEnabled(False)
        self.copy_stop_btn.clicked.connect(self._stop_copy)
        action_row.addWidget(self.copy_stop_btn)

        action_row.addStretch()

        self.copy_progress = QProgressBar()
        self.copy_progress.setMinimumHeight(28)
        self.copy_progress.setTextVisible(True)
        self.copy_progress.setFormat("%p% | %v")
        action_row.addWidget(self.copy_progress, 1)

        status_row = QHBoxLayout()
        self.copy_status_label = QLabel("Ready")
        self.copy_status_label.setStyleSheet("color: #8b949e; font-size: 12px;")
        self.copy_file_label = QLabel("")
        self.copy_file_label.setStyleSheet("color: #484f58; font-size: 12px;")
        status_row.addWidget(self.copy_status_label)
        status_row.addStretch()
        status_row.addWidget(self.copy_file_label)

        self.copy_log = QTextEdit()
        self.copy_log.setReadOnly(True)
        self.copy_log.setMaximumHeight(140)
        self.copy_log.setPlaceholderText("Operation log will appear here...")

        layout.addWidget(options_card)
        layout.addWidget(filters_card)
        layout.addLayout(action_row)
        layout.addLayout(status_row)
        layout.addWidget(self.copy_log, 1)

        return self._wrap_scroll(tab)

    def _wrap_scroll(self, tab: QWidget) -> QScrollArea:
        scroll = QScrollArea()
        scroll.setObjectName("tabScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setWidget(tab)
        scroll.setStyleSheet(
            "QScrollArea#tabScroll { background-color: #0d1117; border: none; }"
            "QScrollArea#tabScroll > QWidget > QWidget { background-color: #0d1117; }"
        )
        return scroll

    def _create_archive_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)

        src_row, self.archive_source = self._create_browse_row("Source:", "File or folder to archive...")
        layout.addLayout(src_row)

        out_row, self.archive_output = self._create_browse_row("Output:", "Output archive path...")
        layout.addLayout(out_row)

        opts_card = ModernCard("Archive Options")
        grid = QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(QLabel("Format:"), 0, 0)
        self.archive_format = QComboBox()
        available = ArchiveEngine.get_available_formats()
        self.archive_format.addItems(available)
        grid.addWidget(self.archive_format, 0, 1)

        grid.addWidget(QLabel("Compression:"), 0, 2)
        self.archive_compression = QSlider(Qt.Orientation.Horizontal)
        self.archive_compression.setRange(0, 9)
        self.archive_compression.setValue(6)
        self.archive_compression.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.archive_compression.setTickInterval(1)
        grid.addWidget(self.archive_compression, 0, 3)

        self.archive_comp_label = QLabel("6")
        self.archive_comp_label.setStyleSheet("color: #3fb950; font-weight: bold;")
        self.archive_compression.valueChanged.connect(lambda v: self.archive_comp_label.setText(str(v)))
        grid.addWidget(self.archive_comp_label, 0, 4)

        self.archive_hidden = QCheckBox("Include hidden")
        grid.addWidget(self.archive_hidden, 1, 0)

        grid.addWidget(QLabel("Password:"), 1, 1)
        self.archive_password = QLineEdit()
        self.archive_password.setPlaceholderText("Optional password")
        self.archive_password.setEchoMode(QLineEdit.EchoMode.Password)
        grid.addWidget(self.archive_password, 1, 2, 1, 3)

        opts_card.layout.addLayout(grid)
        layout.addWidget(opts_card)

        action_row = QHBoxLayout()
        self.archive_start_btn = QPushButton("  Create Archive  ")
        self.archive_start_btn.setObjectName("accentBtn")
        self.archive_start_btn.setMinimumHeight(42)
        self.archive_start_btn.setMinimumWidth(180)
        self.archive_start_btn.clicked.connect(self._start_archive)
        action_row.addWidget(self.archive_start_btn)

        self.archive_stop_btn = QPushButton("Stop")
        self.archive_stop_btn.setObjectName("dangerBtn")
        self.archive_stop_btn.setMinimumHeight(42)
        self.archive_stop_btn.setEnabled(False)
        self.archive_stop_btn.clicked.connect(self._stop_archive)
        action_row.addWidget(self.archive_stop_btn)
        action_row.addStretch()

        self.archive_progress = QProgressBar()
        self.archive_progress.setMinimumHeight(28)
        action_row.addWidget(self.archive_progress, 1)

        self.archive_status = QLabel("Ready")
        self.archive_status.setStyleSheet("color: #8b949e; font-size: 12px;")

        self.archive_log = QTextEdit()
        self.archive_log.setReadOnly(True)
        self.archive_log.setMaximumHeight(140)

        layout.addLayout(action_row)
        layout.addWidget(self.archive_status)
        layout.addWidget(self.archive_log, 1)

        return self._wrap_scroll(tab)

    def _create_split_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)

        split_card = ModernCard("Split File")
        split_src_row, self.split_source = self._create_browse_row("File:", "File to split...")
        split_card.layout.addLayout(split_src_row)

        split_dst_row, self.split_output = self._create_browse_row("Output dir:", "Output directory...")
        split_card.layout.addLayout(split_dst_row)

        split_grid = QGridLayout()
        split_grid.setSpacing(10)

        split_grid.addWidget(QLabel("Part size:"), 0, 0)
        self.split_size = QComboBox()
        self.split_size.addItems([
            "10 MB", "25 MB", "50 MB", "100 MB", "250 MB",
            "500 MB", "700 MB (CD)", "1000 MB", "1 GB",
            "2 GB (FAT32)", "4 GB", "4480 MB (DVD)", "8500 MB (DVD DL)"
        ])
        self.split_size.setCurrentIndex(3)
        split_grid.addWidget(self.split_size, 0, 1)

        self.split_manifest = QCheckBox("Create manifest")
        self.split_manifest.setChecked(True)
        split_grid.addWidget(self.split_manifest, 0, 2)

        split_btn = QPushButton("  Split  ")
        split_btn.setObjectName("primaryBtn")
        split_btn.setMinimumHeight(38)
        split_btn.clicked.connect(self._start_split)
        split_grid.addWidget(split_btn, 0, 3)

        split_card.layout.addLayout(split_grid)
        layout.addWidget(split_card)

        merge_card = ModernCard("Merge Parts")
        merge_src_row, self.merge_source = self._create_browse_row("Parts dir:", "Directory with parts...")
        merge_card.layout.addLayout(merge_src_row)

        merge_dst_row, self.merge_output = self._create_browse_row("Output file:", "Merged output path...")
        merge_card.layout.addLayout(merge_dst_row)

        merge_grid = QGridLayout()
        merge_grid.setSpacing(10)

        self.merge_manifest = QLineEdit()
        self.merge_manifest.setPlaceholderText("Manifest file (auto-detect if empty)")
        merge_grid.addWidget(QLabel("Manifest:"), 0, 0)
        merge_grid.addWidget(self.merge_manifest, 0, 1)

        self.merge_verify = QCheckBox("Verify after merge")
        self.merge_verify.setChecked(True)
        merge_grid.addWidget(self.merge_verify, 0, 2)

        merge_btn = QPushButton("  Merge  ")
        merge_btn.setObjectName("accentBtn")
        merge_btn.setMinimumHeight(38)
        merge_btn.clicked.connect(self._start_merge)
        merge_grid.addWidget(merge_btn, 0, 3)

        merge_card.layout.addLayout(merge_grid)
        layout.addWidget(merge_card)

        action_row = QHBoxLayout()
        self.split_progress = QProgressBar()
        self.split_progress.setMinimumHeight(28)
        action_row.addWidget(self.split_progress, 1)
        layout.addLayout(action_row)

        self.split_status = QLabel("Ready")
        self.split_status.setStyleSheet("color: #8b949e; font-size: 12px;")
        layout.addWidget(self.split_status)

        self.split_log = QTextEdit()
        self.split_log.setReadOnly(True)
        self.split_log.setMaximumHeight(120)
        layout.addWidget(self.split_log, 1)

        return self._wrap_scroll(tab)

    def _create_settings_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)

        general_card = ModernCard("General Settings")
        grid = QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(QLabel("Default workers:"), 0, 0)
        self.set_workers = QSpinBox()
        self.set_workers.setRange(1, 32)
        self.set_workers.setValue(4)
        grid.addWidget(self.set_workers, 0, 1)

        grid.addWidget(QLabel("Default buffer:"), 0, 2)
        self.set_buffer = QComboBox()
        self.set_buffer.addItems(["1 MB", "4 MB", "8 MB", "16 MB", "32 MB", "64 MB"])
        self.set_buffer.setCurrentIndex(2)
        grid.addWidget(self.set_buffer, 0, 3)

        grid.addWidget(QLabel("Theme:"), 1, 0)
        self.set_theme = QComboBox()
        self.set_theme.addItems(["Dark", "Light", "System"])
        grid.addWidget(self.set_theme, 1, 1)

        self.set_verify_default = QCheckBox("Verify by default")
        self.set_verify_default.setChecked(True)
        grid.addWidget(self.set_verify_default, 1, 2)

        self.set_resume_default = QCheckBox("Resume by default")
        self.set_resume_default.setChecked(True)
        grid.addWidget(self.set_resume_default, 1, 3)

        general_card.layout.addLayout(grid)
        layout.addWidget(general_card)

        paths_card = ModernCard("Default Paths")
        paths_grid = QGridLayout()
        paths_grid.setSpacing(8)

        paths_grid.addWidget(QLabel("Temp dir:"), 0, 0)
        self.set_temp_dir = QLineEdit()
        self.set_temp_dir.setPlaceholderText("System default")
        self.set_temp_dir.setText(os.path.join(os.path.expanduser("~"), ".swiftcopy", "temp"))
        paths_grid.addWidget(self.set_temp_dir, 0, 1, 1, 2)
        temp_btn = QPushButton("Browse")
        temp_btn.setFixedWidth(80)
        temp_btn.clicked.connect(lambda: self._browse_folder(self.set_temp_dir))
        paths_grid.addWidget(temp_btn, 0, 3)

        paths_grid.addWidget(QLabel("Log dir:"), 1, 0)
        self.set_log_dir = QLineEdit()
        self.set_log_dir.setPlaceholderText("System default")
        self.set_log_dir.setText(os.path.join(os.path.expanduser("~"), ".swiftcopy", "logs"))
        paths_grid.addWidget(self.set_log_dir, 1, 1, 1, 2)
        log_btn = QPushButton("Browse")
        log_btn.setFixedWidth(80)
        log_btn.clicked.connect(lambda: self._browse_folder(self.set_log_dir))
        paths_grid.addWidget(log_btn, 1, 3)

        paths_card.layout.addLayout(paths_grid)
        layout.addWidget(paths_card)

        layout.addStretch()

        return self._wrap_scroll(tab)

    def _create_history_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)

        header = ModernCard("Transfer History")
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(7)
        self.history_table.setHorizontalHeaderLabels([
            "Time", "Type", "Source", "Destination", "Files", "Size", "Status"
        ])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.history_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.history_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.history_table.verticalHeader().setVisible(False)
        self.history_table.setAlternatingRowColors(True)
        header.layout.addWidget(self.history_table)

        btn_row = QHBoxLayout()
        clear_btn = QPushButton("Clear History")
        clear_btn.clicked.connect(self._clear_history)
        btn_row.addWidget(clear_btn)
        btn_row.addStretch()
        header.layout.addLayout(btn_row)

        layout.addWidget(header)
        return tab

    def _parse_split_size(self) -> int:
        text = self.split_size.currentText()
        parts = text.split()
        value = int(parts[0])
        unit = parts[1].upper()
        multipliers = {
            'MB': 1024 * 1024,
            'GB': 1024 * 1024 * 1024,
        }
        return value * multipliers.get(unit, 1024 * 1024)

    def _parse_buffer_size(self) -> int:
        text = self.copy_buffer.currentText()
        parts = text.split()
        value = int(parts[0])
        return value * 1024 * 1024

    def _start_copy(self):
        if self.current_worker and self.current_worker.isRunning():
            QMessageBox.information(self, "Busy", "A copy operation is already running.")
            return
        if not self.copy_source.text() or not self.copy_dest.text():
            QMessageBox.warning(self, "Missing", "Please select source and destination.")
            return

        opts = CopyOptions()
        opts.source = self.copy_source.text()
        opts.destination = self.copy_dest.text()
        opts.recursive = self.copy_recursive.isChecked()
        opts.overwrite = self.copy_overwrite.isChecked()
        opts.verify = self.copy_verify.isChecked()
        opts.preserve_attributes = self.copy_preserve.isChecked()
        opts.preserve_symlinks = self.copy_symlinks.isChecked()
        opts.skip_hidden = self.copy_skip_hidden.isChecked()
        opts.dry_run = self.copy_dry_run.isChecked()
        opts.resume = self.copy_resume.isChecked()
        opts.include_parent_folder = self.copy_include_parent.isChecked()
        opts.buffer_size = self._parse_buffer_size()
        opts.max_workers = self.copy_workers.value()
        opts.speed_limit = self.copy_speed.value()

        if self.copy_exclude_patterns.text():
            opts.exclude_patterns = [p.strip() for p in self.copy_exclude_patterns.text().split(',')]
        if self.copy_include_patterns.text():
            opts.include_patterns = [p.strip() for p in self.copy_include_patterns.text().split(',')]
        if self.copy_min_size.value() > 0:
            opts.min_size = self.copy_min_size.value() * 1024
        if self.copy_max_size.value() > 0:
            opts.max_size = self.copy_max_size.value() * 1024

        self.copy_start_btn.setEnabled(False)
        self.copy_pause_btn.setEnabled(True)
        self.copy_stop_btn.setEnabled(True)
        self.copy_progress.setValue(0)
        self.copy_status_label.setText("Copying...")

        self.current_worker = CopyWorker(opts)
        self.current_worker.progress.connect(self._on_copy_progress)
        self.current_worker.file_start.connect(self._on_copy_file_start)
        self.current_worker.file_complete.connect(self._on_copy_file_complete)
        self.current_worker.error.connect(self._on_copy_error)
        self.current_worker.complete.connect(self._on_copy_complete)
        self.current_worker.log.connect(lambda msg: self.copy_log.append(msg))
        self.current_worker.start()

    def _pause_copy(self):
        if self.current_worker and self.current_worker.isRunning() and hasattr(self.current_worker, 'engine'):
            try:
                engine = self.current_worker.engine
                if engine.is_paused:
                    engine.resume()
                    self.copy_pause_btn.setText("Pause")
                    self.copy_status_label.setText("Resumed")
                else:
                    engine.pause()
                    self.copy_pause_btn.setText("Resume")
                    self.copy_status_label.setText("Paused")
            except Exception:
                self.copy_pause_btn.setEnabled(False)

    def _stop_copy(self):
        if self.current_worker and self.current_worker.isRunning():
            try:
                self.current_worker.stop()
            except Exception:
                pass
            self.copy_status_label.setText("Stopping...")
            self.copy_stop_btn.setEnabled(False)

    def _on_copy_progress(self, pct, total, filename):
        self.copy_progress.setValue(pct)
        self.copy_file_label.setText(filename)

    def _on_copy_file_start(self, src, dst):
        pass

    def _on_copy_file_complete(self, src, dst, success):
        pass

    def _on_copy_error(self, filepath, msg):
        self.copy_log.append(f"ERROR: {filepath} - {msg}")

    def _on_copy_complete(self, stats):
        self.copy_start_btn.setEnabled(True)
        self.copy_pause_btn.setEnabled(False)
        self.copy_stop_btn.setEnabled(False)
        self.copy_progress.setValue(100)

        elapsed = time.time() - stats.start_time
        speed = (stats.copied_bytes / elapsed / 1024 / 1024) if elapsed > 0 else 0

        self.copy_status_label.setText(
            f"Complete | {stats.copied_files}/{stats.total_files} files | "
            f"{self._format_size(stats.copied_bytes)} | {speed:.1f} MB/s"
        )

        self._add_history("Copy", stats)
        self.current_worker = None

    def _start_archive(self):
        if hasattr(self, 'archive_worker') and self.archive_worker and self.archive_worker.isRunning():
            QMessageBox.information(self, "Busy", "An archive operation is already running.")
            return
        if not self.archive_source.text() or not self.archive_output.text():
            QMessageBox.warning(self, "Missing", "Please select source and output path.")
            return

        opts = ArchiveOptions()
        opts.source = self.archive_source.text()
        opts.output = self.archive_output.text()
        opts.format = self.archive_format.currentText()
        opts.compression_level = self.archive_compression.value()
        opts.password = self.archive_password.text()
        opts.include_hidden = self.archive_hidden.isChecked()

        self.archive_start_btn.setEnabled(False)
        self.archive_stop_btn.setEnabled(True)
        self.archive_progress.setValue(0)
        self.archive_status.setText("Creating archive...")

        self.archive_worker = ArchiveWorker(opts)
        self.archive_worker.progress.connect(lambda p, t, f: (
            self.archive_progress.setValue(p),
            self.archive_status.setText(f"Archiving: {f}")
        ))
        self.archive_worker.complete.connect(self._on_archive_complete)
        self.archive_worker.error.connect(lambda p, m: self.archive_log.append(f"ERROR: {m}"))
        self.archive_worker.log.connect(lambda msg: self.archive_log.append(msg))
        self.archive_worker.start()

    def _stop_archive(self):
        if hasattr(self, 'archive_worker') and self.archive_worker and self.archive_worker.isRunning():
            self.archive_worker.stop()
            self.archive_stop_btn.setEnabled(False)

    def _on_archive_complete(self, path, size):
        self.archive_start_btn.setEnabled(True)
        self.archive_stop_btn.setEnabled(False)
        self.archive_progress.setValue(100)
        self.archive_status.setText(f"Complete: {path} ({self._format_size(size)})")

    def _start_split(self):
        if hasattr(self, 'split_worker') and self.split_worker and self.split_worker.isRunning():
            QMessageBox.information(self, "Busy", "A split/merge operation is already running.")
            return
        if not self.split_source.text() or not self.split_output.text():
            QMessageBox.warning(self, "Missing", "Please select file and output directory.")
            return

        opts = SplitOptions()
        opts.source = self.split_source.text()
        opts.output_dir = self.split_output.text()
        opts.part_size = self._parse_split_size()
        opts.create_manifest = self.split_manifest.isChecked()

        self.split_progress.setValue(0)
        self.split_status.setText("Splitting...")

        self.split_worker = SplitWorker(opts, mode='split')
        self.split_worker.progress.connect(lambda p, t, f: (
            self.split_progress.setValue(p),
            self.split_status.setText(f"Splitting: {f}")
        ))
        self.split_worker.complete.connect(lambda a: (
            self.split_progress.setValue(100),
            self.split_status.setText("Split complete"),
            self.split_log.append("Split operation completed successfully")
        ))
        self.split_worker.log.connect(lambda msg: self.split_log.append(msg))
        self.split_worker.start()

    def _start_merge(self):
        if hasattr(self, 'split_worker') and self.split_worker and self.split_worker.isRunning():
            QMessageBox.information(self, "Busy", "A split/merge operation is already running.")
            return
        if not self.merge_source.text() or not self.merge_output.text():
            QMessageBox.warning(self, "Missing", "Please select parts directory and output file.")
            return

        opts = MergeOptions()
        opts.source_dir = self.merge_source.text()
        opts.output_file = self.merge_output.text()
        opts.manifest_file = self.merge_manifest.text()
        opts.verify = self.merge_verify.isChecked()

        self.split_progress.setValue(0)
        self.split_status.setText("Merging...")

        self.split_worker = SplitWorker(opts, mode='merge')
        self.split_worker.progress.connect(lambda p, t, f: (
            self.split_progress.setValue(p),
            self.split_status.setText(f"Merging: {f}")
        ))
        self.split_worker.complete.connect(lambda a: (
            self.split_progress.setValue(100),
            self.split_status.setText("Merge complete"),
            self.split_log.append("Merge operation completed successfully")
        ))
        self.split_worker.log.connect(lambda msg: self.split_log.append(msg))
        self.split_worker.start()

    def _add_history(self, op_type, stats):
        now = datetime.now().strftime("%H:%M:%S")
        elapsed = time.time() - stats.start_time if stats.start_time else 0
        row = self.history_table.rowCount()
        self.history_table.insertRow(row)
        self.history_table.setItem(row, 0, QTableWidgetItem(now))
        self.history_table.setItem(row, 1, QTableWidgetItem(op_type))
        self.history_table.setItem(row, 2, QTableWidgetItem(str(getattr(stats, 'source', 'N/A'))[:50]))
        self.history_table.setItem(row, 3, QTableWidgetItem(str(getattr(stats, 'destination', 'N/A'))[:50]))
        self.history_table.setItem(row, 4, QTableWidgetItem(str(stats.copied_files)))
        self.history_table.setItem(row, 5, QTableWidgetItem(self._format_size(stats.copied_bytes)))
        status = "Success" if stats.failed_files == 0 else f"{stats.failed_files} failed"
        item = QTableWidgetItem(status)
        if stats.failed_files > 0:
            item.setForeground(QBrush(QColor("#f85149")))
        else:
            item.setForeground(QBrush(QColor("#3fb950")))
        self.history_table.setItem(row, 6, item)

    def _clear_history(self):
        self.history_table.setRowCount(0)

    @staticmethod
    def _format_size(size):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} PB"


def _icon_path(name: str = "icon.png"):
    candidates = []
    if getattr(sys, "frozen", False):
        base = Path(sys._MEIPASS)
        candidates.append(base / "assets" / name)
    candidates.append(Path(__file__).resolve().parent / "assets" / name)
    for c in candidates:
        if c.exists():
            return str(c)
    return None


def main():
    os.makedirs(os.path.join(os.path.expanduser("~"), ".swiftcopy", "temp"), exist_ok=True)
    os.makedirs(os.path.join(os.path.expanduser("~"), ".swiftcopy", "logs"), exist_ok=True)

    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)
    app.setApplicationName("SwiftCopy")
    app.setOrganizationName("SwiftCopy")
    app.setWindowIcon(QIcon(_icon_path("icon.png") or _icon_path("logo.png") or ""))

    font = QFont("Segoe UI", 10)
    font.setHintingPreference(QFont.HintingPreference.PreferNoHinting)
    app.setFont(font)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
