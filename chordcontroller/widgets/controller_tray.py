from PySide6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PySide6.QtGui import QIcon, QPainter, QColor, QFont, QPixmap
from PySide6.QtCore import Qt
from chordcontroller.widgets.controller_overlay import ControllerOverlay


def _create_controller_icon(size=64):
    """Create a controller icon as QIcon."""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Draw a filled circle (controller button)
    circle_radius = size // 2 - 4
    circle_center = size // 2

    # Draw outline
    painter.setPen(QColor(0, 0, 0))
    painter.setBrush(QColor(200, 0, 0))
    painter.drawEllipse(
        circle_center - circle_radius,
        circle_center - circle_radius,
        circle_radius * 2,
        circle_radius * 2,
    )

    # Draw the letter 'A' in the center
    painter.setPen(QColor(255, 255, 255))
    font = QFont("Arial", size // 3, QFont.Weight.Bold)
    painter.setFont(font)
    painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "A")

    painter.end()

    return QIcon(pixmap)


def create_tray_icon(app: QApplication, overlay: ControllerOverlay):
    tray_icon = QSystemTrayIcon(_create_controller_icon(64))
    tray_icon.setToolTip("Controller Overlay")

    menu = QMenu()

    toggle_action = menu.addAction("Show Overlay")
    toggle_action.setCheckable(True)
    try:
        is_shown = not overlay.hidden_by_setting
    except AttributeError:
        is_shown = True
    toggle_action.setChecked(is_shown)

    def on_toggle(checked):
        overlay.hidden_by_setting = not checked
        if checked:
            overlay.show()
        else:
            overlay.hide()

    toggle_action.toggled.connect(on_toggle)

    quit_action = menu.addAction("Quit")
    quit_action.triggered.connect(app.quit)

    tray_icon.setContextMenu(menu)
    tray_icon.show()

    return tray_icon
