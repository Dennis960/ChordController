from pydantic import BaseModel
from typing import Literal
import os
from pathlib import Path

from chordcontroller.paths import get_config_path, ensure_config_dir_exists

ModeName = Literal["default", "global"] | str
"""Name of a mode."""

MouseButtonName = Literal["left", "middle", "right"]
"""A mouse button."""
# fmt: off
KeyboardKey = Literal[
    "a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s",
    "t","u","v","w","x","y","z","ä","ö","ü",
    "A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S",
    "T","U","V","W","X","Y","Z","Ä","Ö","Ü",
    "1","2","3","4","5","6","7","8","9","0",
    "ß","!",'"',"$","%","&","/","(",")","=","?","'","+","#","-",".",",","*",
    "'","_",":",";","<",">","|","{","[","]","}","\\","~","@","€","^","`","°",
    "space","enter","tab","backspace","delete","alt","ctrl","shift","cmd","up","down",
    "left","right","esc","pos1","end",
    "f1","f2","f3","f4","f5","f6","f7","f8","f9","f10","f11","f12",
    "menu"
]
"""A key on the keyboard."""
keyboard_keys = [
    "a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s",
    "t","u","v","w","x","y","z","ä","ö","ü",
    "A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S",
    "T","U","V","W","X","Y","Z","Ä","Ö","Ü",
    "1","2","3","4","5","6","7","8","9","0",
    "ß","!",'"',"$","%","&","/","(",")","=","?","'","+","#","-",".",",","*",
    "'","_",":",";","<",">","|","{","[","]","}","\\","~","@","€","^","`","°",
    "space","enter","tab","backspace","delete"
]
# fmt: on

ControllerButtonName = Literal[
    "dpad_up",
    "dpad_down",
    "dpad_left",
    "dpad_right",
    "face_up",
    "face_down",
    "face_left",
    "face_right",
    "shoulder_l",
    "shoulder_r",
    "trigger_l",
    "trigger_r",
    "stick_left",
    "stick_right",
    "minus",
    "plus",
    "home",
    "capture",
]
"""A button on the controller."""
Chord = frozenset[ControllerButtonName]
"""A combination of controller buttons pressed simultaneously."""
ControllerStickName = Literal["stick_left", "stick_right"]
"""A stick on the controller."""
ControllerButtonEventName = Literal[
    "down",
    "up",
    "click",
    "long_press",
    "double_click",
    "triple_click",
]
"""An event name for a button of the controller being pressed or released."""
ControllerStickEventName = Literal["move"]
"""An event name for a stick of the controller being moved."""

ControllerButtonIndex = (
    int | Literal["dpad-y", "dpad+y", "dpad-x", "dpad+x", "axis-4", "axis-5"]
)
"""Index of a button on the controller or the direction of the dpad buttons."""


class ControllerSettings(BaseModel):
    """Settings for the controller."""

    deadzone: float
    """Deadzone for the controller's sticks."""
    single_click_duration: float
    """Delay in seconds between a controler's button press and release to be registered as a single click."""
    double_click_duration: float
    """Delay in seconds between the release of the last single_click and the new press of the same button on the controller to be registered as a double click."""
    multi_click_duration: float
    """Maximum time in seconds starting from the first press of any button during which more button presses are added to the multi-click event before firing the event."""


class CursorSettings(BaseModel):
    """Settings for the cursor."""

    cursor_speed: int
    """Cursor will move at this speed in normal mode"""
    cursor_boost_speed: int
    """Cursor will move at this speed when boosting"""
    cursor_boost_acceleration_delay: float
    """Cursor will wait for this time before boosting"""
    cursor_boost_acceleration_time: float
    """Cursor will take this time to reach the boost speed"""
    scroll_speed: float
    """Speed of scrolling"""


class Settings(BaseModel):
    """Settings for the application."""

    controller_settings: ControllerSettings
    cursor_settings: CursorSettings


class ComputerKeyDownAction(BaseModel):
    """Action to press a key on the computer."""

    action: Literal["key_down"] = "key_down"
    key: KeyboardKey


class ComputerKeyUpAction(BaseModel):
    """Action to release a key on the computer."""

    action: Literal["key_up"] = "key_up"
    key: KeyboardKey


class ComputerKeyPressAction(BaseModel):
    """Action to press and release a key on the computer."""

    action: Literal["key_press"] = "key_press"
    key: KeyboardKey


class ComputerMouseMoveAction(BaseModel):
    """Action to move the mouse."""

    action: Literal["mouse_move"] = "mouse_move"


class ComputerMouseDownAction(BaseModel):
    """Action to press the mouse button."""

    action: Literal["mouse_down"] = "mouse_down"
    button: MouseButtonName


class ComputerMouseUpAction(BaseModel):
    """Action to release the mouse button."""

    action: Literal["mouse_up"] = "mouse_up"
    button: MouseButtonName


class ComputerScrollAction(BaseModel):
    """Action to scroll the computer."""

    action: Literal["scroll"] = "scroll"


class ComputerTypeAction(BaseModel):
    """Action to type text on the computer."""

    action: Literal["type"] = "type"
    text: str


class SwitchModeAction(BaseModel):
    """Action to switch the mode of the application."""

    action: Literal["switch_mode"] = "switch_mode"
    mode: ModeName


class OpenCheatSheetAction(BaseModel):
    """Action to open the cheat sheet."""

    action: Literal["open_cheat_sheet"] = "open_cheat_sheet"
    preferred_screen_index: int | None = None
    """Index of the screen where the cheat sheet should be displayed. If None or invalid, it will be displayed on the primary screen."""


class CloseCheatSheetAction(BaseModel):
    """Action to close the cheat sheet."""

    action: Literal["close_cheat_sheet"] = "close_cheat_sheet"


class ToggleCheatSheetAction(BaseModel):
    """Action to toggle the cheat sheet."""

    action: Literal["toggle_cheat_sheet"] = "toggle_cheat_sheet"
    preferred_screen_index: int | None = None
    """Index of the screen where the cheat sheet should be displayed. If None or invalid, it will be displayed on the primary screen."""


ComputerAction = (
    ComputerKeyDownAction
    | ComputerKeyUpAction
    | ComputerKeyPressAction
    | ComputerMouseDownAction
    | ComputerMouseUpAction
    | ComputerTypeAction
)
"""Represents a single discrete action that can be performed on the computer."""
ComputerNavigationAction = ComputerMouseMoveAction | ComputerScrollAction
"""Represents a continuous navigation action that can be performed on the computer."""


MiscellaneousAction = OpenCheatSheetAction | CloseCheatSheetAction | SwitchModeAction | ToggleCheatSheetAction
"""Represents an action that does not directly interact with the computer but is part of the software's functionality."""


ButtonAction = dict[
    ControllerButtonEventName,
    MiscellaneousAction | ComputerAction | list[ComputerAction | MiscellaneousAction],
]
"""A mapping of button events to actions for a specific controller button."""


StickAction = dict[
    ControllerStickEventName,
    MiscellaneousAction
    | ComputerNavigationAction
    | list[ComputerNavigationAction | MiscellaneousAction],
]
"""A mapping of stick events to actions for a specific controller stick."""


class MultiControllerButtonAction(BaseModel):
    """
    Defines a set of actions to be performed when a set of buttons are pressed or released during a multi-button event.
    """

    action: Literal["multi_button"] = "multi_button"
    buttons: list[ControllerButtonName]
    actions: ButtonAction


class Mode(BaseModel):
    """
    Represents the currently selected mode of control.
    Each mode specifies its own set of actions for events happening on the controller.
    """

    name: str
    """Name of the mode that is visible in the cheat sheet."""
    button_actions: (
        dict[
            ControllerButtonName,
            ButtonAction,
        ]
        | None
    ) = None
    stick_actions: (
        dict[
            ControllerStickName,
            StickAction,
        ]
        | None
    ) = None
    multi_button_actions: list[MultiControllerButtonAction] | None = None

    def model_validate(self):
        if self.multi_button_actions:
            seen = set()
            for multi_button_action in self.multi_button_actions:
                key = tuple(sorted(multi_button_action.buttons))
                if key in seen:
                    raise ValueError(
                        f"Duplicate multi_button_actions for buttons: {multi_button_action.buttons} with actions {multi_button_action.actions}"
                    )
                seen.add(key)
        return self

    def __init__(self, **data):
        super().__init__(**data)
        self.model_validate()


