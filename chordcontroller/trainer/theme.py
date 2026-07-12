from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication

BACKGROUND = "#11161b"
PANEL = "#19212a"
TEXT = "#e6edf3"
MUTED = "#9aa6b2"
ACCENT = "#3b82f6"


def apply_theme(app: QApplication) -> None:
    """Apply a cohesive, high-contrast palette for the trainer shell."""
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(BACKGROUND))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(TEXT))
    palette.setColor(QPalette.ColorRole.Base, QColor(PANEL))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(BACKGROUND))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(TEXT))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(TEXT))
    palette.setColor(QPalette.ColorRole.Text, QColor(TEXT))
    palette.setColor(QPalette.ColorRole.Button, QColor(PANEL))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(TEXT))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(ACCENT))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#111111"))
    app.setPalette(palette)

    app.setStyleSheet(
        """
        QWidget {
            font-family: 'Noto Sans', 'DejaVu Sans', sans-serif;
            color: #e6edf3;
        }
        QMainWindow, QWidget#root {
            background-color: #11161b;
        }
        QListWidget {
            background-color: #19212a;
            border: 1px solid #2a3642;
            border-radius: 10px;
            padding: 8px;
        }
        QListWidget::item {
            padding: 10px;
            border-radius: 8px;
        }
        QListWidget::item:selected {
            background-color: #3b82f6;
            color: #ffffff;
        }
        QListWidget[controllerFocus="true"] {
            border: 2px solid #3b82f6;
        }
        QFrame#panel {
            background-color: #19212a;
            border: 1px solid #2a3642;
            border-radius: 12px;
        }
        QLabel#title {
            font-size: 24px;
            font-weight: 700;
        }
        QLabel#subtitle {
            color: #9aa6b2;
            font-size: 14px;
        }
        QLabel#topBarPrimary {
            font-size: 15px;
            font-weight: 600;
        }
        QLabel#topBarSecondary {
            font-size: 12px;
            color: #9aa6b2;
        }
        QLabel#promptType {
            font-size: 18px;
            color: #9aa6b2;
            font-weight: 500;
        }
        QLabel#promptMain {
            font-size: 42px;
            font-weight: 700;
            color: #f8fafc;
            letter-spacing: 1px;
        }
        QLabel#promptStatus {
            min-height: 28px;
            font-size: 22px;
            font-weight: 700;
        }
        QLabel#promptStatus[status="ok"] {
            color: #22c55e;
        }
        QLabel#promptStatus[status="error"] {
            color: #ef4444;
        }
        QProgressBar {
            border: 1px solid #2a3642;
            border-radius: 4px;
            background: #0f1419;
        }
        QProgressBar::chunk {
            background-color: #3b82f6;
            border-radius: 3px;
        }
        QLabel#bottomMessage {
            font-size: 13px;
            color: #93c5fd;
            padding: 6px;
        }
        QLabel#completionIcon {
            font-size: 92px;
            font-weight: 700;
            color: #22c55e;
        }
        QLabel#completionSummary {
            font-size: 16px;
            color: #dbe7f3;
        }
        QPushButton {
            background-color: #2563eb;
            border: 1px solid #2563eb;
            border-radius: 8px;
            padding: 8px 16px;
            color: #ffffff;
            font-weight: 600;
        }
        QPushButton:hover {
            background-color: #1d4ed8;
        }
        QPushButton#secondaryButton {
            background-color: #1f2937;
            border: 1px solid #334155;
            color: #cbd5e1;
        }
        QPushButton[controllerFocus="true"],
        QComboBox[controllerFocus="true"],
        QCheckBox[controllerFocus="true"] {
            border: 2px solid #3b82f6;
        }
        QPushButton[controllerActive="true"] {
            background-color: #1d4ed8;
            border: 2px solid #60a5fa;
            color: #ffffff;
        }
        QCheckBox {
            spacing: 8px;
            padding: 4px 8px;
            border-radius: 6px;
        }
        QCheckBox::indicator {
            width: 16px;
            height: 16px;
        }
        QCheckBox::indicator:unchecked {
            border: 1px solid #64748b;
            background: #0f1419;
            border-radius: 3px;
        }
        QCheckBox::indicator:checked {
            border: 1px solid #2563eb;
            background: #2563eb;
            border-radius: 3px;
        }
        """
    )
