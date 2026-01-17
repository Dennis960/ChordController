import os


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


def get_resource_path(relative_path: str) -> str:
    """
    Returns the absolute path to a resource given its relative path
    from the resources directory.
    """
    return os.path.join(CURRENT_DIR, relative_path)


class OutlineResources:
    l = get_resource_path("outline/L.png")
    r = get_resource_path("outline/R.png")
    zl = get_resource_path("outline/ZL.png")
    zr = get_resource_path("outline/ZR.png")
    dpad_none = get_resource_path("outline/Pro D-Pad.png")
    dpad_none_256 = get_resource_path("outline/Pro D-Pad256.png")
    face_none = get_resource_path("outline/Face-Buttons.png")
    stick_left_movement = get_resource_path("outline/Left Stick All.png")
    stick_right_movement = get_resource_path("outline/Right Stick All.png")
    stick_left = get_resource_path("outline/Left Stick Click.png")
    stick_right = get_resource_path("outline/Right Stick Click.png")
    minus = get_resource_path("outline/Minus.png")
    plus = get_resource_path("outline/Plus.png")
    home = get_resource_path("outline/Home.png")
    capture = get_resource_path("outline/Capture.png")
    a = get_resource_path("outline/A.png")
    b = get_resource_path("outline/B.png")
    x = get_resource_path("outline/X.png")
    y = get_resource_path("outline/Y.png")


class SolidResources:
    l = get_resource_path("solid/L.png")
    r = get_resource_path("solid/R.png")
    zl = get_resource_path("solid/ZL.png")
    zr = get_resource_path("solid/ZR.png")
    dpad_up = get_resource_path("solid/Pro D-Pad Up.png")
    dpad_right = get_resource_path("solid/Pro D-Pad Right.png")
    dpad_down = get_resource_path("solid/Pro D-Pad Down.png")
    dpad_left = get_resource_path("solid/Pro D-Pad Left.png")
    dpad_up_right = get_resource_path("solid/Pro D-Pad Up Right.png")
    dpad_up_left = get_resource_path("solid/Pro D-Pad Up Left.png")
    dpad_down_right = get_resource_path("solid/Pro D-Pad Down Right.png")
    dpad_down_left = get_resource_path("solid/Pro D-Pad Down Left.png")
    dpad_up_256 = get_resource_path("solid/Pro D-Pad Up256.png")
    dpad_right_256 = get_resource_path("solid/Pro D-Pad Right256.png")
    dpad_down_256 = get_resource_path("solid/Pro D-Pad Down256.png")
    dpad_left_256 = get_resource_path("solid/Pro D-Pad Left256.png")
    face_up = get_resource_path("solid/Face-Buttons-Up.png")
    face_right = get_resource_path("solid/Face-Buttons-Right.png")
    face_down = get_resource_path("solid/Face-Buttons-Down.png")
    face_left = get_resource_path("solid/Face-Buttons-Left.png")
    face_up_right = get_resource_path("solid/Face-Buttons-Up-Right.png")
    face_up_left = get_resource_path("solid/Face-Buttons-Up-Left.png")
    face_down_right = get_resource_path("solid/Face-Buttons-Down-Right.png")
    face_down_left = get_resource_path("solid/Face-Buttons-Down-Left.png")
    minus = get_resource_path("solid/Minus.png")
    plus = get_resource_path("solid/Plus.png")
    home = get_resource_path("solid/Home.png")
    capture = get_resource_path("solid/Capture.png")
    a = get_resource_path("solid/A.png")
    b = get_resource_path("solid/B.png")
    x = get_resource_path("solid/X.png")
    y = get_resource_path("solid/Y.png")


outline_images = OutlineResources()
solid_images = SolidResources()
