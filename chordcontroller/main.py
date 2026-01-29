"""
Main entry point for the ChordController application.

This module provides the main() function that serves as the entry point
for both package installation (via console_scripts) and direct execution.
"""

import multiprocessing
from chordcontroller.processes.controller_input import controller_input_process_main
from chordcontroller.processes.ui import pyside6_ui_process_main

def main():
    """Main entry point for the ChordController application."""
    # Required for multiprocessing to work correctly on Windows
    multiprocessing.freeze_support()
    
    ui_recv_pipe, ui_send_pipe = multiprocessing.Pipe(duplex=False)
    controller_process = multiprocessing.Process(
        target=controller_input_process_main,
        args=(ui_send_pipe,),
        daemon=True,
    )
    controller_process.start()

    ui_process = multiprocessing.Process(
        target=pyside6_ui_process_main,
        args=(ui_recv_pipe,),
        daemon=False,
    )
    ui_process.start()

    try:
        ui_process.join()
    except KeyboardInterrupt:
        pass
    finally:
        if controller_process.is_alive():
            controller_process.terminate()
        if ui_process.is_alive():
            ui_process.terminate()


if __name__ == "__main__":
    main()
