import json
import random
import sys
from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QApplication, QLabel, QMenu, QWidget


ROOT = Path(__file__).resolve().parents[1]
MESSAGES_FILE = ROOT / "messages" / "messages.json"


class SafeBonz(QWidget):
    def __init__(self):
        super().__init__()
        self.drag_offset = None
        self.muted = False

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(180, 210)

        self.pet = QLabel("🦍", self)
        self.pet.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pet.setStyleSheet("font-size: 90px;")
        self.pet.setGeometry(10, 55, 160, 120)

        self.bubble = QLabel("Hello! 👋", self)
        self.bubble.setWordWrap(True)
        self.bubble.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.bubble.setStyleSheet(
            "background: white; color: black; border: 2px solid #555; "
            "border-radius: 12px; padding: 6px; font-size: 12px;"
        )
        self.bubble.setGeometry(5, 5, 170, 55)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.random_message)
        self.timer.start(15000)

        self.show()

    def random_message(self):
        if self.muted:
            return
        try:
            data = json.loads(MESSAGES_FILE.read_text(encoding="utf-8"))
            message = random.choice(data.get("messages", ["Hi!"]))
        except (OSError, json.JSONDecodeError):
            message = "Hi! 👋"
        self.bubble.setText(message)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
        elif event.button() == Qt.MouseButton.RightButton:
            self.show_menu(event.globalPosition().toPoint())
            event.accept()

    def mouseMoveEvent(self, event):
        if self.drag_offset is not None and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_offset)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.drag_offset = None
        event.accept()

    def show_menu(self, position):
        menu = QMenu(self)

        mute_action = QAction("Unmute" if self.muted else "Mute", menu)
        mute_action.triggered.connect(self.toggle_mute)
        menu.addAction(mute_action)

        pause_action = QAction("Resume" if self.timer.isActive() is False else "Pause", menu)
        pause_action.triggered.connect(self.toggle_pause)
        menu.addAction(pause_action)

        menu.addSeparator()
        exit_action = QAction("Exit Safe Bonz", menu)
        exit_action.triggered.connect(QApplication.quit)
        menu.addAction(exit_action)

        menu.exec(position)

    def toggle_mute(self):
        self.muted = not self.muted
        if self.muted:
            self.bubble.setText("Muted 🤐")

    def toggle_pause(self):
        if self.timer.isActive():
            self.timer.stop()
            self.bubble.setText("Paused 💤")
        else:
            self.timer.start(15000)
            self.bubble.setText("Back! 👋")


def main():
    app = QApplication(sys.argv)
    pet = SafeBonz()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
