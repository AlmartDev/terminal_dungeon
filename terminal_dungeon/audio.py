import vlc
from pathlib import Path

ROOT = Path("terminal_dungeon")
AUDIO_DIR = ROOT / "audio"

class AudioPlayer:
    def __init__(self):
        pass
        #self.instance = vlc.Instance('--input-repeat=-1', '--fullscreen')
        #self.player = self.instance.media_player_new()

    def play_sound(self, sound):
        pass
        #path = AUDIO_DIR / sound
        #media = self.instance.media_new(path)
        #self.player.set_media(media)
        #self.player.play()