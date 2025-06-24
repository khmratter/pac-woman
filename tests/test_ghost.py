import time
import pygame
import pytest
from unittest.mock import patch, Mock

from code.ghost import Ghost
from code.map import Map
from code.tile import Tile
from code.player import Player

# fixtures

@pytest.fixture(scope="module", autouse=True)
def init_pygame():
    """Initialize pygame display so .convert_alpha() works."""
    pygame.init()
    pygame.display.set_mode((1, 1))
    yield
    pygame.quit()

@pytest.fixture
def mock_ghost_image():
    """Mock out pygame.image.load to return a real Surface."""
    with patch("code.ghost.pygame.image.load") as mock_load:
        surf = pygame.Surface((10, 10), flags=pygame.SRCALPHA)
        mock_load.return_value = surf
        yield mock_load

@pytest.fixture
def empty_map():
    """5x5 Map mock with no walls anywhere."""
    m = Mock(spec=Map)
    m.size = 5
    m.grid = [      # create a grid of Tiles with no walls
        [Mock(spec=Tile, wall_top=False, wall_bottom=False, wall_left=False, wall_right=False)
         for _ in range(5)]
        for _ in range(5)
    ]
    return m

@pytest.fixture
def player():
    return Player(2, 2)


# tests


def test_ghost_initialization(mock_ghost_image):
    g = Ghost(1, 1, ghost_type="ghost1")
    assert (g.x, g.y) == (1, 1)
    assert g.ghost_type == "ghost1"
    assert isinstance(g.image, pygame.Surface)
    assert g.special_active is False

def test_can_pass_walls_only_when_active_and_type(mock_ghost_image):
    g = Ghost(0, 0, ghost_type="ghost2")
    assert not g.can_pass_walls()
    g.special_active = True
    assert g.can_pass_walls()

    g1 = Ghost(0, 0, ghost_type="ghost1")
    g1.special_active = True
    assert not g1.can_pass_walls()

def test_update_special_state_toggles_on_interval(mock_ghost_image):
    g = Ghost(0, 0, ghost_type="ghost3")
    now = time.time()
    t0 = now - (now % 10)       # find a time t such that int(t) % 10 == 0
    g.special_active = False
    g.update_special_state(t0)
    assert g.special_active is True
    assert pytest.approx(g.special_start_time, rel=1e-3) == t0

def test_update_special_state_turns_off_after_duration(mock_ghost_image):
    g = Ghost(0, 0, ghost_type="ghost1")
    g.special_active = True
    g.special_start_time = time.time() - 4.0
    g.update_special_state(time.time())
    assert g.special_active is False

def test_move_towards_path_and_random(mock_ghost_image, empty_map, player):
    g = Ghost(0, 0)
    g.last_move = time.time() - 1.0     # bypass the speed delay

    g.move_towards(player, empty_map)       # deterministic path: should move closer
    assert (g.x, g.y) in [(1, 0), (0, 1)]

    g2 = Ghost(4, 4)
    g2.last_move = time.time() - 1.0
    with patch("random.random", return_value=0.99):      # now test random fallback when random.random() is large
        g2.move_towards(player, empty_map)
    assert 0 <= g2.x < empty_map.size
    assert 0 <= g2.y < empty_map.size

def test_draw_calls_blit_correctly(mock_ghost_image, empty_map):
    screen = Mock(spec=pygame.Surface)
    g = Ghost(1, 1)      # normal ghost
    g.special_active = False
    screen.blit = Mock()
    g.draw(screen, offset_x=0, offset_y=0, map_obj=empty_map)
    screen.blit.assert_called_once()

    g3 = Ghost(1, 1, ghost_type="ghost3")
    g3.special_active = True           # ghost3 in special state: should blit 4 times (2x2)
    screen.blit.reset_mock()
    g3.draw(screen, offset_x=0, offset_y=0, map_obj=empty_map)
    assert screen.blit.call_count == 4
