import pygame
import random
import time
import os
from .map import Map
from .player import Player
from .config import TILE_SIZE
from collections import deque
from typing import Optional


class Ghost:
    """
    Represent a ghost (enemy) in a game.

    Initializes a ghost with its own superpowers (3 types of ghosts).
    Specifies ghosts' special abilities if any.
    Defines a way of moving around the map.
    Defines an algorithm of chasing the player.
    Draws the ghost on the screen.

    Attributes:
    x (int): current x position of the ghost
    y (int): current y position of the ghost
    ghost_type (Optional[str]): type of a ghost to determine its special ability
    image (pygame.Surface): scaled image of the ghost that will be shown on the screen
    image_size (int): size of a scaled ghost image in pixels
    last_move (float): time of the ghost's last move used for speed delay
    special_active (bool): shows if the ghost's special ability is activated (default False)
    special_start_time (int): time when the ghost's special ability activates (default 0)

    Methods:
    can_pass_walls(): indicates whether the ghost has the special ability of passing the walls
    move_towards(player, map_obj): algorithm that defines a way in which the ghost moves towards the player
    update_special_state(current_time): updates the state of ghost's special ability based on time activated
    draw(screen, offset_x, offset_y, map_obj): draws the ghost on the screen
    """

    def __init__(
        self,
        x: int,
        y: int,
        image_file: str = "duch.png",
        ghost_type: Optional[str] = None,
    ) -> None:
        """
        Initialize a ghost at certain coordinates.
        Creates a ghost object and loads its image.
        Sets ghost's initial position.
        Sets type of the ghost.

        Arguments:
        x (int): beginning x position of the ghost
        y (int): beginning y position of the ghost
        image_file (str): path to loading ghosts image (default "../img/duch.png")
        ghost_type (Optional[str]): determines type of a ghost and his special abilities (default None)

        Returns:
        None
        """
        self.x = x
        self.y = y
        base_path = os.path.dirname(__file__)
        image_path = os.path.abspath(os.path.join(base_path, "..", "img", image_file))
        self.image = pygame.image.load(image_path).convert_alpha()

        margin = 8
        size = TILE_SIZE - margin
        self.image = pygame.transform.smoothscale(self.image, (size, size))
        self.image_size = size

        self.last_move = time.time()
        self.ghost_type = ghost_type
        self.special_active = False
        self.special_start_time = 0

    def can_pass_walls(self) -> bool:
        """
        Indicate if the ghost has the ability to pass the walls.

        Checks if the ghost is of particular type and if the special ability is active.
        Based on that information claims if the ghost can pass through walls.

        Returns:
        Bool: True if the ghost can pass through the walls, False if can not.
        """
        return self.special_active and self.ghost_type in ["ghost2", "ghost3"]

    def move_towards(self, player: Player, map_obj: Map) -> None:
        """
        Move the ghost towards the player.

        Based on BFS algorithm calculates the shortest path to the player.
        Uses that path to follow the player if the player is close enough.
        Includes special abilities logic to define the path.

        Arguments:
        player (Player): the player object to chase
        map_obj (Map): the map object used to calculate moves and paths

        Returns:
        None
        """
        now = time.time()
        speed_delay = (
            0.25 if self.special_active and self.ghost_type == "ghost1" else 0.5
        )
        if now - self.last_move < speed_delay:
            return
        self.last_move = now

        def can(x1: int, y1: int, x2: int, y2: int) -> bool:
            """
            Tell if the ghost can move from one position to another.

            Indicates if it is possible for the ghost to move from position (x1, y1)
            to position (x2, y2).
            Takes into consideration map size, walls location, state of special activity.

            Arguments:
            x1 (int): starting x-coordinate
            y1 (int): starting y-coordinate
            x2 (int): ending x-coordinate
            y2 (int): ending y-coordinate


            Returns:
            Bool
            """
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
            """
            Find the shortest path to the player from current position using BFS.

            Breadth-First Serach (BFS) algorithm that finds (if possible) the shortest path
            to the player's position from ghost's current position.
            Considers walls blocking the way and ghost's superpower
            to pass through the walls (if has one).

            Arguments:
            start (tuple[int, int]): starting position of the ghost
            goal (tuple[int, int]): target position of the player

            Returns:
            Optional[list[tuple[int, int]]]: returns a path (a list of tuples) if can be found,
            None if can not.
            """
            visited = set()
            queue = deque()
            queue.append((start, []))

            while queue:
                (current_x, current_y), path = queue.popleft()
                if (current_x, current_y) in visited:
                    continue
                visited.add((current_x, current_y))

                if (current_x, current_y) == goal:
                    return path

                for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                    new_x, new_y = current_x + dx, current_y + dy
                    if (new_x, new_y) not in visited and can(
                        current_x, current_y, new_x, new_y
                    ):
                        queue.append(((new_x, new_y), path + [(new_x, new_y)]))
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
        for dest_x, dest_y in dirs:
            nx, ny = self.x + dest_x, self.y + dest_y
            if can(self.x, self.y, nx, ny):
                self.x, self.y = nx, ny
                break

    def update_special_state(self, current_time: float) -> None:
        """
        Update ghost's special ability activation.

        The update of special state activity is based on time it has already been active/inactive.
        Activates special ability every 10 seconds for 3 seconds.

        Arguments:
        current_time (float): measured current time

        Returns:
        None
        """
        if self.special_active and current_time - self.special_start_time >= 3:
            self.special_active = False
        elif not self.special_active and int(current_time) % 10 == 0:
            self.special_active = True
            self.special_start_time = current_time

    def draw(
        self, screen: pygame.Surface, offset_x: int, offset_y: int, map_obj: Map
    ) -> None:
        """
        Draw the ghost on the screen.

        Renders the ghost on the screen at the calculated current position.
        For ghost type "ghost3" in state of active superpower renders its bigger 2x2 version.

        Arguments:
        screen (pygame.Surface): the game screen (surface) where the ghost will be drawn
        offset_x (int): horizontal pixel offset to allocate the ghost
        offset_y (int): vertical pixel offset to allocate the ghost
        map_obj (Map): the map object used to calculate the borders for staying within map size

        Returns:
        None
        """
        x_pos = offset_x + self.x * TILE_SIZE + (TILE_SIZE - self.image_size) // 2
        y_pos = offset_y + self.y * TILE_SIZE + (TILE_SIZE - self.image_size) // 2

        if self.special_active and self.ghost_type == "ghost3":
            map_width = len(map_obj.grid[0])
            map_height = len(map_obj.grid)
            for delta_x in range(2):
                for delta_y in range(2):
                    big_x = self.x + delta_x
                    big_y = self.y + delta_y
                    if big_x < map_width and big_y < map_height:
                        screen_x = (
                            offset_x
                            + big_x * TILE_SIZE
                            + (TILE_SIZE - self.image_size) // 2
                        )
                        screen_y = (
                            offset_y
                            + big_y * TILE_SIZE
                            + (TILE_SIZE - self.image_size) // 2
                        )
                        screen.blit(self.image, (screen_x, screen_y))
        elif not (self.special_active and int(time.time() * 5) % 2 == 0):
            screen.blit(self.image, (x_pos, y_pos))
