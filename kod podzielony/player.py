import pygame
from config import TILE_SIZE, PLAYER_COLOR

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.score = 0
        self.lives = 3

    def move(self, dx, dy, map_obj):
        new_x = self.x + dx
        new_y = self.y + dy
        if 0 <= new_x < map_obj.size and 0 <= new_y < map_obj.size:
            current = map_obj.grid[self.y][self.x]
            target  = map_obj.grid[new_y][new_x]
            if dx == -1 and (current.wall_left or target.wall_right): return
            if dx ==  1 and (current.wall_right or target.wall_left): return
            if dy == -1 and (current.wall_top or target.wall_bottom): return
            if dy ==  1 and (current.wall_bottom or target.wall_top): return
            self.x, self.y = new_x, new_y

    def draw(self, screen, ox, oy):
        pygame.draw.rect(screen, PLAYER_COLOR,
                         (ox + self.x*TILE_SIZE + 2, oy + self.y*TILE_SIZE + 2,
                          TILE_SIZE - 2, TILE_SIZE - 2))
