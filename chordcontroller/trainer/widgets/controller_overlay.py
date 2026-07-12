from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import (
    Property,
    QEasingCurve,
    QParallelAnimationGroup,
    QPropertyAnimation,
    QRect,
    Qt,
    Signal,
    Slot,
)
from PySide6.QtGui import QColor, QFont, QImage, QPaintEvent, QPainter
from PySide6.QtWidgets import QWidget

from chordcontroller.config import ControllerButtonName
from chordcontroller.resources import get_resource_path, outline_images, solid_images

CONTROLLER_IMAGE_SCALE = 3


@dataclass
class ButtonImage:
    default: str
    highlighted: str
    icon_size: int = 128


@dataclass
class ButtonSettings:
    position: tuple[int, int]
    image: ButtonImage
    pulse_start_scale: float = 1.1
    pulse_end_scale: float = 1.4
    pulse_duration: int = 200

    def __post_init__(self):
        self.position = (
            int(self.position[0] / CONTROLLER_IMAGE_SCALE),
            int(self.position[1] / CONTROLLER_IMAGE_SCALE),
        )


# Copied and adapted from experiment module implementation.
button_settings: dict[ControllerButtonName, ButtonSettings] = {
    "face_up": ButtonSettings((772, 207), ButtonImage(outline_images.x, solid_images.x)),
    "face_right": ButtonSettings((861, 284), ButtonImage(outline_images.a, solid_images.a)),
    "face_down": ButtonSettings((772, 363), ButtonImage(outline_images.b, solid_images.b)),
    "face_left": ButtonSettings((684, 284), ButtonImage(outline_images.y, solid_images.y)),
    "dpad_up": ButtonSettings((265, 377), ButtonImage(outline_images.dpad_none_256, solid_images.dpad_up_256, 256), pulse_end_scale=1.2),
    "dpad_right": ButtonSettings((265, 377), ButtonImage(outline_images.dpad_none_256, solid_images.dpad_right_256, 256), pulse_end_scale=1.2),
    "dpad_down": ButtonSettings((265, 377), ButtonImage(outline_images.dpad_none_256, solid_images.dpad_down_256, 256), pulse_end_scale=1.2),
    "dpad_left": ButtonSettings((265, 377), ButtonImage(outline_images.dpad_none_256, solid_images.dpad_left_256, 256), pulse_end_scale=1.2),
    "shoulder_l": ButtonSettings((-7, -47), ButtonImage(outline_images.l, solid_images.l, 150)),
    "shoulder_r": ButtonSettings((965, -47), ButtonImage(outline_images.r, solid_images.r, 150)),
    "trigger_l": ButtonSettings((-11, 33), ButtonImage(outline_images.zl, solid_images.zl, 160)),
    "trigger_r": ButtonSettings((956, 33), ButtonImage(outline_images.zr, solid_images.zr, 160)),
    "plus": ButtonSettings((648, 226), ButtonImage(outline_images.plus, solid_images.plus, 74)),
    "minus": ButtonSettings((384, 226), ButtonImage(outline_images.minus, solid_images.minus, 74)),
    "capture": ButtonSettings((444, 310), ButtonImage(outline_images.capture, solid_images.capture, 78)),
    "home": ButtonSettings((570, 304), ButtonImage(outline_images.home, solid_images.home, 92)),
}

joystick_diameter = 38
joystick_left_position = (
    int(255 / CONTROLLER_IMAGE_SCALE - joystick_diameter / 2),
    int(348 / CONTROLLER_IMAGE_SCALE - joystick_diameter / 2),
)
joystick_right_position = (
    int(684 / CONTROLLER_IMAGE_SCALE - joystick_diameter / 2),
    int(505 / CONTROLLER_IMAGE_SCALE - joystick_diameter / 2),
)


class PulseAnimation(QWidget):
    pulse_signal = Signal()
    _pulse_scale = 1.0
    _pulse_opacity = 0.0
    pulse_start_scale: float
    pulse_end_scale: float
    pulse_duration: int

    @Property(float)
    def pulse_scale(self):
        return self._pulse_scale

    @pulse_scale.setter
    def pulse_scale(self, value: float):
        self._pulse_scale = value
        self.update()

    @Property(float)
    def pulse_opacity(self):
        return self._pulse_opacity

    @pulse_opacity.setter
    def pulse_opacity(self, value: float):
        self._pulse_opacity = value
        self.update()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.pulse_signal.connect(self._pulse)

    def reset_opacity(self):
        self._pulse_opacity = 0.0
        self.update()

    @Slot()
    def _pulse(self):
        group = QParallelAnimationGroup(self)

        scale_anim = QPropertyAnimation(self, b"pulse_scale")
        scale_anim.setDuration(self.pulse_duration)
        scale_anim.setStartValue(self.pulse_start_scale)
        scale_anim.setEndValue(self.pulse_end_scale)
        scale_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)

        opacity_anim = QPropertyAnimation(self, b"pulse_opacity")
        opacity_anim.setDuration(self.pulse_duration)
        opacity_anim.setStartValue(1.0)
        opacity_anim.setEndValue(0.0)
        opacity_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        opacity_anim.finished.connect(self.reset_opacity)

        group.addAnimation(scale_anim)
        group.addAnimation(opacity_anim)
        group.start()

    def pulse(self):
        self.pulse_signal.emit()


