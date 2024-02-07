import json
from pathlib import Path
import numpy as np

MAP_DIR = Path("terminal_dungeon") / "UI"

class UI:
    # read the file "ui.txt"
    def __init__(self, player):
        self._ui = []
        with open(MAP_DIR / "ui.txt", "r") as file:
            for line in file:
                self._ui.append(line.strip())

        self.lines = len(self._ui) 
        self.player = player

        # 111 is a placeholder for player's health
        # 333 is a placeholder for player's ammo
        # See ui.txt to see how the placeholders are used

        # hp and ammo should always be 3 digits long

        self.pos = 5, -105
        self.width = .4
        self.height = .5

    def update(self):
        self._ui = []
        with open(MAP_DIR / "ui.txt", "r") as file:
            for line in file:
                self._ui.append(line.strip())

        self.lines = len(self._ui) 

        # 000 is a placeholder for player's health
        # 111 is a placeholder for player's ammo
        # See ui.txt to see how the placeholders are used

        # hp and ammo should always be 3 digits long

        # Replace placeholders with player's health and ammo
        for lines in range(self.lines):
            hp_length = len(str(self.player.hp))
            ammo_length = len(str(self.player.ammo))

            if hp_length < 3:
                self._ui[lines] = self._ui[lines].replace("111", "0" * (3 - hp_length) + str(self.player.hp))
            else:
                self._ui[lines] = self._ui[lines].replace("111", str(self.player.hp))

            if ammo_length < 3:
                self._ui[lines] = self._ui[lines].replace("222", "0" * (3 - ammo_length) + str(self.player.ammo))
            else:
                self._ui[lines] = self._ui[lines].replace("222", str(self.player.ammo))