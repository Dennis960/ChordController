"""
Joystick calibration widget that displays both joysticks and asks the user
to rotate them in all directions.
"""

import math
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QPainter, QColor, QPen, QBrush


class DirectionalCalibration:
    """Tracks which cardinal directions have been pressed on the joystick."""

    # Target positions: Up, Right, Down, Left
    TARGETS = [
        (0.0, -1.0),   # Up (negative Y in screen coordinates)
        (1.0, 0.0),    # Right
        (0.0, 1.0),    # Down (positive Y in screen coordinates)
        (-1.0, 0.0),   # Left
    ]
    
    TOLERANCE = 0.1  # Distance tolerance for hitting a target

    def __init__(self, tolerance: float = None):
        """
        Initialize the calibration tracker.
        
        Args:
            tolerance: Distance tolerance for hitting targets (default 0.1)
        """
        self.tolerance = tolerance if tolerance is not None else self.TOLERANCE
        self.targets_hit = set()  # Indices of targets that have been hit
    
    def check_position(self, x: float, y: float):
        """Check if current position hits any target."""
        for i, (target_x, target_y) in enumerate(self.TARGETS):
            if i not in self.targets_hit:
                distance = math.sqrt((x - target_x) ** 2 + (y - target_y) ** 2)
                if distance <= self.tolerance:
                    self.targets_hit.add(i)
    
    def get_completion_percentage(self) -> float:
        """Get the percentage of targets hit (0-100)."""
        return (len(self.targets_hit) / len(self.TARGETS)) * 100.0
    
    def is_complete(self) -> bool:
        """Check if all targets have been hit."""
        return len(self.targets_hit) == len(self.TARGETS)
    
    def is_target_hit(self, index: int) -> bool:
        """Check if a specific target has been hit."""
        return index in self.targets_hit
    
    def reset(self):
        """Reset the calibration state."""
        self.targets_hit.clear()


class JoystickDisplay(QWidget):
    """A widget that displays a single joystick position."""

    def __init__(self, name: str, parent=None):
        super().__init__(parent)
        self.name = name
        self.pos_x = 0.0
        self.pos_y = 0.0
        self.calibration = DirectionalCalibration()
        self.setMinimumSize(150, 150)
        self.setMaximumSize(150, 150)

    def set_position(self, x: float, y: float):
        """Set the joystick position (-1 to 1 for both axes)."""
        self.pos_x = max(-1.0, min(1.0, x))
        self.pos_y = max(-1.0, min(1.0, y))
        
        # Check if position hits any target
        if not self.calibration.is_complete():
            self.calibration.check_position(x, y)
        
        self.update()

    def get_completion_percentage(self) -> float:
        """Get the current completion percentage (0-100)."""
        return self.calibration.get_completion_percentage()
    
    def is_complete(self):
        """Return whether calibration is complete."""
        return self.calibration.is_complete()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Get widget dimensions
        w = self.width()
        h = self.height()
        center_x = w // 2
        center_y = h // 2
        radius = min(w, h) // 2 - 10

        # Draw outer circle (boundary)
        painter.setPen(QPen(QColor(100, 100, 100), 2))
        painter.setBrush(QBrush(QColor(40, 40, 40)))
        painter.drawEllipse(center_x - radius, center_y - radius, radius * 2, radius * 2)

        # Draw crosshairs
        painter.setPen(QPen(QColor(70, 70, 70), 1))
        painter.drawLine(center_x - radius, center_y, center_x + radius, center_y)
        painter.drawLine(center_x, center_y - radius, center_x, center_y + radius)

        # Draw target positions
        target_radius = 12
        for i, (target_x, target_y) in enumerate(DirectionalCalibration.TARGETS):
            # Convert target position to screen coordinates
            tx = center_x + int(target_x * (radius - 15))
            ty = center_y + int(target_y * (radius - 15))
            
            # Choose color based on whether target is hit
            if self.calibration.is_target_hit(i):
                target_color = QColor(0, 255, 0, 180)  # Green with transparency
            else:
                target_color = QColor(100, 100, 100, 180)  # Grey with transparency
            
            painter.setPen(QPen(target_color, 2))
            painter.setBrush(QBrush(target_color))
            painter.drawEllipse(tx - target_radius, ty - target_radius, 
                              target_radius * 2, target_radius * 2)

        # Draw joystick position
        dot_x = center_x + int(self.pos_x * (radius - 10))
        dot_y = center_y + int(self.pos_y * (radius - 10))
        
        dot_color = QColor(0, 255, 0) if self.calibration.is_complete() else QColor(0, 200, 255)
        painter.setPen(QPen(dot_color, 2))
        painter.setBrush(QBrush(dot_color))
        painter.drawEllipse(dot_x - 8, dot_y - 8, 16, 16)

        # Draw label with completion status
        painter.setPen(QColor(255, 255, 255))
        if self.calibration.is_complete():
            label_text = f"{self.name} ✓"
        else:
            completion = self.get_completion_percentage()
            label_text = f"{self.name}: {completion:.0f}%"
        painter.drawText(5, 15, label_text)
        
        # Draw position coordinates
        painter.setPen(QColor(180, 180, 180))
        coord_text = f"({self.pos_x:.2f}, {self.pos_y:.2f})"
        painter.drawText(5, h - 5, coord_text)


