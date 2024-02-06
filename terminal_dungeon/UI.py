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

        # 000 is a placeholder for player's health
        # 111 is a placeholder for player's ammo
        # See ui.txt to see how the placeholders are used

        # hp and ammo should always be 3 digits long

        # Replace placeholders with player's health and ammo
        for lines in range(self.lines):
            if len(str(player.hp)) < 3:
                self._ui[lines] = self._ui[lines].replace("000", "0" + str(player.hp))
            elif len(str(player.hp)) < 2:
                self._ui[lines] = self._ui[lines].replace("000", "00" + str(player.hp))
            else:
                self._ui[lines] = self._ui[lines].replace("000", str(player.hp))

            if len(str(player.ammo)) < 2:
                self._ui[lines] = self._ui[lines].replace("11", "0" + str(player.ammo))
            else:
                self._ui[lines] = self._ui[lines].replace("11", str(player.ammo))

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
            self._ui[lines] = self._ui[lines].replace("000", str(self.player.hp))
            self._ui[lines] = self._ui[lines].replace("11", str(self.player.ammo))
