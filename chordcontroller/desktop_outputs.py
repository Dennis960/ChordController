from pynput.keyboard import Controller as KeyboardController, Key
from pynput.mouse import Controller as MouseController, Button
import subprocess
import sys
import os
from chordcontroller.config import KeyboardKey, MouseButtonName


def string_to_pynput_compatible(key: KeyboardKey) -> Key | str:
    """Convert a string to a pynput compatible key."""
    if key == "space":
        return Key.space
    elif key == "enter":
        return Key.enter
    elif key == "tab":
        return Key.tab
    elif key == "backspace":
        return Key.backspace
    elif key == "delete":
        return Key.delete
    elif key == "alt":
        return Key.alt
    elif key == "ctrl":
        return Key.ctrl
    elif key == "shift":
        return Key.shift
    elif key == "cmd":
        return Key.cmd
    elif key == "up":
        return Key.up
    elif key == "down":
        return Key.down
    elif key == "left":
        return Key.left
    elif key == "right":
        return Key.right
    elif key == "esc":
        return Key.esc
    elif key == "pos1":
        return Key.home
    elif key == "end":
        return Key.end
    elif key.startswith("f") and key[1:].isdigit():
        f_key_number = int(key[1:])
        if 1 <= f_key_number <= 24:
            return getattr(Key, f"f{f_key_number}")
        else:
            return key
    elif key == "menu":
        return Key.menu
    else:
        return key


MODIFIERS: list[KeyboardKey] = ["shift", "ctrl", "alt", "cmd"]
SPECIAL_KEYS: list[KeyboardKey] = [
    "space",
    "enter",
    "tab",
    "backspace",
    "alt",
    "ctrl",
    "shift",
    "cmd",
    "up",
    "down",
    "left",
    "right",
    "esc",
    "pos1",
    "end",
]

has_xdotool = False


def check_xdotool_installation():
    global has_xdotool
    if has_xdotool:
        return

    if sys.platform == "linux":
        try:
            subprocess.run(["xdotool", "--version"], check=True)
            has_xdotool = True
        except Exception:
            print(
                "xdotool not found. Please install for better special character typing support by running 'sudo apt install xdotool'"
            )


class Keyboard:
    def __init__(self):
        check_xdotool_installation()
        self.keyboard = KeyboardController()

    def type(self, text: str):
        if os.name == "nt":
            # Windows has problems typing ^ and ´
            if "´" in text or "^" in text:
                # add a space after the character to avoid issues
                text = text.replace("´", "´ ").replace("^", "^ ")
        self.keyboard.type(text)

    def press(self, key: KeyboardKey):
        if key in MODIFIERS or key in SPECIAL_KEYS or not has_xdotool:
            self.keyboard.press(string_to_pynput_compatible(key))
        else:
            subprocess.run(["xdotool", "type", key])

    def release(self, key: KeyboardKey):
        if key in MODIFIERS or key in SPECIAL_KEYS or not has_xdotool:
            self.keyboard.release(string_to_pynput_compatible(key))


class Mouse:
    def __init__(self):
        self.mouse = MouseController()

    def press(self, button_name: MouseButtonName):
        if button_name == "left":
            button = Button.left
        elif button_name == "middle":
            button = Button.middle
        elif button_name == "right":
            button = Button.right
        self.mouse.press(button)

    def release(self, button_name: MouseButtonName):
        if button_name == "left":
            button = Button.left
        elif button_name == "middle":
            button = Button.middle
        elif button_name == "right":
            button = Button.right
        self.mouse.release(button)

    def move(self, x: int, y: int):
        if x != 0 or y != 0:
            self.mouse.move(x, y)

    def scroll(self, x: int, y: int):
        if x != 0 or y != 0:
            self.mouse.scroll(x, y)


if __name__ == "__main__":
    keyboard = Keyboard()
    keyboard.type(
        "1234567890ß!\"$%&/()=?'+#-.,*'_:;<>|{[]}\\~@€^`°qwertzuiopüasdfghjklöäyxcvbnmQWERTZUIOPÜASDFGHJKLÖÄYXCVBNM \n\t"
    )
    keyboard.press("shift")
    keyboard.type("qwertzuiopüasdfghjklöäyxcvbnm")
    keyboard.release("shift")