class JoystickCalibrationWindow(QWidget):
    """Window that displays both joysticks and asks user to rotate them."""
    
    calibration_complete = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Joystick Calibration")
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Window
        )
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        # Setup UI
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # Instructions
        self.instruction_label = QLabel(
            """On Windows, manual joystick calibration is required.
Press each joystick fully in all four directions: Up, Right, Down, Left."""
        )
        self.instruction_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.instruction_label.setStyleSheet(
            "QLabel { color: white; font-size: 16px; font-weight: bold; }"
        )
        layout.addWidget(self.instruction_label)

        # Joystick displays
        joystick_layout = QHBoxLayout()
        joystick_layout.setSpacing(30)

        self.left_joystick = JoystickDisplay("Left Stick")
        self.right_joystick = JoystickDisplay("Right Stick")

        joystick_layout.addWidget(self.left_joystick)
        joystick_layout.addWidget(self.right_joystick)
        layout.addLayout(joystick_layout)

        # Status label
        self.status_label = QLabel("Press each joystick in all four directions...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("QLabel { color: gray; font-size: 12px; }")
        layout.addWidget(self.status_label)

        # Style the window
        self.setStyleSheet(
            """
            QWidget {
                background-color: #2b2b2b;
            }
        """
        )

        # Timer to check completion
        self.check_timer = QTimer(self)
        self.check_timer.timeout.connect(self._check_completion)
        self.check_timer.start(100)  # Check every 100ms

        self.adjustSize()
        self.setFixedSize(self.sizeHint())

    def _check_completion(self):
        """Check if both joysticks have been pressed in all directions."""
        left_done = self.left_joystick.is_complete()
        right_done = self.right_joystick.is_complete()
        
        if left_done and right_done:
            self.status_label.setText("Calibration complete!")
            self.check_timer.stop()
            self.calibration_complete.emit()
            self.close()
        elif left_done:
            self.status_label.setText("Left stick complete! Now press right stick in all directions...")
        elif right_done:
            self.status_label.setText("Right stick complete! Now press left stick in all directions...")

    def update_left_joystick(self, x: float, y: float):
        """Update the left joystick display position."""
        self.left_joystick.set_position(x, y)

    def update_right_joystick(self, x: float, y: float):
        """Update the right joystick display position."""
        self.right_joystick.set_position(x, y)

    def update_joysticks(self, left_x: float, left_y: float, right_x: float, right_y: float):
        """Update both joystick positions at once."""
        self.left_joystick.set_position(left_x, left_y)
        self.right_joystick.set_position(right_x, right_y)

if __name__ == "__main__":
    import sys
    import pygame
    from PySide6.QtWidgets import QApplication

    # Initialize pygame and joystick
    pygame.init()
    pygame.joystick.init()
    
    if pygame.joystick.get_count() == 0:
        print("No joystick detected!")
        sys.exit(1)
    
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    print(f"Detected joystick: {joystick.get_name()}")
    print(f"Number of axes: {joystick.get_numaxes()}")

    app = QApplication(sys.argv)
    window = JoystickCalibrationWindow()
    
    # Create a timer to poll joystick input
    def update_joystick_positions():
        pygame.event.pump()  # Process pygame events
        
        # Read joystick axes (typically axes 0-1 are left stick, 2-3 are right stick)
        # Adjust indices based on your controller layout
        if joystick.get_numaxes() >= 4:
            left_x = joystick.get_axis(0)
            left_y = joystick.get_axis(1)
            right_x = joystick.get_axis(2)
            right_y = joystick.get_axis(3)
            window.update_joysticks(left_x, left_y, right_x, right_y)
        elif joystick.get_numaxes() >= 2:
            # If only 2 axes available, show them on left stick
            left_x = joystick.get_axis(0)
            left_y = joystick.get_axis(1)
            window.update_left_joystick(left_x, left_y)
    
    # Poll joystick at 60 Hz
    poll_timer = QTimer()
    poll_timer.timeout.connect(update_joystick_positions)
    poll_timer.start(16)  # ~60 FPS
    
    window.show()
    exit_code = app.exec()
    
    # Cleanup
    pygame.quit()
    sys.exit(exit_code)
