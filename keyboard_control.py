import numpy as np
from pygame.locals import *
import pygame

from snake_env import SnakeEnv
import time


num_agents = 3
e = SnakeEnv(num_agents=num_agents, num_fruits=3)
e.render()

while True:
    actions = None
    index = 0

    while True:
        pygame.event.pump()
        keys = pygame.key.get_pressed()
        actions = np.ones(num_agents) * -1

        if np.any(keys[49:58]):
            index = keys[49:58].index(1)
            if index > num_agents:
                index = 0

        if (keys[K_RIGHT]):
            actions[index] = 0
            break  

        if (keys[K_LEFT]):
            actions[index] = 1
            break  

        if (keys[K_UP]):
            actions[index] = 2
            break  

        if (keys[K_DOWN]):
            actions[index] = 3
            break  

    e.render()

    obs, r, done, _ = e.step(actions)

    if done:
        e.reset()

    actions = None
    time.sleep(25.0 / 1000.0)

