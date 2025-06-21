import pygame
from map import Map
from config import TILE_SIZE

class Player:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
        self.score = 0
        self.lives = 3
        self.direction = 'right'  

        original_image = pygame.image.load(
            "player.png").convert_alpha()
        original_size = original_image.get_size()
        max_dim = TILE_SIZE - 1

        scale_ratio = min(
            max_dim / original_size[0], max_dim / original_size[1])
        new_size = (int(
            original_size[0] * scale_ratio), int(
                original_size[1] * scale_ratio))

        self.base_image = pygame.transform.smoothscale(
            original_image, new_size)
        self.image = self.base_image

    def move(self, dx: int, dy: int, map_obj: Map) -> None:
        new_x = self.x + dx
        new_y = self.y + dy

        if dx == -1: self.direction = 'left'
        elif dx == 1: self.direction = 'right'
        elif dy == -1: self.direction = 'up'
        elif dy == 1: self.direction = 'down'

        if 0 <= new_x < map_obj.size and 0 <= new_y < map_obj.size:
            current = map_obj.grid[self.y][self.x]
            target = map_obj.grid[new_y][new_x]
            if dx == -1 and (
                current.wall_left or target.wall_right): return
            if dx == 1 and (
                current.wall_right or target.wall_left): return
            if dy == -1 and (
                current.wall_top or target.wall_bottom): return
            if dy == 1 and (
                current.wall_bottom or target.wall_top): return
            self.x, self.y = new_x, new_y

    def draw(self, screen, ox, oy) -> pygame.Rect:
        if self.direction == 'right':
            image = self.base_image
        elif self.direction == 'left':
            image = pygame.transform.flip(
                self.base_image, True, False)
        elif self.direction == 'up':
            image = pygame.transform.rotate(
                self.base_image, 90)
        elif self.direction == 'down':
            image = pygame.transform.rotate(
                self.base_image, -90)

       
        image_rect = image.get_rect()
        x_pos = ox + self.x * TILE_SIZE + (
            TILE_SIZE - image_rect.width) // 2
        y_pos = oy + self.y * TILE_SIZE + (
            TILE_SIZE - image_rect.height) // 2
        screen.blit(image, (x_pos, y_pos))
