import pygame
import time
import os
from .map import Map
from .player import Player
from .ghost import Ghost
from .config import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    SCREEN_COLOR,
    FONT_COLOR,
    MAX_LEVEL,
    TILE_SIZE,
)


class Game:
    """
    Manage the Pac-Woman game flow.

    Handles the core logic, events, rendering.
    Encapsulates the main game loop.
    Illustrates player-ghost interaction.
    Manages the overall game flow.

    Attributes:
    level (int): current game level (default 1)
    ox (int): x offset for centering the map
    oy (int): y offset for centering the map
    map (Map): game map generated based on the current level
    screen (pygame.Surface): display surface where game elements are drawn
    ghosts (list[Ghost]): list of ghosts included in the game
    player (Player): main player object controlled by the user
    clock (pygame.time.Clock): Clock object to manage fps
    font (pygame.font.Font): text font used for rendering user interface
    running (bool): indicates whether the game loop is active (default True)
    game_over (bool): indicates whether the game is over (default False)
    time_game_over (int): time when the game ended (default 0)
    victory_image_original (pygame.Surface): player's image shown on victory
    music (NoneType): background looped music

    Methods:
    calculate_offset(): calcucates the offsets to place the map in the center
    _add_extra_ghosts(): adds additional ghosts depending on current level
    next_level(): upgrades the game level or indicates victory
    handle_events(): handles user's input when pressing the buttons
    update(): defines ghosts' behavior, collisions, game over
    draw_ui(): draws UI on the top of the screen.
    Showing player's lives, score, current level
    render(): renders the screen depending on remaining lives and level
    reset_game(): resets the game to its beginning state for a new game
    """

    def __init__(self) -> None:
        """
        Initialize the Pac-Woman game.

        Sets up the first game level. Creates a game map.
        Initializes the player and ghosts. Sets their positions.
        Sets the game title, clock, font, states of the game.
        Loads the resources (images, background music).

        Raises:
        pygame.error: if there was a problem loading image or music
        FileNotFoundError: if the image is missing

        Returns:
        None
        """
        pygame.init()
        self.level = 1
        self.map = Map(self.level)
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.calculate_offset()
        center_x, center_y = self.map.size // 2, self.map.size // 2
        self.ghosts = [Ghost(center_x, center_y)]           # Initialize ghost's starting position
        self.player = Player(center_x, min(center_y + 2, self.map.size - 1))          # Initialize player's starting position
        self._add_extra_ghosts()
        pygame.display.set_caption("PacWoman OOP")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 30)
        self.running = True
        self.game_over = False
        self.time_game_over = 0

        base_path = os.path.dirname(__file__)
        victory_path = os.path.abspath(
            os.path.join(base_path, "..", "img", "player_win.png")          # Return absolute path for player's victory image
        )
        try:
            self.victory_image_original = pygame.image.load(            # Load victory image if possible
                victory_path
            ).convert_alpha()
        except (pygame.error, FileNotFoundError):
            self.victory_image_original = pygame.Surface((100, 100))
            self.victory_image_original.fill((0, 255, 0))

        music_path = os.path.abspath(
            os.path.join(base_path, "..", "mp3", "background_music.mp3")          # Return absolute path for background music
        )
        try:
            self.music = pygame.mixer.music.load(music_path)         # Load background music if possible
            pygame.mixer.music.play(-1)
        except pygame.error:
            print("Nie udało się załadować muzyki.")

    def calculate_offset(self) -> None:
        """
        Calculate the offsets to center the map.

        Computes x and y offsets to place the map in the center.
        Depends on the window size.

        Returns:
        None
        """
        ms = self.map.size * TILE_SIZE          # Calculate map size in pixels
        self.ox = (WINDOW_WIDTH - ms) // 2
        self.oy = (WINDOW_HEIGHT - ms) // 2

    def _add_extra_ghosts(self) -> None:
        """
        Add additional ghosts at certain levels.

        At levels 3 and up and 5 and up adds extra ghosts of other types.
        Complicates the game by adding extra ghosts.

        Returns:
        None
        """
        if self.level >= 3:
            self.ghosts.append(
                Ghost(self.map.size - 1, 0, "duch1.png", ghost_type="ghost2")
            )
        if self.level >= 5:
            self.ghosts.append(
                Ghost(
                    self.map.size - 2,
                    self.map.size - 2,
                    "duch2.png",
                    ghost_type="ghost3",
                )
            )

    def next_level(self) -> None:
        """
        Upgrate the game to next level.

        When advancing to the next level plays a level-up sound.
        Resets the player's and ghosts' positions.
        Indicates the victory when maximum level achieved.
        Marks the game as over. Plays a victory sound.

        Returns:
        None
        """
        base_path = os.path.dirname(__file__)
        lvl_path = os.path.abspath(
            os.path.join(base_path, "..", "mp3", "level_up.mp3")          # Return absolute path for level up sound
        ) 
        try:
            pygame.mixer.Sound(lvl_path).play()          # Load level up sound if possible
        except pygame.error:
            print("Nie udało się załadować dźwięku.")
        self.level += 1
        if self.level > MAX_LEVEL:
            vic_path = os.path.abspath(
                os.path.join(base_path, "..", "mp3", "victory.mp3")         # Return absolute path for victory sound
            )
            try:
                pygame.mixer.Sound(vic_path).play()             # Load victory sound if possible
            except pygame.error:
                print("Nie udało się załadować dźwięku.")
            self.game_over = True
            return
        self.map = Map(self.level)          # Render next level of the game
        self.calculate_offset()
        cx, cy = self.map.size // 2, self.map.size // 2
        self.ghosts = [Ghost(cx, cy)]
        self.player.x, self.player.y = cx, min(cy + 2, self.map.size - 1)
        self._add_extra_ghosts()

    def handle_events(self) -> None:
        """
        Handle user's input.

        Operates keybord presses. Spacebar for skipping the level.
        Arrow keys for proceeding player's movement.
        Handles mouse clicks on the buttons at the end of the game.
        Defines whether to restart or quit the game.

        Returns:
        None
        """
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                self.running = False

            elif e.type == pygame.KEYDOWN and not self.game_over:
                if e.key == pygame.K_SPACE:
                    self.next_level()
                else:
                    keys = {
                        pygame.K_UP: (0, -1),
                        pygame.K_DOWN: (0, 1),
                        pygame.K_LEFT: (-1, 0),
                        pygame.K_RIGHT: (1, 0),
                    }
                    if e.key in keys:
                        dest_x, dest_y = keys[e.key]
                        self.player.move(dest_x, dest_y, self.map)

            elif e.type == pygame.MOUSEBUTTONDOWN and self.game_over:
                mouse_x, mouse_y = e.pos
                if self.restart_btn.collidepoint(mouse_x, mouse_y):
                    self.reset_game()
                elif self.quit_btn.collidepoint(mouse_x, mouse_y):
                    self.running = False

    def update(self) -> None:
        """
        Update state of the game.

        Advances the game to the next level when all the points are collected.
        Determines the ghosts' movement towards the player.
        Checks for collisions. Plays a sound if collision happend.
        Handles the player's lives and game over conditions.
        Plays a sound when lost all the lives and the game ends.

        Raises:
        ImportError: if there was a problem loading the music

        Returns:
        None
        """
        base_path = os.path.dirname(__file__)
        if self.game_over:
            return
        tile = self.map.grid[self.player.y][self.player.x]      
        if tile.point:
            self.player.score += 1          # Collect the point if standing on one
            tile.point = False
        if not any(tile.point for row in self.map.grid for tile in row):
            self.next_level()

        now = time.time()
        for ghost in self.ghosts:
            ghost.update_special_state(now)
            ghost.move_towards(self.player, self.map)
            collision = (ghost.x == self.player.x and ghost.y == self.player.y) or (
                ghost.ghost_type == "ghost3"
                and ghost.special_active
                and self.player.x in [ghost.x, ghost.x + 1]
                and self.player.y in [ghost.y, ghost.y + 1]
            )
            if collision:
                try:
                    ouch = os.path.abspath(
                        os.path.join(base_path, "..", "mp3", "ouch.mp3")            # Return absolute path for collision sound
                    )
                    pygame.mixer.Sound(ouch).play()             # Load collision sound if possible
                except ImportError:
                    print("Nie udało się załadować dźwięku.")
                self.player.lives -= 1
                if self.player.lives <= 0:
                    try:
                        sound_over = pygame.mixer.Sound(                # Load game over sound if possible
                            os.path.abspath(
                                os.path.join(base_path, "..", "mp3", "game_over.mp3")           # Return absolute path for game over sound
                            )
                        )
                        sound_over.set_volume(0.3)
                        sound_over.play()
                    except ImportError:
                        print("Nie udało się załadować dźwięku.")
                    self.game_over = True
                    self.time_game_over = now
                else:
                    curr_x, curr_y = (
                        self.map.size // 2,
                        min(self.map.size // 2 + 2, self.map.size - 1),
                    )
                    self.player.x, self.player.y = curr_x, curr_y           # Reset the player's position to the starting one after losing a life

    def draw_ui(self) -> None:
        """
        Draw UI on top of the screen.

        Renders user interface (UI).
        Displays player's remaining lives, current score and level.

        Returns:
        None
        """
        txt = self.font.render(
            f"Punkty: {self.player.score}  Życia: {self.player.lives}  Poziom: {self.level}",
            True,
            FONT_COLOR,
        )
        self.screen.blit(txt, (10, 10))

    def render(self) -> None:
        """
        Render the screen depanding on the current level.

        Draws the entire game frame.
        If the game is over, draw the game over screen with buttons.
        Game over screen can show either voctory of failure.
        Renders the quit and restart buttons.
        If the game continues,
        draws a new game screen with the map, ghosts, player.

        Returns:
        None
        """
        self.screen.fill(SCREEN_COLOR)

        if self.game_over:
            if self.level > MAX_LEVEL and self.player.lives > 0:            
                scale_factor = 0.20
                new_width = int(WINDOW_WIDTH * scale_factor)

                aspect_ratio = (
                    self.victory_image_original.get_height()
                    / self.victory_image_original.get_width()
                )
                new_height = int(new_width * aspect_ratio)

                scaled_image = pygame.transform.smoothscale(
                    self.victory_image_original, (new_width, new_height)
                )

                img_rect = scaled_image.get_rect(
                    center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50)
                )
                self.screen.blit(scaled_image, img_rect)                # Draw victory screen

                victory_text = self.font.render("ZWYCIĘSTWO!", True, (0, 255, 0))
                text_x = (WINDOW_WIDTH - victory_text.get_width()) // 2
                text_y = img_rect.top - 30
                self.screen.blit(victory_text, (text_x, text_y))
            elif self.game_over:
                game_over_text = self.font.render("KONIEC GRY!", True, (255, 50, 50))
                self.screen.blit(                                       # Draw game over screen
                    game_over_text,
                    (
                        (WINDOW_WIDTH - game_over_text.get_width()) // 2,
                        (WINDOW_HEIGHT - game_over_text.get_height()) // 2 - 50,
                    ),
                )

            self.restart_btn = pygame.Rect(
                WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 + 50, 200, 40
            )
            self.quit_btn = pygame.Rect(
                WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 + 110, 200, 40
            )

            pygame.draw.rect(
                self.screen, (255, 105, 180), self.restart_btn, border_radius=12        # Draw a restart button
            )
            pygame.draw.rect(self.screen, (200, 0, 0), self.quit_btn, border_radius=12)         # Draw a quit button

            restart_txt = self.font.render("Restartuj", True, (255, 255, 255))
            quit_txt = self.font.render("Zakończ", True, (255, 255, 255))

            self.screen.blit(
                restart_txt,
                (
                    self.restart_btn.centerx - restart_txt.get_width() // 2,
                    self.restart_btn.centery - restart_txt.get_height() // 2,
                ),
            )
            self.screen.blit(
                quit_txt,
                (
                    self.quit_btn.centerx - quit_txt.get_width() // 2,
                    self.quit_btn.centery - quit_txt.get_height() // 2,
                ),
            )
        else:
            self.map.draw(self.screen, self.ox, self.oy)            # Draw next game level
            for ghost in self.ghosts:
                ghost.draw(self.screen, self.ox, self.oy, self.map)
            self.player.draw(self.screen, self.ox, self.oy)
            self.draw_ui()

        pygame.display.flip()

    def reset_game(self) -> None:
        """
        Reset the game to its initial state.

        Resets the game to default settings.
        Resets the map, the ghosts, the player.
        Used when the user clicks reset button.

        Returns:
        None
        """
        self.level = 1
        self.map = Map(self.level)
        self.calculate_offset()
        center_x, center_y = self.map.size // 2, self.map.size // 2
        self.ghosts = [Ghost(center_x, center_y)]
        self.player = Player(center_x, min(center_y + 2, self.map.size - 1))
        self._add_extra_ghosts()
        self.running = True
        self.game_over = False
        self.time_game_over = 0
