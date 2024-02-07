import numpy as np
from math import cos, sin

def rotation_matrix(theta):
    """
    Returns a 2-dimensional rotation array of a given angle.
    """
    r = cos(theta)
    q = sin(theta)

    return np.array([[ r, q],
                     [-q, r]])


class Player:
    """
    Player class with methods for moving and updating any effects on the
    player such as falling.
    """
    field_of_view = .6  # Somewhere between 0 and 1 is reasonable
    speed = .1

    rotate_speed = .07
    left = rotation_matrix(-rotate_speed)
    right = rotation_matrix(rotate_speed)
    perp = rotation_matrix(3 * np.pi / 2)

    jump_time = 10
    is_jumping = False
    z = 0.0  # "height" off the ground

    def __init__(self, game_map, pos=np.array([5., 5.]), initial_angle=0):
        self.game_map = game_map
        self.pos = pos

        self.hp = 100 # Health points
        self.ammo = 25 # Ammo

        if initial_angle == 0:
            initial_angle += 0.0001  # Nudge to avoid divide-by-zero errors
        self.cam = np.array([[1, 0], [0, self.field_of_view]]) @ rotation_matrix(initial_angle)

        # generate z sequence for jumping
        t = np.arange(self.jump_time + 1)
        self.zs = 2 * t * (self.jump_time - t) / self.jump_time**2

    def jump(self):
        # Return True if a starting a new jump.
        if self.is_jumping:
            return False

        self.is_jumping = True
        self.iter_z = self.z_gen()
        return True

    def z_gen(self):
        """
        Set each z value in self.zs to self.z consecutively,
        then set self.is_jumping to False.
        """
        for z in self.zs:
            self.z = z
            yield

        self.is_jumping = False
        yield

    def update(self):
        # We'll have more to do here eventually, e.g., decrement timers on power-ups.
        if self.is_jumping:
            next(self.iter_z)

    def turn(self, left=True):
        self.cam = self.cam @ (self.left if left else self.right)

    def move(self, direction, strafe=False):
        next_step = self.pos + direction * self.speed * (self.cam[0] @ self.perp if strafe else self.cam[0])

        if self.game_map[next_step[0], self.pos[1]] == 0:
            self.pos[0] = next_step[0]

        if self.game_map[self.pos[0], next_step[1]] == 0:
            self.pos[1] = next_step[1]

        if self.game_map[next_step[0], self.pos[1]] == 3:
            self.pos[0] = next_step[0]

        if self.game_map[self.pos[0], next_step[1]] == 3:
            self.pos[1] = next_step[1]
            

    #--------------------- Game mechanics ---------------------
    def getDamage(self, damage):
        self.hp -= damage

        if self.hp <= 0:
            exit()  # Game over (TODO: Change this?)
    
    def getHeal(self, heal):
        self.hp += heal

        if self.hp > 100:
            self.hp = 100   # Max HP is 100

    def getAmmo(self, ammo):
        self.ammo += ammo
        if self.ammo > 50:
            self.ammo = 100  # Max ammo is 100
            
    def shoot(self):
        self.ammo -= 1

        if self.ammo < 0:
            self.ammo = 0
