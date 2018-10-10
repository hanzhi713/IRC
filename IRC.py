import pygame
import sys
from math import *
import random
import time


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

    @staticmethod
    def if_collide(cir1, cir2):
        if (cir1.x - cir2.x) ** 2 + (cir1.y - cir2.y) ** 2 <= (cir1.radius + cir2.radius) ** 2:
            return True

    def __init__(self, id=0, pos=Vec(0, 0), vel=Vec(0, 0), radius=12):
        self.pos = pos
        self.vel = vel
        self.ppos = pos
        self.id = id
        self.radius = radius
        self.mass = radius * radius * pi
        self.image = pygame.transform.smoothscale(pygame.image.load("interesting.png"), (radius * 2, radius * 2))
        self.left_edge = radius
        self.right_edge = 800 - radius
        self.top_edge = radius
        self.bottom_edge = 600 - radius

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

    # move without concerning any collision
    def abs_move(self, vel_multiplier):
        self.ppos = self.pos
        self.pos += self.vel * vel_multiplier

    def draw(self, screen):
        screen.blit(self.image, (self.pos.x - self.radius, self.pos.y - self.radius))


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((800, 630))
    pygame.display.set_caption("Molecules")

    instructions = ["Instructions:", "Use the key UP and DOWN to change the velocity",
                    "If velocity is negative, then molecules will be able to move out of the window"]
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

    # instantiate molecule objects and generate distinct initial positions
    while len(molecule_list) < number:
        flag = False
        radius = random.randint(r_lower, r_upper)
        new = Molecule(id=len(molecule_list), pos=Vec(random.randint(0, 765), random.randint(0, 565)),
                       vel=Vec(random.random() * 2 - 1, random.random() * 2 - 1), radius=radius)
        for obj in molecule_list:
            if abs(new.pos - obj.pos) <= new.radius + obj.radius:
                flag = True
                break
        if flag:
            continue
        molecule_list.append(new)
    my_font1 = pygame.font.SysFont("Calibri", 20, True)
    my_font2 = pygame.font.SysFont("Calibri", 20, True)
    # main game loop
    vel = 1
    multiplier = 1 / 30
    frames = 0
    FPS = my_font2.render("FPS: Calculating", True, (0, 255, 0))
    t0 = time.clock()

    clock = pygame.time.Clock()

    while True:
        dt = clock.tick(240)
        for i in range(len(molecule_list)):
            molecule_list[i].move(vel * multiplier * dt, molecule_list[i + 1:])

        screen.fill((0, 0, 0))

        for m in molecule_list:
            m.draw(screen)

        pygame.draw.rect(screen, (0, 0, 0), (700, 605, 100, 30))
        pygame.draw.line(screen, (255, 100, 0), (0, 602), (800, 602), 2)
        text_surf = my_font1.render("Velocity: {0}".format(vel), True, (0, 255, 0))
        frames += 1
        pygame.draw.rect(screen, (0, 0, 0), (0, 605, 150, 30))
        if frames % 30 == 0:
            frames = 0
            FPS = my_font2.render("FPS: {0}".format(round(30 / (time.clock() - t0), 1)), True, (0, 255, 0))
            t0 = time.clock()
        screen.blit(FPS, (0, 605))
        screen.blit(text_surf, (690, 605))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    vel += 1
                elif event.key == pygame.K_DOWN:
                    vel -= 1
