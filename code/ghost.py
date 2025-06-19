import pygame
import random
import time
from config import TILE_SIZE
from collections import deque


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

        def can(x1, y1, x2, y2):
            if not (0 <= x2 < map_obj.size and 0 <= y2 < map_obj.size):
                return False
            if self.can_pass_walls():
                return True
            c = map_obj.grid[y1][x1]
            t = map_obj.grid[y2][x2]
            if x2 > x1 and (c.wall_right or t.wall_left):
                return False
            if x2 < x1 and (c.wall_left or t.wall_right):
                return False
            if y2 > y1 and (c.wall_bottom or t.wall_top):
                return False
            if y2 < y1 and (c.wall_top or t.wall_bottom):
                return False
            return True

        def bfs_path(start, goal):
            visited = set()
            queue = deque()
            queue.append((start, []))

            while queue:
                (cx, cy), path = queue.popleft()
                if (cx, cy) in visited:
                    continue
                visited.add((cx, cy))

                if (cx, cy) == goal:
                    return path

                for dx_, dy_ in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                    nx, ny = cx + dx_, cy + dy_
                    if (nx, ny) not in visited and can(cx, cy, nx, ny):
                        queue.append(((nx, ny), path + [(nx, ny)]))
            return None

        path = bfs_path((self.x, self.y), (player.x, player.y))

        if path and len(path) <= 3:
            next_x, next_y = path[0]
            self.x, self.y = next_x, next_y
            return

        if path and random.random() < 0.4:
            next_x, next_y = path[0]
            self.x, self.y = next_x, next_y
            return

        dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        random.shuffle(dirs)
        for dx_, dy_ in dirs:
            nx, ny = self.x + dx_, self.y + dy_
            if can(self.x, self.y, nx, ny):
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
