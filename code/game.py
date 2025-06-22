import pygame
import time
from config import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    SCREEN_COLOR,
    FONT_COLOR,
    MAX_LEVEL,
    TILE_SIZE,
)
from map import Map
from player import Player
from ghost import Ghost


class Game:
    def __init__(self) -> None:
        pygame.init()
        self.level = 1
        self.map = Map(self.level)
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.calculate_offset()
        cx, cy = self.map.size // 2, self.map.size // 2
        self.ghosts = [Ghost(cx, cy)]
        self.player = Player(cx, min(cy + 2, self.map.size - 1))
        self._add_extra_ghosts()
        pygame.display.set_caption("PacWoman OOP")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 30)
        self.running = True
        self.game_over = False
        self.time_game_over = 0
        self.victory_image_original = pygame.image.load(
            "../img/player_win.png"
        ).convert_alpha()
        try:
            pygame.mixer.music.load("../mp3/background_music.mp3")
            pygame.mixer.music.play(-1)
        except ImportError:
            print("Nie udało się załadować muzyki.")

    def calculate_offset(self) -> None:
        ms = self.map.size * TILE_SIZE
        self.ox = (WINDOW_WIDTH - ms) // 2
        self.oy = (WINDOW_HEIGHT - ms) // 2

    def _add_extra_ghosts(self) -> None:
        if self.level >= 3:
            self.ghosts.append(
                Ghost(self.map.size - 1, 0, "../img/duch1.png", ghost_type="ghost2")
            )
        if self.level >= 5:
            self.ghosts.append(
                Ghost(self.map.size - 2, self.map.size - 2, "../img/duch2.png", ghost_type="ghost3")
            )

    def next_level(self) -> None:
        try:
            pygame.mixer.Sound("../mp3/level_up.mp3").play()
        except ImportError:
            pass
        self.level += 1
        if self.level > MAX_LEVEL:
            try:
                pygame.mixer.Sound("../mp3/victory.mp3").play()
            except ImportError:
                pass
            self.game_over = True
            return
        self.map = Map(self.level)
        self.calculate_offset()
        cx, cy = self.map.size // 2, self.map.size // 2
        self.ghosts = [Ghost(cx, cy)]
        self.player.x, self.player.y = cx, min(cy + 2, self.map.size - 1)
        self._add_extra_ghosts()

    def handle_events(self) -> None:
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
                        dx, dy = keys[e.key]
                        self.player.move(dx, dy, self.map)

            elif e.type == pygame.MOUSEBUTTONDOWN and self.game_over:
                mx, my = e.pos
                if self.restart_btn.collidepoint(mx, my):
                    self.reset_game()
                elif self.quit_btn.collidepoint(mx, my):
                    self.running = False

    def update(self) -> None:
        if self.game_over:
            return
        tile = self.map.grid[self.player.y][self.player.x]
        if tile.point:
            self.player.score += 1
            tile.point = False
        if not any(tile.point for row in self.map.grid for tile in row):
            self.next_level()

        now = time.time()
        for g in self.ghosts:
            g.update_special_state(now)
            g.move_towards(self.player, self.map)
            collision = (g.x == self.player.x and g.y == self.player.y) or (
                g.ghost_type == "ghost3"
                and g.special_active
                and self.player.x in [g.x, g.x + 1]
                and self.player.y in [g.y, g.y + 1]
            )
            if collision:
                try:
                    pygame.mixer.Sound("../mp3/ouch.mp3").play()
                except ImportError:
                    pass
                self.player.lives -= 1
                if self.player.lives <= 0:
                    try:
                        sound_over = pygame.mixer.Sound("../mp3/game_over.mp3")
                        sound_over.set_volume(0.3)
                        sound_over.play()
                    except ImportError:
                        pass
                    self.game_over = True
                    self.time_game_over = now
                else:
                    cx, cy = (
                        self.map.size // 2,
                        min(self.map.size // 2 + 2, self.map.size - 1),
                    )
                    self.player.x, self.player.y = cx, cy

    def draw_ui(self) -> None:
        txt = self.font.render(
            f"Punkty: {self.player.score}  Życia: {self.player.lives}  Poziom: {self.level}",
            True,
            FONT_COLOR,
        )
        self.screen.blit(txt, (10, 10))

    def render(self) -> None:
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
                self.screen.blit(scaled_image, img_rect)

                victory_text = self.font.render("ZWYCIĘSTWO!", True, (0, 255, 0))
                text_x = (WINDOW_WIDTH - victory_text.get_width()) // 2
                text_y = img_rect.top - 30
                self.screen.blit(victory_text, (text_x, text_y))
            elif self.game_over:
                go = self.font.render("KONIEC GRY!", True, (255, 50, 50))
                self.screen.blit(
                    go,
                    (
                        (WINDOW_WIDTH - go.get_width()) // 2,
                        (WINDOW_HEIGHT - go.get_height()) // 2 - 50,
                    ),
                )

            self.restart_btn = pygame.Rect(
                WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 + 50, 200, 40
            )
            self.quit_btn = pygame.Rect(
                WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 + 110, 200, 40
            )

            pygame.draw.rect(
                self.screen, (255, 105, 180), self.restart_btn, border_radius=12
            )
            pygame.draw.rect(self.screen, (200, 0, 0), self.quit_btn, border_radius=12)

            restart_txt = self.font.render("Restart", True, (255, 255, 255))
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
            self.map.draw(self.screen, self.ox, self.oy)
            for g in self.ghosts:
                g.draw(self.screen, self.ox, self.oy, self.map)
            self.player.draw(self.screen, self.ox, self.oy)
            self.draw_ui()

        pygame.display.flip()

    def handle_game_over(self) -> None:
        pass

    def reset_game(self) -> None:
        self.level = 1
        self.map = Map(self.level)
        self.calculate_offset()
        cx, cy = self.map.size // 2, self.map.size // 2
        self.ghosts = [Ghost(cx, cy)]
        self.player = Player(cx, min(cy + 2, self.map.size - 1))
        self._add_extra_ghosts()
        self.running = True
        self.game_over = False
        self.time_game_over = 0
