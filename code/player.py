import pygame
import os
from .map import Map
from .config import TILE_SIZE


class Player:
    """
    Represent a player in the game.

    Initializes the player, defines how the player moves across the map.
    Generates the player image on the screen.

    Attributes:
    x (int): current x position of the player
    y (int): current y position of the player
    score (int): current score of the player (collected points) (default 0)
    lives (int): number of player's remaining lives (default 3)
    direction (str): current facing direction of the player (default "right")
    base_image (pygame.Surface): the base image used for scaling to fit
    image (pygame.Surface): scaled image of the player that will be shown on the screen when rendering the player

    Methods:
    move(dx, dy, map_obj): defines how and where the player can or cannot move across the map
    draw(screen, offset_x, offset_y): draws the player on the screen
    """

    def __init__(self, x: int, y: int) -> None:
        """
        Initialize a player at the current x and y position.

        Creates a player with a loaded and scaled image.
        Sets initial position, score, live count and direction.

        Arguments:
        x (int): beginning x position of the player
        y (int): beginning y position of the player

        Raises:
        pygame.error: if there was a problem with a path to the image file

        Returns:
        None
        """
        self.x = x
        self.y = y
        self.score = 0
        self.lives = 3
        self.direction = "right"

        try:
            base_path = os.path.dirname(__file__)
            image_path = os.path.abspath(
                os.path.join(base_path, "..", "img", "player.png")          # Return absolute path for the player's image
            )
            original_image = pygame.image.load(image_path).convert_alpha()
        except pygame.error:
            original_image = pygame.Surface((10, 10))           # If the image doesn't exist create empty one

        original_size = original_image.get_size()
        max_dim = TILE_SIZE - 1

        scale_ratio = min(max_dim / original_size[0], max_dim / original_size[1])
        new_size = (
            int(original_size[0] * scale_ratio),
            int(original_size[1] * scale_ratio),
        )

        self.base_image = pygame.transform.smoothscale(original_image, new_size)        # Scale the image to fit the cell
        self.image = self.base_image

    def move(self, dx: int, dy: int, map_obj: Map) -> None:
        """
        Move the player to a new position on the map if possible.

        Checks if new coordinates are within the map and whether there are any walls blocking the player's way.
        If not, moves the player to a new position.
        Changes the player's direction accordingly.

        Arguments:
        dx (int): change in x-coordinate (horizontal coordinate)
        dy (int): change in y-coordinate (vertical coordinate)
        map_obj (Map): Map object around which the player is moving with information of the location of walls

        Returns:
        None
        """
        new_x = self.x + dx
        new_y = self.y + dy

        diff_to_text = {
            (-1, 0): "left",
            (1, 0): "right",
            (0, -1): "up",
            (0, 1): "down",
        }
        self.direction = diff_to_text.get((dx, dy))         # Update the players direction

        if 0 <= new_x < map_obj.size and 0 <= new_y < map_obj.size:         # Make sure a new position is within the map
            current = map_obj.grid[self.y][self.x]
            target = map_obj.grid[new_y][new_x]
            walls_blocking = {
                (-1, 0): ("wall_left", "wall_right"),
                (1, 0): ("wall_right", "wall_left"),
                (0, -1): ("wall_top", "wall_bottom"),
                (0, 1): ("wall_bottom", "wall_top"),
            }
            walls = walls_blocking.get((dx, dy))         # Get the pair direction-blocking walls
            current_wall, target_wall = walls
            if getattr(current, current_wall) or getattr(target, target_wall):         # Check if any walls block current or target tile
                return
            self.x, self.y = new_x, new_y

    def draw(self, screen: pygame.Surface, offset_x: int, offset_y: int) -> None:
        """
        Draw the player on the screen.

        Renders the player image on the screen at the correctly calculated position.
        The image is rotated according to the set direction.

        Arguments:
        screen (pygame.Surface): the game screen (surface) where the player will be drawn
        offset_x (int): horizontal pixel offset to allocate the player
        offset_y (int): vertical pixel offset to allocate the player

        Returns:
        None
        """
        directions = {
            "right": lambda png: png,
            "left": lambda png: pygame.transform.flip(png, True, False),
            "up": lambda png: pygame.transform.rotate(png, 90),
            "down": lambda png: pygame.transform.rotate(png, -90),
        }
        image = directions[self.direction](self.base_image)         # Rotate the image according to the new direction

        image_rect = image.get_rect()
        x_pos = offset_x + self.x * TILE_SIZE + (TILE_SIZE - image_rect.width) // 2
        y_pos = offset_y + self.y * TILE_SIZE + (TILE_SIZE - image_rect.height) // 2
        screen.blit(image, (x_pos, y_pos))
