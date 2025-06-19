import pygame
import random
import time
from config import TILE_SIZE


class Ghost:
    def __init__(self, x, y, image_file="../img/duch.png", ghost_type=None):
        self.x = x
        self.y = y
        self.image = pygame.image.load(image_file).convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))
        self.last_move = time.time()
        self.ghost_type = ghost_type
        self.special_active = False
        self.special_start_time = 0

    def can_pass_walls(self):
        return self.special_active and self.ghost_type in ["ghost2", "ghost3"]

    def move_towards(self, player, map_obj):
        now = time.time()
        speed_delay = (
            0.25 if self.special_active and self.ghost_type == "ghost1" else 0.5
        )
        if now - self.last_move < speed_delay:
            return
        self.last_move = now

        dx = player.x - self.x
        dy = player.y - self.y
        dist = abs(dx) + abs(dy)

        def can(nx, ny):
            if not (0 <= nx < map_obj.size and 0 <= ny < map_obj.size):
                return False
            if self.can_pass_walls():
                return True
            c = map_obj.grid[self.y][self.x]
            t = map_obj.grid[ny][nx]
            if nx > self.x and (c.wall_right or t.wall_left): 
                return False
            if nx < self.x and (c.wall_left or t.wall_right):
                return False
            if ny > self.y and (c.wall_bottom or t.wall_top):
                return False
            if ny < self.y and (c.wall_top or t.wall_bottom):
                return False
            return True

        if dist <= 3 or random.random() < 0.2:
            if abs(dx) > abs(dy):
                nx = self.x + (1 if dx > 0 else -1)
                if can(nx, self.y):
                    self.x = nx
                    return
            if dy != 0:
                ny = self.y + (1 if dy > 0 else -1)
                if can(self.x, ny):
                    self.y = ny
                    return

        dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        random.shuffle(dirs)
        for dx_, dy_ in dirs:
            nx, ny = self.x + dx_, self.y + dy_
            if can(nx, ny):
                self.x, self.y = nx, ny
                break

    def update_special_state(self, current_time):
        if self.special_active and current_time - self.special_start_time >= 3:
            self.special_active = False
        elif not self.special_active and int(current_time) % 10 == 0:
            self.special_active = True
            self.special_start_time = current_time

    def draw(self, screen, ox, oy):
        if self.special_active and self.ghost_type == "ghost3":
            for dx in range(2):
                for dy in range(2):
                    screen.blit(
                        self.image,
                        (
                            ox + (self.x + dx) * TILE_SIZE,
                            oy + (self.y + dy) * TILE_SIZE,
                        ),
                    )
        elif not (self.special_active and int(time.time() * 5) % 2 == 0):
            screen.blit(self.image, (ox + self.x * TILE_SIZE, oy + self.y * TILE_SIZE))
