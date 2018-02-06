from pygame.locals import *
from random import randint
import pygame
import time
from copy import deepcopy
 
SPRITE_SIZE = 22

PLAYER_COLORS = [
    (0, 255, 0),
    (0, 0, 255),
    (255, 255, 0),
    (255, 0, 255),
]

class Fruit:
    global SPRITE_SIZE
    step = SPRITE_SIZE
 
    def __init__(self,x,y):
        self.x = x * self.step
        self.y = y * self.step
 
    def draw(self, surface, image):
        surface.blit(image,(self.x, self.y)) 


class Wall:
    global SPRITE_SIZE
    
    def __init__(self, h, w):
        self.h = h
        self.w = w
        self.step = SPRITE_SIZE


    def draw(self, surface, image):
        for i in range(0, self.h, self.step):
            surface.blit(image,(0, i))
            surface.blit(image,(self.w - self.step, i))

        for i in range(0, self.w, self.step):
            surface.blit(image,(i, 0))
            surface.blit(image,(i, self.h - self.step))

 
class Player:
    global SPRITE_SIZE
    step = SPRITE_SIZE
    direction = 0
    length = 3
 
    updateCountMax = 2
    updateCount = 0
 
    def __init__(self, length, x, y):
       self.length = length
       self.x = [x]
       self.y = [y]
       for i in range(0,2000): 
           self.x.append(-1)
           self.y.append(-1)
 
       # initial positions, no collision.
       self.x[1] = 1*SPRITE_SIZE
       self.x[2] = 2*SPRITE_SIZE
 
    def update(self):
        self.updateCount = self.updateCount + 1
        if self.updateCount > self.updateCountMax:
 
            # update previous positions
            for i in range(self.length-1,0,-1):
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
 
    def moveRight(self):
        if self.direction == 1:
            return

        self.direction = 0
 
    def moveLeft(self):
        if self.direction == 0:
            return

        self.direction = 1
 
    def moveUp(self):
        if self.direction == 3:
            return

        self.direction = 2
 
    def moveDown(self):
        if self.direction == 2:
            return

        self.direction = 3 
 
    def draw(self, surface, image):
        for i in range(0,self.length):
            surface.blit(image, (self.x[i], self.y[i])) 
  
class App:
    def __init__(self, num_players=3, num_fruits=2, window_dimension=616, sprite_size=22):
        self._running = True
        self._display_surf = None
        self._image_surf = None
        self._apple_surf = None
        self.players = []
        self.fruits = []
        self.num_players = num_players
        self.window_dimension = 616 
        self.sprite_size = 22
        
        global SPRITE_SIZE

        for p in range(num_players):
            if p == 0:
                x = 22 * (p + 1)
                y = 22 * (p + 1)

            else:
                x = 22 * (p + 10)
                y = 22 * (1)
            
            player = Player(3, x, y)
            player.color_idx = p % len(PLAYER_COLORS)

            if p == 1:
                player.direction = 1

            self.players.append(player)

        self.killed = [False] * num_players

        for f in range(num_fruits):
            self.fruits.append(Fruit(randint(1, 12), randint(1, 12)))

        self.wall = Wall(self.window_dimension, self.window_dimension)

        self.sprite_size = SPRITE_SIZE
 
    def on_init(self):
        pygame.init()
        self._display_surf = pygame.display.set_mode((self.window_dimension, self.window_dimension), pygame.HWSURFACE)

        self._running = True

        self._player_surfs = []

        global PLAYER_COLORS
        for i, p in enumerate(self.players):
            image_surf = pygame.Surface([self.sprite_size - 4, self.sprite_size - 4])
            image_surf.fill(PLAYER_COLORS[i % len(PLAYER_COLORS)])
            self._player_surfs.append(image_surf)

        self._fruit_surf = pygame.Surface([self.sprite_size - 4, self.sprite_size - 4])
        self._fruit_surf.fill((255, 0, 0))

        self._wall_surf = pygame.Surface([self.sprite_size - 4, self.sprite_size - 4])
        self._wall_surf.fill((255, 255, 255))


    def collided(self, x1, y1, x2, y2, block_size):
        if x1 >= x2 and x1 <= x2 + block_size:
            if y1 >= y2 and y1 <= y2 + block_size:
                return True

        return False
 
    def on_event(self, event):
        if event.type == QUIT:
            self._running = False
 
    def on_loop(self):
        for idx, p in enumerate(self.players):
            p.update()

            for other_player_idx in range(idx + 1, len(self.players)):
                other_player = self.players[other_player_idx]
                for idx_player_len in range(0, other_player.length):
                    if self.collided(p.x[0], p.y[0], other_player.x[idx_player_len], other_player.y[idx_player_len], 20):
                        self.killed[idx] = True
                        self.killed[other_player_idx] = True

            # does snake eat apple?
            for i in range(0, p.length):
                for f in self.fruits:
                    if self.collided(f.x, f.y, p.x[i], p.y[i], 19):
                        f.x = randint(2, self.window_dimension / self.sprite_size - 2) * SPRITE_SIZE
                        f.y = randint(2, self.window_dimension / self.sprite_size - 2) * SPRITE_SIZE
                        p.length = p.length + 1
     
            # does snake collide with itself?
            for i in range(2, p.length):
                if self.collided(p.x[0], p.y[0], p.x[i], p.y[i], 19):
                    self.killed[idx] = True

            # going off the edge
            if p.x[0] < self.sprite_size or p.y[0] < self.sprite_size:
                self.killed[idx] = True

            if p.x[0] > self.window_dimension - self.sprite_size or p.y[0] > self.window_dimension - self.sprite_size:
                self.killed[idx] = True
        
        players_new = []

        for idx, p in enumerate(self.players):
            if not self.killed[idx]:
                players_new.append(self.players[idx])

        self.players = deepcopy(players_new)
        self.num_players = len(self.players)
        self.killed = [False] * self.num_players

        if self.num_players == 0:
            exit()

        
    def on_render(self):
        self._display_surf.fill((0,0,0))

        for i, f in enumerate(self.fruits):
            f.draw(self._display_surf, self._fruit_surf)

        for i, p in enumerate(self.players):
            p.draw(self._display_surf, self._player_surfs[p.color_idx])

        self.wall.draw(self._display_surf, self._wall_surf)

        pygame.display.flip()
 
 
    def on_cleanup(self):
        pygame.quit()
 
 
    def on_execute(self):
        if self.on_init() == False:
            self._running = False
 
        while( self._running ):
            pygame.event.pump()
            keys = pygame.key.get_pressed() 
 
            if (keys[K_RIGHT]):
                for p in self.players:
                    p.moveRight()
 
            if (keys[K_LEFT]):
                for p in self.players:
                    p.moveLeft()
 
            if (keys[K_UP]):
                for p in self.players:
                    p.moveUp()
 
            if (keys[K_DOWN]):
                for p in self.players:
                    p.moveDown()
 
            if (keys[K_ESCAPE]):
                self._running = False
 
            self.on_loop()
            self.on_render()
 
            time.sleep (25.0 / 1000.0);

        self.on_cleanup()
 
if __name__ == "__main__" :
    theApp = App()
    theApp.on_execute()