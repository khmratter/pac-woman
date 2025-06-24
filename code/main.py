from .game import Game
import pygame


def main() -> None:
    """
    Execute the program.

    Runs the main game loop when executing the main.py file from console.
    This method  is not designed to be called like a method from a module.
    Initializes the game until the game is no longer running.
    Limits fps (frames per second) to 60.
    
    Returns: 
    None
    """
    game = Game()
    while game.running:
        game.handle_events()
        game.update()
        game.render()
        game.handle_game_over()
        game.clock.tick(60)  # 60 fps
    pygame.quit()


if __name__ == "__main__":
    main()
