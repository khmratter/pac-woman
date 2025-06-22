import pygame
from map import Map
from config import TILE_SIZE


class Player:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
        self.score = 0
        self.lives = 3
        self.direction = "right"

        original_image = pygame.image.load("../img/player.png").convert_alpha()
        original_size = original_image.get_size()
        max_dim = TILE_SIZE - 1

        scale_ratio = min(max_dim / original_size[0], max_dim / original_size[1])
        new_size = (
            int(original_size[0] * scale_ratio),
            int(original_size[1] * scale_ratio),
        )

        self.base_image = pygame.transform.smoothscale(original_image, new_size)
        self.image = self.base_image

    def move(self, dx: int, dy: int, map_obj: Map) -> None:
        new_x = self.x + dx
        new_y = self.y + dy

        d_to_text = {
            (-1, 0): "left",
            (1, 0): "right",
            (0, -1): "up",
            (0, 1): "down",
        }
        self.direction = d_to_text.get((dx, dy))

        if 0 <= new_x < map_obj.size and 0 <= new_y < map_obj.size:
            current = map_obj.grid[self.y][self.x]
            target = map_obj.grid[new_y][new_x]
            walls_blocking = {
                (-1, 0): ("wall_left", "wall_right"),
                (1, 0): ("wall_right", "wall_left"),
                (0, -1): ("wall_top", "wall_bottom"),
                (0, 1): ("wall_bottom", "wall_top"),
            }
            walls = walls_blocking.get((dx, dy))
            current_wall, target_wall = walls
            if getattr(current, current_wall) or getattr(target, target_wall):
                return
            self.x, self.y = new_x, new_y

    def draw(self, screen: pygame.Surface, ox: int, oy: int) -> None:
        directions = {
            "right": lambda png: png,
            "left": lambda png: pygame.transform.flip(png, True, False),
            "up": lambda png: pygame.transform.rotate(png, 90),
            "down": lambda png: pygame.transform.rotate(png, -90),
        }
        image = directions[self.direction](self.base_image)

        image_rect = image.get_rect()
        x_pos = ox + self.x * TILE_SIZE + (TILE_SIZE - image_rect.width) // 2
        y_pos = oy + self.y * TILE_SIZE + (TILE_SIZE - image_rect.height) // 2
        screen.blit(image, (x_pos, y_pos))
