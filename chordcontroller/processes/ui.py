import os
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from shiboken6 import isValid
from chordcontroller.widgets.controller_overlay import ControllerOverlay
from chordcontroller.widgets.cheatsheet import CheatSheet
from chordcontroller.widgets.joystick_calibration import JoystickCalibrationWindow
from chordcontroller.config import Config
from multiprocessing.connection import Connection
from chordcontroller.widgets.controller_tray import create_tray_icon


def pyside6_ui_process_main(ui_receive_pipe: Connection, ui_send_pipe: Connection):
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    config = Config.load_config()
    global_mode = config.modes["global"]
    default_mode = Config.merge_modes(config.modes["default"], global_mode)
    current_mode = default_mode

    overlay = ControllerOverlay()
    overlay.show()

    cheatsheet = CheatSheet(current_mode)

    if os.name == "nt":
        # Calibration only needed on Windows
        calibration_window = JoystickCalibrationWindow()
    else:
        calibration_window = None

    def on_calibration_complete():
        nonlocal calibration_window
        ui_send_pipe.send({"cmd": "calibration_complete"})
        calibration_window = None

    def on_calibration_destroyed():
        nonlocal calibration_window
        calibration_window = None

    calibration_window.calibration_complete.connect(on_calibration_complete)
    calibration_window.destroyed.connect(on_calibration_destroyed)
    calibration_window.show()

    # Create system tray icon
    tray_icon = create_tray_icon(app, overlay)

    def handle_message():
        nonlocal current_mode, calibration_window

        while ui_receive_pipe.poll():
            msg: dict = ui_receive_pipe.recv()
            cmd = msg.get("cmd")

            if cmd == "set_mode":
                mode_name = msg.get("mode_name", "default")
                mode = config.modes.get(mode_name)
                if mode:
                    merged_mode = Config.merge_modes(mode, global_mode)
                    current_mode = merged_mode
                    cheatsheet.set_mode(merged_mode)
                    overlay.set_title(mode_name)
            elif cmd == "controller_connected":
                overlay.set_text(
                    current_mode.name.capitalize() if current_mode.name else "Default"
                )
            elif cmd == "controller_disconnected":
                overlay.set_text("Controller Disconnected")
            elif cmd == "open_cheatsheet":
                screen_index = msg.get("screen", 0)
                cheatsheet.open(screen_index)
            elif cmd == "close_cheatsheet":
                cheatsheet.close()
            elif cmd == "toggle_cheatsheet":
                screen_index = msg.get("screen", 0)
                cheatsheet.toggle(screen_index)
            elif cmd == "quit":
                app.quit()
            elif cmd == "open_overlay":
                overlay.show()
            elif cmd == "close_overlay":
                overlay.hide()
            elif cmd == "joystick_update":
                # Update joystick positions in calibration window
                if calibration_window is not None and isValid(calibration_window) and calibration_window.isVisible():
                    calibration_window.update_joysticks(
                        msg.get("left_x", 0.0),
                        msg.get("left_y", 0.0),
                        msg.get("right_x", 0.0),
                        msg.get("right_y", 0.0),
                    )
                elif calibration_window is not None:
                    on_calibration_complete()

    timer = QTimer()
    timer.timeout.connect(handle_message)
    timer.start(16)

    sys.exit(app.exec())