class ButtonWidget(PulseAnimation):
    highlighted = False
    color: QColor = Qt.GlobalColor.white

    def __init__(self, name: ControllerButtonName, settings: ButtonSettings, parent=None):
        super().__init__(parent)
        self.name = name
        self.settings = settings
        self.setGeometry(
            settings.position[0],
            settings.position[1],
            settings.image.icon_size,
            settings.image.icon_size,
        )
        self.pulse_start_scale = settings.pulse_start_scale
        self.pulse_end_scale = settings.pulse_end_scale
        self.pulse_duration = settings.pulse_duration

    def set_highlighted(self, highlighted):
        self.highlighted = highlighted
        self.update()

    def set_color(self, color: QColor):
        self.color = color
        self.update()

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        image_path = self.settings.image.highlighted if self.highlighted else self.settings.image.default

        original_size = int(self.settings.image.icon_size / CONTROLLER_IMAGE_SCALE)
        scaled_size = int(self.settings.image.icon_size / CONTROLLER_IMAGE_SCALE * self._pulse_scale)

        image = QImage(image_path).scaled(
            original_size,
            original_size,
            Qt.AspectRatioMode.IgnoreAspectRatio,
        )

        if self.color:
            tinted = QImage(image.size(), QImage.Format.Format_ARGB32)
            tinted.fill(Qt.GlobalColor.transparent)
            temp_painter = QPainter(tinted)
            temp_painter.drawImage(0, 0, image)
            temp_painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceAtop)
            temp_painter.fillRect(tinted.rect(), self.color)
            temp_painter.end()
            image = tinted

        pulse_img = QImage(self.settings.image.default).scaled(
            scaled_size,
            scaled_size,
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        painter.save()
        painter.setOpacity(self._pulse_opacity)
        delta_size = original_size - scaled_size
        offset = delta_size // 2
        painter.drawImage(offset, offset, pulse_img)
        painter.restore()
        painter.drawImage(0, 0, image)


class JoystickWidget(ButtonWidget):
    def __init__(self, name: ControllerButtonName, position, diameter, parent=None):
        super().__init__(name, ButtonSettings(position, ButtonImage("", "")), parent)
        self.position = position
        self.diameter = diameter
        self.setGeometry(position[0], position[1], diameter + 1, diameter + 1)

    def move_to(self, x, y):
        scale_factor = 10
        self.move(self.position[0] + x * scale_factor, self.position[1] + y * scale_factor)

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        if self.highlighted:
            painter.setBrush(Qt.GlobalColor.white)
            painter.setPen(Qt.PenStyle.NoPen)
        else:
            pen = painter.pen()
            pen.setWidth(2)
            painter.setPen(pen)
        painter.drawEllipse(0, 0, self.diameter, self.diameter)


class ControllerOverlay(PulseAnimation):
    controller_size = (int(1106 / CONTROLLER_IMAGE_SCALE), int(891 / CONTROLLER_IMAGE_SCALE))
    controller_image = get_resource_path("Controller-Empty.png")
    highlight_color: QColor = QColor("#3b82f6")
    pulse_color: QColor = Qt.GlobalColor.white

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: transparent;")
        self.resize(*self.controller_size)
        self.setMinimumSize(*self.controller_size)
        self.setMaximumSize(*self.controller_size)
        self.title = ""

        self.buttons: dict[ControllerButtonName, ButtonWidget] = {}
        for button_name, settings in button_settings.items():
            self.buttons[button_name] = ButtonWidget(button_name, settings, self)
        self.buttons["stick_left"] = JoystickWidget("stick_left", joystick_left_position, joystick_diameter, self)
        self.buttons["stick_right"] = JoystickWidget("stick_right", joystick_right_position, joystick_diameter, self)

        self.pulse_start_scale = 1.01
        self.pulse_end_scale = 1.05
        self.pulse_duration = 200

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        scaled_image = QImage(self.controller_image).scaled(
            int(self.controller_size[0] * self._pulse_scale),
            int(self.controller_size[1] * self._pulse_scale),
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        if self.pulse_color != Qt.GlobalColor.white:
            tinted = QImage(scaled_image.size(), QImage.Format.Format_ARGB32)
            tinted.fill(Qt.GlobalColor.transparent)
            temp_painter = QPainter(tinted)
            temp_painter.drawImage(0, 0, scaled_image)
            temp_painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceAtop)
            temp_painter.fillRect(tinted.rect(), self.pulse_color)
            temp_painter.end()
            scaled_image = tinted

        x = (self.width() - scaled_image.width()) // 2
        y = (self.height() - scaled_image.height()) // 2
        painter.save()
        painter.setOpacity(self._pulse_opacity)
        painter.drawImage(x, y, scaled_image)
        painter.restore()

        image = QImage(self.controller_image).scaled(
            self.controller_size[0],
            self.controller_size[1],
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        painter.drawImage(0, 0, image)

        if self.title:
            font = QFont()
            font.setPointSize(13)
            painter.setFont(font)
            painter.setPen(QColor("#e5e7eb"))
            title_rect = QRect(0, 0, self.controller_size[0], 28)
            painter.drawText(title_rect, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop, self.title)

    def set_title(self, title: str):
        self.title = title
        self.update()

    def highlight_buttons(self, button_names: list[ControllerButtonName]):
        for button_widget in self.buttons.values():
            button_widget.set_color(Qt.GlobalColor.white)
            button_widget.set_highlighted(False)
        for button_name in button_names:
            if button_name in self.buttons:
                self.buttons[button_name].set_color(self.highlight_color)
                self.buttons[button_name].set_highlighted(True)

    def set_highlight_color(self, color: QColor):
        self.highlight_color = color
        for button_widget in self.buttons.values():
            if button_widget.highlighted:
                button_widget.set_color(color)

    def set_pulse_color(self, color: QColor):
        self.pulse_color = color
