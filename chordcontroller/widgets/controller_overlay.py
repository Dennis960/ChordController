from PySide6.QtWidgets import QMainWindow, QLabel, QApplication
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QCursor
from multiprocessing.connection import Connection


class HeadlessOverlayHandler:
    """Simplified overlay handler that only sends mode changes."""

    pulse_animation_enabled: bool = True
    listeners_disconnect_functions: list = []

    def __init__(self, pipe: Connection):
        self.pipe = pipe
        self.current_mode = "default"
        self.tag = "controller_overlay"

    def set_title(self, title: str):
        self.current_mode = title
        self.pipe.send({"cmd": "set_mode", "mode_name": title})

    def open_cheatsheet(self, screen_index: int | None):
        self.pipe.send(
            {
                "cmd": "open_cheatsheet",
                "screen": screen_index if screen_index is not None else 0,
            }
        )

    def close_cheatsheet(self):
        self.pipe.send({"cmd": "close_cheatsheet"})

    def toggle_cheatsheet(self, screen_index: int | None):
        self.pipe.send(
            {
                "cmd": "toggle_cheatsheet",
                "screen": screen_index if screen_index is not None else 0,
            }
        )


class ControllerOverlay(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowDoesNotAcceptFocus
            | Qt.WindowType.WindowTransparentForInput
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        self.label = QLabel(self)
        self.label.setStyleSheet(
            """
            QLabel {
                color: white;
                background-color: rgba(0, 0, 0, 180);
                padding: 10px 20px;
                border-radius: 5px;
            }
        """
        )
        font = QFont()
        font.setPixelSize(20)
        font.setBold(True)
        self.label.setFont(font)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        self.set_text("Default")
        self.position_top_left()

        self.setMouseTracking(True)
        self.label.setMouseTracking(True)

        self._mouse_check_timer = QTimer(self)
        self._mouse_check_timer.timeout.connect(self._check_mouse_over)
        self._mouse_check_timer.start(100)
        self._is_hidden_due_to_mouse = False
        self.hidden_by_setting = False

    def position_top_left(self):
        """Position the window in the top-left corner of the primary screen."""

        screen = QApplication.primaryScreen().geometry()

        self.label.adjustSize()
        label_size = self.label.size()

        # Set window size to label size
        self.setFixedSize(label_size)

        # Position in top-left
        x = screen.x()
        y = screen.y()
        self.move(x, y)

    def set_text(self, text: str):
        """Set the text to display."""
        self.label.setText(text)
        self.label.adjustSize()
        self.setFixedSize(self.label.size())
        # Reposition after size change
        if self.isVisible():
            self.position_top_left()

    def set_title(self, title: str):
        """Compatibility method for mode changes."""
        self.set_text(title.capitalize())

    def _check_mouse_over(self):
        margin = 50
        mouse_pos = QCursor.pos()
        geo = self.geometry()
        # Expand the geometry by 50px in all directions
        expanded_geo = geo.adjusted(-margin, -margin, margin, margin)
        if expanded_geo.contains(mouse_pos):
            if not self._is_hidden_due_to_mouse:
                self.hide()
                self._is_hidden_due_to_mouse = True
        else:
            if self._is_hidden_due_to_mouse and not self.hidden_by_setting:
                self.show()
                self._is_hidden_due_to_mouse = False
