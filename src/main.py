import json
import random
import sys
from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QPainter, QPen
from PySide6.QtWidgets import QApplication, QMenu, QWidget

if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    ROOT = Path(sys._MEIPASS)
else:
    ROOT = Path(__file__).resolve().parents[1]

MESSAGES_FILE = ROOT / "messages" / "messages.json"


class SafeBonz(QWidget):
    """Original animated Safe Bonz desktop pet."""

    def __init__(self):
        super().__init__()
        self.drag_offset = None
        self.dragging = False
        self.muted = False
        self.paused = False
        self.frame = 0
        self.expression = "normal"
        self.message = "Hi! I'm Safe Bonz!"

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(200, 250)

        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self.animate)
        self.anim_timer.start(110)

        self.message_timer = QTimer(self)
        self.message_timer.timeout.connect(self.random_message)
        self.message_timer.start(15000)

    def animate(self):
        if not self.paused:
            self.frame = (self.frame + 1) % 16
            self.update()

    def random_message(self):
        if self.muted or self.paused:
            return
        try:
            data = json.loads(MESSAGES_FILE.read_text(encoding="utf-8"))
            messages = data.get("messages", ["Hi!"])
            self.message = random.choice(messages)
        except (OSError, json.JSONDecodeError):
            self.message = "Hi! 👋"
        self.expression = "happy"
        QTimer.singleShot(1800, self.reset_expression)
        self.update()

    def reset_expression(self):
        if not self.dragging:
            self.expression = "normal"
            self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Speech bubble
        p.setPen(QPen(Qt.GlobalColor.black, 2))
        p.setBrush(Qt.GlobalColor.white)
        p.drawRoundedRect(7, 7, 186, 65, 13, 13)
        p.setFont(QFont("Arial", 9))
        p.setPen(Qt.GlobalColor.black)
        p.drawText(17, 17, 166, 45, Qt.TextFlag.TextWordWrap | Qt.AlignmentFlag.AlignCenter, self.message)

        # Original purple mascot body
        bob = 3 if self.frame % 8 in (1, 2, 3, 7) else 0
        if self.dragging:
            bob += 5 if self.frame % 2 else -2

        cx, cy = 100, 155 + bob
        p.setPen(QPen(Qt.GlobalColor.black, 3))
        p.setBrush(Qt.GlobalColor.darkMagenta)
        p.drawEllipse(cx - 63, cy - 72, 126, 112)
        p.setBrush(Qt.GlobalColor.magenta)
        p.drawEllipse(cx - 51, cy - 56, 102, 90)

        # Ears
        p.setBrush(Qt.GlobalColor.darkMagenta)
        p.drawEllipse(cx - 68, cy - 35, 25, 35)
        p.drawEllipse(cx + 43, cy - 35, 25, 35)

        # Eyes
        p.setBrush(Qt.GlobalColor.white)
        p.drawEllipse(cx - 31, cy - 34, 25, 31)
        p.drawEllipse(cx + 6, cy - 34, 25, 31)
        p.setBrush(Qt.GlobalColor.black)
        eye_shift = 0
        if self.dragging:
            eye_shift = 5 if self.frame % 2 else -5
        p.drawEllipse(cx - 22 + eye_shift, cy - 25, 9, 14)
        p.drawEllipse(cx + 15 + eye_shift, cy - 25, 9, 14)

        # Nose
        p.drawEllipse(cx - 7, cy - 3, 14, 10)

        # Mouth / expression
        if self.expression == "surprised":
            p.drawEllipse(cx - 10, cy + 9, 20, 27)
        elif self.expression == "happy":
            p.drawArc(cx - 28, cy + 4, 56, 36, 200 * 16, 140 * 16)
        else:
            p.drawArc(cx - 24, cy + 3, 48, 30, 200 * 16, 140 * 16)

        # Arms react while being dragged.
        arm_wave = 10 if self.frame % 4 < 2 else -5
        p.setPen(QPen(Qt.GlobalColor.black, 7))
        p.drawLine(cx - 48, cy + 30, cx - 76, cy + 55 + (arm_wave if self.dragging else 0))
        p.drawLine(cx + 48, cy + 30, cx + 76, cy + 55 - (arm_wave if self.dragging else 0))

        # Feet shuffle during idle / dragging.
        step = 7 if self.frame % 4 < 2 else -7
        if self.dragging:
            step *= 2
        p.setPen(QPen(Qt.GlobalColor.black, 5))
        p.drawLine(cx - 27, cy + 42, cx - 36 + step, cy + 70)
        p.drawLine(cx + 27, cy + 42, cx + 36 - step, cy + 70)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self.dragging = True
            self.expression = "surprised"
            self.message = random.choice(["Whoa!", "HEY! Easy!", "I'm moving!", "Wheeee! 🚀"])
            self.update()
            event.accept()
        elif event.button() == Qt.MouseButton.RightButton:
            self.show_menu(event.globalPosition().toPoint())
            event.accept()

    def mouseMoveEvent(self, event):
        if self.drag_offset is not None and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_offset)
            event.accept()

    def mouseReleaseEvent(self, event):
        if self.dragging:
            self.dragging = False
            self.expression = "happy"
            self.message = random.choice(["That was fun! 😎", "Back on solid ground!", "Nice trip!", "Again? 👀"])
            QTimer.singleShot(1800, self.reset_expression)
            self.update()
        self.drag_offset = None
        event.accept()

    def show_menu(self, position):
        menu = QMenu(self)
        pause_action = menu.addAction("Resume" if self.paused else "Pause")
        mute_action = menu.addAction("Unmute" if self.muted else "Mute")
        say_action = menu.addAction("Say something")
        menu.addSeparator()
        exit_action = menu.addAction("Exit Safe Bonz")
        action = menu.exec(position)

        if action == pause_action:
            self.paused = not self.paused
            self.message = "Paused 💤" if self.paused else "I'm back! 👋"
            self.update()
        elif action == mute_action:
            self.muted = not self.muted
            if self.muted:
                self.message = "Muted 🤐"
            self.update()
        elif action == say_action:
            self.random_message()
        elif action == exit_action:
            QApplication.quit()


def main():
    app = QApplication(sys.argv)
    pet = SafeBonz()
    pet.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
