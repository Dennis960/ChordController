from __future__ import annotations

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QLabel, QWidget

from chordcontroller.config import ControllerButtonName
from chordcontroller.resources import solid_images, outline_images

ICON_SIZE = 64


class SingleButton(QWidget):
    """Small controller button icon widget copied from the experiment UI style."""

    def __init__(self, controller_button_name: ControllerButtonName, scale: float = 1.0, parent=None):
        super().__init__(parent)
        self.scale = scale
        self.setFixedSize(int(self.scale * ICON_SIZE), int(self.scale * ICON_SIZE))
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setGeometry(0, 0, int(self.scale * ICON_SIZE), int(self.scale * ICON_SIZE))
        self.label.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.set_state(controller_button_name)

    def set_state(self, controller_button_name: ControllerButtonName) -> None:
        image_path = ""
        if controller_button_name == "minus":
            image_path = solid_images.minus
        elif controller_button_name == "plus":
            image_path = solid_images.plus
        elif controller_button_name == "home":
            image_path = solid_images.home
        elif controller_button_name == "capture":
            image_path = solid_images.capture
        elif controller_button_name == "stick_left":
            image_path = outline_images.stick_left_movement
        elif controller_button_name == "stick_right":
            image_path = outline_images.stick_right_movement
        elif controller_button_name == "shoulder_l":
            image_path = solid_images.l
        elif controller_button_name == "shoulder_r":
            image_path = solid_images.r
        elif controller_button_name == "trigger_l":
            image_path = solid_images.zl
        elif controller_button_name == "trigger_r":
            image_path = solid_images.zr
        elif controller_button_name == "face_up":
            image_path = solid_images.face_up
        elif controller_button_name == "face_right":
            image_path = solid_images.face_right
        elif controller_button_name == "face_down":
            image_path = solid_images.face_down
        elif controller_button_name == "face_left":
            image_path = solid_images.face_left

        icon = QIcon(image_path)
        pixmap = icon.pixmap(
            QSize(int(self.scale * ICON_SIZE), int(self.scale * ICON_SIZE)),
            QIcon.Mode.Normal,
            QIcon.State.Off,
        )
        self.label.setPixmap(pixmap)
