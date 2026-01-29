import pygame
from chordcontroller.controller_inputs import Controller
from chordcontroller.config import Config
from chordcontroller.controller_input_handler import ControllerInputHandler
from multiprocessing.connection import Connection
from chordcontroller.widgets.controller_overlay import HeadlessOverlayHandler


def controller_input_process_main(ui_send_pipe: Connection, ui_recv_pipe: Connection):
    """Main loop for controller input processing."""
    pygame.init()

    config = Config.load_config()
    controller = Controller(config)

    overlay_handler = HeadlessOverlayHandler(ui_send_pipe)
    input_handler: ControllerInputHandler | None = None

    clock = pygame.time.Clock()
    last_controller_connected = controller.pygame_controller is not None
    calibration_complete = False

    if controller.pygame_controller is not None:
        ui_send_pipe.send({"cmd": "controller_connected"})
    else:
        ui_send_pipe.send({"cmd": "controller_disconnected"})

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            controller.handle_pygame_event(event)

        controller.update_check_controller_connection()

        controller_connected = controller.pygame_controller is not None
        if controller_connected != last_controller_connected:
            last_controller_connected = controller_connected
            if controller_connected:
                ui_send_pipe.send({"cmd": "controller_connected"})
            else:
                ui_send_pipe.send({"cmd": "controller_disconnected"})

        # Check for messages from UI process
        while ui_recv_pipe.poll():
            msg = ui_recv_pipe.recv()
            cmd = msg.get("cmd")
            if cmd == "calibration_complete":
                calibration_complete = True
                # Create input handler now that calibration is done
                input_handler = ControllerInputHandler(controller, config, overlay_handler)

        # During calibration, send joystick positions to UI
        if not calibration_complete:
            left_stick = controller.sticks.get("stick_left")
            right_stick = controller.sticks.get("stick_right")
            ui_send_pipe.send({
                "cmd": "joystick_update",
                "left_x": left_stick.x if left_stick else 0.0,
                "left_y": left_stick.y if left_stick else 0.0,
                "right_x": right_stick.x if right_stick else 0.0,
                "right_y": right_stick.y if right_stick else 0.0,
            })

        # Only update input handler if calibration is complete
        if input_handler is not None:
            input_handler.update()

        clock.tick(60)

    if input_handler is not None:
        input_handler.stop()
    pygame.quit()
