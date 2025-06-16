import pygame
import time
from config import WINDOW_WIDTH, WINDOW_HEIGHT, SCREEN_COLOR, FONT_COLOR, MAX_LEVEL, TILE_SIZE
from map import Map
from player import Player
from ghost import Ghost

class Game:
    def __init__(self):
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
        try:
            pygame.mixer.music.load("background_music.mp3")
            pygame.mixer.music.play(-1)
        except:
            print("Nie udało się załadować muzyki.")

    def calculate_offset(self):
        ms = self.map.size * TILE_SIZE
        self.ox = (WINDOW_WIDTH - ms) // 2
        self.oy = (WINDOW_HEIGHT - ms) // 2

    def _add_extra_ghosts(self):
        if self.level >= 3:
            self.ghosts.append(Ghost(self.map.size - 1, 0, "duch1.png", ghost_type="ghost2"))
        if self.level >= 5:
            self.ghosts.append(Ghost(self.map.size - 2, self.map.size - 2, "duch2.png", ghost_type="ghost3"))

    def next_level(self):
        try:
            pygame.mixer.Sound("level_up.mp3").play()
        except:
            pass
        self.level += 1
        if self.level > MAX_LEVEL:
            try:
                pygame.mixer.Sound("victory.mp3").play()
            except:
                pass
            self.game_over = True
            return
        self.map = Map(self.level)
        self.calculate_offset()
        cx, cy = self.map.size // 2, self.map.size // 2
        self.ghosts = [Ghost(cx, cy)]
        self.player.x, self.player.y = cx, min(cy + 2, self.map.size - 1)
        self._add_extra_ghosts()

    def handle_events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                self.running = False
            if not self.game_over and e.type == pygame.KEYDOWN:
                if e.key == pygame.K_SPACE:
                    self.next_level()
                elif e.key == pygame.K_UP:
                    self.player.move(0, -1, self.map)
                elif e.key == pygame.K_DOWN:
                    self.player.move(0, 1, self.map)
                elif e.key == pygame.K_LEFT:
                    self.player.move(-1, 0, self.map)
                elif e.key == pygame.K_RIGHT:
                    self.player.move(1, 0, self.map)

    def update(self):
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
                g.ghost_type == 'ghost3' and g.special_active and
                self.player.x in [g.x, g.x + 1] and self.player.y in [g.y, g.y + 1])
            if collision:
                try:
                    pygame.mixer.Sound("ouch.mp3").play()
                except:
                    pass
                self.player.lives -= 1
                if self.player.lives <= 0:
                    try:
                        s = pygame.mixer.Sound("game_over.mp3")
                        s.set_volume(0.3)
                        s.play()
                    except:
                        pass
                    self.game_over = True
                    self.time_game_over = now
                else:
                    cx, cy = self.map.size // 2, min(self.map.size // 2 + 2, self.map.size - 1)
                    self.player.x, self.player.y = cx, cy

    def draw_ui(self):
        txt = self.font.render(f"Punkty: {self.player.score}  Życia: {self.player.lives}  Poziom: {self.level}", True, FONT_COLOR)
        self.screen.blit(txt, (10, 10))

    def render(self):
        self.screen.fill(SCREEN_COLOR)
        if self.game_over and self.level > MAX_LEVEL and self.player.lives > 0:
            go = self.font.render("ZWYCIĘSTWO!", True, (0, 255, 0))
            self.screen.blit(go, ((WINDOW_WIDTH - go.get_width()) // 2, (WINDOW_HEIGHT - go.get_height()) // 2))
        elif self.game_over:
            go = self.font.render("KONIEC GRY!", True, (255, 50, 50))
            self.screen.blit(go, ((WINDOW_WIDTH - go.get_width()) // 2, (WINDOW_HEIGHT - go.get_height()) // 2))
        else:
            self.map.draw(self.screen, self.ox, self.oy)
            for g in self.ghosts:
                g.draw(self.screen, self.ox, self.oy)
            self.player.draw(self.screen, self.ox, self.oy)
            self.draw_ui()
        pygame.display.flip()

    def handle_game_over(self):
        if self.game_over and self.time_game_over:
            if time.time() - self.time_game_over > 10:
                pygame.mixer.music.stop()
                self.running = False
