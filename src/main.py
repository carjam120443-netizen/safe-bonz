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
    """Original purple desktop assistant inspired by classic desktop pets."""

    def __init__(self):
        super().__init__()
        self.drag_offset = None
        self.dragging = False
        self.muted = False
        self.paused = False
        self.leaving = False
        self.frame = 0
        self.expression = "normal"
        self.message = "Hi! I'm Safe Bonz!"

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(220, 275)

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
        if self.muted or self.paused or self.leaving:
            return
        try:
            data = json.loads(MESSAGES_FILE.read_text(encoding="utf-8"))
            self.message = random.choice(data.get("messages", ["Hi!"]))
        except (OSError, json.JSONDecodeError):
            self.message = "Hi! 👋"
        self.expression = "happy"
        QTimer.singleShot(1800, self.reset_expression)
        self.update()

    def reset_expression(self):
        if not self.dragging and not self.leaving:
            self.expression = "normal"
            self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Speech bubble
        p.setPen(QPen(Qt.GlobalColor.black, 2))
        p.setBrush(Qt.GlobalColor.white)
        p.drawRoundedRect(7, 7, 206, 68, 13, 13)
        p.setFont(QFont("Arial", 9))
        p.setPen(Qt.GlobalColor.black)
        p.drawText(17, 17, 186, 48, Qt.TextFlag.TextWordWrap | Qt.AlignmentFlag.AlignCenter, self.message)

        # Original purple desktop-assistant sprite: large head, ears, suit-like body,
        # expressive face and waving hands. It is not a copy of any existing sprite.
        bob = 3 if self.frame % 8 in (1, 2, 3, 7) else 0
        if self.dragging:
            bob += 5 if self.frame % 2 else -2
        cx, cy = 110, 157 + bob

        # Body / jacket silhouette
        p.setPen(QPen(Qt.GlobalColor.black, 3))
        p.setBrush(Qt.GlobalColor.darkMagenta)
        p.drawRoundedRect(cx - 55, cy + 25, 110, 72, 28, 28)
        p.setBrush(Qt.GlobalColor.magenta)
        p.drawEllipse(cx - 62, cy - 72, 124, 108)

        # Ears
        p.setBrush(Qt.GlobalColor.darkMagenta)
        p.drawEllipse(cx - 72, cy - 35, 27, 38)
        p.drawEllipse(cx + 45, cy - 35, 27, 38)

        # Eyes
        p.setBrush(Qt.GlobalColor.white)
        p.drawEllipse(cx - 34, cy - 35, 27, 33)
        p.drawEllipse(cx + 7, cy - 35, 27, 33)
        p.setBrush(Qt.GlobalColor.black)
        eye_shift = 0
        if self.dragging:
            eye_shift = 6 if self.frame % 2 else -6
        p.drawEllipse(cx - 24 + eye_shift, cy - 26, 10, 15)
        p.drawEllipse(cx + 17 + eye_shift, cy - 26, 10, 15)

        # Muzzle and nose
        p.setBrush(Qt.GlobalColor.lightGray)
        p.drawEllipse(cx - 35, cy - 2, 70, 45)
        p.setBrush(Qt.GlobalColor.black)
        p.drawEllipse(cx - 8, cy + 2, 16, 11)

        if self.expression == "surprised":
            p.drawEllipse(cx - 11, cy + 14, 22, 29)
        elif self.expression == "happy":
            p.drawArc(cx - 27, cy + 10, 54, 32, 200 * 16, 140 * 16)
        else:
            p.drawArc(cx - 24, cy + 9, 48, 28, 200 * 16, 140 * 16)

        # Tie / collar accent
        p.setBrush(Qt.GlobalColor.darkBlue)
        p.drawPolygon([cx - 13, cy + 27, cx + 13, cy + 27, cx + 7, cy + 45, cx, cy + 55, cx - 7, cy + 45])
        p.setBrush(Qt.GlobalColor.white)
        p.drawPolygon([cx - 25, cy + 25, cx, cy + 38, cx - 7, cy + 49, cx - 30, cy + 32])
        p.drawPolygon([cx + 25, cy + 25, cx, cy + 38, cx + 7, cy + 49, cx + 30, cy + 32])

        # Arms / hands
        wave = 12 if self.frame % 4 < 2 else -5
        p.setPen(QPen(Qt.GlobalColor.black, 8))
        p.drawLine(cx - 50, cy + 45, cx - 82, cy + 72 + (wave if self.dragging else 0))
        p.drawLine(cx + 50, cy + 45, cx + 82, cy + 72 - (wave if self.dragging else 0))
        p.setBrush(Qt.GlobalColor.magenta)
        p.drawEllipse(cx - 94, cy + 65 + (wave if self.dragging else 0), 25, 25)
        p.drawEllipse(cx + 69, cy + 65 - (wave if self.dragging else 0), 25, 25)

        # Feet
        step = 7 if self.frame % 4 < 2 else -7
        if self.dragging:
            step *= 2
        p.setPen(QPen(Qt.GlobalColor.black, 7))
        p.drawLine(cx - 25, cy + 92, cx - 38 + step, cy + 115)
        p.drawLine(cx + 25, cy + 92, cx + 38 - step, cy + 115)

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

    def leave_desktop(self):
        if self.leaving:
            return
        self.leaving = True
        self.anim_timer.stop()
        self.message = random.choice([
            "Aww, you're sending me away already? Bye! 👋",
            "Okay! I'll get outta here. See you later! 🫡",
            "Goodbye! Safe Bonz is leaving the desktop! 💜",
            "Fineee, I'm leaving! Don't forget me! 😭"
        ])
        self.expression = "sad"
        self.update()
        QTimer.singleShot(2500, QApplication.quit)

    def show_menu(self, position):
        menu = QMenu(self)
        pause_action = menu.addAction("Resume" if self.paused else "Pause")
        mute_action = menu.addAction("Unmute" if self.muted else "Mute")
        say_action = menu.addAction("Say something")
        menu.addSeparator()
        exit_action = menu.addAction("Leave desktop")
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
            self.leave_desktop()


def main():
    app = QApplication(sys.argv)
    pet = SafeBonz()
    pet.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
