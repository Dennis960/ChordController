from PySide6.QtWidgets import QWidget, QLabel
from PySide6.QtGui import QPixmap, QPainter
from PySide6.QtCore import Qt, QSize
from chordcontroller.resources import outline_images, solid_images
from chordcontroller.controller_inputs import ControllerButtonName
from chordcontroller.config import Chord

ICON_HEIGHT = 64


def load_scaled_pixmap(path: str, height: int) -> QPixmap:
    """Load and scale a pixmap to the specified height maintaining aspect ratio."""
    pixmap = QPixmap(path)
    if pixmap.isNull():
        return QPixmap()
    return pixmap.scaledToHeight(height, Qt.TransformationMode.SmoothTransformation)


class Button(QWidget):
    """Base button widget class for PySide6."""
    def __init__(self, scale=1.0, parent=None):
        super().__init__(parent)
        self.scale = scale
        self._width = 0
        self._height = 0
        self.pixmap = QPixmap()
        
    def get_size(self):
        return (self._width, self._height)
    
    def sizeHint(self):
        return QSize(self._width, self._height)
    
    def paintEvent(self, event):
        """Override to draw the button pixmap."""
        if not self.pixmap.isNull():
            painter = QPainter(self)
            painter.drawPixmap(0, 0, self.pixmap)


class ShoulderButtons(Button):
    def __init__(self, chord: Chord = frozenset(), scale=1.0, parent=None):
        super().__init__(scale, parent)
        self.chord = chord
        self.offset_y = -17
        self.positions = {
            "l": (0, self.offset_y),
            "r": (64, self.offset_y),
            "zl": (3, 30 + self.offset_y),
            "zr": (61, 30 + self.offset_y),
        }
        self.icon_size = int(self.scale * ICON_HEIGHT)
        self._width = int(self.scale * 2 * ICON_HEIGHT)
        self._height = self.icon_size
        self.images = {}
        self.set_chord(chord)
        self.setFixedSize(self._width, self._height)

    def set_chord(self, chord: Chord):
        self.chord = chord
        l_img = solid_images.l if "shoulder_l" in chord else outline_images.l
        r_img = solid_images.r if "shoulder_r" in chord else outline_images.r
        zl_img = solid_images.zl if "trigger_l" in chord else outline_images.zl
        zr_img = solid_images.zr if "trigger_r" in chord else outline_images.zr
        s = int(self.scale * ICON_HEIGHT)
        self.images = {
            "l": load_scaled_pixmap(l_img, s),
            "r": load_scaled_pixmap(r_img, s),
            "zl": load_scaled_pixmap(zl_img, s),
            "zr": load_scaled_pixmap(zr_img, s),
        }
        self._create_composite_pixmap()
    
    def _create_composite_pixmap(self):
        """Create a composite pixmap with all shoulder buttons."""
        self.pixmap = QPixmap(QSize(self._width, self._height))
        self.pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(self.pixmap)
        
        for key in ["l", "r", "zl", "zr"]:
            img = self.images[key]
            pos = self.positions[key]
            painter.drawPixmap(
                int(self.scale * pos[0]),
                int(self.scale * pos[1]),
                img
            )
        painter.end()
        self.update()


class DPad(Button):
    def __init__(self, chord: Chord = frozenset(), scale=1.0, parent=None):
        super().__init__(scale, parent)
        self.chord = chord
        self.set_chord(chord)

    def set_chord(self, chord: Chord):
        self.chord = chord
        if "dpad_up" in chord:
            if "dpad_right" in chord:
                image_path = solid_images.dpad_up_right
            elif "dpad_left" in chord:
                image_path = solid_images.dpad_up_left
            else:
                image_path = solid_images.dpad_up
        elif "dpad_down" in chord:
            if "dpad_right" in chord:
                image_path = solid_images.dpad_down_right
            elif "dpad_left" in chord:
                image_path = solid_images.dpad_down_left
            else:
                image_path = solid_images.dpad_down
        elif "dpad_right" in chord:
            image_path = solid_images.dpad_right
        elif "dpad_left" in chord:
            image_path = solid_images.dpad_left
        else:
            image_path = outline_images.dpad_none
        
        s = int(self.scale * ICON_HEIGHT)
        self.pixmap = load_scaled_pixmap(image_path, s)
        self._width = self.pixmap.width()
        self._height = self.pixmap.height()
        self.setFixedSize(self._width, self._height)
        self.update()


