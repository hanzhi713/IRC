import pygame
import sys
pygame.init()
screen = pygame.display.set_mode((800, 630))
pygame.display.set_caption("Molecules")
from math import *


class Point:

    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def get_distance(self, target=None):
        if target is None: target = Point(0, 0)
        return ((self.x - target.x) ** 2 + (self.y - target.y) ** 2) ** 0.5


class Circle:

    def __init__(self, center=Point(0, 0), radius=10):
        self.center = center
        self.radius = radius

    def draw(self, screen, color):
        pygame.draw.circle(screen, color, (int(self.center.x), int(self.center.y)), self.radius)

    # return True if two circles overlap
    def if_collide(self, cir):
        if self.center.get_distance(cir.center) < self.radius + cir.radius:
            return True
        return False


class Molecule:

    def __init__(self, x=0, y=0, angle=0, radius=12):
        self.x = x
        self.y = y
        # collide box slightly bigger than the picture
        self.circle = Circle(Point(self.x, self.y), radius + 1)
        self.actual_radius = radius
        self.image = pygame.transform.smoothscale(pygame.image.load("Interesting.png"), (radius*2, radius*2))
        self.angle = angle
        self.left_edge = self.circle.radius
        self.right_edge = 800 - self.circle.radius
        self.top_edge = self.circle.radius
        self.bottom_edge = 600 - self.circle.radius

    # move with a given distance and an angle. Checking collision in the meantime
    def move(self, dist, others):
        self.circle.draw(screen, (0, 0, 0))
        self.x += dist * cos(self.angle)
        self.y -= dist * sin(self.angle)
        self.circle.center.x = self.x
        self.circle.center.y = self.y
        if self.x >= self.right_edge:
            if self.angle < 0.5*pi or self.angle > 1.5*pi:
                self.angle = pi - self.angle
        if self.x <= self.left_edge:
            if 0.5*pi < self.angle < 1.5*pi:
                self.angle = pi - self.angle
        if self.y >= self.bottom_edge:
            if pi < self.angle < 2*pi:
                self.angle = -self.angle
        if self.y <= self.top_edge:
            if 0 < self.angle < pi:
                self.angle = -self.angle
        if self.angle < 0:
            self.angle += 2*pi
        # detect collisions between any two molecules
        for one in others:
            if self is not one:
                if self.circle.if_collide(one.circle):
                    # if collide, exchange their velocity vectors
                    (self.angle, one.angle) = (one.angle, self.angle)
                    # move them immediately to avoid repetitive collision detection
                    self.abs_move(dist)
                    one.abs_move(dist)
        screen.blit(self.image, (self.x-self.actual_radius, self.y-self.actual_radius))
        pygame.display.flip()

    # move without concerning any collision
    def abs_move(self, dist):
        self.circle.draw(screen, (0, 0, 0))
        self.x += dist * cos(self.angle)
        self.y -= dist * sin(self.angle)
        self.circle.center.x = self.x
        self.circle.center.y = self.y
        screen.blit(self.image, (self.x-self.actual_radius, self.y-self.actual_radius))
        pygame.display.flip()
import random
import time
molecule_list = []
number = 25
# instantiate molecule objects and generate distinct initial positions
while len(molecule_list) < number:
    flag = False
    new = Molecule(random.randint(0, 765), random.randint(0, 565), radians(random.randint(0,359)), 18)
    for obj in molecule_list:
        if new.circle.if_collide(obj.circle):
            flag = True
            break
    if flag:
        continue
    molecule_list.append(new)
my_font1 = pygame.font.SysFont("Calibri", 20, True)
my_font2 = pygame.font.SysFont("Calibri", 20, True)
# main game loop
vel = 1
instructions = ["Instructions:", "Use the key UP and DOWN to change the velocity",
                "If velocity is negative, then molecules will be able to move out of the window"]
for ins in instructions:
    print(ins)
frames = 0
FPS = my_font2.render("FPS: Calculating", True, (0, 255, 0))
t0 = time.clock()
while 1:
    for molecule in molecule_list:
        molecule.move(vel, molecule_list)
    pygame.draw.rect(screen, (0, 0, 0), (700, 605, 100, 30))
    pygame.draw.line(screen, (255, 100, 0), (0, 602), (800, 602), 2)
    text_surf = my_font1.render("Velocity: {0}".format(vel), True, (0, 255, 0))
    frames += 1
    pygame.draw.rect(screen, (0, 0, 0), (0, 605, 150, 30))
    if frames % 30 == 0:
        frames = 0
        FPS = my_font2.render("FPS: {0}".format(round(30 / (time.clock()- t0),1)), True, (0, 255, 0))
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