class Config(BaseModel):
    settings: Settings
    button_mapping: dict[ControllerButtonName, ControllerButtonIndex]
    """Mapping of controller buttons to their respective index used by pygame or the axis of the dpad for the dpad buttons."""
    stick_mapping: dict[ControllerStickName, tuple[int, int]]
    """Mapping of controller sticks to their respective axis indices used by pygame."""
    modes: dict[ModeName, Mode]
    """Mapping of mode names to their respective mode configurations."""

    @classmethod
    def load_config(cls, path: str | Path | None = None) -> "Config":
        if path is None:
            config_path = get_config_path()
        else:
            config_path = Path(path)
        
        if not config_path.exists():
            print(f"Config file not found at {config_path}. Using default config.")
            return default_config
        
        with open(config_path, "r", encoding="utf-8") as f:
            config = cls.model_validate_json(f.read())
            print(f"Config loaded from {config_path}.")
            return config

    def save_config(self, path: str | Path | None = None):
        if path is None:
            ensure_config_dir_exists()
            config_path = get_config_path()
        else:
            config_path = Path(path)
        
        # Ensure parent directory exists
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, "w", encoding="utf-8") as f:
            f.write(self.model_dump_json(indent=4))
        print(f"Config saved to {config_path}.")

    @classmethod
    def merge_modes(cls, mode1: Mode, mode2: Mode) -> Mode:
        """
        Returns a new Mode object that merges mode2 into mode1 for button_actions and stick_actions if not already present in mode1.
        The original mode1 and mode2 are not modified.
        """
        button_actions = dict(mode1.button_actions) if mode1.button_actions else {}
        stick_actions = dict(mode1.stick_actions) if mode1.stick_actions else {}
        multi_button_actions = (
            list(mode1.multi_button_actions) if mode1.multi_button_actions else []
        )

        if mode2.button_actions is not None:
            for controller_button_name, action_details in mode2.button_actions.items():
                if controller_button_name not in button_actions:
                    button_actions[controller_button_name] = action_details
        if mode2.stick_actions is not None:
            for controller_stick_name, action_details in mode2.stick_actions.items():
                if controller_stick_name not in stick_actions:
                    stick_actions[controller_stick_name] = action_details
        if mode2.multi_button_actions is not None:
            # Only add multi_button_actions from mode2 that are not already present in mode1
            existing_keys = {tuple(sorted(mba.buttons)) for mba in multi_button_actions}
            for mba in mode2.multi_button_actions:
                key = tuple(sorted(mba.buttons))
                if key not in existing_keys:
                    multi_button_actions.append(mba)
                    existing_keys.add(key)

        return Mode(
            name=mode1.name,
            button_actions=button_actions,
            stick_actions=stick_actions,
            multi_button_actions=multi_button_actions,
        )


def get_switch_pro_button_mapping() -> (
    dict[ControllerButtonName, ControllerButtonIndex]
):
    is_linux = os.name == "posix"
    if is_linux:
        return {
            "dpad_up": "dpad-y",
            "dpad_down": "dpad+y",
            "dpad_left": "dpad-x",
            "dpad_right": "dpad+x",
            "face_down": 0,
            "face_right": 1,
            "face_up": 2,
            "face_left": 3,
            "shoulder_l": 5,
            "shoulder_r": 6,
            "trigger_l": 7,
            "trigger_r": 8,
            "stick_left": 12,
            "stick_right": 13,
            "capture": 4,
            "minus": 9,
            "plus": 10,
            "home": 11,
        }
    else:
        return {
            "dpad_up": 11,
            "dpad_down": 12,
            "dpad_left": 13,
            "dpad_right": 14,
            "face_down": 1,
            "face_right": 0,
            "face_up": 2,
            "face_left": 3,
            "shoulder_l": 9,
            "shoulder_r": 10,
            "trigger_l": "axis-4",
            "trigger_r": "axis-5",
            "stick_left": 7,
            "stick_right": 8,
            "capture": 15,
            "minus": 4,
            "plus": 6,
            "home": 5,
        }


