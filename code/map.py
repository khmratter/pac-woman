import random
import pygame
from tile import Tile
from config import TILE_SIZE, TILE_COLOR, POINT_COLOR, WALL_COLOR


class Map:
    def __init__(self, level: int) -> None:
        self.level = level
        self.size = 5 + level - 1
        self.grid = [[Tile() for _ in range(self.size)] for _ in range(self.size)]
        self._gen_maze()
        self._add_extra_passages(extra=self.level + 3)
        self._break_long_walls(max_len=3)
        self._place_points()
        self._mark_accessible()

    # Generuje labirynt metodą DFS
    def _gen_maze(self) -> None:
        size = self.size
        for y in range(size):
            for x in range(size):
                t = self.grid[y][x]
                t.wall_top = t.wall_bottom = t.wall_left = t.wall_right = True

        dirs = [
            ("top", 0, -1, "bottom"),
            ("bottom", 0, 1, "top"),
            ("left", -1, 0, "right"),
            ("right", 1, 0, "left"),
        ]
        visited = [[False] * size for _ in range(size)]

        def dfs(x: int, y: int) -> None:
            visited[y][x] = True
            dir_order = dirs[:]
            random.shuffle(dir_order)
            for wall, dx, dy, opposite_wall in dir_order:
                steps = random.randint(1, 3)
                current_x, current_y = x, y
                for _ in range(steps):
                    new_x, new_y = current_x + dx, current_y + dy
                    if 0 <= new_x < size and 0 <= new_y < size and not visited[new_y][new_x]:
                        setattr(self.grid[current_y][current_x], f"wall_{wall}", False)
                        setattr(self.grid[new_y][new_x], f"wall_{opposite_wall}", False)
                        visited[new_y][new_x] = True
                        dfs(new_x, new_y)
                        break
                    else:
                        break

        dfs(self.size // 2, self.size // 2)

    # Dodaje losowe dodatkowe przejścia
    def _add_extra_passages(self, extra: int = 5) -> None:
        count = 0
        size = self.size
        while count < extra:
            x = random.randint(0, size - 2)
            y = random.randint(0, size - 2)
            tile1 = self.grid[y][x]
            if random.choice([True, False]):
                tile2 = self.grid[y][x + 1]
                if tile1.wall_right and tile2.wall_left:
                    tile1.wall_right = False
                    tile2.wall_left = False
                    count += 1
            else:
                tile2 = self.grid[y + 1][x]
                if tile1.wall_bottom and tile2.wall_top:
                    tile1.wall_bottom = False
                    tile2.wall_top = False
                    count += 1

    # Przerywa zbyt długie ściany
    def _break_long_walls(self, max_len: int = 3) -> None:
        for y in range(self.size):
            count = 0
            for x in range(self.size - 1):
                if self.grid[y][x].wall_right and self.grid[y][x + 1].wall_left:
                    count += 1
                    if count >= max_len:
                        self.grid[y][x].wall_right = False
                        self.grid[y][x + 1].wall_left = False
                        count = 0
                else:
                    count = 0
        for x in range(self.size):
            count = 0
            for y in range(self.size - 1):
                if self.grid[y][x].wall_bottom and self.grid[y + 1][x].wall_top:
                    count += 1
                    if count >= max_len:
                        self.grid[y][x].wall_bottom = False
                        self.grid[y + 1][x].wall_top = False
                        count = 0
                else:
                    count = 0

    # Ustawia punkt na każdym wolnym polu (oprócz pola startowego gracza)
    def _place_points(self) -> None:
        start_x = self.size // 2
        start_y = min(self.size // 2 + 2, self.size - 1)
        for y in range(self.size):
            for x in range(self.size):
                if (x, y) == (start_x, start_y):
                    continue  # pomijamy pole startowe gracza
                self.grid[y][x].point = True

    # Na razie pusta – można użyć np. do oznaczenia dostępnych pól
    def _mark_accessible(self) -> None:
        pass

    # Rysowanie planszy
    def draw(self, screen: pygame.Surface, offset_x: int, offset_y: int) -> None:
        for y in range(self.size):
            for x in range(self.size):
                tile = self.grid[y][x]
                tile_x, tile_y = offset_x + x * TILE_SIZE, offset_y + y * TILE_SIZE
                pygame.draw.rect(screen, TILE_COLOR, (tile_x, tile_y, TILE_SIZE, TILE_SIZE))
                if tile.point:
                    pygame.draw.circle(
                        screen,
                        POINT_COLOR,
                        (tile_x + TILE_SIZE // 2, tile_y + TILE_SIZE // 2),
                        TILE_SIZE // 5,
                    )
                walls = [
                    ("wall_top", ((tile_x, tile_y), (tile_x + TILE_SIZE, tile_y))),
                    ("wall_bottom", ((tile_x, tile_y + TILE_SIZE), (tile_x + TILE_SIZE, tile_y + TILE_SIZE))),
                    ("wall_left", ((tile_x, tile_y), (tile_x, tile_y + TILE_SIZE))),
                    ("wall_right",((tile_x + TILE_SIZE, tile_y), (tile_x + TILE_SIZE, tile_y + TILE_SIZE))),
                ]

                for wall_position, coord in walls:
                    if getattr(tile, wall_position):
                        pygame.draw.line(screen, WALL_COLOR, coord[0], coord[1], 2)
