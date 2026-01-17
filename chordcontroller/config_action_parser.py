from chordcontroller.config import (
    MultiControllerButtonAction,
    KeyboardKey,
    ButtonAction,
    StickAction,
)


def parse_multi_controller_button_action(
    multi_controller_button_action: MultiControllerButtonAction,
) -> str:
    """
    Returns a string representation of the actions defined in a
    MultiControllerButtonAction.
    """
    if not multi_controller_button_action.actions:
        return "No action defined"

    keys: list[KeyboardKey] = []

    for (
        controller_button_event_name,
        actions,
    ) in multi_controller_button_action.actions.items():
        actions = actions if isinstance(actions, list) else [actions]
        for action in actions:
            if action.action == "key_down":
                keys.append(action.key)

    # Join all subsequent keys that are a single character into a single string
    # Join other subsequent keys with " + "
    action_string: list[str] = []
    current_chars: list[str] = []
    for key in keys:
        if not action_string and key == "space":
            current_chars.append("␣")
        elif len(key) == 1 or (current_chars and (key == "space" or key == "enter")):
            if key == "space":
                current_chars.append("␣")
            elif key == "enter":
                current_chars.append("¶")
            else:
                current_chars.append(key)
        else:
            if current_chars:
                action_string.append("".join(current_chars))
                current_chars = []
            action_string.append(key)
    if current_chars:
        action_string.append("".join(current_chars))

    return " + ".join(action_string)


def parse_button_action(
    button_action: ButtonAction,
) -> str:
    """
    Returns a string representation of the actions defined in a ButtonAction.
    """

    if not button_action:
        return "No action defined"

    action_string: list[KeyboardKey | str] = []

    for (
        controller_button_event_name,
        actions,
    ) in button_action.items():
        actions = actions if isinstance(actions, list) else [actions]
        for action in actions:
            if action.action == "key_down" or action.action == "key_press":
                action_string.append(action.key)
            elif action.action == "switch_mode":
                action_string.append(f"mode: {action.mode}")
            elif (
                action.action == "close_cheat_sheet"
                or action.action == "toggle_cheat_sheet"
            ):
                action_string.append("Close")
            elif action.action == "type":
                action_string.append(action.text)
            elif action.action == "mouse_down":
                action_string.append(f"Mouse {action.button}")

    return " + ".join(action_string)


def parse_stick_action(
    stick_action: StickAction,
) -> str:
    """
    Returns a string representation of the actions defined in a StickAction.
    """
    if not stick_action:
        return "No action defined"

    action_string: list[str] = []

    for (
        controller_button_event_name,
        actions,
    ) in stick_action.items():
        actions = actions if isinstance(actions, list) else [actions]
        for action in actions:
            if action.action == "mouse_move":
                action_string.append(f"Mouse Move")
            elif action.action == "scroll":
                action_string.append(f"Scroll")
            elif action.action == "mouse_down":
                action_string.append(f"Mouse {action.button}")
            elif action.action == "switch_mode":
                action_string.append(f"Mode: {action.mode}")

    return " + ".join(action_string)


if __name__ == "__main__":
    from chordcontroller.config import (
        ComputerKeyDownAction,
        SwitchModeAction,
    )

    example_action = MultiControllerButtonAction(
        buttons=["face_up", "face_right"],
        actions={
            "down": [
                ComputerKeyDownAction(key="A"),
                ComputerKeyDownAction(key="B"),
            ]
        },
    )
    print(
        f"Example MultiControllerButtonAction: {parse_multi_controller_button_action(example_action)}"
    )

    example_button_action: ButtonAction = {
        "down": [
            ComputerKeyDownAction(key="A"),
            SwitchModeAction(mode="typing"),
        ],
        "up": [
            ComputerKeyDownAction(key="B"),
        ],
    }
    print(f"Example ButtonAction: {parse_button_action(example_button_action)}")
