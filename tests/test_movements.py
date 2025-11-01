import pytest
from mined_out.types import Position
from mined_out.config import (
    PLAYAREA_START_ROW,
    PLAYAREA_END_ROW,
    TOP_WALL_ROW,
    BOTTOM_WALL_ROW,
)
from mined_out.movement import (
    Direction,
    get_next_position,
    is_valid_position,
    can_move_to,
)


@pytest.mark.parametrize(
    "current_pos,direction,expected_pos",
    [
        (Position(15, 15), Direction.UP, Position(15, 14)),
        (Position(15, 15), Direction.DOWN, Position(15, 16)),
        (Position(15, 15), Direction.LEFT, Position(14, 15)),
        (Position(15, 15), Direction.RIGHT, Position(16, 15)),
    ],
)
def test_get_next_position_returns_correct_position(
    current_pos, direction, expected_pos
):
    result = get_next_position(current_pos, direction)
    assert result == expected_pos, (
        f"Moving {direction.name} from {current_pos} should result in {expected_pos}"
    )


@pytest.mark.parametrize(
    "position,expected",
    [
        (Position(1, PLAYAREA_START_ROW), True),
        (Position(30, PLAYAREA_START_ROW), True),
        (Position(15, PLAYAREA_END_ROW), True),
        (Position(15, PLAYAREA_START_ROW), True),
        (Position(0, PLAYAREA_START_ROW), False),
        (Position(31, PLAYAREA_START_ROW), False),
        (Position(15, TOP_WALL_ROW), False),
        (Position(15, BOTTOM_WALL_ROW), False),
        (Position(15, 1), False),
        (Position(15, 22), False),
        (Position(-1, 15), False),
        (Position(32, 15), False),
        (Position(15, -1), False),
        (Position(15, 24), False),
    ],
)
def test_is_valid_position_boundary_checks(position, expected):
    result = is_valid_position(position)
    assert result == expected, (
        f"Position {position} should be {'valid' if expected else 'invalid'}"
    )


def test_is_valid_position_accepts_all_playable_positions():
    for x in range(1, 31):
        for y in range(PLAYAREA_START_ROW, PLAYAREA_END_ROW + 1):
            position = Position(x, y)
            assert is_valid_position(position), (
                f"Position {position} should be valid in playable area"
            )


@pytest.mark.parametrize(
    "position,expected",
    [
        (Position(15, PLAYAREA_START_ROW), True),
        (Position(1, 10), True),
        (Position(30, 10), True),
        (Position(0, 10), False),
        (Position(31, 10), False),
        (Position(15, TOP_WALL_ROW), False),
        (Position(15, BOTTOM_WALL_ROW), False),
    ],
)
def test_can_move_to_basic_validation(position, expected):
    result = can_move_to(position)
    assert result == expected, (
        f"Should {'be able' if expected else 'not be able'} to move to {position}"
    )


@pytest.mark.parametrize(
    "start_pos,direction,expected",
    [
        (Position(1, PLAYAREA_START_ROW), Direction.LEFT, False),
        (Position(30, PLAYAREA_START_ROW), Direction.RIGHT, False),
        (Position(15, PLAYAREA_START_ROW), Direction.UP, False),
        (Position(15, PLAYAREA_END_ROW), Direction.DOWN, False),
        (Position(15, 10), Direction.UP, True),
        (Position(15, 10), Direction.DOWN, True),
        (Position(15, 10), Direction.LEFT, True),
        (Position(15, 10), Direction.RIGHT, True),
    ],
)
def test_can_move_to_edge_cases(start_pos, direction, expected):
    next_pos = get_next_position(start_pos, direction)
    result = can_move_to(next_pos)
    assert result == expected, (
        f"Should {'be able' if expected else 'not be able'} to move {direction.name} from {start_pos}"
    )
