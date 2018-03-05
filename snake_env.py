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
    AGENT_COLORS = [
        (0, 255, 0),
        (0, 0, 255),
        (255, 255, 0),
        (255, 0, 255),
    ]

    class Agent:
        def __init__(self, x, y, spacing, length=3, direction=0):
            self.init_length = length
            self.length = length

            self.direction = direction

            self.update_count_max = 2
            self.update_count = 0
            self.spacing = spacing
            self.step = spacing

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
                for i in range(self.length, 0, -1):
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


    def __init__(self, num_agents=2, num_fruits=3, window_dimension=616, spacing=22, init_length=3):
        self._running = True

        self._display_surf = None
        self._image_surf = None
        self._fruit_surf = None

        self.agents = []
        self.fruits = []
        self.num_agents = num_agents
        self.active_agents = num_agents
        self.num_fruits = num_fruits
        self.init_length = init_length

        self.window_dimension = window_dimension
        self.spacing = spacing

        assert self.window_dimension % self.spacing == 0, "window_dimension needs to be a multiple of spacing"

        self.max_spawn_idx = self.window_dimension / self.spacing - self.init_length
        for i in range(self.num_agents):
            agent = self._create_agent(i, self.init_length)
            self.agents.append(agent)

        self.killed = [False] * self.num_agents

        # Initialize goals
        for f in range(num_fruits):
            self.fruits.append(self._generate_goal())


        self.observation_space = spaces.Box(low=-1, high=3, shape=(self.num_agents,    self.window_dimension // self.spacing, self.window_dimension // self.spacing))

        self.action_space = spaces.Tuple(
            [spaces.Discrete(4) for i in range(self.num_agents)]
        )

        self.reward_range = (-1.0, 1.0)

        self._pygame_init()


    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]


    def step(self, actions):
        new_obs = []
        killed_on_step = [False] * self.num_agents
        rewards = [0.0] * self.num_agents

        for i, a in enumerate(actions):
            if self.killed[i]: continue
            self.agents[i]._act(a)
            self.agents[i]._update()

        for i, p in enumerate(self.agents):
            # Did a snake eat an apple?
            if self.killed[i]: continue

            for len_idx in range(0, p.length):
                for f_i, f in enumerate(self.fruits):
                    if self._check_collision(f[0], f[1], p.x[len_idx], p.y[len_idx]):
                        self.fruits[f_i] = self._generate_goal()
                        p.length = p.length + 1
                        rewards[i] = 1.0

            # does snake collide with itself?
            for len_idx in range(1, p.length):
                if self._check_collision(p.x[0], p.y[0], p.x[len_idx], p.y[len_idx]):
                    killed_on_step[i] = True

            # does snake hit a wall?
            if p.x[0] < self.spacing or p.y[0] < self.spacing:
                killed_on_step[i] = True

            elif p.x[0] >= self.window_dimension - self.spacing or \
                 p.y[0] >= self.window_dimension - self.spacing:
                killed_on_step[i] = True

            # does snake collide with another agent?
            for agent_i in range(i + 1, len(self.agents)):
                agent = self.agents[agent_i]
                for i_agent_len in range(0, agent.length):
                    if self._check_collision(p.x[0], p.y[0], agent.x[i_agent_len], agent.y[i_agent_len]):
                        killed_on_step[i] = True
                        killed_on_step[agent_i] = True

        for i, k in enumerate(killed_on_step):
            if k:
                rewards[i] = -1.0
                self.active_agents -= 1
                self.killed[i] = True

        done = False
        if self.active_agents == 0:
            done = True

        for i in range(self.num_agents):
            ob = self._generate_obs(i)
            new_obs.append(ob)

        return deepcopy(new_obs), deepcopy(rewards), done, {}


    def render(self, mode='human'):
        if self._pygame_init() == False:
            self._running = False

        self._draw_env()

        for i, f in enumerate(self.fruits):
            self._pygame_draw(self._display_surf, self._fruit_surf, f)

        for i, p in enumerate(self.agents):
            if self.killed[i]: continue
            p._draw(self._display_surf, self._agent_surfs[p.color_i])

        pygame.display.flip()


    def reset(self):
        for i, p in enumerate(self.agents):
            self.killed[i] = False

            x = np.random.randint(1, self.max_spawn_idx - 1) * self.spacing
            y = np.random.randint(1, self.max_spawn_idx - 1) * self.spacing
            direction = np.random.randint(0, 1) # TODO: Fix vertical spawning

            p._reset(x, y, direction)

        for f in range(self.num_fruits):
            self.fruits[f] = self._generate_goal()

        self.active_agents = self.num_agents

        for i in range(self.num_agents):
            ob = self._generate_obs(i)
            new_obs.append(ob)

        return deepcopy(new_obs)


    def close(self):
        pygame.quit()


    def _check_collision(self, x1, y1, x2, y2):
        bounding_box = 20

        if x1 >= x2 and x1 <= x2 + bounding_box:
            if y1 >= y2 and y1 <= y2 + bounding_box:
                return True

        return False


    def _create_agent(self, i, init_length):
        x = np.random.randint(init_length, self.max_spawn_idx - init_length) * self.spacing
        y = np.random.randint(init_length, self.max_spawn_idx - init_length) * self.spacing
        direction = np.random.randint(0, 1) # TODO: Fix Vertical spawning

        agent = self.Agent(x, y, self.spacing, direction=direction, length=init_length)
        agent.color_i = i % len(self.AGENT_COLORS)

        return deepcopy(agent)


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
        obs = np.zeros((self.window_dimension // self.spacing, self.window_dimension // self.spacing))

        if self.killed[agent]: return -1 * np.ones((self.window_dimension // self.spacing, self.window_dimension // self.spacing))

        for i in range(self.agents[agent].length):
            obs[self.agents[agent].x[i] // self.spacing][self.agents[agent].y[i] // self.spacing] = 1

        for i, p in enumerate(self.agents):
            if self.killed[i]: continue
            for j in range(p.length):
                obs[p.x[j] // self.spacing ][p.y[j] // self.spacing ] = 2

        for i, f in enumerate(self.fruits):
            obs[f[0] // self.spacing ][f[1] // self.spacing ] = 3

        obs[:][0] = -1
        obs[:][self.window_dimension // self.spacing - 1] = -1

        obs[0][:] = -1
        obs[self.window_dimension // self.spacing - 1][:] = -1

        return deepcopy(obs)


    def _pygame_draw(self, surface, image, pos):
        surface.blit(image, (pos[0], pos[1]))


    def _pygame_init(self):
        pygame.init()
        self._display_surf = pygame.display.set_mode((self.window_dimension, self.window_dimension), pygame.HWSURFACE)
        self._agent_surfs = []
        self._running = True

        for i, p in enumerate(self.agents):
            image_surf = pygame.Surface([self.spacing - 4, self.spacing - 4])
            image_surf.fill(self.AGENT_COLORS[i % len(self.AGENT_COLORS)])
            self._agent_surfs.append(image_surf)

        self._fruit_surf = pygame.Surface([self.spacing - 4, self.spacing - 4])
        self._fruit_surf.fill((255, 0, 0))

        self._wall_surf = pygame.Surface([self.spacing - 4, self.spacing - 4])
        self._wall_surf.fill((255, 255, 255))
