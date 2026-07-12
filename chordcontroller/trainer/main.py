from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from chordcontroller.trainer.app import TrainerMainWindow
from chordcontroller.trainer.controller_runtime import ControllerRuntime
from chordcontroller.trainer.theme import apply_theme


def main() -> int:
    app = QApplication(sys.argv)
    apply_theme(app)

    controller_runtime = ControllerRuntime()
    controller_runtime.start()

    window = TrainerMainWindow(controller_runtime)
    window.showFullScreen()

    exit_code = app.exec()
    controller_runtime.stop()
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
