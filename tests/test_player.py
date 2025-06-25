import pygame
import pytest
from unittest.mock import Mock, patch

from code.player import Player
from code.map import Map
from code.tile import Tile

# fixtures


@pytest.fixture(scope="module", autouse=True)
def init_pygame():
    """Init and quit pygame for all tests."""
    pygame.init()
    yield
    pygame.quit()


@pytest.fixture
def mock_player_image():
    """
    Patch pygame.image.load to return a real Surface (so smoothscale works).
    """
    with patch("code.player.pygame.image.load") as mock_load:
        surf = pygame.Surface(
            (10, 10), flags=pygame.SRCALPHA
        )  # create a small surface with alpha
        mock_load.return_value = surf
        yield mock_load


@pytest.fixture
def empty_map():
    """5x5 Map mock with no walls anywhere."""
    m = Mock(spec=Map)
    m.size = 5
    m.grid = [
        [
            Mock(
                spec=Tile,
                wall_top=False,
                wall_bottom=False,
                wall_left=False,
                wall_right=False,
            )
            for _ in range(5)
        ]
        for _ in range(5)
    ]
    return m


# tests


def test_player_initialization(mock_player_image):
    p = Player(2, 3)
    assert (p.x, p.y) == (2, 3)
    assert p.score == 0
    assert p.lives == 3
    assert p.direction == "right"
    assert isinstance(p.image, pygame.Surface)
    mock_player_image.assert_called_once()


def test_player_move_valid(mock_player_image, empty_map):
    p = Player(2, 2)
    p.move(1, 0, empty_map)
    assert (p.x, p.y) == (3, 2)
    assert p.direction == "right"


def test_player_move_blocked_by_wall(mock_player_image):
    m = Mock(spec=Map)
    m.size = 5
    cur = Mock(
        spec=Tile, wall_right=True, wall_left=False, wall_top=False, wall_bottom=False
    )
    tgt = Mock(
        spec=Tile, wall_right=False, wall_left=True, wall_top=False, wall_bottom=False
    )
    m.grid = [[Mock(spec=Tile) for _ in range(5)] for _ in range(5)]
    m.grid[2][2], m.grid[2][3] = cur, tgt

    p = Player(2, 2)
    p.move(1, 0, m)
    assert (p.x, p.y) == (2, 2)


def test_player_move_outside_bounds(mock_player_image, empty_map):
    p = Player(4, 2)
    p.move(1, 0, empty_map)
    assert p.x == 4

    p.x = 0
    p.move(-1, 0, empty_map)
    assert p.x == 0


def test_player_direction_changes(mock_player_image, empty_map):
    p = Player(1, 1)
    p.move(0, -1, empty_map)
    assert p.direction == "up"
    p.move(1, 0, empty_map)
    assert p.direction == "right"
    p.move(0, 1, empty_map)
    assert p.direction == "down"
    p.move(-1, 0, empty_map)
    assert p.direction == "left"


def test_player_draw_method(mock_player_image):
    p = Player(2, 3)
    screen = Mock(spec=pygame.Surface)
    p.direction = "up"
    p.draw(screen, offset_x=5, offset_y=7)
    screen.blit.assert_called_once()
