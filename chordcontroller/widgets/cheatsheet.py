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
    QHBoxLayout,
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


class CheatSheetWindow(QMainWindow):
    def __init__(self, mode: Mode, rows=29, cols=8):
        super().__init__()
        self.rows = rows
        self.cols = cols
        self.mode = mode

        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setWindowTitle(f"Cheatsheet - {mode.name or 'Default'}")
        self.setStyleSheet("QMainWindow { background-color: black; }")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(0)

        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(5)
        main_layout.addLayout(self.grid_layout)

        self.populate_grid()

    def populate_grid(self):
        # Clear existing widgets
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Collect all actions with their button widgets
        actions_list = []
        scale = 0.5

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

        # Add items to grid
        for idx, (button_widget, action_text) in enumerate(actions_list):
            if idx >= self.rows * self.cols:
                break

            row = idx % self.rows
            col = idx // self.rows

            # Create container widget with button and label
            container = QWidget()
            container_layout = QHBoxLayout(container)
            container_layout.setContentsMargins(0, 0, 0, 0)
            container_layout.setSpacing(8)

            # Add button widget
            container_layout.addWidget(button_widget)

            # Add action label
            label = QLabel(action_text)
            label.setStyleSheet("QLabel { color: white; font-size: 10pt; }")
            label.setWordWrap(False)
            container_layout.addWidget(label)
            container_layout.addStretch()

            self.grid_layout.addWidget(container, row, col)

    def set_mode(self, mode: Mode):
        self.mode = mode
        self.setWindowTitle(f"Cheatsheet - {mode.name or 'Default'}")
        self.populate_grid()
        # Reset size constraints and resize to fit content
        self.setMinimumSize(0, 0)
        self.setMaximumSize(16777215, 16777215)  # QWIDGETSIZE_MAX
        self.adjustSize()
        # Process events to ensure layout is updated
        from PySide6.QtWidgets import QApplication

        QApplication.processEvents()


class CheatSheet:
    """Manager class for the cheatsheet window."""

    def __init__(self, mode: Mode, rows=29, cols=8):
        self.rows = rows
        self.cols = cols
        self.mode = mode
        self.window = CheatSheetWindow(mode, rows, cols)
        self.last_screen_index = 0

    def _get_current_screen(self):
        """Get the screen the window is currently on."""
        screens = QApplication.screens()
        window_center = self.window.geometry().center()

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

        # Reset size constraints and resize to fit content
        self.window.setMinimumSize(0, 0)
        self.window.setMaximumSize(16777215, 16777215)  # QWIDGETSIZE_MAX
        self.window.adjustSize()

        # Process events to ensure layout is updated
        QApplication.processEvents()

        # Get screen geometry and center window
        screen_geometry = screen.geometry()
        window_size = self.window.size()

        x = screen_geometry.x() + (screen_geometry.width() - window_size.width()) // 2
        y = screen_geometry.y() + (screen_geometry.height() - window_size.height()) // 2

        self.window.move(x, y)
        self.last_screen_index = screen_index

    def set_mode(self, mode: Mode):
        self.mode = mode
        # Get current screen before updating
        current_screen = self._get_current_screen()
        if current_screen is not None:
            self.last_screen_index = current_screen

        self.window.set_mode(mode)

        # Resize and recenter on current screen
        self._center_on_screen(self.last_screen_index)

    def open(self, screen_index=None):
        if screen_index is not None:
            self.last_screen_index = screen_index

        self._center_on_screen(self.last_screen_index)
        self.window.show()

    def close(self):
        # Remember screen before closing
        current_screen = self._get_current_screen()
        if current_screen is not None:
            self.last_screen_index = current_screen
        self.window.hide()

    def toggle(self, screen_index=None):
        if self.window.isVisible():
            self.close()
        else:
            self.open(screen_index)


if __name__ == "__main__":
    from chordcontroller.config import Config

    app = QApplication(sys.argv)

    config = Config.load_config()
    global_mode = config.modes["global"]
    mode = Config.merge_modes(config.modes["typing"], global_mode)

    cheatsheet = CheatSheet(mode)
    cheatsheet.open()

    sys.exit(app.exec())
