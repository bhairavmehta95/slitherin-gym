import math
import gym
from gym import spaces, logger
from gym.utils import seeding
import numpy as np
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
           self.x[1] = 1 * self.spacing
           self.x[2] = 2 * self.spacing


        def _reset(self):
            self.length = length
            self.direction = direction

            self.update_count = 0

            self.x = [x]
            self.y = [y]
            for i in range(0, 2000): 
               self.x.append(-1)
               self.y.append(-1)

            # initial positions, no collision.
            self.x[1] = 1 * self.spacing
            self.x[2] = 2 * self.spacing
         

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
     

        def _draw(self, surface, image):
            for i in range(0,self.length):
                surface.blit(image, (self.x[i], self.y[i]))


    def __init__(self, num_players=3, num_fruits=2, window_dimension=616, spacing=22):
        self._running = True

        self._display_surf = None
        self._image_surf = None
        self._fruit_surf = None

        self.players = []
        self.fruits = []
        self.num_players = num_playerss
        self.num_fruits = num_fruits

        self.window_dimension = window_dimension 
        self.spacing = spacing

        assert self.window_dimension % self.spacing == 0

        self.max_spawn_idx = self.window_dimension / self.spacing
        for i in range(self.num_players):
            player = self._create_player() 
            self.players.append(player)

        self.killed = [False] * self.num_players

        # Initialize goals
        for f in range(num_fruits):
            self.fruits.append(self._generate_goal())


    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]


    def step(self, actions):
        for i, a in enumerate(actions):
            if self.killed[i]: continue

            self.players[i]._act(a)
            self.players[i]._update()

        rewards = [0.0] * self.num_players

        for i, p in enumerate(self.players):
            # Did a snake eat an apple?
            if self.killed[i]: continue 

            for i in range(0, p.length):
                for f_i, f in enumerate(self.fruits):
                    if self._check_collision(f.x, f.y, p.x[i], p.y[i]):
                        self.fruits[f_i] = self._generate_goal() 
                        p.length = p.length + 1
                        rewards[i] = 1.0

            # does snake collide with itself?
            for i in range(2, p.length):
                if self._check_collision(p.x[0], p.y[0], p.x[i], p.y[i]):
                    self.killed[i] = True

            # does snake hit a wall?
            if p.x[0] < self.sprite_size or p.y[0] < self.sprite_size:
                self.killed[i] = True

            elif p.x[0] > self.window_dimension - self.sprite_size or \
                 p.y[0] > self.window_dimension - self.sprite_size:

                self.killed[i] = True

            # does snake collide with another agent?
            for agent_i in range(i + 1, len(self.players)):
                agent = self.players[agent_i]
                for i_player_len in range(0, agent.length):
                    if self._check_collision(p.x[0], p.y[0], agent.x[i_player_len], agent.y[i_player_len]):
                        self.killed[i] = True
                        self.killed[other_player_i] = True

        for i, k in self.killed:
            if k: rewards[i] = -1.0

        done = False
        if self.num_players == 0:
            done = True






    def render(self, mode='human'):
        if self._pygame_init() == False:
            self._running = False

        self._display_surf.fill((0,0,0))

        for i, f in enumerate(self.fruits):
            self._pygame_draw(self._display_surf, self._fruit_surf)

        for i, p in enumerate(self.players):
            if self.killed[i]: continue
            p.draw(self._display_surf, self._player_surfs[p.color_i])

        self._pygame_draw(self._display_surf, self._wall_surf)
        pygame.display.flip()


    def reset(self):
        pass
    

    def close(self):
        pygame.quit()


    def _check_collision(self, x1, y1, x2, y2):
        bounding_box = self.spacing - 1

        if x1 >= x2 and x1 <= x2 + bounding_box:
            if y1 >= y2 and y1 <= y2 + bounding_box:
                return True

        return False


    def _create_player(self):
        x = np.randint(1, self.mac_spawn_i - 1) * self.spacing
        y = np.randint(1, self.mac_spawn_i - 1) * self.spacing
        direction = np.randint(0, 4)
        
        player = Player(x, y, spacing, direction=direction)
        player.color_i = p_i % len(self.PLAYER_COLORS)

        return deepcopy(player)

    def _generate_goal(self):
        x = np.randint(1, self.mac_spawn_i - 1) * self.spacing, 
        y = np.randint(1, self.mac_spawn_i - 1) * self.spacing

        return [x, y]


    def _pygame_init(self):
        pygame.init()
        self._display_surf = pygame.display.set_mode((self.window_dimension, self.window_dimension), pygame.HWSURFACE)
        self._player_surfs = []
        self._running = True

        for i, p in enumerate(self.players):
            image_surf = pygame.Surface([self.spacing - 4, self.spacing - 4])
            image_surf.fill(PLAYER_COLORS[i % len(self.PLAYER_COLORS)])
            self._player_surfs.append(image_surf)

        self._fruit_surf = pygame.Surface([self.spacing - 4, self.spacing - 4])
        self._fruit_surf.fill((255, 0, 0))

        self._wall_surf = pygame.Surface([self.spacing - 4, self.spacing - 4])
        self._wall_surf.fill((255, 255, 255))
