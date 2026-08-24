import json
import random
import sys
from pathlib import Path

from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QFont, QPainter, QPen
from PySide6.QtWidgets import QApplication, QMenu, QWidget

try:
    from PySide6.QtMultimedia import QSoundEffect
except ImportError:
    QSoundEffect = None


class SafeBonz(QWidget):
    """Tiny, harmless desktop pet with animations, movement reactions, and optional sounds."""

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(180, 220)
        self.drag_offset = None
        self.paused = False
        self.muted = False
        self.frame = 0
        self.dragging = False
        self.message = "Hi! I'm Safe Bonz!"
        self.expression = "normal"

        self.messages = self._load_messages()
        self.sounds = {}
        self._load_sounds()

        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self.animate)
        self.anim_timer.start(120)

        self.message_timer = QTimer(self)
        self.message_timer.timeout.connect(self.speak_random)
        self.message_timer.start(15000)

    def _load_messages(self):
        path = Path(__file__).parent.parent / "messages" / "messages.json"
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return data.get("messages", data if isinstance(data, list) else [])
        except Exception:
            return ["Hello!", "I'm just a harmless desktop pet.", "Have a nice day!"]

    def _load_sounds(self):
        if QSoundEffect is None:
            return
        sound_dir = Path(__file__).parent.parent / "assets" / "sounds"
        for name in ("hello", "move", "click"):
            path = sound_dir / f"{name}.wav"
            if path.exists():
                effect = QSoundEffect(self)
                effect.setSource(path.as_uri())
                effect.setVolume(0.35)
                self.sounds[name] = effect

    def play_sound(self, name):
        if not self.muted and name in self.sounds:
            self.sounds[name].play()

    def animate(self):
        if not self.paused:
            self.frame = (self.frame + 1) % 12
            self.update()

    def speak_random(self):
        if not self.paused and not self.muted and self.messages:
            self.message = random.choice(self.messages)
            self.expression = "happy"
            self.play_sound("hello")
            self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        bob = 3 if self.frame in (1, 2, 3, 8, 9) else 0
        if self.dragging:
            bob += 4 if self.frame % 2 else -2
        x, y = 90, 145 + bob

        p.setPen(QPen(Qt.black, 2))
        p.setBrush(Qt.white)
        p.drawRoundedRect(8, 8, 164, 62, 12, 12)
        p.setPen(Qt.black)
        p.setFont(QFont("Arial", 9))
        p.drawText(18, 20, 144, 45, Qt.TextWordWrap, self.message)

        p.setPen(QPen(Qt.black, 3))
        p.setBrush(Qt.GlobalColor.darkMagenta)
        p.drawEllipse(x - 55, y - 65, 110, 105)
        p.setBrush(Qt.GlobalColor.magenta)
        p.drawEllipse(x - 43, y - 48, 86, 82)

        p.setBrush(Qt.white)
        p.drawEllipse(x - 27, y - 27, 22, 28)
        p.drawEllipse(x + 5, y - 27, 22, 28)
        p.setBrush(Qt.black)

        eye_shift = 0
        if self.dragging:
            eye_shift = 4 if self.frame % 2 else -4
        p.drawEllipse(x - 19 + eye_shift, y - 18, 8, 12)
        p.drawEllipse(x + 13 + eye_shift, y - 18, 8, 12)

        if self.expression == "happy":
            p.drawArc(x - 25, y - 2, 50, 35, 200 * 16, 140 * 16)
        elif self.expression == "surprised":
            p.drawEllipse(x - 9, y + 5, 18, 23)
        else:
            p.drawArc(x - 25, y - 2, 50, 35, 200 * 16, 140 * 16)

        foot_shift = 5 if self.frame % 2 else -5
        if self.dragging:
            foot_shift *= 2
        p.setPen(QPen(Qt.black, 2))
        p.drawLine(x - 25, y + 39, x - 35 + foot_shift, y + 55)
        p.drawLine(x + 25, y + 39, x + 35 - foot_shift, y + 55)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self.dragging = True
            self.expression = "surprised"
            self.message = random.choice(["Whoa!", "I'm moving! 😵", "Hey! Easy!", "Wheee! 🚀"])
            self.play_sound("move")
            self.update()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.drag_offset is not None and event.buttons() & Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_offset)
            event.accept()

    def mouseReleaseEvent(self, event):
        if self.dragging:
            self.dragging = False
            self.expression = "happy"
            self.message = random.choice(["That was fun! 😎", "Back on solid ground!", "You moved me!", "Nice trip!"])
            self.play_sound("click")
            self.update()
        self.drag_offset = None
        event.accept()

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
