import math
import gym
from gym import spaces, logger
from gym.utils import seeding
import numpy as np
from copy import deepcopy

from pygame.locals import *
import pygame
import time
from copy import deepcopy


class SnakeEnv(gym.Env):
    PLAYER_COLORS = [
        (0, 255, 0),
        (0, 0, 255),
        (255, 255, 0),
        (255, 0, 255),
    ]

    class Player:
        def __init__(self, x, y, spacing, length=3, direction=0):
            self.init_length = length
            self.length = length

            self.direction = direction
            print('Direction: {}'.format(direction))

            self.update_count_max = 2
            self.update_count = 0
            self.spacing = spacing
            self.step = spacing

            self.x = [x]
            self.y = [y]
            for i in range(0, 2000): 
               self.x.append(-1)
               self.y.append(-1)

            print('Direction {} Self Spacing {}'.format(self.direction, self.spacing))
     
           # initial positions, no collision.
            if self.direction == 0:
                self.x[1] = x - (1 * self.spacing)
                self.x[2] = x - (2 * self.spacing)
                self.y[1] = y
                self.y[2] = y

            if self.direction == 1:
                self.x[1] = x + (1 * self.spacing)
                self.x[2] = x + (2 * self.spacing)
                self.y[1] = y
                self.y[2] = y

            if self.direction == 2:
                self.y[1] = y + (1 * self.spacing)
                self.y[2] = y + (2 * self.spacing)
                self.x[1] = x
                self.x[2] = x

            if self.direction == 3:
                self.y[1] = y - (1 * self.spacing)
                self.y[2] = y - (2 * self.spacing)
                self.x[1] = x
                self.x[2] = x

        def _reset(self, x, y, direction):
            self.length = self.init_length

            self.update_count = 0
            self.direction = direction

            self.x = [x]
            self.y = [y]
            for i in range(0, 2000): 
               self.x.append(-1)
               self.y.append(-1)


            # initial positions, no collision.
            if self.direction == 0:
                self.x[1] = x - (1 * self.spacing)
                self.x[2] = x - (2 * self.spacing)
                self.y[1] = y
                self.y[2] = y

            if self.direction == 1:
                self.x[1] = x + (1 * self.spacing)
                self.x[2] = x + (2 * self.spacing)
                self.y[1] = y
                self.y[2] = y

            if self.direction == 2:
                self.y[1] = y - (1 * self.spacing)
                self.y[2] = y - (2 * self.spacing)
                self.x[1] = x
                self.x[2] = x

            if self.direction == 3:
                self.y[1] = y + (1 * self.spacing)
                self.y[2] = y + (2 * self.spacing)
                self.x[1] = x
                self.x[2] = x

            print(self.x[0:3], self.y[0:3])


        def _act(self, action):
            if action == 0:
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
     
                self.update_count = 0
     

        def _draw(self, surface, image):
            for i in range(0,self.length):
                surface.blit(image, (self.x[i], self.y[i]))


    def __init__(self, num_players=2, num_fruits=2, window_dimension=616, spacing=22, init_length=3):
        self._running = True

        self._display_surf = None
        self._image_surf = None
        self._fruit_surf = None

        self.players = []
        self.fruits = []
        self.num_players = num_players
        self.active_players = num_players
        self.num_fruits = num_fruits
        self.init_length = init_length

        self.window_dimension = window_dimension 
        self.spacing = spacing

        assert self.window_dimension % self.spacing == 0, "window_dimension needs to be a multiple of spacing"

        self.max_spawn_idx = self.window_dimension / self.spacing - self.init_length
        for i in range(self.num_players):
            player = self._create_player(i, self.init_length) 
            self.players.append(player)

        self.killed = [False] * self.num_players

        # Initialize goals
        for f in range(num_fruits):
            self.fruits.append(self._generate_goal())


    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]


    def step(self, actions):
        new_obs = []
        killed_on_step = [False] * self.num_players
        rewards = [0.0] * self.num_players

        for i, a in enumerate(actions):
            if self.killed[i]: continue

            self.players[i]._act(a)
            self.players[i]._update()        

        for i, p in enumerate(self.players):
            # Did a snake eat an apple?
            if self.killed[i]: continue 

            for len_idx in range(0, p.length):
                for f_i, f in enumerate(self.fruits):
                    if self._check_collision(f[0], f[1], p.x[len_idx], p.y[len_idx]):
                        self.fruits[f_i] = self._generate_goal() 
                        p.length = p.length + 1
                        rewards[i] = 1.0

            # does snake collide with itself?
            for len_idx in range(2, p.length):
                if self._check_collision(p.x[0], p.y[0], p.x[len_idx], p.y[len_idx]):
                    killed_on_step[i] = True
                    print("collide w self")

            # does snake hit a wall?
            if p.x[0] < self.spacing or p.y[0] < self.spacing:
                killed_on_step[i] = True

            elif p.x[0] >= self.window_dimension - self.spacing or \
                 p.y[0] >= self.window_dimension - self.spacing:
                killed_on_step[i] = True

            # does snake collide with another agent?
            for agent_i in range(i + 1, len(self.players)):
                agent = self.players[agent_i]
                for i_player_len in range(0, agent.length):
                    if self._check_collision(p.x[0], p.y[0], agent.x[i_player_len], agent.y[i_player_len]):
                        killed_on_step[i] = True
                        killed_on_step[agent_i] = True

        for i, k in enumerate(killed_on_step):
            if k: 
                rewards[i] = -1.0
                self.active_players -= 1
                self.killed[i] = True

        done = False
        if self.active_players == 0:
            done = True

        for i in range(self.num_players):
            ob = self._generate_obs(i)
            new_obs.append(ob)

        # print(self.active_players)
        return deepcopy(new_obs), deepcopy(rewards), done, {}


    def render(self, mode='human'):
        if self._pygame_init() == False:
            self._running = False

        self._draw_env()

        for i, f in enumerate(self.fruits):
            self._pygame_draw(self._display_surf, self._fruit_surf, f)

        for i, p in enumerate(self.players):
            if self.killed[i]: continue
            p._draw(self._display_surf, self._player_surfs[p.color_i])

        pygame.display.flip()


    def reset(self):
        for i, p in enumerate(self.players):
            self.killed[i] = False

            x = np.random.randint(1, self.max_spawn_idx - 1) * self.spacing
            y = np.random.randint(1, self.max_spawn_idx - 1) * self.spacing
            direction = np.random.randint(0, 4)

            p._reset(x, y, direction)

        for f in range(self.num_fruits):
            self.fruits[f] = self._generate_goal()

        self.active_players = self.num_players
    

    def close(self):
        pygame.quit()


    def _check_collision(self, x1, y1, x2, y2):
        bounding_box = self.spacing - 10


        if x1 >= x2 and x1 <= x2 + bounding_box:
            if y1 >= y2 and y1 <= y2 + bounding_box:
                print(x1, x2, y1, y2)
                return True

        return False


    def _create_player(self, i, init_length):
        x = np.random.randint(init_length, self.max_spawn_idx - init_length) * self.spacing
        y = np.random.randint(init_length, self.max_spawn_idx - init_length) * self.spacing
        direction = np.random.randint(0, 4)
        
        player = self.Player(x, y, self.spacing, direction=direction, length=init_length)
        player.color_i = i % len(self.PLAYER_COLORS)

        return deepcopy(player)


    def _draw_env(self):
        self._display_surf.fill((0,0,0))

        for i in range(0, self.window_dimension, self.spacing):
            self._display_surf.blit(self._wall_surf, (0, i))
            self._display_surf.blit(self._wall_surf, (self.window_dimension - self.spacing, i))

        for i in range(0, self.window_dimension, self.spacing):
            self._display_surf.blit(self._wall_surf, (i, 0))
            self._display_surf.blit(self._wall_surf, (i, self.window_dimension - self.spacing))


    def _generate_goal(self):
        x = np.random.randint(1, self.max_spawn_idx - 1) * self.spacing 
        y = np.random.randint(1, self.max_spawn_idx - 1) * self.spacing

        return [x, y]


    def _generate_obs(self, agent):
        obs = np.zeros((self.window_dimension, self.window_dimension))

        if self.killed[agent]: return -1 * np.ones((self.window_dimension, self.window_dimension))

        for i in range(self.players[agent].length):
            obs[self.players[agent].x[i]][self.players[agent].y[i]] = 1

        for i, p in enumerate(self.players):
            if self.killed[i]: continue 
            for j in range(p.length):
                obs[p.x[j]][p.y[j]] = 2

        for i, f in enumerate(self.fruits):
            obs[f[0]][f[1]] = 3

        obs[:][0] = -1
        obs[:][self.window_dimension - 1] = -1

        obs[0][:] = -1
        obs[self.window_dimension - 1][:] = -1

        return deepcopy(obs)


    def _pygame_draw(self, surface, image, pos):
        surface.blit(image, (pos[0], pos[1])) 


    def _pygame_init(self):
        pygame.init()
        self._display_surf = pygame.display.set_mode((self.window_dimension, self.window_dimension), pygame.HWSURFACE)
        self._player_surfs = []
        self._running = True

        for i, p in enumerate(self.players):
            image_surf = pygame.Surface([self.spacing - 4, self.spacing - 4])
            image_surf.fill(self.PLAYER_COLORS[i % len(self.PLAYER_COLORS)])
            self._player_surfs.append(image_surf)

        self._fruit_surf = pygame.Surface([self.spacing - 4, self.spacing - 4])
        self._fruit_surf.fill((255, 0, 0))

        self._wall_surf = pygame.Surface([self.spacing - 4, self.spacing - 4])
        self._wall_surf.fill((255, 255, 255))


if __name__ == '__main__':
    e = SnakeEnv() 
    e.render()  

    while True:
        e._pygame_init()
        actions = None
        while actions is None:
            pygame.event.pump()
            keys = pygame.key.get_pressed() 

            if (keys[K_RIGHT]):
                actions = [0, 0]

            if (keys[K_LEFT]):
                actions = [1, 1]

            if (keys[K_UP]):
                actions = [2, 2]

            if (keys[K_DOWN]):
                actions = [3, 3]
 
        # actions = [np.random.randint(0,4)]
        
        e.render()
        
        obs, r, done, _ = e.step(actions)
        print(r)

        if done:
            e.reset()
        
        actions = None
        time.sleep (25.0 / 1000.0);
