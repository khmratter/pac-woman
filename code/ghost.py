import pygame
import random
import time
from map import Map
from player import Player
from config import TILE_SIZE
from collections import deque
from typing import Optional


class Ghost:
    def __init__(self, x: int, y: int, image_file: str = "../img/duch.png", ghost_type: Optional[str] = None) -> None:
        self.x = x
        self.y = y
        self.image = pygame.image.load(image_file).convert_alpha()

        margin = 8
        size = TILE_SIZE - margin
        self.image = pygame.transform.smoothscale(self.image, (size, size))
        self.image_size = size

        self.last_move = time.time()
        self.ghost_type = ghost_type
        self.special_active = False
        self.special_start_time = 0

    def can_pass_walls(self) -> bool:
        return self.special_active and self.ghost_type in ["ghost2", "ghost3"]

    def move_towards(self, player: Player, map_obj: Map) -> None:
        now = time.time()
        speed_delay = (
            0.25 if self.special_active and self.ghost_type == "ghost1" else 0.5
        )
        if now - self.last_move < speed_delay:
            return
        self.last_move = now

        def can(x1: int, y1: int, x2: int, y2: int) -> bool:
            if not (0 <= x2 < map_obj.size and 0 <= y2 < map_obj.size):
                return False
            if self.can_pass_walls():
                return True

            curr = map_obj.grid[y1][x1]
            targ = map_obj.grid[y2][x2]
            diff_x = x2 - x1
            diff_y = y2 - y1

            walls_blocking = {
                (1, 0): ("wall_right", "wall_left"),
                (-1, 0): ("wall_left", "wall_right"),
                (0, 1): ("wall_bottom", "wall_top"),
                (0, -1): ("wall_top", "wall_bottom"),
            }
            walls = walls_blocking.get((diff_x, diff_y))

            current_wall, target_wall = walls
            if getattr(curr, current_wall) or getattr(targ, target_wall):
                return False
            return True

        def bfs_path(
            start: tuple[int, int], goal: tuple[int, int]
        ) -> Optional[list[tuple[int, int]]]:
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

    def update_special_state(self, current_time: float) -> None:
        if self.special_active and current_time - self.special_start_time >= 3:
            self.special_active = False
        elif not self.special_active and int(current_time) % 10 == 0:
            self.special_active = True
            self.special_start_time = current_time

    def draw(self, screen: pygame.Surface, ox: int, oy: int, map_obj: Map) -> None:
        x_pos = ox + self.x * TILE_SIZE + (TILE_SIZE - self.image_size) // 2
        y_pos = oy + self.y * TILE_SIZE + (TILE_SIZE - self.image_size) // 2

        if self.special_active and self.ghost_type == "ghost3":
            map_width = len(map_obj.grid[0])
            map_height = len(map_obj.grid)
            for dx in range(2):
                for dy in range(2):
                    bx = self.x + dx
                    by = self.y + dy
                    if bx < map_width and by < map_height:
                        sx = ox + bx * TILE_SIZE + (TILE_SIZE - self.image_size) // 2
                        sy = oy + by * TILE_SIZE + (TILE_SIZE - self.image_size) // 2
                        screen.blit(self.image, (sx, sy))
        elif not (self.special_active and int(time.time() * 5) % 2 == 0):
            screen.blit(self.image, (x_pos, y_pos))
