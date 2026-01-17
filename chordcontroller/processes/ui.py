import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from chordcontroller.widgets.controller_overlay import ControllerOverlay
from chordcontroller.widgets.cheatsheet import CheatSheet
from chordcontroller.config import Config
from multiprocessing.connection import Connection
from chordcontroller.widgets.controller_tray import create_tray_icon


def pyside6_ui_process_main(ui_receive_pipe: Connection):
    app = QApplication(sys.argv)

    config = Config.load_config()
    global_mode = config.modes["global"]
    default_mode = Config.merge_modes(config.modes["default"], global_mode)
    current_mode = default_mode

    overlay = ControllerOverlay()
    overlay.show()

    cheatsheet = CheatSheet(current_mode)

    # Create system tray icon
    tray_icon = create_tray_icon(app, overlay)

    def handle_message():
        nonlocal current_mode

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

    timer = QTimer()
    timer.timeout.connect(handle_message)
    timer.start(16)

    sys.exit(app.exec())
