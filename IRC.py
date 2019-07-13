import pygame
import sys
from math import *
import random
import time
import os


class Vec:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vec(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vec(self.x - other.x, self.y - other.y)

    def __mul__(self, other):
        if type(other) == int or type(other) == float:
            return Vec(self.x * other, self.y * other)
        elif type(other) == Vec:
            return self.dot(other)

    def __truediv__(self, other):
        if type(other) == int or type(other) == float:
            return Vec(self.x / other, self.y / other)

    def __abs__(self):
        return sqrt(self.x ** 2 + self.y ** 2)

    def angle(self):
        return atan2(self.y, self.x)

    def dot(self, other):
        return self.x * other.x + self.y * other.y

    def __str__(self):
        return str((self.x, self.y))


class Molecule:

    def __init__(self, id=0, pos=Vec(0, 0), vel=Vec(0, 0), radius=12, w=800, h=600):
        self.pos = pos
        self.vel = vel
        self.ppos = pos
        self.id = id
        self.radius = radius
        self.mass = radius * radius * pi
        self.image = pygame.transform.smoothscale(pygame.image.load(os.path.join(os.path.dirname(__file__), "Interesting.png")), (radius * 2, radius * 2))
        self.left_edge = radius
        self.right_edge = w - radius
        self.top_edge = radius
        self.bottom_edge = h - radius
        self.grid_r_idx = -1
        self.grid_c_idx = -1

    # move with a given distance and an angle. Checking collision in the meantime
    def move(self, vel_multiplier, others):
        self.ppos = self.pos
        self.pos += self.vel * vel_multiplier
        if self.pos.x >= self.right_edge:
            if self.vel.x > 0:
                self.vel.x = -self.vel.x
        if self.pos.x <= self.left_edge:
            if self.vel.x < 0:
                self.vel.x = -self.vel.x
        if self.pos.y >= self.bottom_edge:
            if self.vel.y > 0:
                self.vel.y = - self.vel.y
        if self.pos.y <= self.top_edge:
            if self.vel.y < 0:
                self.vel.y = -self.vel.y

        # detect collisions between any two molecules
        for one in others:
            if self is not one:
                cent_vector = self.pos - one.pos
                dist = abs(cent_vector)
                if dist <= self.radius + one.radius:
                    unit_cent = cent_vector / dist
                    a = ((unit_cent * 2) * (self.vel - one.vel)) / (1 / self.mass + 1 / one.mass)
                    self.vel = self.vel - unit_cent * (a / self.mass)
                    one.vel = one.vel + unit_cent * (a / one.mass)
                    self.abs_move(vel_multiplier)
                    one.abs_move(vel_multiplier)
                    pass

    def update_boundary(self, w, h):
        self.right_edge = w - self.radius
        self.bottom_edge = h - self.radius

    # move without concerning any collision
    def abs_move(self, vel_multiplier):
        self.ppos = self.pos
        self.pos += self.vel * vel_multiplier

    def draw(self, screen):
        screen.blit(self.image, (self.pos.x - self.radius, self.pos.y - self.radius))


if __name__ == "__main__":
    instructions = ["Instructions:", "Use the key UP and DOWN to change the velocity",
                    "If velocity is negative, molecules will be able to move out of the window"]
    for ins in instructions:
        print(ins)


    def parse_int(prompt, default):
        temp = input(prompt)
        if len(temp) == 0:
            return default
        else:
            while True:
                try:
                    num = int(temp)
                    return num
                except ValueError:
                    print("Please enter an integer")


    molecule_list = []
    number = parse_int("Please specify the total number of molecules (25):", 25)
    r_lower = parse_int("Please enter the lower bound of the radius (10):", 10)
    r_upper = parse_int("Please enter the upper bound of the radius (20):", 20)

    grid_size = r_upper * 2
    grid_row = 630 // grid_size
    if 630 % grid_size != 0:
        grid_row += 1
    grid_col = 800 // grid_size
    if 800 % grid_size != 0:
        grid_col += 1
    grid = [[] for i in range(0, grid_row * grid_col)]

    # instantiate molecule objects and generate distinct initial positions
    while len(molecule_list) < number:
        flag = False
        radius = random.randint(r_lower, r_upper)
        new = Molecule(id=len(molecule_list), pos=Vec(random.randint(0, 765), random.randint(0, 565)),
                       vel=Vec(random.random() * 2 - 1, random.random() * 2 - 1), radius=radius)
        for obj in molecule_list:
            if abs(new.pos - obj.pos) <= new.radius + obj.radius + 2:
                flag = True
                break
        if flag:
            continue
        molecule_list.append(new)
        r_idx = int(new.pos.y // grid_size)
        c_idx = int(new.pos.x // grid_size)
        new.grid_r_idx = r_idx
        new.grid_c_idx = c_idx
        grid[r_idx * grid_col + c_idx].append(new)
    # main game loop
    vel = 1
    ticks = 120
    multiplier = 5
    frames = 0
    clock = pygame.time.Clock()
    w, h = 800, 630
    pw, ph = w, h
    pygame.init()
    screen = pygame.display.set_mode((w, h), pygame.RESIZABLE)
    pygame.display.set_caption("Molecules")

    t0 = time.clock()
    my_font = pygame.font.SysFont("Calibri", 20, True)
    FPS = my_font.render("FPS: Calculating", True, (0, 255, 0))
    while True:
        dt = clock.tick(ticks)
        for i in range(len(molecule_list)):
            # neighbors
            neighbors = []
            for a in range(-1, 2):
                for b in range(-1, 2):
                    temp_r = molecule_list[i].grid_r_idx + a
                    temp_c = molecule_list[i].grid_c_idx + b
                    if temp_r < 0 or temp_c < 0 or temp_r >= grid_row or temp_c >= grid_row:
                        continue
                    neighbors.extend(grid[temp_r * grid_col + temp_c])

            molecule_list[i].move(vel * multiplier * dt / ticks, neighbors)

        # update grid
        if w != pw or h != ph:
            grid_row = h // grid_size
            if h % grid_size != 0:
                grid_row += 1
            grid_col = w // grid_size
            if w % grid_size != 0:
                grid_col += 1
            grid = [[] for i in range(0, grid_row * grid_col)]
            pw, ph = w, h
        else:
            for i in range(len(grid)):
                grid[i].clear()

        for i in range(len(molecule_list)):
            r_idx = int(molecule_list[i].pos.y // grid_size)
            c_idx = int(molecule_list[i].pos.x // grid_size)
            molecule_list[i].grid_r_idx = r_idx
            molecule_list[i].grid_c_idx = c_idx
            grid[r_idx * grid_col + c_idx].append(molecule_list[i])

        screen.fill((0, 0, 0))

        for m in molecule_list:
            m.draw(screen)

        pygame.draw.line(screen, (255, 100, 0), (0, h - 28), (w, h - 28), 2)
        Vel_Text = my_font.render("Velocity: {0}".format(vel), True, (0, 255, 0))
        frames += 1
        if frames % 30 == 0:
            frames = 0
            FPS = my_font.render("FPS: {0}".format(round(30 / (time.clock() - t0), 1)), True, (0, 255, 0))
            t0 = time.clock()
        screen.blit(FPS, (0, h - 25))
        screen.blit(Vel_Text, (w - 110, h - 25))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    vel += 1
                elif event.key == pygame.K_DOWN:
                    vel -= 1
            elif event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
                pygame.display.flip()
                w, h = event.w, event.h
                for m in molecule_list:
                    m.update_boundary(w, h - 30)
