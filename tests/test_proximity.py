import pytest
from mined_out.types import Position, Minefield
from mined_out.config import PLAYABLE_WIDTH, PLAYABLE_HEIGHT
from mined_out.proximity import count_adjacent_mines, get_adjacent_positions


@pytest.mark.parametrize(
    "position,expected_positions",
    [
        (
            Position(10, 10),
            [Position(10, 9), Position(10, 11), Position(9, 10), Position(11, 10)],
        ),
        (
            Position(5, 5),
            [Position(5, 4), Position(5, 6), Position(4, 5), Position(6, 5)],
        ),
        (
            Position(15, 15),
            [Position(15, 14), Position(15, 16), Position(14, 15), Position(16, 15)],
        ),
    ],
)
def test_get_adjacent_positions_returns_cardinal_neighbors(
    position, expected_positions
):
    result = get_adjacent_positions(position)
    assert set(result) == set(expected_positions), (
        f"Should return 4 cardinal neighbors for {position}"
    )
    assert len(result) == 4, f"Should return exactly 4 positions for {position}"


def test_get_adjacent_positions_excludes_diagonals():
    position = Position(10, 10)
    result = get_adjacent_positions(position)
    diagonals = [
        Position(9, 9),
        Position(11, 9),
        Position(9, 11),
        Position(11, 11),
    ]
    for diagonal in diagonals:
        assert diagonal not in result, (
            f"Should not include diagonal position {diagonal}"
        )


@pytest.mark.parametrize(
    "player_pos,mine_positions,expected_count",
    [
        (Position(10, 10), [], 0),
        (Position(10, 10), [Position(10, 9)], 1),
        (Position(10, 10), [Position(10, 9), Position(10, 11)], 2),
        (Position(10, 10), [Position(10, 9), Position(10, 11), Position(9, 10)], 3),
        (
            Position(10, 10),
            [
                Position(10, 9),
                Position(10, 11),
                Position(9, 10),
                Position(11, 10),
            ],
            4,
        ),
    ],
)
def test_count_adjacent_mines_counts_cardinal_neighbors(
    player_pos, mine_positions, expected_count
):
    minefield = Minefield(
        width=PLAYABLE_WIDTH,
        height=PLAYABLE_HEIGHT,
        mines=frozenset(mine_positions),
    )
    result = count_adjacent_mines(player_pos, minefield)
    assert result == expected_count, (
        f"Should count {expected_count} adjacent mines at {player_pos}"
    )


def test_count_adjacent_mines_ignores_diagonal_mines():
    player_pos = Position(10, 10)
    diagonal_mines = [
        Position(9, 9),
        Position(11, 9),
        Position(9, 11),
        Position(11, 11),
    ]
    minefield = Minefield(
        width=PLAYABLE_WIDTH,
        height=PLAYABLE_HEIGHT,
        mines=frozenset(diagonal_mines),
    )
    result = count_adjacent_mines(player_pos, minefield)
    assert result == 0, "Should ignore diagonal mines"


def test_count_adjacent_mines_ignores_distant_mines():
    player_pos = Position(10, 10)
    distant_mines = [
        Position(10, 8),
        Position(10, 12),
        Position(8, 10),
        Position(12, 10),
    ]
    minefield = Minefield(
        width=PLAYABLE_WIDTH,
        height=PLAYABLE_HEIGHT,
        mines=frozenset(distant_mines),
    )
    result = count_adjacent_mines(player_pos, minefield)
    assert result == 0, "Should ignore mines more than 1 tile away"


@pytest.mark.parametrize(
    "edge_pos,mine_offset,expected_count",
    [
        (Position(1, 10), Position(0, 0), 0),
        (Position(1, 10), Position(1, 0), 1),
        (Position(30, 10), Position(1, 0), 0),
        (Position(30, 10), Position(0, 1), 1),
        (Position(15, 2), Position(0, -1), 0),
        (Position(15, 21), Position(0, 1), 0),
    ],
)
def test_count_adjacent_mines_handles_edges(edge_pos, mine_offset, expected_count):
    mine_pos = edge_pos + mine_offset
    minefield = Minefield(
        width=PLAYABLE_WIDTH, height=PLAYABLE_HEIGHT, mines=frozenset([mine_pos])
    )
    result = count_adjacent_mines(edge_pos, minefield)
    assert result == expected_count, (
        f"Should count {expected_count} mine(s) at edge position {edge_pos}"
    )


def test_count_adjacent_mines_at_corner_position():
    corner_pos = Position(1, 2)
    adjacent_mines = [Position(2, 2), Position(1, 3)]
    minefield = Minefield(
        width=PLAYABLE_WIDTH,
        height=PLAYABLE_HEIGHT,
        mines=frozenset(adjacent_mines),
    )
    result = count_adjacent_mines(corner_pos, minefield)
    assert result == 2, "Should count mines adjacent to corner position"


def test_count_adjacent_mines_only_counts_valid_positions():
    edge_pos = Position(1, 2)
    mines_including_invalid = [
        Position(0, 2),
        Position(2, 2),
        Position(1, 1),
    ]
    minefield = Minefield(
        width=PLAYABLE_WIDTH,
        height=PLAYABLE_HEIGHT,
        mines=frozenset(mines_including_invalid),
    )
    result = count_adjacent_mines(edge_pos, minefield)
    assert result == 1, "Should only count mine at valid position (2, 2)"


@pytest.mark.parametrize(
    "position,mine_config,expected",
    [
        (Position(10, 10), [], 0),
        (Position(10, 10), [Position(10, 9)], 1),
        (Position(10, 10), [Position(10, 9), Position(11, 10)], 2),
        (Position(10, 10), [Position(10, 9), Position(11, 10), Position(10, 11)], 3),
        (
            Position(10, 10),
            [
                Position(10, 9),
                Position(11, 10),
                Position(10, 11),
                Position(9, 10),
            ],
            4,
        ),
    ],
)
def test_count_adjacent_mines_various_configurations(position, mine_config, expected):
    minefield = Minefield(
        width=PLAYABLE_WIDTH, height=PLAYABLE_HEIGHT, mines=frozenset(mine_config)
    )
    result = count_adjacent_mines(position, minefield)
    assert result == expected, (
        f"Position {position} should have {expected} adjacent mines"
    )


def test_count_adjacent_mines_with_many_distant_mines():
    player_pos = Position(10, 10)
    many_mines = [Position(x, y) for x in range(2, 9) for y in range(3, 8)]
    minefield = Minefield(
        width=PLAYABLE_WIDTH, height=PLAYABLE_HEIGHT, mines=frozenset(many_mines)
    )
    result = count_adjacent_mines(player_pos, minefield)
    assert result == 0, "Should not count any distant mines"


def test_count_adjacent_mines_mixed_adjacent_and_distant():
    player_pos = Position(10, 10)
    mines = [
        Position(10, 9),
        Position(10, 11),
        Position(5, 5),
        Position(20, 20),
        Position(15, 15),
    ]
    minefield = Minefield(
        width=PLAYABLE_WIDTH, height=PLAYABLE_HEIGHT, mines=frozenset(mines)
    )
    result = count_adjacent_mines(player_pos, minefield)
    assert result == 2, "Should count only the 2 adjacent mines"
