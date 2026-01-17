from chordcontroller.controller_inputs import Controller
import time
from chordcontroller.config import *
from chordcontroller.desktop_outputs import Keyboard, Mouse
from chordcontroller.widgets.controller_overlay import HeadlessOverlayHandler


keyboard = Keyboard()
mouse = Mouse()

CONTROLLER_INPUT_EVENT_LISTENER_TAG = "controller_input_handler"


class ControllerInputHandler:
    """
    This class handles the connection between the controller and the desktop by executing the actions defined in the configuration.
    It also implements logic for smooth boosted mouse movement and scrolling.
    """

    mode: Mode

    def __init__(
        self,
        controller: Controller,
        config: Config,
        controller_overlay_handler: HeadlessOverlayHandler,
        skip_setup=False,
    ):
        self.controller = controller
        self.config = config
        self.controller_overlay_handler = controller_overlay_handler
        self.last_time = time.time()
        self.boost = False
        self.boost_start_time = 0.0
        self.target_scroll_x = 0  # used for mouse scrolling
        self.target_scroll_y = 0  # used for mouse scrolling
        self.target_distance_x = 0  # used for mouse movement
        self.target_distance_y = 0  # used for mouse movement
        self.pressed_keys: list[KeyboardKey] = []
        if not skip_setup:
            self.toggle_mode("default")

    def execute_action(self, action: ComputerAction | MiscellaneousAction):
        if action.action == "switch_mode":
            self.toggle_mode(action.mode)
        elif action.action == "key_down":
            if action.key not in self.pressed_keys:
                self.pressed_keys.append(action.key)
                keyboard.press(action.key)
        elif action.action == "key_up":
            if action.key in self.pressed_keys:
                self.pressed_keys.remove(action.key)
                keyboard.release(action.key)
        elif action.action == "mouse_down":
            mouse.press(action.button)
        elif action.action == "mouse_up":
            mouse.release(action.button)
        elif action.action == "type":
            keyboard.type(action.text)
        elif action.action == "key_press":
            keyboard.press(action.key)
            keyboard.release(action.key)
        elif action.action == "open_cheat_sheet":
            self.controller_overlay_handler.open_cheatsheet(
                action.preferred_screen_index
            )
        elif action.action == "close_cheat_sheet":
            self.controller_overlay_handler.close_cheatsheet()
        elif action.action == "toggle_cheat_sheet":
            self.controller_overlay_handler.toggle_cheatsheet(
                action.preferred_screen_index
            )
        else:
            print(f"Action {action.action} not found")

    def add_button_action_listeners(
        self,
        controller_button_name: ControllerButtonName,
        controller_button_event_name: ControllerButtonEventName,
        actions: list[ComputerAction | MiscellaneousAction],
    ):
        button = self.controller.buttons.get(controller_button_name, None)
        if button is None:
            print(f"Button {controller_button_name} not found")
            return

        for action in actions:
            button.add_event_listener(
                controller_button_event_name,
                lambda button, action=action: self.execute_action(action),
                CONTROLLER_INPUT_EVENT_LISTENER_TAG,
            )

    def add_stick_action_listeners(
        self,
        controller_stick_name: ControllerStickName,
        controller_stick_event_name: ControllerStickEventName,
        actions: list[ComputerNavigationAction | MiscellaneousAction],
    ):
        stick = self.controller.sticks.get(controller_stick_name, None)
        if stick is None:
            print(f"Stick {controller_stick_name} not found")
            return

        for action in actions:
            if action.action == "switch_mode":
                stick.add_event_listener(
                    controller_stick_event_name,
                    lambda stick, action=action: self.execute_action(action),
                    CONTROLLER_INPUT_EVENT_LISTENER_TAG,
                )
            elif action.action == "mouse_move":
                pass
            elif action.action == "scroll":
                pass
            elif (
                action.action == "open_cheat_sheet"
                or action.action == "show_cheat_sheet"
            ):
                stick.add_event_listener(
                    controller_stick_event_name,
                    lambda stick, action=action: self.execute_action(action),
                    CONTROLLER_INPUT_EVENT_LISTENER_TAG,
                )
            else:
                print(f"Action {action.action} not found")

    def on_multi_button_event(
        self,
        actions: list[ComputerAction | MiscellaneousAction],
    ):
        for action in actions:
            self.execute_action(action)

    def release_all_keyboard_buttons(self):
        """
        Used to release all keyboard buttons when switching modes. This will prevent buttons from being stuck.
        """
        for key in self.pressed_keys:
            keyboard.release(key)
        self.pressed_keys = []

    def toggle_mode(self, mode_name: str):
        print(f"Switching to mode {mode_name}")
        self.release_all_keyboard_buttons()
        self.controller.remove_all_event_listeners(CONTROLLER_INPUT_EVENT_LISTENER_TAG)

        config_mode = self.config.modes.get(mode_name, None)
        assert config_mode is not None, f"Mode {mode_name} not found in config"
        self.mode = config_mode
        if self.mode is None:
            print(f"Mode {self.mode} not found. Falling back to default mode")
            self.mode = self.config.modes["default"]
        global_mode = self.config.modes["global"]
        self.mode = Config.merge_modes(self.mode, global_mode)

        # Send mode change to UI process via overlay handler pipe
        self.controller_overlay_handler.set_title(mode_name)

        if self.mode.button_actions is not None:
            for (
                controller_button_name,
                action_details,
            ) in self.mode.button_actions.items():
                for controller_button_event_name, actions in action_details.items():
                    if not isinstance(actions, list):
                        actions = [actions]
                    self.add_button_action_listeners(
                        controller_button_name, controller_button_event_name, actions
                    )

        if self.mode.stick_actions is not None:
            for (
                controller_stick_name,
                action_details,
            ) in self.mode.stick_actions.items():
                for controller_stick_event_name, actions in action_details.items():
                    if not isinstance(actions, list):
                        actions = [actions]
                    self.add_stick_action_listeners(
                        controller_stick_name, controller_stick_event_name, actions
                    )

        if self.mode.multi_button_actions is not None:
            for multi_button_action in self.mode.multi_button_actions:
                for (
                    controller_button_event_name,
                    actions,
                ) in multi_button_action.actions.items():
                    if not isinstance(actions, list):
                        actions = [actions]
                    self.controller.multi_button_events.add_event_listener(
                        controller_button_event_name,
                        multi_button_action.buttons,
                        lambda buttons, actions=actions: self.on_multi_button_event(
                            actions
                        ),
                        CONTROLLER_INPUT_EVENT_LISTENER_TAG,
                    )
        self.controller_overlay_handler.set_title(self.mode.name)

    def on_update_stick_move_event(
        self,
        delta_time: float,
        controller_stick_name: ControllerStickName,
        action: ComputerNavigationAction,
    ):
        stick = self.controller.sticks.get(controller_stick_name, None)
        if stick is None:
            print(f"Stick {controller_stick_name} not found")
            return

        if action.action == "mouse_move":
            self.move_cursor(stick.x, stick.y, delta_time)
        elif action.action == "scroll":
            self.scroll(stick.y, stick.x, delta_time)
        else:
            print(f"Action {action.action} not found")

    def update(self):
        """
        Called every frame. Updates the cursor position and scrolls the mouse if necessary.
        """
        current_time = time.time()
        delta_time = current_time - self.last_time
        self.last_time = current_time
        self._update(delta_time)

    def _update(self, delta_time: float):
        if self.mode.stick_actions is None:
            return
        for controller_stick_name, action_details in self.mode.stick_actions.items():
            for controller_stick_event_name, actions in action_details.items():
                if not isinstance(actions, list):
                    actions = [actions]
                for action in [
                    action
                    for action in actions
                    if isinstance(action, ComputerNavigationAction)
                ]:
                    if controller_stick_event_name == "move":
                        self.on_update_stick_move_event(
                            delta_time,
                            controller_stick_name,
                            action,
                        )
                    else:
                        print(f"Event {controller_stick_event_name} not found")

    def stop(self):
        self.controller.remove_all_event_listeners(CONTROLLER_INPUT_EVENT_LISTENER_TAG)
        self.release_all_keyboard_buttons()

    def get_cursor_speed(self, x_value, y_value):
        """
        Returns the target speed of the cursor based on the x and y values of the stick.
        Uses an exponential function to calculate the speed.
        Applies boost if the stick is pushed to the edge.
        """
        speed = pow(pow(x_value, 2) + pow(y_value, 2), 0.5)  # Between 0 and 1
        is_boosting = False
        if speed > 0.95:
            speed = 1
            if not self.boost:
                self.boost = True
                self.boost_start_time = time.time()
            elif (
                time.time() - self.boost_start_time
                >= self.config.settings.cursor_settings.cursor_boost_acceleration_delay
            ):
                is_boosting = True
        else:
            self.boost = False
        if is_boosting:
            boost_time = (
                time.time()
                - self.boost_start_time
                - self.config.settings.cursor_settings.cursor_boost_acceleration_delay
            )
            boost_factor = (
                boost_time
                / self.config.settings.cursor_settings.cursor_boost_acceleration_time
            )  # Between 0 and 1
            if boost_factor > 1:
                boost_factor = 1
            if boost_factor < 0:
                boost_factor = 0
            speed = (
                1
                + boost_factor * self.config.settings.cursor_settings.cursor_boost_speed
            )
        elif speed < 0.05:
            speed = 0
        else:
            speed = 1.5 * pow(2.4, 4.3 * (speed - 1.1))  # ~ Between 0 and 1
        return speed

    def move_cursor(self, x_value, y_value, delta_time):
        speed = self.get_cursor_speed(x_value, y_value)

        x_value *= speed
        y_value *= speed
        distance_x = (
            x_value * self.config.settings.cursor_settings.cursor_speed * delta_time
        )
        distance_y = (
            y_value * self.config.settings.cursor_settings.cursor_speed * delta_time
        )
        # distances might be too small to move the cursor, so accumulate the distances over time and move the curser when the accumulated distance is bigger than 1
        # 1. Get accumulated distance. If cursor switches direction, reset accumulated distance
        if (x_value > 0) != (self.target_distance_x > 0):
            self.target_distance_x = 0
        if (y_value > 0) != (self.target_distance_y > 0):
            self.target_distance_y = 0
        # 2. Add new distance to accumulated distance
        self.target_distance_x += distance_x
        self.target_distance_y += distance_y
        # 3. If accumulated distance is bigger than 1, move the cursor by a hole integer and subtract the integer from the accumulated distance
        target_distance_x = 0
        target_distance_y = 0
        if abs(self.target_distance_x) >= 1:
            target_distance_x = int(self.target_distance_x)
            self.target_distance_x -= target_distance_x
        if abs(self.target_distance_y) >= 1:
            target_distance_y = int(self.target_distance_y)
            self.target_distance_y -= target_distance_y
        mouse.move(target_distance_x, target_distance_y)

    def scroll(self, y_value, x_value, delta_time):
        if (y_value > 0) != (self.target_scroll_y > 0):
            self.target_scroll_y = 0
        self.target_scroll_y += (
            y_value * self.config.settings.cursor_settings.scroll_speed
        )
        if (x_value > 0) != (self.target_scroll_x > 0):
            self.target_scroll_x = 0
        self.target_scroll_x += (
            x_value * self.config.settings.cursor_settings.scroll_speed
        )
        scroll_amount_y = 0
        scroll_amount_x = 0
        if abs(self.target_scroll_y) >= 1:
            scroll_amount_y = int(self.target_scroll_y)
            self.target_scroll_y -= scroll_amount_y
        if abs(self.target_scroll_x) >= 1:
            scroll_amount_x = int(self.target_scroll_x)
            self.target_scroll_x -= scroll_amount_x
        if scroll_amount_x != 0 or scroll_amount_y != 0:
            mouse.scroll(scroll_amount_x, -scroll_amount_y)


if __name__ == "__main__":
    chars = "1234567890ß!\"$%&/()=?'+#-.,*'_:;<>|{[]}\\~@€^`°qwertzuiopüasdfghjklöäyxcvbnmQWERTZUIOPÜASDFGHJKLÖÄYXCVBNM \n\t"
    cursor = ControllerInputHandler(None, None, None, True)  # type: ignore
    for char in chars:
        print(f"keyboard.press('{char}')")
        cursor.execute_action(ComputerTypeAction(text=char))