default_config = Config(
    settings=Settings(
        controller_settings=ControllerSettings(
            deadzone=0.1,
            single_click_duration=0.6,
            double_click_duration=0.2,
            multi_click_duration=0.2,
        ),
        cursor_settings=CursorSettings(
            cursor_speed=500,
            cursor_boost_speed=10,
            cursor_boost_acceleration_delay=0.1,
            cursor_boost_acceleration_time=0.5,
            scroll_speed=0.5,
        ),
    ),
    button_mapping=get_switch_pro_button_mapping(),
    stick_mapping={
        "stick_left": (0, 1),
        "stick_right": (2, 3),
    },
    modes={
        "global": Mode(
            name="Global",
            button_actions={
                "home": {
                    "down": SwitchModeAction(mode="default"),
                },
                "capture": {
                    "down": ComputerKeyDownAction(key="esc"),
                    "up": ComputerKeyUpAction(key="esc"),
                },
                "plus": {
                    "down": [
                        ToggleCheatSheetAction(preferred_screen_index=2),
                    ],
                },
            }
        ),
        "default": Mode(
            name="Default",
            button_actions={
                "dpad_up": {
                    "down": [
                        SwitchModeAction(mode="selection"),
                    ],
                },
                "dpad_down": {
                    "down": [
                        SwitchModeAction(mode="selection"),
                    ],
                },
                "dpad_left": {
                    "down": [
                        SwitchModeAction(mode="selection"),
                    ],
                },
                "dpad_right": {
                    "down": [
                        SwitchModeAction(mode="selection"),
                    ],
                },
                "face_right": {
                    "down": ComputerMouseDownAction(button="left"),
                    "up": ComputerMouseUpAction(button="left"),
                },
                "face_down": {
                    "down": ComputerMouseDownAction(button="right"),
                    "up": ComputerMouseUpAction(button="right"),
                },
                "face_up": {
                    "down": ComputerMouseDownAction(button="middle"),
                    "up": ComputerMouseUpAction(button="middle"),
                },
                "stick_right": {
                    "down": ComputerMouseDownAction(button="middle"),
                    "up": ComputerMouseUpAction(button="middle"),
                },
                "shoulder_l": {
                    "click": SwitchModeAction(mode="typing"),
                },
                "shoulder_r": {
                    "down": ComputerKeyDownAction(key="alt"),
                    "up": ComputerKeyUpAction(key="alt"),
                },
                "trigger_r": {
                    "down": ComputerKeyDownAction(key="ctrl"),
                    "up": ComputerKeyUpAction(key="ctrl"),
                },
                "trigger_l": {
                    "down": ComputerKeyDownAction(key="shift"),
                    "up": ComputerKeyUpAction(key="shift"),
                },
            },
            stick_actions={
                "stick_left": {
                    "move": ComputerMouseMoveAction(),
                },
                "stick_right": {
                    "move": ComputerScrollAction(),
                },
            },
        ),
        "selection": Mode(
            name="Selection",
            button_actions={
                "dpad_up": {
                    "down": ComputerKeyDownAction(key="up"),
                    "up": ComputerKeyUpAction(key="up"),
                },
                "dpad_right": {
                    "down": ComputerKeyDownAction(key="right"),
                    "up": ComputerKeyUpAction(key="right"),
                },
                "dpad_down": {
                    "down": ComputerKeyDownAction(key="down"),
                    "up": ComputerKeyUpAction(key="down"),
                },
                "dpad_left": {
                    "down": ComputerKeyDownAction(key="left"),
                    "up": ComputerKeyUpAction(key="left"),
                },
                "face_up": {
                    "down": ComputerKeyDownAction(key="shift"),
                    "up": ComputerKeyUpAction(key="shift"),
                },
                "face_right": {
                    "down": ComputerKeyDownAction(key="cmd"),
                    "up": ComputerKeyUpAction(key="cmd"),
                },
                "face_down": {
                    "down": ComputerKeyDownAction(key="alt"),
                    "up": ComputerKeyUpAction(key="alt"),
                },
                "stick_left": {
                    "down": ComputerKeyDownAction(key="ctrl"),
                    "up": ComputerKeyUpAction(key="ctrl"),
                },
                "shoulder_l": {
                    "click": SwitchModeAction(mode="typing"),
                },
                "shoulder_r": {
                    "click": SwitchModeAction(mode="typing"),
                },
                "trigger_l": {
                    "down": ComputerKeyDownAction(key="pos1"),
                    "up": ComputerKeyUpAction(key="pos1"),
                },
                "trigger_r": {
                    "down": ComputerKeyDownAction(key="end"),
                    "up": ComputerKeyUpAction(key="end"),
                },
            },
            stick_actions={
                "stick_right": {
                    "move": SwitchModeAction(mode="default"),
                },
                "stick_left": {
                    "move": SwitchModeAction(mode="default"),
                },
            },
        ),
        "typing": Mode(
            name="Typing",
            stick_actions={
                "stick_left": {
                    "move": SwitchModeAction(mode="default"),
                },
                "stick_right": {
                    "move": ComputerScrollAction(),
                },
            },
            multi_button_actions=[
                MultiControllerButtonAction(buttons=["dpad_left"],actions={"down": [ComputerKeyDownAction(key="a")],"up": [ComputerKeyUpAction(key="a")]}),
                MultiControllerButtonAction(buttons=["face_left", "shoulder_r"],actions={"down": [ComputerKeyDownAction(key="b")],"up": [ComputerKeyUpAction(key="b")]}),
                MultiControllerButtonAction(buttons=["shoulder_r", "face_up"],actions={"down": [ComputerKeyDownAction(key="c")],"up": [ComputerKeyUpAction(key="c")]}),
                MultiControllerButtonAction(buttons=["face_down"],actions={"down": [ComputerKeyDownAction(key="d")],"up": [ComputerKeyUpAction(key="d")]}),
                MultiControllerButtonAction(buttons=["trigger_l"],actions={"down": [ComputerKeyDownAction(key="e")],"up": [ComputerKeyUpAction(key="e")]}),
                MultiControllerButtonAction(buttons=["trigger_r", "face_down"],actions={"down": [ComputerKeyDownAction(key="f")],"up": [ComputerKeyUpAction(key="f")]}),
                MultiControllerButtonAction(buttons=["trigger_r", "face_left"],actions={"down": [ComputerKeyDownAction(key="g")],"up": [ComputerKeyUpAction(key="g")]}),
                MultiControllerButtonAction(buttons=["trigger_l", "face_right"],actions={"down": [ComputerKeyDownAction(key="h")],"up": [ComputerKeyUpAction(key="h")]}),
                MultiControllerButtonAction(buttons=["dpad_down"],actions={"down": [ComputerKeyDownAction(key="i")],"up": [ComputerKeyUpAction(key="i")]}),
                MultiControllerButtonAction(buttons=["trigger_r", "shoulder_r", "face_up"],actions={"down": [ComputerKeyDownAction(key="j")],"up": [ComputerKeyUpAction(key="j")]}),
                MultiControllerButtonAction(buttons=["trigger_r", "shoulder_r", "face_down"],actions={"down": [ComputerKeyDownAction(key="k")],"up": [ComputerKeyUpAction(key="k")]}),
                MultiControllerButtonAction(buttons=["shoulder_r", "face_down"],actions={"down": [ComputerKeyDownAction(key="l")],"up": [ComputerKeyUpAction(key="l")]}),
                MultiControllerButtonAction(buttons=["face_left"],actions={"down": [ComputerKeyDownAction(key="m")],"up": [ComputerKeyUpAction(key="m")]}),
                MultiControllerButtonAction(buttons=["trigger_r"],actions={"down": [ComputerKeyDownAction(key="n")],"up": [ComputerKeyUpAction(key="n")]}),
                MultiControllerButtonAction(buttons=["dpad_right"],actions={"down": [ComputerKeyDownAction(key="o")],"up": [ComputerKeyUpAction(key="o")]}),
                MultiControllerButtonAction(buttons=["trigger_r", "face_right"],actions={"down": [ComputerKeyDownAction(key="p")],"up": [ComputerKeyUpAction(key="p")]}),
                MultiControllerButtonAction(buttons=["trigger_r", "face_right", "face_up"],actions={"down": [ComputerKeyDownAction(key="q")],"up": [ComputerKeyUpAction(key="q")]}),
                MultiControllerButtonAction(buttons=["shoulder_r", "face_right"],actions={"down": [ComputerKeyDownAction(key="r")],"up": [ComputerKeyUpAction(key="r")]}),
                MultiControllerButtonAction(buttons=["face_up"],actions={"down": [ComputerKeyDownAction(key="s")],"up": [ComputerKeyUpAction(key="s")]}),
                MultiControllerButtonAction(buttons=["face_right"],actions={"down": [ComputerKeyDownAction(key="t")],"up": [ComputerKeyUpAction(key="t")]}),
                MultiControllerButtonAction(buttons=["dpad_up"],actions={"down": [ComputerKeyDownAction(key="u")],"up": [ComputerKeyUpAction(key="u")]}),
                MultiControllerButtonAction(buttons=["face_left", "face_down"],actions={"down": [ComputerKeyDownAction(key="v")],"up": [ComputerKeyUpAction(key="v")]}),
                MultiControllerButtonAction(buttons=["trigger_r", "shoulder_r"],actions={"down": [ComputerKeyDownAction(key="w")],"up": [ComputerKeyUpAction(key="w")]}),
                MultiControllerButtonAction(buttons=["shoulder_r", "face_right", "face_up"],actions={"down": [ComputerKeyDownAction(key="x")],"up": [ComputerKeyUpAction(key="x")]}),
                MultiControllerButtonAction(buttons=["shoulder_r", "face_right", "trigger_l"],actions={"down": [ComputerKeyDownAction(key="y")],"up": [ComputerKeyUpAction(key="y")]}),
                MultiControllerButtonAction(buttons=["face_left", "shoulder_r", "face_down"],actions={"down": [ComputerKeyDownAction(key="z")],"up": [ComputerKeyUpAction(key="z")]}),
                MultiControllerButtonAction(buttons=["trigger_l", "dpad_left", "dpad_up"],actions={"down": [ComputerKeyDownAction(key="\u00e4")],"up": [ComputerKeyUpAction(key="\u00e4")]}),
                MultiControllerButtonAction(buttons=["trigger_l", "dpad_up", "dpad_right"],actions={"down": [ComputerKeyDownAction(key="\u00f6")],"up": [ComputerKeyUpAction(key="\u00f6")]}),
                MultiControllerButtonAction(buttons=["trigger_l", "dpad_down", "dpad_right"],actions={"down": [ComputerKeyDownAction(key="\u00fc")],"up": [ComputerKeyUpAction(key="\u00fc")]}),
                MultiControllerButtonAction(buttons=["dpad_left", "shoulder_l"],actions={"down": [ComputerKeyDownAction(key="A")],"up": [ComputerKeyUpAction(key="A")]}),
                MultiControllerButtonAction(buttons=["face_left", "shoulder_r", "shoulder_l"],actions={"down": [ComputerKeyDownAction(key="B")],"up": [ComputerKeyUpAction(key="B")]}),
                MultiControllerButtonAction(buttons=["shoulder_r", "face_up", "shoulder_l"],actions={"down": [ComputerKeyDownAction(key="C")],"up": [ComputerKeyUpAction(key="C")]}),
                MultiControllerButtonAction(buttons=["face_down", "shoulder_l"],actions={"down": [ComputerKeyDownAction(key="D")],"up": [ComputerKeyUpAction(key="D")]}),
                MultiControllerButtonAction(buttons=["trigger_l", "shoulder_l"],actions={"down": [ComputerKeyDownAction(key="E")],"up": [ComputerKeyUpAction(key="E")]}),
                MultiControllerButtonAction(buttons=["trigger_r", "face_down", "shoulder_l"],actions={"down": [ComputerKeyDownAction(key="F")],"up": [ComputerKeyUpAction(key="F")]}),
                MultiControllerButtonAction(buttons=["trigger_r", "face_left", "shoulder_l"],actions={"down": [ComputerKeyDownAction(key="G")],"up": [ComputerKeyUpAction(key="G")]}),
                MultiControllerButtonAction(buttons=["trigger_l", "face_right", "shoulder_l"],actions={"down": [ComputerKeyDownAction(key="H")],"up": [ComputerKeyUpAction(key="H")]}),
                MultiControllerButtonAction(buttons=["dpad_down", "shoulder_l"],actions={"down": [ComputerKeyDownAction(key="I")],"up": [ComputerKeyUpAction(key="I")]}),
                MultiControllerButtonAction(buttons=["trigger_r", "shoulder_r", "face_up", "shoulder_l"],actions={"down": [ComputerKeyDownAction(key="J")],"up": [ComputerKeyUpAction(key="J")]}),
                MultiControllerButtonAction(buttons=["trigger_r", "shoulder_r", "face_down", "shoulder_l"],actions={"down": [ComputerKeyDownAction(key="K")],"up": [ComputerKeyUpAction(key="K")]}),
                MultiControllerButtonAction(buttons=["shoulder_r", "face_down", "shoulder_l"],actions={"down": [ComputerKeyDownAction(key="L")],"up": [ComputerKeyUpAction(key="L")]}),
                MultiControllerButtonAction(buttons=["face_left", "shoulder_l"],actions={"down": [ComputerKeyDownAction(key="M")],"up": [ComputerKeyUpAction(key="M")]}),
                MultiControllerButtonAction(buttons=["trigger_r", "shoulder_l"],actions={"down": [ComputerKeyDownAction(key="N")],"up": [ComputerKeyUpAction(key="N")]}),
                MultiControllerButtonAction(buttons=["shoulder_l", "dpad_right"],actions={"down": [ComputerKeyDownAction(key="O")],"up": [ComputerKeyUpAction(key="O")]}),
                MultiControllerButtonAction(buttons=["trigger_r", "face_right", "shoulder_l"],actions={"down": [ComputerKeyDownAction(key="P")],"up": [ComputerKeyUpAction(key="P")]}),
                MultiControllerButtonAction(buttons=["trigger_r", "face_right", "face_up", "shoulder_l"],actions={"down": [ComputerKeyDownAction(key="Q")],"up": [ComputerKeyUpAction(key="Q")]}),
                MultiControllerButtonAction(buttons=["shoulder_r", "face_right", "shoulder_l"],actions={"down": [ComputerKeyDownAction(key="R")],"up": [ComputerKeyUpAction(key="R")]}),
                MultiControllerButtonAction(buttons=["face_up", "shoulder_l"],actions={"down": [ComputerKeyDownAction(key="S")],"up": [ComputerKeyUpAction(key="S")]}),
                MultiControllerButtonAction(buttons=["face_right", "shoulder_l"],actions={"down": [ComputerKeyDownAction(key="T")],"up": [ComputerKeyUpAction(key="T")]}),
                MultiControllerButtonAction(buttons=["dpad_up", "shoulder_l"],actions={"down": [ComputerKeyDownAction(key="U")],"up": [ComputerKeyUpAction(key="U")]}),
                MultiControllerButtonAction(buttons=["face_left", "face_down", "shoulder_l"],actions={"down": [ComputerKeyDownAction(key="V")],"up": [ComputerKeyUpAction(key="V")]}),
                MultiControllerButtonAction(buttons=["trigger_r", "shoulder_r", "shoulder_l"],actions={"down": [ComputerKeyDownAction(key="W")],"up": [ComputerKeyUpAction(key="W")]}),
                MultiControllerButtonAction(buttons=["shoulder_r", "face_right", "face_up", "shoulder_l"],actions={"down": [ComputerKeyDownAction(key="X")],"up": [ComputerKeyUpAction(key="X")]}),
                MultiControllerButtonAction(buttons=["shoulder_r", "face_right", "trigger_l", "shoulder_l"],actions={"down": [ComputerKeyDownAction(key="Y")],"up": [ComputerKeyUpAction(key="Y")]}),
                MultiControllerButtonAction(buttons=["face_left", "shoulder_r", "face_down", "shoulder_l"],actions={"down": [ComputerKeyDownAction(key="Z")],"up": [ComputerKeyUpAction(key="Z")]}),
                MultiControllerButtonAction(buttons=["trigger_l", "dpad_left", "dpad_up", "shoulder_l"],actions={"down": [ComputerKeyDownAction(key="\u00c4")],"up": [ComputerKeyUpAction(key="\u00c4")]}),
                MultiControllerButtonAction(buttons=["trigger_l", "dpad_up", "shoulder_l", "dpad_right"],actions={"down": [ComputerKeyDownAction(key="\u00d6")],"up": [ComputerKeyUpAction(key="\u00d6")]}),
                MultiControllerButtonAction(buttons=["trigger_l", "dpad_down", "shoulder_l", "dpad_right"],actions={"down": [ComputerKeyDownAction(key="\u00dc")],"up": [ComputerKeyUpAction(key="\u00dc")]}),
                MultiControllerButtonAction(buttons=["shoulder_r", "dpad_left"],actions={"down": [ComputerKeyDownAction(key="0")],"up": [ComputerKeyUpAction(key="0")]}),
                MultiControllerButtonAction(buttons=["face_right", "dpad_left"],actions={"down": [ComputerKeyDownAction(key="1")],"up": [ComputerKeyUpAction(key="1")]}),
                MultiControllerButtonAction(buttons=["face_right", "shoulder_r", "dpad_left"],actions={"down": [ComputerKeyDownAction(key="2")],"up": [ComputerKeyUpAction(key="2")]}),
                MultiControllerButtonAction(buttons=["shoulder_r", "dpad_left", "face_up"],actions={"down": [ComputerKeyDownAction(key="3")],"up": [ComputerKeyUpAction(key="3")]}),
                MultiControllerButtonAction(buttons=["face_left", "dpad_left"],actions={"down": [ComputerKeyDownAction(key="4")],"up": [ComputerKeyUpAction(key="4")]}),
                MultiControllerButtonAction(buttons=["dpad_left", "shoulder_r", "face_down"],actions={"down": [ComputerKeyDownAction(key="5")],"up": [ComputerKeyUpAction(key="5")]}),
                MultiControllerButtonAction(buttons=["trigger_r", "dpad_left"],actions={"down": [ComputerKeyDownAction(key="6")],"up": [ComputerKeyUpAction(key="6")]}),
                MultiControllerButtonAction(buttons=["trigger_r", "trigger_l", "dpad_left"],actions={"down": [ComputerKeyDownAction(key="7")],"up": [ComputerKeyUpAction(key="7")]}),
                MultiControllerButtonAction(buttons=["shoulder_r", "dpad_left", "trigger_l"],actions={"down": [ComputerKeyDownAction(key="8")],"up": [ComputerKeyUpAction(key="8")]}),
                MultiControllerButtonAction(buttons=["face_left", "shoulder_r", "dpad_left"],actions={"down": [ComputerKeyDownAction(key="9")],"up": [ComputerKeyUpAction(key="9")]}),
                MultiControllerButtonAction(buttons=["face_left", "shoulder_r", "face_up"],actions={"down": [ComputerKeyDownAction(key="!")],"up": [ComputerKeyUpAction(key="!")]}),
                MultiControllerButtonAction(buttons=["shoulder_r", "face_up", "trigger_l"],actions={"down": [ComputerKeyDownAction(key="\"")],"up": [ComputerKeyUpAction(key="\"")]}),
                MultiControllerButtonAction(buttons=["face_right", "dpad_down"],actions={"down": [ComputerKeyDownAction(key="#")],"up": [ComputerKeyUpAction(key="#")]}),
                MultiControllerButtonAction(buttons=["shoulder_r", "dpad_left", "dpad_down"],actions={"down": [ComputerKeyDownAction(key="$")],"up": [ComputerKeyUpAction(key="$")]}),
                MultiControllerButtonAction(buttons=["dpad_left", "face_up", "shoulder_l"],actions={"down": [ComputerKeyDownAction(key="%")],"up": [ComputerKeyUpAction(key="%")]}),
                MultiControllerButtonAction(buttons=["face_left", "face_up"],actions={"down": [ComputerKeyDownAction(key="&")],"up": [ComputerKeyUpAction(key="&")]}),
                MultiControllerButtonAction(buttons=["trigger_r", "trigger_l", "face_up"],actions={"down": [ComputerKeyDownAction(key="'")],"up": [ComputerKeyUpAction(key="'")]}),
                MultiControllerButtonAction(buttons=["dpad_left", "dpad_down"],actions={"down": [ComputerKeyDownAction(key="(")],"up": [ComputerKeyUpAction(key="(")]}),
                MultiControllerButtonAction(buttons=["trigger_r", "face_up"],actions={"down": [ComputerKeyDownAction(key=")")],"up": [ComputerKeyUpAction(key=")")]}),
                MultiControllerButtonAction(buttons=["face_up", "dpad_down"],actions={"down": [ComputerKeyDownAction(key="*")],"up": [ComputerKeyUpAction(key="*")]}),
                MultiControllerButtonAction(buttons=["shoulder_r", "face_up", "dpad_down"],actions={"down": [ComputerKeyDownAction(key="+")],"up": [ComputerKeyUpAction(key="+")]}),
                MultiControllerButtonAction(buttons=["trigger_r", "trigger_l", "face_right"],actions={"down": [ComputerKeyDownAction(key=",")],"up": [ComputerKeyUpAction(key=",")]}),
                MultiControllerButtonAction(buttons=["trigger_l", "face_down"],actions={"down": [ComputerKeyDownAction(key="-")],"up": [ComputerKeyUpAction(key="-")]}),
                MultiControllerButtonAction(buttons=["shoulder_r", "trigger_l"],actions={"down": [ComputerKeyDownAction(key=".")],"up": [ComputerKeyUpAction(key=".")]}),
                MultiControllerButtonAction(buttons=["trigger_l", "face_up"],actions={"down": [ComputerKeyDownAction(key="/")],"up": [ComputerKeyUpAction(key="/")]}),
                MultiControllerButtonAction(buttons=["shoulder_r", "face_down", "trigger_l"],actions={"down": [ComputerKeyDownAction(key=":")],"up": [ComputerKeyUpAction(key=":")]}),
                MultiControllerButtonAction(buttons=["trigger_r", "shoulder_r", "face_right", "trigger_l"],actions={"down": [ComputerKeyDownAction(key=";")],"up": [ComputerKeyUpAction(key=";")]}),
                MultiControllerButtonAction(buttons=["dpad_left", "face_up"],actions={"down": [ComputerKeyDownAction(key="<")],"up": [ComputerKeyUpAction(key="<")]}),
                MultiControllerButtonAction(buttons=["dpad_left", "face_down"],actions={"down": [ComputerKeyDownAction(key="=")],"up": [ComputerKeyUpAction(key="=")]}),
                MultiControllerButtonAction(buttons=["dpad_left", "dpad_down", "shoulder_l"],actions={"down": [ComputerKeyDownAction(key=">")],"up": [ComputerKeyUpAction(key=">")]}),
                MultiControllerButtonAction(buttons=["dpad_up", "shoulder_l", "dpad_right"],actions={"down": [ComputerKeyDownAction(key="?")],"up": [ComputerKeyUpAction(key="?")]}),
                MultiControllerButtonAction(buttons=["shoulder_r", "dpad_down", "dpad_right"],actions={"down": [ComputerKeyDownAction(key="@")],"up": [ComputerKeyUpAction(key="@")]}),
                MultiControllerButtonAction(buttons=["shoulder_r", "dpad_left", "shoulder_l"],actions={"down": [ComputerKeyDownAction(key="[")],"up": [ComputerKeyUpAction(key="[")]}),
                MultiControllerButtonAction(buttons=["shoulder_r", "dpad_down", "shoulder_l"],actions={"down": [ComputerKeyDownAction(key="\\")],"up": [ComputerKeyUpAction(key="\\")]}),
                MultiControllerButtonAction(buttons=["face_left", "shoulder_r", "trigger_l"],actions={"down": [ComputerKeyDownAction(key="]")],"up": [ComputerKeyUpAction(key="]")]}),
                MultiControllerButtonAction(buttons=["trigger_r", "shoulder_r", "face_down", "face_left"],actions={"down": [ComputerKeyDownAction(key="^")],"up": [ComputerKeyUpAction(key="^")]}),
                MultiControllerButtonAction(buttons=["trigger_l", "dpad_down"],actions={"down": [ComputerKeyDownAction(key="_")],"up": [ComputerKeyUpAction(key="_")]}),
                MultiControllerButtonAction(buttons=["face_down", "dpad_down"],actions={"down": [ComputerKeyDownAction(key="`")],"up": [ComputerKeyUpAction(key="`")]}),
                MultiControllerButtonAction(buttons=["dpad_down", "dpad_right"],actions={"down": [ComputerKeyDownAction(key="{")],"up": [ComputerKeyUpAction(key="{")]}),
                MultiControllerButtonAction(buttons=["face_right", "trigger_r", "shoulder_r", "face_down"],actions={"down": [ComputerKeyDownAction(key="|")],"up": [ComputerKeyUpAction(key="|")]}),
                MultiControllerButtonAction(buttons=["dpad_down", "shoulder_l", "dpad_right"],actions={"down": [ComputerKeyDownAction(key="}")],"up": [ComputerKeyUpAction(key="}")]}),
                MultiControllerButtonAction(buttons=["face_right", "face_down", "dpad_up", "shoulder_l"],actions={"down": [ComputerKeyDownAction(key="~")],"up": [ComputerKeyUpAction(key="~")]}),
                MultiControllerButtonAction(buttons=["trigger_r", "shoulder_r", "face_right", "dpad_right"],actions={"down": [ComputerKeyDownAction(key="\u00b0")],"up": [ComputerKeyUpAction(key="\u00b0")]}),
                MultiControllerButtonAction(buttons=["trigger_r", "face_down", "face_left"],actions={"down": [ComputerKeyDownAction(key="\u00df")],"up": [ComputerKeyUpAction(key="\u00df")]}),
                MultiControllerButtonAction(buttons=["trigger_r", "face_left", "shoulder_r", "face_down", "shoulder_l"],actions={"down": [ComputerKeyDownAction(key="\u20ac")],"up": [ComputerKeyUpAction(key="\u20ac")]}),
                MultiControllerButtonAction(buttons=["shoulder_r", "dpad_left", "dpad_up"],actions={"down": [ComputerKeyDownAction(key="f1")],"up": [ComputerKeyUpAction(key="f1")]}),
                MultiControllerButtonAction(buttons=["shoulder_r", "shoulder_l", "dpad_right"],actions={"down": [ComputerKeyDownAction(key="f2")],"up": [ComputerKeyUpAction(key="f2")]}),
                MultiControllerButtonAction(buttons=["face_right", "dpad_up"],actions={"down": [ComputerKeyDownAction(key="f5")],"up": [ComputerKeyUpAction(key="f5")]}),
                MultiControllerButtonAction(buttons=["shoulder_r", "face_right", "dpad_up"],actions={"down": [ComputerKeyDownAction(key="f12")],"up": [ComputerKeyUpAction(key="f12")]}),
                MultiControllerButtonAction(buttons=["face_right", "shoulder_r", "face_down", "shoulder_l"],actions={"down": [ComputerKeyDownAction(key="up")],"up": [ComputerKeyUpAction(key="up")]}),
                MultiControllerButtonAction(buttons=["trigger_r", "shoulder_r", "face_right", "shoulder_l"],actions={"down": [ComputerKeyDownAction(key="end")],"up": [ComputerKeyUpAction(key="end")]}),
                MultiControllerButtonAction(buttons=["trigger_r", "face_right", "face_down", "dpad_down"],actions={"down": [ComputerKeyDownAction(key="menu")],"up": [ComputerKeyUpAction(key="menu")]}),
                MultiControllerButtonAction(buttons=["face_right", "face_down", "shoulder_l"],actions={"down": [ComputerKeyDownAction(key="right")],"up": [ComputerKeyUpAction(key="right")]}),
                MultiControllerButtonAction(buttons=["face_right", "face_down", "dpad_up"],actions={"down": [ComputerKeyDownAction(key="delete")],"up": [ComputerKeyUpAction(key="delete")]}),
                MultiControllerButtonAction(buttons=["face_right", "shoulder_r", "face_down"],actions={"down": [ComputerKeyDownAction(key="tab")],"up": [ComputerKeyUpAction(key="tab")]}),
                MultiControllerButtonAction(buttons=["shoulder_r", "dpad_up", "shoulder_l"],actions={"down": [ComputerKeyDownAction(key="esc")],"up": [ComputerKeyUpAction(key="esc")]}),
                MultiControllerButtonAction(buttons=["face_right", "face_up", "shoulder_l"],actions={"down": [ComputerKeyDownAction(key="pos1")],"up": [ComputerKeyUpAction(key="pos1")]}),
                MultiControllerButtonAction(buttons=["face_right", "face_down"],actions={"down": [ComputerKeyDownAction(key="left")],"up": [ComputerKeyUpAction(key="left")]}),
                MultiControllerButtonAction(buttons=["shoulder_r", "shoulder_l"],actions={"down": [ComputerKeyDownAction(key="backspace")],"up": [ComputerKeyUpAction(key="backspace")]}),
                MultiControllerButtonAction(buttons=["shoulder_r", "dpad_up"],actions={"down": [ComputerKeyDownAction(key="down")],"up": [ComputerKeyUpAction(key="down")]}),
                MultiControllerButtonAction(buttons=["shoulder_r"],actions={"down": [ComputerKeyDownAction(key="enter")],"up": [ComputerKeyUpAction(key="enter")]}),
                MultiControllerButtonAction(buttons=["shoulder_l"],actions={"down": [ComputerKeyDownAction(key="space")],"up": [ComputerKeyUpAction(key="space")]}),
                MultiControllerButtonAction(buttons=["trigger_l", "shoulder_l", "dpad_right"],actions={"down": [ComputerKeyDownAction(key="ctrl"), ComputerKeyDownAction(key="a")],"up": [ComputerKeyUpAction(key="ctrl"), ComputerKeyUpAction(key="a")]}),
                MultiControllerButtonAction(buttons=["face_right", "dpad_right", "trigger_l", "face_down", "shoulder_l"],actions={"down": [ComputerKeyDownAction(key="ctrl"), ComputerKeyDownAction(key="b")],"up": [ComputerKeyUpAction(key="ctrl"), ComputerKeyUpAction(key="b")]}),
                MultiControllerButtonAction(buttons=["shoulder_r", "dpad_right"],actions={"down": [ComputerKeyDownAction(key="ctrl"), ComputerKeyDownAction(key="c")],"up": [ComputerKeyUpAction(key="ctrl"), ComputerKeyUpAction(key="c")]}),
                MultiControllerButtonAction(buttons=["trigger_r", "shoulder_r", "dpad_left", "trigger_l"],actions={"down": [ComputerKeyDownAction(key="ctrl"), ComputerKeyDownAction(key="d")],"up": [ComputerKeyUpAction(key="ctrl"), ComputerKeyUpAction(key="d")]}),
                MultiControllerButtonAction(buttons=["face_right", "face_down", "dpad_down", "dpad_right"],actions={"down": [ComputerKeyDownAction(key="ctrl"), ComputerKeyDownAction(key="e")],"up": [ComputerKeyUpAction(key="ctrl"), ComputerKeyUpAction(key="e")]}),
                MultiControllerButtonAction(buttons=["trigger_l", "shoulder_r", "dpad_up"],actions={"down": [ComputerKeyDownAction(key="ctrl"), ComputerKeyDownAction(key="f")],"up": [ComputerKeyUpAction(key="ctrl"), ComputerKeyUpAction(key="f")]}),
                MultiControllerButtonAction(buttons=["trigger_r", "face_up", "face_left"],actions={"down": [ComputerKeyDownAction(key="ctrl"), ComputerKeyDownAction(key="h")],"up": [ComputerKeyUpAction(key="ctrl"), ComputerKeyUpAction(key="h")]}),
                MultiControllerButtonAction(buttons=["trigger_l", "face_up", "shoulder_l"],actions={"down": [ComputerKeyDownAction(key="ctrl"), ComputerKeyDownAction(key="i")],"up": [ComputerKeyUpAction(key="ctrl"), ComputerKeyUpAction(key="i")]}),
                MultiControllerButtonAction(buttons=["shoulder_r", "trigger_l", "dpad_right"],actions={"down": [ComputerKeyDownAction(key="ctrl"), ComputerKeyDownAction(key="k")],"up": [ComputerKeyUpAction(key="ctrl"), ComputerKeyUpAction(key="k")]}),
                MultiControllerButtonAction(buttons=["trigger_l", "face_up", "dpad_right"],actions={"down": [ComputerKeyDownAction(key="ctrl"), ComputerKeyDownAction(key="l")],"up": [ComputerKeyUpAction(key="ctrl"), ComputerKeyUpAction(key="l")]}),
                MultiControllerButtonAction(buttons=["trigger_r", "trigger_l", "shoulder_l", "dpad_right"],actions={"down": [ComputerKeyDownAction(key="ctrl"), ComputerKeyDownAction(key="n")],"up": [ComputerKeyUpAction(key="ctrl"), ComputerKeyUpAction(key="n")]}),
                MultiControllerButtonAction(buttons=["face_right", "trigger_l", "face_down"],actions={"down": [ComputerKeyDownAction(key="ctrl"), ComputerKeyDownAction(key="s")],"up": [ComputerKeyUpAction(key="ctrl"), ComputerKeyUpAction(key="s")]}),
                MultiControllerButtonAction(buttons=["trigger_r", "shoulder_l", "dpad_right"],actions={"down": [ComputerKeyDownAction(key="ctrl"), ComputerKeyDownAction(key="t")],"up": [ComputerKeyUpAction(key="ctrl"), ComputerKeyUpAction(key="t")]}),
                MultiControllerButtonAction(buttons=["trigger_r", "face_right", "shoulder_r", "face_down", "shoulder_l"],actions={"down": [ComputerKeyDownAction(key="ctrl"), ComputerKeyDownAction(key="u")],"up": [ComputerKeyUpAction(key="ctrl"), ComputerKeyUpAction(key="u")]}),
                MultiControllerButtonAction(buttons=["trigger_r", "face_right", "face_down"],actions={"down": [ComputerKeyDownAction(key="ctrl"), ComputerKeyDownAction(key="v")],"up": [ComputerKeyUpAction(key="ctrl"), ComputerKeyUpAction(key="v")]}),
                MultiControllerButtonAction(buttons=["trigger_l", "shoulder_r", "dpad_up", "shoulder_l"],actions={"down": [ComputerKeyDownAction(key="ctrl"), ComputerKeyDownAction(key="w")],"up": [ComputerKeyUpAction(key="ctrl"), ComputerKeyUpAction(key="w")]}),
                MultiControllerButtonAction(buttons=["trigger_r", "face_right", "face_down", "shoulder_l"],actions={"down": [ComputerKeyDownAction(key="ctrl"), ComputerKeyDownAction(key="x")],"up": [ComputerKeyUpAction(key="ctrl"), ComputerKeyUpAction(key="x")]}),
                MultiControllerButtonAction(buttons=["face_right", "shoulder_r", "face_down", "dpad_down"],actions={"down": [ComputerKeyDownAction(key="ctrl"), ComputerKeyDownAction(key="y")],"up": [ComputerKeyUpAction(key="ctrl"), ComputerKeyUpAction(key="y")]}),
                MultiControllerButtonAction(buttons=["face_right", "face_down", "dpad_down"],actions={"down": [ComputerKeyDownAction(key="ctrl"), ComputerKeyDownAction(key="z")],"up": [ComputerKeyUpAction(key="ctrl"), ComputerKeyUpAction(key="z")]}),
                MultiControllerButtonAction(buttons=["trigger_r", "shoulder_r", "face_up", "trigger_l"],actions={"down": [ComputerKeyDownAction(key="ctrl"), ComputerKeyDownAction(key="f5")],"up": [ComputerKeyUpAction(key="ctrl"), ComputerKeyUpAction(key="f5")]}),
                MultiControllerButtonAction(buttons=["face_right", "shoulder_r", "face_down", "trigger_l"],actions={"down": [ComputerKeyDownAction(key="ctrl"), ComputerKeyDownAction(key="right")],"up": [ComputerKeyUpAction(key="ctrl"), ComputerKeyUpAction(key="right")]}),
                MultiControllerButtonAction(buttons=["shoulder_r", "trigger_l", "shoulder_l", "dpad_right"],actions={"down": [ComputerKeyDownAction(key="ctrl"), ComputerKeyDownAction(key="enter")],"up": [ComputerKeyUpAction(key="ctrl"), ComputerKeyUpAction(key="enter")]}),
                MultiControllerButtonAction(buttons=["trigger_r", "shoulder_r", "face_right", "face_up"],actions={"down": [ComputerKeyDownAction(key="ctrl"), ComputerKeyDownAction(key="down")],"up": [ComputerKeyUpAction(key="ctrl"), ComputerKeyUpAction(key="down")]}),
                MultiControllerButtonAction(buttons=["trigger_r", "trigger_l", "face_right", "face_up"],actions={"down": [ComputerKeyDownAction(key="ctrl"), ComputerKeyDownAction(key="menu")],"up": [ComputerKeyUpAction(key="ctrl"), ComputerKeyUpAction(key="menu")]}),
                MultiControllerButtonAction(buttons=["trigger_r", "dpad_up", "shoulder_l"],actions={"down": [ComputerKeyDownAction(key="ctrl"), ComputerKeyDownAction(key="delete")],"up": [ComputerKeyUpAction(key="ctrl"), ComputerKeyUpAction(key="delete")]}),
                MultiControllerButtonAction(buttons=["trigger_r", "dpad_up"],actions={"down": [ComputerKeyDownAction(key="ctrl"), ComputerKeyDownAction(key="left")],"up": [ComputerKeyUpAction(key="ctrl"), ComputerKeyUpAction(key="left")]}),
                MultiControllerButtonAction(buttons=["shoulder_r", "dpad_down"],actions={"down": [ComputerKeyDownAction(key="ctrl"), ComputerKeyDownAction(key="backspace")],"up": [ComputerKeyUpAction(key="ctrl"), ComputerKeyUpAction(key="backspace")]}),
                MultiControllerButtonAction(buttons=["face_up", "dpad_up"],actions={"down": [ComputerKeyDownAction(key="ctrl"), ComputerKeyDownAction(key="space")],"up": [ComputerKeyUpAction(key="ctrl"), ComputerKeyUpAction(key="space")]}),
                MultiControllerButtonAction(buttons=["face_up", "dpad_right"],actions={"down": [ComputerKeyDownAction(key="ctrl"), ComputerKeyDownAction(key="tab")],"up": [ComputerKeyUpAction(key="ctrl"), ComputerKeyUpAction(key="tab")]}),
                MultiControllerButtonAction(buttons=["face_left", "trigger_l", "face_up"],actions={"down": [ComputerKeyDownAction(key="ctrl"), ComputerKeyDownAction(key="shift"), ComputerKeyDownAction(key="a")],"up": [ComputerKeyUpAction(key="ctrl"), ComputerKeyUpAction(key="shift"), ComputerKeyUpAction(key="a")]}),
                MultiControllerButtonAction(buttons=["trigger_r", "trigger_l", "face_down", "shoulder_l"],actions={"down": [ComputerKeyDownAction(key="ctrl"), ComputerKeyDownAction(key="shift"), ComputerKeyDownAction(key="c")],"up": [ComputerKeyUpAction(key="ctrl"), ComputerKeyUpAction(key="shift"), ComputerKeyUpAction(key="c")]}),
                MultiControllerButtonAction(buttons=["face_right", "dpad_up", "shoulder_l"],actions={"down": [ComputerKeyDownAction(key="ctrl"), ComputerKeyDownAction(key="shift"), ComputerKeyDownAction(key="d")],"up": [ComputerKeyUpAction(key="ctrl"), ComputerKeyUpAction(key="shift"), ComputerKeyUpAction(key="d")]}),
                MultiControllerButtonAction(buttons=["trigger_r", "shoulder_r", "trigger_l", "shoulder_l"],actions={"down": [ComputerKeyDownAction(key="ctrl"), ComputerKeyDownAction(key="shift"), ComputerKeyDownAction(key="e")],"up": [ComputerKeyUpAction(key="ctrl"), ComputerKeyUpAction(key="shift"), ComputerKeyUpAction(key="e")]}),
                MultiControllerButtonAction(buttons=["trigger_r", "trigger_l", "dpad_up"],actions={"down": [ComputerKeyDownAction(key="ctrl"), ComputerKeyDownAction(key="shift"), ComputerKeyDownAction(key="f")],"up": [ComputerKeyUpAction(key="ctrl"), ComputerKeyUpAction(key="shift"), ComputerKeyUpAction(key="f")]}),
                MultiControllerButtonAction(buttons=["face_left", "shoulder_r", "face_up", "shoulder_l"],actions={"down": [ComputerKeyDownAction(key="ctrl"), ComputerKeyDownAction(key="shift"), ComputerKeyDownAction(key="g")],"up": [ComputerKeyUpAction(key="ctrl"), ComputerKeyUpAction(key="shift"), ComputerKeyUpAction(key="g")]}),
                MultiControllerButtonAction(buttons=["trigger_r", "shoulder_r", "face_up", "face_left"],actions={"down": [ComputerKeyDownAction(key="ctrl"), ComputerKeyDownAction(key="shift"), ComputerKeyDownAction(key="h")],"up": [ComputerKeyUpAction(key="ctrl"), ComputerKeyUpAction(key="shift"), ComputerKeyUpAction(key="h")]}),
                MultiControllerButtonAction(buttons=["trigger_r", "face_right", "face_down", "dpad_up"],actions={"down": [ComputerKeyDownAction(key="ctrl"), ComputerKeyDownAction(key="shift"), ComputerKeyDownAction(key="j")],"up": [ComputerKeyUpAction(key="ctrl"), ComputerKeyUpAction(key="shift"), ComputerKeyUpAction(key="j")]}),
                MultiControllerButtonAction(buttons=["face_right", "shoulder_r", "face_down", "dpad_up"],actions={"down": [ComputerKeyDownAction(key="ctrl"), ComputerKeyDownAction(key="shift"), ComputerKeyDownAction(key="k")],"up": [ComputerKeyUpAction(key="ctrl"), ComputerKeyUpAction(key="shift"), ComputerKeyUpAction(key="k")]}),
                MultiControllerButtonAction(buttons=["shoulder_r", "face_up", "dpad_right"],actions={"down": [ComputerKeyDownAction(key="ctrl"), ComputerKeyDownAction(key="shift"), ComputerKeyDownAction(key="l")],"up": [ComputerKeyUpAction(key="ctrl"), ComputerKeyUpAction(key="shift"), ComputerKeyUpAction(key="l")]}),
                MultiControllerButtonAction(buttons=["shoulder_r", "dpad_down", "trigger_l"],actions={"down": [ComputerKeyDownAction(key="ctrl"), ComputerKeyDownAction(key="shift"), ComputerKeyDownAction(key="s")],"up": [ComputerKeyUpAction(key="ctrl"), ComputerKeyUpAction(key="shift"), ComputerKeyUpAction(key="s")]}),
                MultiControllerButtonAction(buttons=["face_right", "shoulder_r", "dpad_up", "face_down", "shoulder_l"],actions={"down": [ComputerKeyDownAction(key="ctrl"), ComputerKeyDownAction(key="shift"), ComputerKeyDownAction(key="v")],"up": [ComputerKeyUpAction(key="ctrl"), ComputerKeyUpAction(key="shift"), ComputerKeyUpAction(key="v")]}),
                MultiControllerButtonAction(buttons=["face_right", "shoulder_r", "face_down", "dpad_down", "shoulder_l"],actions={"down": [ComputerKeyDownAction(key="ctrl"), ComputerKeyDownAction(key="shift"), ComputerKeyDownAction(key="backspace")],"up": [ComputerKeyUpAction(key="ctrl"), ComputerKeyUpAction(key="shift"), ComputerKeyUpAction(key="backspace")]}),
                MultiControllerButtonAction(buttons=["trigger_r", "dpad_left", "dpad_up"],actions={"down": [ComputerKeyDownAction(key="ctrl"), ComputerKeyDownAction(key="shift"), ComputerKeyDownAction(key="end")],"up": [ComputerKeyUpAction(key="ctrl"), ComputerKeyUpAction(key="shift"), ComputerKeyUpAction(key="end")]}),
                MultiControllerButtonAction(buttons=["trigger_r", "dpad_down"],actions={"down": [ComputerKeyDownAction(key="ctrl"), ComputerKeyDownAction(key="shift"), ComputerKeyDownAction(key="left")],"up": [ComputerKeyUpAction(key="ctrl"), ComputerKeyUpAction(key="shift"), ComputerKeyUpAction(key="left")]}),
                MultiControllerButtonAction(buttons=["trigger_r", "dpad_right"],actions={"down": [ComputerKeyDownAction(key="ctrl"), ComputerKeyDownAction(key="shift"), ComputerKeyDownAction(key="right")],"up": [ComputerKeyUpAction(key="ctrl"), ComputerKeyUpAction(key="shift"), ComputerKeyUpAction(key="right")]}),
                MultiControllerButtonAction(buttons=["trigger_r", "trigger_l", "face_right", "shoulder_l"],actions={"down": [ComputerKeyDownAction(key="ctrl"), ComputerKeyDownAction(key="cmd"), ComputerKeyDownAction(key="left")],"up": [ComputerKeyUpAction(key="ctrl"), ComputerKeyUpAction(key="cmd"), ComputerKeyUpAction(key="left")]}),
                MultiControllerButtonAction(buttons=["face_right", "dpad_left", "dpad_up"],actions={"down": [ComputerKeyDownAction(key="ctrl"), ComputerKeyDownAction(key="cmd"), ComputerKeyDownAction(key="right")],"up": [ComputerKeyUpAction(key="ctrl"), ComputerKeyUpAction(key="cmd"), ComputerKeyUpAction(key="right")]}),
                MultiControllerButtonAction(buttons=["face_right", "shoulder_r", "trigger_l", "face_down", "shoulder_l"],actions={"down": [ComputerKeyDownAction(key="shift"), ComputerKeyDownAction(key="tab")],"up": [ComputerKeyUpAction(key="shift"), ComputerKeyUpAction(key="tab")]}),
                MultiControllerButtonAction(buttons=["face_right", "trigger_l", "face_down", "shoulder_l"],actions={"down": [ComputerKeyDownAction(key="shift"), ComputerKeyDownAction(key="up")],"up": [ComputerKeyUpAction(key="shift"), ComputerKeyUpAction(key="up")]}),
                MultiControllerButtonAction(buttons=["trigger_r", "shoulder_r", "face_down", "trigger_l"],actions={"down": [ComputerKeyDownAction(key="shift"), ComputerKeyDownAction(key="backspace")],"up": [ComputerKeyUpAction(key="shift"), ComputerKeyUpAction(key="backspace")]}),
                MultiControllerButtonAction(buttons=["face_right", "shoulder_r", "face_down", "dpad_right"],actions={"down": [ComputerKeyDownAction(key="shift"), ComputerKeyDownAction(key="right")],"up": [ComputerKeyUpAction(key="shift"), ComputerKeyUpAction(key="right")]}),
                MultiControllerButtonAction(buttons=["face_right", "face_down", "dpad_down", "shoulder_l"],actions={"down": [ComputerKeyDownAction(key="shift"), ComputerKeyDownAction(key="end")],"up": [ComputerKeyUpAction(key="shift"), ComputerKeyUpAction(key="end")]}),
                MultiControllerButtonAction(buttons=["face_left", "face_up", "shoulder_l"],actions={"down": [ComputerKeyDownAction(key="shift"), ComputerKeyDownAction(key="left")],"up": [ComputerKeyUpAction(key="shift"), ComputerKeyUpAction(key="left")]}),
                MultiControllerButtonAction(buttons=["trigger_l", "face_down", "shoulder_l"],actions={"down": [ComputerKeyDownAction(key="shift"), ComputerKeyDownAction(key="space")],"up": [ComputerKeyUpAction(key="shift"), ComputerKeyUpAction(key="space")]}),
                MultiControllerButtonAction(buttons=["face_right", "face_down", "dpad_right"],actions={"down": [ComputerKeyDownAction(key="shift"), ComputerKeyDownAction(key="down")],"up": [ComputerKeyUpAction(key="shift"), ComputerKeyUpAction(key="down")]}),
                MultiControllerButtonAction(buttons=["trigger_l", "dpad_down", "shoulder_l"],actions={"down": [ComputerKeyDownAction(key="shift"), ComputerKeyDownAction(key="enter")],"up": [ComputerKeyUpAction(key="shift"), ComputerKeyUpAction(key="enter")]}),
                MultiControllerButtonAction(buttons=["face_right", "trigger_r", "trigger_l", "face_down"],actions={"down": [ComputerKeyDownAction(key="shift"), ComputerKeyDownAction(key="alt"), ComputerKeyDownAction(key="F")],"up": [ComputerKeyUpAction(key="shift"), ComputerKeyUpAction(key="alt"), ComputerKeyUpAction(key="F")]}),
                MultiControllerButtonAction(buttons=["trigger_r", "dpad_down", "shoulder_l"],actions={"down": [ComputerKeyDownAction(key="shift"), ComputerKeyDownAction(key="alt"), ComputerKeyDownAction(key="down")],"up": [ComputerKeyUpAction(key="shift"), ComputerKeyUpAction(key="alt"), ComputerKeyUpAction(key="down")]}),
                MultiControllerButtonAction(buttons=["trigger_r", "trigger_l", "dpad_up", "shoulder_l"],actions={"down": [ComputerKeyDownAction(key="shift"), ComputerKeyDownAction(key="cmd"), ComputerKeyDownAction(key="S")],"up": [ComputerKeyUpAction(key="shift"), ComputerKeyUpAction(key="cmd"), ComputerKeyUpAction(key="S")]}),
                MultiControllerButtonAction(buttons=["shoulder_r", "face_down", "trigger_l", "shoulder_l"],actions={"down": [ComputerKeyDownAction(key="shift"), ComputerKeyDownAction(key="cmd"), ComputerKeyDownAction(key="right")],"up": [ComputerKeyUpAction(key="shift"), ComputerKeyUpAction(key="cmd"), ComputerKeyUpAction(key="right")]}),
                MultiControllerButtonAction(buttons=["trigger_l", "dpad_left", "dpad_down", "shoulder_l"],actions={"down": [ComputerKeyDownAction(key="shift"), ComputerKeyDownAction(key="cmd"), ComputerKeyDownAction(key="left")],"up": [ComputerKeyUpAction(key="shift"), ComputerKeyUpAction(key="cmd"), ComputerKeyUpAction(key="left")]}),
                MultiControllerButtonAction(buttons=["face_left", "trigger_l", "shoulder_l"],actions={"down": [ComputerKeyDownAction(key="shift"), ComputerKeyDownAction(key="cmd"), ComputerKeyDownAction(key="up")],"up": [ComputerKeyUpAction(key="shift"), ComputerKeyUpAction(key="cmd"), ComputerKeyUpAction(key="up")]}),
                MultiControllerButtonAction(buttons=["face_up", "trigger_l", "face_right", "shoulder_r"],actions={"down": [ComputerKeyDownAction(key="alt"), ComputerKeyDownAction(key="?")],"up": [ComputerKeyUpAction(key="alt"), ComputerKeyUpAction(key="?")]}),
                MultiControllerButtonAction(buttons=["trigger_l", "face_right", "face_up"],actions={"down": [ComputerKeyDownAction(key="alt"), ComputerKeyDownAction(key="f4")],"up": [ComputerKeyUpAction(key="alt"), ComputerKeyUpAction(key="f4")]}),
                MultiControllerButtonAction(buttons=["shoulder_r", "face_down", "dpad_up"],actions={"down": [ComputerKeyDownAction(key="alt"), ComputerKeyDownAction(key="up")],"up": [ComputerKeyUpAction(key="alt"), ComputerKeyUpAction(key="up")]}),
                MultiControllerButtonAction(buttons=["shoulder_r", "face_up", "dpad_up"],actions={"down": [ComputerKeyDownAction(key="alt"), ComputerKeyDownAction(key="tab")],"up": [ComputerKeyUpAction(key="alt"), ComputerKeyUpAction(key="tab")]}),
                MultiControllerButtonAction(buttons=["face_down", "dpad_up"],actions={"down": [ComputerKeyDownAction(key="alt"), ComputerKeyDownAction(key="down")],"up": [ComputerKeyUpAction(key="alt"), ComputerKeyUpAction(key="down")]}),
                MultiControllerButtonAction(buttons=["face_right", "shoulder_l", "dpad_right"],actions={"down": [ComputerKeyDownAction(key="cmd"), ComputerKeyDownAction(key="e")],"up": [ComputerKeyUpAction(key="cmd"), ComputerKeyUpAction(key="e")]}),
                MultiControllerButtonAction(buttons=["shoulder_r", "face_right", "dpad_right"],actions={"down": [ComputerKeyDownAction(key="cmd"), ComputerKeyDownAction(key="k")],"up": [ComputerKeyUpAction(key="cmd"), ComputerKeyUpAction(key="k")]}),
                MultiControllerButtonAction(buttons=["face_right", "dpad_right"],actions={"down": [ComputerKeyDownAction(key="cmd"), ComputerKeyDownAction(key="l")],"up": [ComputerKeyUpAction(key="cmd"), ComputerKeyUpAction(key="l")]}),
                MultiControllerButtonAction(buttons=["trigger_r", "face_right", "shoulder_r", "trigger_l", "face_down"],actions={"down": [ComputerKeyDownAction(key="cmd"), ComputerKeyDownAction(key="p")],"up": [ComputerKeyUpAction(key="cmd"), ComputerKeyUpAction(key="p")]}),
                MultiControllerButtonAction(buttons=["trigger_r", "trigger_l", "face_up", "shoulder_l"],actions={"down": [ComputerKeyDownAction(key="cmd"), ComputerKeyDownAction(key="r")],"up": [ComputerKeyUpAction(key="cmd"), ComputerKeyUpAction(key="r")]}),
                MultiControllerButtonAction(buttons=["face_right", "shoulder_r", "dpad_up", "trigger_l", "face_down"],actions={"down": [ComputerKeyDownAction(key="cmd"), ComputerKeyDownAction(key="tab")],"up": [ComputerKeyUpAction(key="cmd"), ComputerKeyUpAction(key="tab")]}),
                MultiControllerButtonAction(buttons=["shoulder_r", "face_up", "trigger_l", "shoulder_l"],actions={"down": [ComputerKeyDownAction(key="cmd"), ComputerKeyDownAction(key="up")],"up": [ComputerKeyUpAction(key="cmd"), ComputerKeyUpAction(key="up")]}),
                MultiControllerButtonAction(buttons=["trigger_l", "dpad_left", "shoulder_r", "dpad_up"],actions={"down": [ComputerKeyDownAction(key="cmd"), ComputerKeyDownAction(key="end")],"up": [ComputerKeyUpAction(key="cmd"), ComputerKeyUpAction(key="end")]}),
                MultiControllerButtonAction(buttons=["face_left", "shoulder_r", "face_up", "trigger_l"],actions={"down": [ComputerKeyDownAction(key="cmd"), ComputerKeyDownAction(key="space")],"up": [ComputerKeyUpAction(key="cmd"), ComputerKeyUpAction(key="space")]}),
                MultiControllerButtonAction(buttons=["face_left", "trigger_l", "face_down"],actions={"down": [ComputerKeyDownAction(key="cmd"), ComputerKeyDownAction(key="pos1")],"up": [ComputerKeyUpAction(key="cmd"), ComputerKeyUpAction(key="pos1")]}),
                MultiControllerButtonAction(buttons=["face_right", "dpad_up", "dpad_right"],actions={"down": [ComputerKeyDownAction(key="cmd"), ComputerKeyDownAction(key="right")],"up": [ComputerKeyUpAction(key="cmd"), ComputerKeyUpAction(key="right")]}),
                MultiControllerButtonAction(buttons=["trigger_r", "face_up", "shoulder_l"],actions={"down": [ComputerKeyDownAction(key="="), ComputerKeyDownAction(key="space")],"up": [ComputerKeyUpAction(key="="), ComputerKeyUpAction(key="space")]}),
                MultiControllerButtonAction(buttons=["trigger_r", "trigger_l", "face_left"],actions={"down": [ComputerKeyDownAction(key="i"), ComputerKeyDownAction(key="o"), ComputerKeyDownAction(key="n")],"up": [ComputerKeyUpAction(key="i"), ComputerKeyUpAction(key="o"), ComputerKeyUpAction(key="n")]}),
                MultiControllerButtonAction(buttons=["trigger_l", "dpad_up", "shoulder_l"],actions={"down": [ComputerKeyDownAction(key="e"), ComputerKeyDownAction(key="n")],"up": [ComputerKeyUpAction(key="e"), ComputerKeyUpAction(key="n")]}),
                MultiControllerButtonAction(buttons=["shoulder_r", "trigger_l", "shoulder_l"],actions={"down": [ComputerKeyDownAction(key="e"), ComputerKeyDownAction(key="space")],"up": [ComputerKeyUpAction(key="e"), ComputerKeyUpAction(key="space")]}),
                MultiControllerButtonAction(buttons=["trigger_r", "shoulder_r", "face_left"],actions={"down": [ComputerKeyDownAction(key="s"), ComputerKeyDownAction(key="t")],"up": [ComputerKeyUpAction(key="s"), ComputerKeyUpAction(key="t")]}),
                MultiControllerButtonAction(buttons=["trigger_r", "shoulder_r", "face_right"],actions={"down": [ComputerKeyDownAction(key="a"), ComputerKeyDownAction(key="t")],"up": [ComputerKeyUpAction(key="a"), ComputerKeyUpAction(key="t")]}),
                MultiControllerButtonAction(buttons=["dpad_left", "dpad_up", "shoulder_l"],actions={"down": [ComputerKeyDownAction(key="a"), ComputerKeyDownAction(key="n")],"up": [ComputerKeyUpAction(key="a"), ComputerKeyUpAction(key="n")]}),
                MultiControllerButtonAction(buttons=["trigger_r", "trigger_l", "face_down"],actions={"down": [ComputerKeyDownAction(key="s"), ComputerKeyDownAction(key="space")],"up": [ComputerKeyUpAction(key="s"), ComputerKeyUpAction(key="space")]}),
                MultiControllerButtonAction(buttons=["trigger_r", "shoulder_r", "trigger_l"],actions={"down": [ComputerKeyDownAction(key="a"), ComputerKeyDownAction(key="l")],"up": [ComputerKeyUpAction(key="a"), ComputerKeyUpAction(key="l")]}),
                MultiControllerButtonAction(buttons=["trigger_l", "dpad_left", "shoulder_l"],actions={"down": [ComputerKeyDownAction(key="l"), ComputerKeyDownAction(key="e")],"up": [ComputerKeyUpAction(key="l"), ComputerKeyUpAction(key="e")]}),
                MultiControllerButtonAction(buttons=["trigger_l", "dpad_left", "dpad_down"],actions={"down": [ComputerKeyDownAction(key="a"), ComputerKeyDownAction(key="r")],"up": [ComputerKeyUpAction(key="a"), ComputerKeyUpAction(key="r")]}),
                MultiControllerButtonAction(buttons=["trigger_r", "trigger_l", "shoulder_l"],actions={"down": [ComputerKeyDownAction(key="t"), ComputerKeyDownAction(key="space")],"up": [ComputerKeyUpAction(key="t"), ComputerKeyUpAction(key="space")]}),
                MultiControllerButtonAction(buttons=["face_left", "trigger_l"],actions={"down": [ComputerKeyDownAction(key=";"), ComputerKeyDownAction(key="enter")],"up": [ComputerKeyUpAction(key=";"), ComputerKeyUpAction(key="enter")]}),
                MultiControllerButtonAction(buttons=["trigger_l", "dpad_right"],actions={"down": [ComputerKeyDownAction(key="i"), ComputerKeyDownAction(key="n")],"up": [ComputerKeyUpAction(key="i"), ComputerKeyUpAction(key="n")]}),
                MultiControllerButtonAction(buttons=["dpad_left", "dpad_up"],actions={"down": [ComputerKeyDownAction(key="o"), ComputerKeyDownAction(key="n")],"up": [ComputerKeyUpAction(key="o"), ComputerKeyUpAction(key="n")]}),
                MultiControllerButtonAction(buttons=["face_right", "face_up"],actions={"down": [ComputerKeyDownAction(key="t"), ComputerKeyDownAction(key="h")],"up": [ComputerKeyUpAction(key="t"), ComputerKeyUpAction(key="h")]}),
                MultiControllerButtonAction(buttons=["trigger_l", "dpad_up"],actions={"down": [ComputerKeyDownAction(key="e"), ComputerKeyDownAction(key="r")],"up": [ComputerKeyUpAction(key="e"), ComputerKeyUpAction(key="r")]}),
                MultiControllerButtonAction(buttons=["trigger_l", "dpad_left"],actions={"down": [ComputerKeyDownAction(key="r"), ComputerKeyDownAction(key="e")],"up": [ComputerKeyUpAction(key="r"), ComputerKeyUpAction(key="e")]}),
                MultiControllerButtonAction(buttons=["dpad_up", "dpad_right"],actions={"down": [ComputerKeyDownAction(key="o"), ComputerKeyDownAction(key="r")],"up": [ComputerKeyUpAction(key="o"), ComputerKeyUpAction(key="r")]}),
                MultiControllerButtonAction(buttons=["trigger_r", "trigger_l"],actions={"down": [ComputerKeyDownAction(key=","), ComputerKeyDownAction(key="space")],"up": [ComputerKeyUpAction(key=","), ComputerKeyUpAction(key="space")]})
            ],
        ),
    },
)


if __name__ == "__main__":
    default_config_string = default_config.model_dump_json(indent=4)
    new_config = Config.model_validate_json(default_config_string)
    assert (
        default_config.model_dump() == new_config.model_dump()
    ), "Default config is not valid!"
    print("Default config is valid!")
