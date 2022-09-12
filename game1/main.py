import pygame
import sys
from timeit import default_timer as timer
from level import Level
from settings import *

pygame.init()
screen = pygame.display.set_mode((screen_width, screen_height))
clock = pygame.time.Clock()
level = Level(level_map, screen)

while True:
    ti = timer()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
    screen.fill('black')
    level.run()

    pygame.display.update()

    clock.tick(60)
    tf = timer() - ti
    print(1/tf)