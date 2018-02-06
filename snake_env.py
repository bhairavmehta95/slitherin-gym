import math
import gym
from gym import spaces, logger
from gym.utils import seeding
import numpy as np


class SnakeEnv(gym.Env):
    PLAYER_COLORS = [
        (0, 255, 0),
        (0, 0, 255),
        (255, 255, 0),
        (255, 0, 255),
    ]

    class Player:
        def __init__(self, x, y, sprite_size, length=3, direction=0):
           self.length = length
           self.direction = direction
         
           self.update_count_max = 2
           self.update_count = 0
           self.sprite_size = sprite_size
           self.step = sprite_size

           self.x = [x]
           self.y = [y]
           for i in range(0, 2000): 
               self.x.append(-1)
               self.y.append(-1)
     
           # initial positions, no collision.
           self.x[1] = 1 * self.sprite_size
           self.x[2] = 2 * self.sprite_size
     
        def _update(self):
            self.update_count = self.update_count + 1
            if self.update_count > self.update_count_max:
     
                # update previous positions
                for i in range(self.length - 1, 0, -1):
                    self.x[i] = self.x[i-1]
                    self.y[i] = self.y[i-1]
     
                # update position of head of snake
                if self.direction == 0:
                    self.x[0] = self.x[0] + self.step
                if self.direction == 1:
                    self.x[0] = self.x[0] - self.step
                if self.direction == 2:
                    self.y[0] = self.y[0] - self.step
                if self.direction == 3:
                    self.y[0] = self.y[0] + self.step
     
                self.updateCount = 0
     
        def _act(self, action):
            if action == 0 
                if self.direction == 1:
                    return
                self.direction = 0

            elif action == 1:
                if self.direction == 0:
                    return
                self.direction = 1

            elif action == 2:
                if self.direction == 3:
                    return
                self.direction = 2

            elif action == 3:
                if self.direction == 2:
                    return
                self.direction = 3

            else:
                # Should never reach
                pass
     
        def _draw(self, surface, image):
            for i in range(0,self.length):
                surface.blit(image, (self.x[i], self.y[i]))


    def __init__(self, num_players=3, num_fruits=2, window_dimension=616, sprite_size=22):
        self._running = True
        self._display_surf = None
        self._image_surf = None
        self._apple_surf = None
        self.players = []
        self.fruits = []
        self.num_players = num_players
        self.window_dimension = window_dimension 
        self.sprite_size = sprite_size

        assert self.window_dimension % self.sprite_size == 0

        self.total_length = self.window_dimension / self.sprite_size

        for p_idx in range(self.num_players):
            x = np.randint(1, self.total_length - 1) * self.sprite_size
            y = np.randint(1, self.total_length - 1) * self.sprite_size
            direction = np.randint(0, 4)

            player = Player(x, y, sprite_size, direction=direction)
            player.color_idx = p_idx % len(self.PLAYER_COLORS)

        self.killed = [False] * num_players

        # Initialize goals
        for f in range(num_fruits):
            self.fruits.append(self._generate_goal())


    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]


    def step(self, actions):
        pass


    def render(self, mode='human'):
        pass


    def reset(self):
        pass
    

    def close(self):
        pygame.quit()


    def _check_collision(self, x1, y1, x2, y2):
        bounding_box = self.sprite_size - 1

        if x1 >= x2 and x1 <= x2 + bounding_box:
            if y1 >= y2 and y1 <= y2 + bounding_box:
                return True

        return False


    def _generate_goal(self):
        x = np.randint(1, self.total_length - 1) * self.sprite_size, 
        y = np.randint(1, self.total_length - 1) * self.sprite_size

        return [x, y]
