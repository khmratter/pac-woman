from game import Game
import pygame


def main():
    game = Game()
    while game.running:
        game.handle_events()
        game.update()
        game.render()
        game.handle_game_over()
        game.clock.tick(60)
    pygame.quit()


if __name__ == "__main__":
    main()
