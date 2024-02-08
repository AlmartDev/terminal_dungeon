import os
import numpy as np
from pathlib import Path

ROOT = Path("terminal_dungeon")

WALL_DIR = ROOT / "wall_textures"
SPRITE_DIR = ROOT / "sprite_textures"
ITEM_DIR = ROOT / "item_textures"

def clamp(mi, val, ma):
    return max(min(ma, val), mi)


class Renderer:
    """
    Graphic engine.  Casts rays.  Casts sprites.  Kicks ass.

    Notes
    -----
    If one wanted to add ceiling/floor textures, weapons, or anything new, just add a method
    """
    max_hops = 20  # How far rays are cast.

    # Shading constants -- Modifying ascii_map should be safe.
    ascii_map = np.array(list(' .,:;<+*LtCa4U80dQM@'))
    shades = len(ascii_map) - 1
    side_shade = (shades + 1) // 5
    shade_dif = shades - side_shade

    _textures_on = True

    minimap_width = .2  # Fraction of screen
    minimap_height = .3
    minimap_pos = 5, 5  # minimap's lower-right corner's offset from screen's lower-right corner
    pad = 50  # How much extra space is added around the edge of the mini-map -- for large terminals this will need to be increased.

    def __init__(self, screen, player, wall_textures=None, sprite_textures=None, item_textures=None, UI=None):
        self.screen = screen
        self.resize()

        self.UI = UI

        self.player = player
        self.game_map = player.game_map
        self.mini_map = np.pad(np.where(self.game_map._map.T, '#', ' '), self.pad, constant_values=' ')

        self._load_textures(wall_textures or [ ], sprite_textures or [ ], item_textures or [ ])

    @property
    def textures_on(self):
        return self.wall_textures and self._textures_on

    def toggle_textures(self):
        self._textures_on = not self._textures_on

    def resize(self):
        try: # linux
            w, h = os.get_terminal_size()
        except: # windows
            h, w = self.screen.getmaxyx()

        w -= 1
        self.height = h
        self.width = w
        self.angle_increment = 1 / w
        self.floor_y = h // 2
        self.cieling_y = -(h // 2)
        self.distances = np.zeros(w)
        self.buffer = np.full((h, w), " ")
            
    def _load_textures(self, wall_textures, sprite_textures, item_textures):
        # Wall textures will be integer arrays, while sprite textures are character arrays.
        # This because the values in wall textures will add or subtract brightness to the current wall shading.
        # If we used character arrays for walls, we wouldn't have different shades for N/S and E/W walls and
        # walls further away wouldn't be dimmer, diminishing the 3d effect.
        # This could be changed though, and would simplify some of the texture drawing logic in `cast_ray`.
        self.wall_textures = [ ]
        for name in wall_textures:
            wall_lines = (WALL_DIR / (name + ".txt")).read_text().splitlines()
            wall_as_integer_array = [list(map(int, line)) for line in wall_lines]
            self.wall_textures.append(np.array(wall_as_integer_array).T)

        self.sprite_textures = { }
        for name in sprite_textures:
            sprite_lines = (SPRITE_DIR / (name + ".txt")).read_text().splitlines()
            sprite_as_character_array = list(map(list, sprite_lines))
            self.sprite_textures[name] = np.array(sprite_as_character_array).T

        self.item_textures = { }
        for name in item_textures:
            item_lines = (ITEM_DIR / (name + ".txt")).read_text().splitlines()
            item_as_character_array = list(map(list, item_lines))
            self.item_textures[name] = np.array(item_as_character_array).T

    def cast_ray(self, column):
        """
        Cast rays and draw columns whose heights correspond to the distance a ray traveled
        until it hit a wall.
        """
        player = self.player

        ray_angle = np.array((1, 2 * column * self.angle_increment - 1)) @ player.cam
        map_pos = player.pos.astype(int)
        delta = abs(1 / ray_angle)
        step = np.sign(ray_angle)
        side_dis = step * (np.heaviside(step, 1) - player.pos % 1) * delta

        # Cast a ray until we hit a wall or hit max_hops
        for _ in range(self.max_hops):
            side = 0 if side_dis[0] < side_dis[1] else 1
            side_dis[side] += delta[side]
            map_pos[side] += step[side]
            if self.game_map[map_pos]:
                break
        else:  # No walls in range
            self.distances[column] = float("inf")
            return

        # Not euclidean distance to avoid fish-eye effect.
        wall_dis = (map_pos[side] - player.pos[side] + (0 if step[side] == 1 else 1)) / ray_angle[side]
        # Save distance for sprite calculations.
        self.distances[column] = wall_dis

        h = self.height
        line_height = int(h / wall_dis) # if wall_dis else h  -- possible divide-by-0 error
        if line_height == 0:
            return  # Draw nothing

        jump_height = player.z * line_height
        line_start = max(0, int((h - line_height) / 2 + jump_height))
        line_end = min(h, int((h + line_height) / 2 + jump_height))
        drawn_height = line_end - line_start

        shade = min(drawn_height, self.shade_dif)
        shade += 0 if side else self.side_shade  # One side is brighter

        shade_buffer = np.full(drawn_height, shade)

        if self.textures_on:
            tex = self.wall_textures[self.game_map[map_pos] - 1]
            texture_width, texture_height = tex.shape

            wall_x = (player.pos[1 - side] + wall_dis * ray_angle[1 - side]) % 1
            tex_x = int(wall_x * texture_width)
            if (-1 if side == 1 else 1) * ray_angle[side] < 0:
                tex_x = texture_width - tex_x - 1

            offset = (line_height - drawn_height) / 2
            ys = np.arange(drawn_height) + offset
            tex_ys = (ys * texture_height / line_height).astype(int)
            # Add or subtract texture values to shade values
            # Note 2 * n - 12 is 0 for n = 6, i.e., values above 6 are additive and
            # below 6 are subtractive. For larger ascii maps, one may want to use linear
            # equation with a larger slope.
            shade_buffer += 2 * tex[tex_x, tex_ys] - 12
            np.clip(shade_buffer, 1, self.shades, out=shade_buffer)

        self.buffer[line_start:line_end, column] = self.ascii_map[shade_buffer]

    def cast_sprites(self):
        buffer = self.buffer
        player = self.player
        h = self.height
        w = self.width
        sprites = self.game_map.sprites

        for sprite in sprites:
            # Relative position of sprite to player
            sprite.relative = player.pos - sprite.pos
        sprites.sort()

        # Camera Inverse used to calculate transformed position of sprites.
        cam_inv = np.linalg.inv(-player.cam[::-1])

        for sprite in sprites:  # Draw each sprite from furthest to closest.
            # Transformed position of sprites due to camera position
            x, y = sprite.relative @ cam_inv
            # Sprite x-position on screen
            sprite_x = int(w / 2 * (1 + x / y))

            sprite_height = int(h / y)
            sprite_width = int(w / y / 2)

            if sprite_height == 0 or sprite_width == 0:  # Sprite too small.
                continue

            jump_height = player.z * sprite_height
            start_y = clamp(0, int((h - sprite_height) / 2 + jump_height), h)
            end_y = clamp(0, int((h + sprite_height) / 2 + jump_height), h)

            start_x = clamp(0, -sprite_width // 2 + sprite_x, w)
            end_x = clamp(0, sprite_width // 2 + sprite_x, w)

            columns = np.arange(start_x, end_x)
            columns = columns[(0 <= columns) & (columns <= w) & (y <= self.distances[columns])]

            tex = self.sprite_textures[sprite.tex]
            tex_width, tex_height = tex.shape

            clip_y = (sprite_height - h) / 2 - jump_height
            tex_ys = np.clip((np.arange(start_y, end_y) + clip_y) * tex_height / sprite_height, 0, None).astype(int)

            clip_x = sprite_x - sprite_width / 2
            tex_xs = ((columns - clip_x) * tex_width / sprite_width).astype(int)

            tex_rect = tex[tex_xs][:, tex_ys].T
            buffer[start_y:end_y, columns] = np.where(tex_rect != "0", tex_rect, buffer[start_y:end_y, columns])

    def cast_items(self):
        buffer = self.buffer
        player = self.player
        h = self.height
        w = self.width
        items = self.game_map.items

        for item in items:
            item.relative = player.pos - item.pos

        cam_inv = np.linalg.inv(-player.cam[::-1])

        for item in items:  # Draw each item from furthest to closest.
            if item.is_grabbed:
                continue

            # Transformed position of sprites due to camera position
            x, y = item.relative @ cam_inv
            item_x = int(w / 2 * (1 + x / y))

            if item.relative[0] < .35 and item.relative[1] < .35:
                item.on_pickup(player)

            item_height = int(h / y / 4)    # Divided to make it smaller
            item_width = int(w / y / 6)     # Same here!

            if item_height == 0 or item_width == 0:  # item too small.
                continue

            jump_height = player.z * item_height
            start_y = clamp(0, int((h - item_height) / 2 + jump_height), h)
            end_y = clamp(0, int((h + item_height) / 2 + jump_height), h)

            start_x = clamp(0, -item_width // 2 + item_x, w)
            end_x = clamp(0, item_width // 2 + item_x, w)

            columns = np.arange(start_x, end_x)
            columns = columns[(0 <= columns) & (columns <= w) & (y <= self.distances[columns])]

            tex = self.item_textures[item.tex]
            tex_width, tex_height = tex.shape

            clip_y = (item_height - h) / 2 - jump_height
            tex_ys = np.clip((np.arange(start_y, end_y) + clip_y) * tex_height / item_height, 0, None).astype(int)

            clip_x = item_x - item_width / 2
            tex_xs = ((columns - clip_x) * tex_width / item_width).astype(int)

            tex_rect = tex[tex_xs][:, tex_ys].T
            buffer[start_y:end_y, columns] = np.where(tex_rect != "0", tex_rect, buffer[start_y:end_y, columns])

    def draw_minimap(self):
        x_offset, y_offset = self.minimap_pos
        width = int(self.minimap_width * self.width)
        width += width % 2

        hw = width // 2
        height = int(self.minimap_height * self.height)
        height += height % 2
        hh = height // 2  # half-height

        x, y = self.player.pos.astype(int) + self.pad

        r = -height - y_offset
        c = -width - x_offset
        self.buffer[r: -y_offset, c: -x_offset] = self.mini_map[y - hh: y + hh, x - hw: x + hw]
        self.buffer[r + hh, c + hw] = '@'

    def draw_ui(self):    
        self.draw_minimap()

        gun = self.player.gun
        gun._load_texture()

        x_offset, y_offset = self.UI.pos
        width = int(self.UI.width * self.width)
        width += width % 2

        height = int(self.UI.height * self.height)
        height += height % 2

        r = -height - y_offset
        c = -width - x_offset

        # Gun is rendered before UI so UI is always at the top
        for line in range(len(gun.texture)):
            for char in range(len(gun.texture[line])):
                if gun.texture[line][char] != "0":
                    self.buffer[c + width - line + 4, r + height + char - 15] = gun.texture[line][char]

        for line in range(self.UI.lines):
            for char in range(len(self.UI._ui[line])):
                self.buffer[c + width + line, r + height + char - 6] = self.UI._ui[line][char] 

    def update(self):
        self.buffer[:, :] = " "  # Clear buffer

        self.buffer[self.floor_y:, ::2] = self.ascii_map[1]  # Draw floor

        self.buffer[:self.cieling_y, ::3] = self.ascii_map[0]   # Draw cieling

        for column in range(self.width):  # Draw walls
            self.cast_ray(column)

        self.cast_items()
        self.cast_sprites()

        # updates UI textures from ./UI/ui.txt
        self.UI.update()

        self.draw_ui()  # Gun, UI and minimap

        # Push buffer to screen
        for row_num, row in enumerate(self.buffer):
            self.screen.addstr(row_num, 0, ''.join(row))
        self.screen.refresh()