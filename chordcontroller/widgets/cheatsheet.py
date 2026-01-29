"""
PySide6 Cheatsheet window showing controller actions for current mode.
"""

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QGridLayout,
    QLabel,
)
from PySide6.QtCore import Qt
import sys

from chordcontroller.config import Mode
from chordcontroller.config_action_parser import (
    parse_multi_controller_button_action,
    parse_button_action,
    parse_stick_action,
)
from chordcontroller.widgets.controller_buttons import (
    MultiButton,
    DPad,
    FaceButtons,
    SingleButton,
    ShoulderButtons,
    StickMovement,
)


class _CheatSheetWindow(QMainWindow):
    """Individual cheatsheet window for a specific mode."""

    def __init__(self, mode: Mode, rows=29, cols=8, scale=0.5):
        super().__init__()
        self.mode = mode
        self.rows = rows
        self.cols = cols
        self.current_screen_index = 0

        # Window setup
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setWindowTitle(f"Cheatsheet - {mode.name}")
        self.setStyleSheet("QMainWindow { background-color: black; }")

        # Central widget with main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Grid layout for action items - use fixed 2 columns (button + label)
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(2)
        self.grid_layout.setColumnStretch(0, 0)  # Button column - fixed width
        self.grid_layout.setColumnStretch(1, 1)  # Action label column - expandable
        main_layout.addLayout(self.grid_layout)
        main_layout.addStretch()

        self._populate_grid(scale)

    def _get_current_screen(self):
        """Get the screen the window is currently on."""
        screens = QApplication.screens()
        window_center = self.geometry().center()

        for i, screen in enumerate(screens):
            if screen.geometry().contains(window_center):
                return i
        return 0

    def _center_on_screen(self, screen_index):
        """Center window on the specified screen."""
        screens = QApplication.screens()

        if screen_index < len(screens):
            screen = screens[screen_index]
        else:
            screen = QApplication.primaryScreen()
            screen_index = 0

        # Get screen geometry and center window
        screen_geometry = screen.geometry()
        window_size = self.size()

        x = screen_geometry.x() + (screen_geometry.width() - window_size.width()) // 2
        y = screen_geometry.y() + (screen_geometry.height() - window_size.height()) // 2

        self.move(x, y)
        self.current_screen_index = screen_index

    def _populate_grid(self, scale=0.5):
        """Populate grid with current mode's actions."""
        # Clear existing widgets
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Collect all actions with their button widgets
        actions_list: list[tuple[QWidget, str]] = []

        # Multi-button actions
        if self.mode.multi_button_actions:
            for multi_button_action in self.mode.multi_button_actions:
                action_string = parse_multi_controller_button_action(
                    multi_button_action
                )
                button_widget = MultiButton(
                    frozenset(multi_button_action.buttons), scale=scale
                )
                actions_list.append((button_widget, action_string))

        # Button actions
        if self.mode.button_actions:
            for (
                controller_button_name,
                button_action_dict,
            ) in self.mode.button_actions.items():
                action_string = parse_button_action(button_action_dict)

                # Create appropriate button widget based on button type
                if controller_button_name in [
                    "shoulder_l",
                    "shoulder_r",
                    "trigger_l",
                    "trigger_r",
                ]:
                    button_widget = ShoulderButtons(
                        frozenset([controller_button_name]), scale=scale
                    )
                elif controller_button_name in [
                    "dpad_up",
                    "dpad_right",
                    "dpad_down",
                    "dpad_left",
                ]:
                    button_widget = DPad(
                        frozenset([controller_button_name]), scale=scale
                    )
                elif controller_button_name in [
                    "face_up",
                    "face_right",
                    "face_down",
                    "face_left",
                ]:
                    button_widget = FaceButtons(
                        frozenset([controller_button_name]), scale=scale
                    )
                else:
                    button_widget = SingleButton(controller_button_name, scale=scale)

                actions_list.append((button_widget, action_string))

        # Stick actions
        if self.mode.stick_actions:
            for stick_name, stick_action in self.mode.stick_actions.items():
                action_string = parse_stick_action(stick_action)

                if stick_name == "stick_left":
                    button_widget = StickMovement(is_left=True, scale=scale)
                elif stick_name == "stick_right":
                    button_widget = StickMovement(is_left=False, scale=scale)
                else:
                    button_widget = None

                if button_widget:
                    actions_list.append((button_widget, action_string))

        # Add items to grid - fill down rows, then across cols
        for idx, (button_widget, action_text) in enumerate(actions_list):
            if idx >= self.rows * self.cols:
                break

            row = idx % self.rows
            col = idx // self.rows

            # Add button widget to grid (column pair: col*2)
            self.grid_layout.addWidget(button_widget, row, col * 2)

            # Add action label to grid (column pair: col*2 + 1)
            label = QLabel(action_text)
            label.setStyleSheet("QLabel { color: white; font-size: 10pt; }")
            # label.setWordWrap(True)
            self.grid_layout.addWidget(label, row, col * 2 + 1)

    def open(self, screen_index=None):
        """Open and display the cheatsheet window."""
        if screen_index is not None:
            self.current_screen_index = screen_index

        self.show()
        self._center_on_screen(self.current_screen_index)

    def close(self):
        """Close and hide the cheatsheet window."""
        # Remember screen before closing
        current_screen = self._get_current_screen()
        if current_screen is not None:
            self.current_screen_index = current_screen
        self.hide()

    def toggle(self, screen_index=None):
        """Toggle the cheatsheet window visibility."""
        if self.isVisible():
            self.close()
        else:
            self.open(screen_index)


