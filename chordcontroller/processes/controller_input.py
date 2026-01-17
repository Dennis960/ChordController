import pygame
from chordcontroller.controller_inputs import Controller
from chordcontroller.config import Config
from chordcontroller.controller_input_handler import ControllerInputHandler
from multiprocessing.connection import Connection
from chordcontroller.widgets.controller_overlay import HeadlessOverlayHandler


def controller_input_process_main(ui_send_pipe: Connection):
    """Main loop for controller input processing."""
    pygame.init()

    config = Config.load_config()
    controller = Controller(config)

    overlay_handler = HeadlessOverlayHandler(ui_send_pipe)
    input_handler = ControllerInputHandler(controller, config, overlay_handler)

    clock = pygame.time.Clock()
    last_controller_connected = controller.pygame_controller is not None

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

        input_handler.update()

        clock.tick(60)

    input_handler.stop()
    pygame.quit()
