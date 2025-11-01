import pytest
from mined_out.types import Position, LevelConfig, Minefield, GameState, ReplayState


def test_position_creation():
    pos = Position(5, 10)
    assert pos.x == 5, "Position x should be 5"
    assert pos.y == 10, "Position y should be 10"


def test_position_immutable():
    pos = Position(5, 10)
    with pytest.raises(Exception):
        pos.x = 7


def test_position_addition():
    pos1 = Position(5, 10)
    pos2 = Position(3, -2)
    result = pos1 + pos2
    assert result.x == 8, "Position addition should sum x coordinates"
    assert result.y == 8, "Position addition should sum y coordinates"


def test_position_equality():
    pos1 = Position(5, 10)
    pos2 = Position(5, 10)
    pos3 = Position(5, 11)
    assert pos1 == pos2, "Positions with same coordinates should be equal"
    assert pos1 != pos3, "Positions with different coordinates should not be equal"


def test_minefield_creation():
    mines = frozenset([Position(1, 1), Position(2, 3)])
    minefield = Minefield(width=10, height=10, mines=mines)
    assert minefield.width == 10, "Minefield width should be 10"
    assert minefield.height == 10, "Minefield height should be 10"
    assert len(minefield.mines) == 2, "Minefield should have 2 mines"


def test_minefield_has_mine_at():
    mines = frozenset([Position(1, 1), Position(2, 3)])
    minefield = Minefield(width=10, height=10, mines=mines)
    assert minefield.has_mine_at(Position(1, 1)), "Should detect mine at (1, 1)"
    assert minefield.has_mine_at(Position(2, 3)), "Should detect mine at (2, 3)"
    assert not minefield.has_mine_at(Position(0, 0)), "Should not detect mine at (0, 0)"


def test_game_state_creation():
    minefield = Minefield(width=30, height=20, mines=frozenset())
    state = GameState(
        level_number=1,
        minefield=minefield,
        player_pos=Position(15, 21),
        visited=frozenset([Position(15, 21)]),
        move_history=(Position(15, 21),),
        lives=3,
        score=0,
        move_count=0,
    )
    assert state.level_number == 1, "Level number should be 1"
    assert state.lives == 3, "Lives should be 3"
    assert state.is_replay is False, "is_replay should default to False"


def test_game_state_immutable():
    minefield = Minefield(width=30, height=20, mines=frozenset())
    state = GameState(
        level_number=1,
        minefield=minefield,
        player_pos=Position(15, 21),
        visited=frozenset(),
        move_history=(),
        lives=3,
        score=0,
        move_count=0,
    )
    with pytest.raises(Exception):
        state.lives = 2
