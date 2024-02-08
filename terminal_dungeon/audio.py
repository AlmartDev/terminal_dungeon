import playsound
from pathlib import Path

ROOT = Path("terminal_dungeon")
AUDIO_DIR = ROOT / "audio"

class Audio():
    def __init__(self):
        self.music = None
        self.sound = None

    def play_sound(self, sound):
        playsound.playsound(AUDIO_DIR / sound)

    def stop_music(self):
        playsound.playsound(None)