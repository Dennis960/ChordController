import os
import subprocess
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
    trainer_process: subprocess.Popen | None = None

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    config = Config.load_config()
    global_mode = config.modes["global"]
    default_mode = Config.merge_modes(config.modes["default"], global_mode)
    current_mode = default_mode

    overlay = ControllerOverlay()
    overlay.show()

    cheatsheet = CheatSheet(current_mode)

    def on_calibration_complete():
        nonlocal calibration_window
        ui_send_pipe.send({"cmd": "calibration_complete"})
        calibration_window = None

    def on_calibration_destroyed():
        nonlocal calibration_window
        calibration_window = None

    def open_trainer() -> None:
        nonlocal trainer_process
        if trainer_process is not None and trainer_process.poll() is None:
            return

        ui_send_pipe.send({"cmd": "suspend_controller_input"})
        trainer_process = subprocess.Popen([sys.executable, "-m", "chordcontroller.trainer.main"])
        tray_icon.set_trainer_action_enabled(False)

    def check_trainer_process() -> None:
        nonlocal trainer_process
        if trainer_process is None:
            return
        if trainer_process.poll() is None:
            return

        trainer_process = None
        ui_send_pipe.send({"cmd": "resume_controller_input"})
        tray_icon.set_trainer_action_enabled(True)

    def quit_all() -> None:
        nonlocal trainer_process
        if trainer_process is not None and trainer_process.poll() is None:
            trainer_process.terminate()
            trainer_process = None
        app.quit()

    if os.name == "nt":
        # Calibration only needed on Windows
        calibration_window = JoystickCalibrationWindow()
        calibration_window.calibration_complete.connect(on_calibration_complete)
        calibration_window.destroyed.connect(on_calibration_destroyed)
        calibration_window.show()
    else:
        calibration_window = None
        ui_send_pipe.send({"cmd": "calibration_complete"})


    # Create system tray icon
    tray_icon = create_tray_icon(app, overlay, on_open_trainer=open_trainer)
    quit_action = tray_icon.contextMenu().actions()[-1]
    quit_action.triggered.disconnect()
    quit_action.triggered.connect(quit_all)

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
                    overlay.set_title(merged_mode.name)
            elif cmd == "set_sticky_modifiers":
                overlay.set_sticky_modifiers(msg.get("modifiers", []))
            elif cmd == "controller_connected":
                overlay.set_title(current_mode.name if current_mode.name else "Default")
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

    trainer_timer = QTimer()
    trainer_timer.timeout.connect(check_trainer_process)
    trainer_timer.start(200)

    exit_code = app.exec()
    if trainer_process is not None and trainer_process.poll() is None:
        trainer_process.terminate()
    sys.exit(exit_code)
