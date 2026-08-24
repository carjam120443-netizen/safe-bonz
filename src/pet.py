import random
import sys
from pathlib import Path

from PySide6.QtCore import QPoint, QTimer, Qt
from PySide6.QtGui import QFont, QPainter, QPen
from PySide6.QtWidgets import QApplication, QMenu, QWidget


class SafeBonz(QWidget):
    """Tiny, harmless desktop pet. No networking or system modification."""

    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(180, 220)
        self.drag_offset = None
        self.paused = False
        self.muted = False
        self.frame = 0
        self.message = "Hi! I'm Safe Bonz!"

        self.messages = self._load_messages()

        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self.animate)
        self.anim_timer.start(180)

        self.message_timer = QTimer(self)
        self.message_timer.timeout.connect(self.speak_random)
        self.message_timer.start(15000)

    def _load_messages(self):
        path = Path(__file__).parent.parent / "messages" / "messages.json"
        try:
            import json
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return ["Hello!", "I'm just a harmless desktop pet.", "Have a nice day!"]

    def animate(self):
        if not self.paused:
            self.frame = (self.frame + 1) % 8
            self.update()

    def speak_random(self):
        if not self.paused and not self.muted and self.messages:
            self.message = random.choice(self.messages)
            self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        # Original simple mascot: deliberately not a ripped Bonzi Buddy sprite.
        bob = 2 if self.frame in (1, 2, 3, 7) else 0
        x, y = 90, 145 + bob

        # Speech bubble
        p.setPen(QPen(Qt.black, 2))
        p.setBrush(Qt.white)
        p.drawRoundedRect(8, 8, 164, 62, 12, 12)
        p.setPen(Qt.black)
        p.setFont(QFont("Arial", 9))
        p.drawText(18, 20, 144, 45, Qt.TextWordWrap, self.message)

        # Mascot body/head
        p.setPen(QPen(Qt.black, 3))
        p.setBrush(Qt.GlobalColor.darkMagenta)
        p.drawEllipse(x - 55, y - 65, 110, 105)
        p.setBrush(Qt.GlobalColor.magenta)
        p.drawEllipse(x - 43, y - 48, 86, 82)

        # Eyes
        p.setBrush(Qt.white)
        p.drawEllipse(x - 27, y - 27, 22, 28)
        p.drawEllipse(x + 5, y - 27, 22, 28)
        p.setBrush(Qt.black)
        p.drawEllipse(x - 19, y - 18, 8, 12)
        p.drawEllipse(x + 13, y - 18, 8, 12)

        # Smile
        p.drawArc(x - 25, y - 2, 50, 35, 200 * 16, 140 * 16)

        # Tiny feet with alternating animation
        foot_shift = 3 if self.frame % 2 else -3
        p.setPen(QPen(Qt.black, 2))
        p.drawLine(x - 25, y + 39, x - 35 + foot_shift, y + 55)
        p.drawLine(x + 25, y + 39, x + 35 - foot_shift, y + 55)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.drag_offset is not None and event.buttons() & Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_offset)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.drag_offset = None

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        pause = menu.addAction("Resume" if self.paused else "Pause")
        mute = menu.addAction("Unmute" if self.muted else "Mute")
        say = menu.addAction("Say something")
        menu.addSeparator()
        exit_action = menu.addAction("Exit")
        action = menu.exec(event.globalPos())

        if action == pause:
            self.paused = not self.paused
        elif action == mute:
            self.muted = not self.muted
        elif action == say:
            self.speak_random()
        elif action == exit_action:
            QApplication.quit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    pet = SafeBonz()
    pet.show()
    sys.exit(app.exec())