class FaceButtons(Button):
    def __init__(self, chord: Chord = frozenset(), scale=1.0, parent=None):
        super().__init__(scale, parent)
        self.chord = chord
        self.set_chord(chord)

    def set_chord(self, chord: Chord):
        self.chord = chord
        if "face_up" in chord:
            if "face_right" in chord:
                image_path = solid_images.face_up_right
            elif "face_left" in chord:
                image_path = solid_images.face_up_left
            else:
                image_path = solid_images.face_up
        elif "face_down" in chord:
            if "face_right" in chord:
                image_path = solid_images.face_down_right
            elif "face_left" in chord:
                image_path = solid_images.face_down_left
            else:
                image_path = solid_images.face_down
        elif "face_right" in chord:
            image_path = solid_images.face_right
        elif "face_left" in chord:
            image_path = solid_images.face_left
        else:
            image_path = outline_images.face_none
        
        s = int(self.scale * ICON_HEIGHT)
        self.pixmap = load_scaled_pixmap(image_path, s)
        self._width = self.pixmap.width()
        self._height = self.pixmap.height()
        self.setFixedSize(self._width, self._height)
        self.update()


class SingleButton(Button):
    def __init__(self, controller_button_name: ControllerButtonName, scale=1.0, parent=None):
        super().__init__(scale, parent)
        self.set_state(controller_button_name)

    def set_state(self, controller_button_name: ControllerButtonName):
        image_path = ""
        if controller_button_name == "minus":
            image_path = outline_images.minus
        elif controller_button_name == "plus":
            image_path = outline_images.plus
        elif controller_button_name == "home":
            image_path = outline_images.home
        elif controller_button_name == "capture":
            image_path = outline_images.capture
        elif controller_button_name == "stick_left":
            image_path = outline_images.stick_left
        elif controller_button_name == "stick_right":
            image_path = outline_images.stick_right
        elif controller_button_name == "shoulder_l":
            image_path = outline_images.l
        elif controller_button_name == "shoulder_r":
            image_path = outline_images.r
        elif controller_button_name == "trigger_l":
            image_path = outline_images.zl
        elif controller_button_name == "trigger_r":
            image_path = outline_images.zr
        
        s = int(self.scale * ICON_HEIGHT)
        self.pixmap = load_scaled_pixmap(image_path, s)
        self._width = self.pixmap.width()
        self._height = self.pixmap.height()
        self.setFixedSize(self._width, self._height)
        self.update()


class StickMovement(Button):
    def __init__(self, is_left: bool, scale=1.0, parent=None):
        super().__init__(scale, parent)
        self.set_state(is_left)

    def set_state(self, is_left: bool):
        if is_left:
            image_path = outline_images.stick_left_movement
        else:
            image_path = outline_images.stick_right_movement
        
        s = int(self.scale * ICON_HEIGHT)
        self.pixmap = load_scaled_pixmap(image_path, s)
        self._width = self.pixmap.width()
        self._height = self.pixmap.height()
        self.setFixedSize(self._width, self._height)
        self.update()


class MultiButton(Button):
    def __init__(self, chord: Chord = frozenset(), scale=1.0, parent=None):
        super().__init__(scale, parent)
        self.chord = chord
        self.shoulder_buttons = ShoulderButtons(chord, scale=self.scale)
        self.dpad = DPad(chord, scale=self.scale)
        self.face_buttons = FaceButtons(chord, scale=self.scale)
        self._width, self._height = self._calculate_size()
        self.set_chord(chord)
        self.setFixedSize(self._width, self._height)

    def set_chord(self, chord: Chord):
        self.chord = chord
        self.shoulder_buttons.set_chord(chord)
        self.dpad.set_chord(chord)
        self.face_buttons.set_chord(chord)
        self._create_composite_pixmap()

    def _calculate_size(self):
        w1, h1 = self.shoulder_buttons.get_size()
        w2, h2 = self.dpad.get_size()
        w3, h3 = self.face_buttons.get_size()
        return (w1 + w2 + w3, max(h1, h2, h3))
    
    def _create_composite_pixmap(self):
        """Create a composite pixmap with all buttons side by side."""
        self.pixmap = QPixmap(QSize(self._width, self._height))
        self.pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(self.pixmap)
        
        # Draw shoulder buttons
        painter.drawPixmap(0, 0, self.shoulder_buttons.pixmap)
        
        # Draw D-pad
        painter.drawPixmap(2 * int(self.scale * ICON_HEIGHT), 0, self.dpad.pixmap)
        
        # Draw face buttons
        painter.drawPixmap(3 * int(self.scale * ICON_HEIGHT), 0, self.face_buttons.pixmap)
        
        painter.end()
        self.update()
