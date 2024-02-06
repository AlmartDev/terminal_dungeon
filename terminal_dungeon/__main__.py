"""
A terminal based ray-casting engine.

'esc' to exit
't' to turn off textures
'wasdqe' or arrow-keys to move
'space' to jump

Depending on your terminal font, Renderer.ascii_map may need to be adjusted.
If you'd like to make an ascii map more suitable to your terminal's font,
check my Snippets repository for a script that grabs mean brightness of
unicode characters.

Values stored in textures should range from 0-9.  Values below 6 are
subtractive and above 6 are additive.
"""
import curses
from .map_loader import Map
from .player import Player
from .renderer import Renderer
from .controller import Controller
from .UI import UI

def init_curses(screen):
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    screen.attron(curses.color_pair(1))
    screen.nodelay(True)

@curses.wrapper
def main(screen):
    init_curses(screen)

    #healthpack1 = HealthPack(30, "healthpack/HealthPack1")

    items = "healthpack", "healthpack"  # items should be a list 

    game_map = Map("map_1")
    player = Player(game_map)
    game_UI = UI(player)
    wall_textures = "wall_1", "wall_2"
    sprite_textures = "dragon", "tree"

    Controller(Renderer(screen, player, wall_textures, sprite_textures, game_UI, items)).start()

    curses.flushinp()
    curses.endwin()
