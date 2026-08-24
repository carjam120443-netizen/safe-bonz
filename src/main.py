import json
import random
import sys
from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QImage, QPainter, QPixmap
from PySide6.QtWidgets import QApplication, QMenu, QWidget

if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    ROOT = Path(sys._MEIPASS)
else:
    ROOT = Path(__file__).resolve().parents[1]

MESSAGES_FILE = ROOT / "messages" / "messages.json"
SPRITE_ROOT = ROOT / "assets" / "sprites"


class SafeBonz(QWidget):
    """Sprite-based Safe Bonz desktop pet."""

    def __init__(self):
        super().__init__()
        self.drag_offset = None
        self.dragging = False
        self.muted = False
        self.paused = False
        self.leaving = False
        self.frame = 0
        self.message = "Hi! I'm Safe Bonz!"
        self.sprite_frames = self.load_sprite_frames()

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(320, 360)

        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self.animate)
        self.anim_timer.start(120)

        self.message_timer = QTimer(self)
        self.message_timer.timeout.connect(self.random_message)
        self.message_timer.start(15000)

    def load_sprite_frames(self):
        if not SPRITE_ROOT.exists():
            return []
        files = sorted(
            p for p in SPRITE_ROOT.rglob("*")
            if p.is_file() and p.suffix.lower() in {".png", ".gif", ".bmp", ".jpg", ".jpeg"}
        )
        frames = []
        for path in files:
            image = QImage(str(path))
            if not image.isNull():
                frames.append(QPixmap.fromImage(image))
        return frames

    def animate(self):
        if not self.paused and not self.leaving and self.sprite_frames:
            self.frame = (self.frame + 1) % len(self.sprite_frames)
            self.update()

    def random_message(self):
        if self.muted or self.paused or self.leaving:
            return
        try:
            data = json.loads(MESSAGES_FILE.read_text(encoding="utf-8"))
            self.message = random.choice(data.get("messages", ["Hi!"]))
        except (OSError, json.JSONDecodeError):
            self.message = "Hi!"
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        p.setPen(Qt.GlobalColor.black)
        p.setBrush(Qt.GlobalColor.white)
        p.drawRoundedRect(10, 10, 300, 72, 12, 12)
        p.setFont(QFont("Arial", 10))
        p.drawText(20, 20, 280, 52, Qt.TextFlag.TextWordWrap | Qt.AlignmentFlag.AlignCenter, self.message)

        if not self.sprite_frames:
            p.drawText(20, 130, 280, 40, Qt.AlignmentFlag.AlignCenter, "Sprite assets were not found.")
            return

        sprite = self.sprite_frames[self.frame]
        size = sprite.size()
        size.scale(290, 255, Qt.AspectRatioMode.KeepAspectRatio)
        x = (self.width() - size.width()) // 2
        y = 90
        if self.dragging:
            y += 4 if self.frame % 2 else -2
        p.drawPixmap(x, y, size.width(), size.height(), sprite)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self.dragging = True
            self.message = random.choice(["Whoa! Easy!", "Hey! I'm being moved!", "Wheee!", "Where are we going?"])
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
            self.message = random.choice(["That was fun!", "Back on solid ground!", "Nice trip!", "Please don't squish me! 😭"])
            self.update()
        self.drag_offset = None
        event.accept()

    def show_menu(self, position):
        menu = QMenu(self)
        pause_action = menu.addAction("Resume" if self.paused else "Pause")
        mute_action = menu.addAction("Unmute" if self.muted else "Mute")
        say_action = menu.addAction("Say something")
        menu.addSeparator()
        leave_action = menu.addAction("Leave desktop")
        action = menu.exec(position)

        if action == pause_action:
            self.paused = not self.paused
            self.message = "I'm back! 👋" if not self.paused else "I'll stay right here. 💤"
            self.update()
        elif action == mute_action:
            self.muted = not self.muted
            self.message = "Unmuted!" if not self.muted else "Muted 🤐"
            self.update()
        elif action == say_action:
            self.random_message()
        elif action == leave_action:
            self.leave_desktop()

    def leave_desktop(self):
        if self.leaving:
            return
        self.leaving = True
        self.anim_timer.stop()
        self.message = random.choice([
            "Aww, you're sending me away already? Bye! 👋",
            "Okay! I'll get outta here. See you later!",
            "Goodbye! Safe Bonz is leaving the desktop!",
            "Fineee, I'm leaving! Don't forget me! 😭",
        ])
        self.update()
        QTimer.singleShot(2500, QApplication.quit)


def main():
    app = QApplication(sys.argv)
    pet = SafeBonz()
    pet.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