class CheatSheet:
    """Manager class for cached cheatsheet windows per mode."""

    def __init__(self, mode: Mode, rows=29, cols=8):
        self.rows = rows
        self.cols = cols
        self.mode = mode
        self.windows: dict[str, _CheatSheetWindow] = {}
        self.last_screen_index = 0

        # Create initial window for the provided mode
        self._get_or_create_window(mode)

    def _get_or_create_window(self, mode: Mode) -> _CheatSheetWindow:
        """Get existing window for a mode or create a new one."""
        mode_key = mode.name
        if mode_key not in self.windows:
            if len(mode.button_actions or []) + len(mode.stick_actions or []) + len(mode.multi_button_actions or []) > 50:
                scale = 0.4
            else:
                scale = 0.5
            self.windows[mode_key] = _CheatSheetWindow(mode, self.rows, self.cols, scale)
        return self.windows[mode_key]

    def _get_current_screen(self):
        """Get the screen the current window is on."""
        current_window = self._get_or_create_window(self.mode)
        screens = QApplication.screens()
        window_center = current_window.geometry().center()

        for i, screen in enumerate(screens):
            if screen.geometry().contains(window_center):
                return i
        return 0

    def set_mode(self, mode: Mode):
        """Switch to a different mode window."""
        # Get current screen from active window
        current_screen = self._get_current_screen()
        if current_screen is not None:
            self.last_screen_index = current_screen

        # Hide current mode window if visible
        current_window = self._get_or_create_window(self.mode)
        was_visible = current_window.isVisible()
        if was_visible:
            current_window.close()

        # Switch to new mode
        self.mode = mode
        new_window = self._get_or_create_window(mode)
        new_window.current_screen_index = self.last_screen_index
        
        # Show new window if old one was visible
        if was_visible:
            new_window.show()
            new_window._center_on_screen(self.last_screen_index)

    def open(self, screen_index=None):
        """Open and display the cheatsheet window for current mode."""
        if screen_index is not None:
            self.last_screen_index = screen_index

        window = self._get_or_create_window(self.mode)
        window.show()
        window._center_on_screen(self.last_screen_index)

    def close(self):
        """Close and hide the cheatsheet window for current mode."""
        # Remember screen before closing
        current_screen = self._get_current_screen()
        if current_screen is not None:
            self.last_screen_index = current_screen

        window = self._get_or_create_window(self.mode)
        window.hide()

    def toggle(self, screen_index=None):
        """Toggle the cheatsheet window visibility for current mode."""
        window = self._get_or_create_window(self.mode)
        if window.isVisible():
            self.close()
        else:
            self.open(screen_index)


if __name__ == "__main__":
    from chordcontroller.config import Config

    app = QApplication(sys.argv)

    config = Config.load_config()
    global_mode = config.modes["global"]
    typing_mode = Config.merge_modes(config.modes["typing"], global_mode)
    default_mode = Config.merge_modes(config.modes["default"], global_mode)

    cheatsheet = CheatSheet(typing_mode)
    cheatsheet.open()
    # cheatsheet.set_mode(default_mode)

    sys.exit(app.exec())
