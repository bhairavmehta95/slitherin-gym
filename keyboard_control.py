from pygame.locals import *
import pygame
from snake_env import SnakeEnv
import time

e = SnakeEnv() 
e.render()  

while True:
    e._pygame_init()
    actions = None
    while actions is None:
        pygame.event.pump()
        keys = pygame.key.get_pressed() 

        if (keys[K_RIGHT]):
            actions = [0]

        if (keys[K_LEFT]):
            actions = [1]

        if (keys[K_UP]):
            actions = [2]

        if (keys[K_DOWN]):
            actions = [3]
    
    e.render()
    
    obs, r, done, _ = e.step(actions)

    if done:
        e.reset()
    
    actions = None
    time.sleep(25.0 / 1000.0)
    
