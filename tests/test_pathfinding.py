import pytest
from mined_out.types import Position, Minefield
from mined_out.config import PLAYABLE_WIDTH, PLAYABLE_HEIGHT
from mined_out.pathfinding import has_path, find_path


@pytest.mark.parametrize(
    "start,goal,mines,expected",
    [
        (Position(15, 21), Position(15, 2), [], True),
        (Position(15, 21), Position(15, 2), [Position(15, 20)], True),
        (Position(15, 21), Position(15, 2), [Position(15, 10)], True),
        (Position(1, 2), Position(30, 21), [], True),
        (Position(1, 2), Position(1, 21), [], True),
    ],
)
def test_has_path_returns_true_for_open_paths(start, goal, mines, expected):
    minefield = Minefield(
        width=PLAYABLE_WIDTH, height=PLAYABLE_HEIGHT, mines=frozenset(mines)
    )
    result = has_path(start, goal, minefield)
    assert result == expected, f"Should find path from {start} to {goal}"


@pytest.mark.parametrize(
    "start,goal,blocking_mines",
    [
        (
            Position(15, 21),
            Position(15, 2),
            [Position(x, 20) for x in range(1, 31)],
        ),
        (
            Position(15, 21),
            Position(15, 2),
            [Position(14, y) for y in range(2, 22)]
            + [Position(16, y) for y in range(2, 22)]
            + [Position(15, 10)],
        ),
    ],
)
def test_has_path_returns_false_when_blocked(start, goal, blocking_mines):
    minefield = Minefield(
        width=PLAYABLE_WIDTH, height=PLAYABLE_HEIGHT, mines=frozenset(blocking_mines)
    )
    result = has_path(start, goal, minefield)
    assert result == False, f"Should not find path when completely blocked"


def test_has_path_handles_start_equals_goal():
    start = Position(15, 15)
    goal = Position(15, 15)
    minefield = Minefield(
        width=PLAYABLE_WIDTH, height=PLAYABLE_HEIGHT, mines=frozenset()
    )
    result = has_path(start, goal, minefield)
    assert result == True, "Should return True when start equals goal"


def test_has_path_avoids_mines():
    start = Position(10, 10)
    goal = Position(10, 12)
    mines = [Position(10, 11)]
    minefield = Minefield(
        width=PLAYABLE_WIDTH, height=PLAYABLE_HEIGHT, mines=frozenset(mines)
    )
    result = has_path(start, goal, minefield)
    assert result == True, "Should find path around mine"


def test_has_path_uses_cardinal_directions_only():
    start = Position(10, 10)
    goal = Position(11, 11)
    minefield = Minefield(
        width=PLAYABLE_WIDTH, height=PLAYABLE_HEIGHT, mines=frozenset()
    )
    result = has_path(start, goal, minefield)
    assert result == True, "Should find path using cardinal moves (no diagonals needed)"


def test_has_path_respects_boundaries():
    start = Position(1, 2)
    goal = Position(30, 21)
    minefield = Minefield(
        width=PLAYABLE_WIDTH, height=PLAYABLE_HEIGHT, mines=frozenset()
    )
    result = has_path(start, goal, minefield)
    assert result == True, "Should find path within valid boundaries"


def test_has_path_complex_maze():
    start = Position(2, 2)
    goal = Position(2, 21)
    mines = [Position(2, y) for y in range(3, 21)]
    minefield = Minefield(
        width=PLAYABLE_WIDTH, height=PLAYABLE_HEIGHT, mines=frozenset(mines)
    )
    result = has_path(start, goal, minefield)
    assert result == True, "Should find alternate path in complex maze"


def test_has_path_no_path_exists():
    start = Position(2, 2)
    goal = Position(2, 21)
    mines = [Position(x, 10) for x in range(1, 31)]
    minefield = Minefield(
        width=PLAYABLE_WIDTH, height=PLAYABLE_HEIGHT, mines=frozenset(mines)
    )
    result = has_path(start, goal, minefield)
    assert result == False, "Should return False when path is impossible"


@pytest.mark.parametrize(
    "start,goal,mines",
    [
        (Position(15, 21), Position(15, 2), []),
        (Position(1, 2), Position(30, 21), []),
        (Position(15, 15), Position(20, 20), [Position(16, 16)]),
    ],
)
def test_find_path_returns_valid_path(start, goal, mines):
    minefield = Minefield(
        width=PLAYABLE_WIDTH, height=PLAYABLE_HEIGHT, mines=frozenset(mines)
    )
    path = find_path(start, goal, minefield)
    assert path is not None, f"Should find path from {start} to {goal}"
    assert len(path) > 0, "Path should not be empty"
    assert path[0] == start, "Path should start at start position"
    assert path[-1] == goal, "Path should end at goal position"


def test_find_path_returns_none_when_no_path():
    start = Position(15, 21)
    goal = Position(15, 2)
    blocking_mines = [Position(x, 20) for x in range(1, 31)]
    minefield = Minefield(
        width=PLAYABLE_WIDTH, height=PLAYABLE_HEIGHT, mines=frozenset(blocking_mines)
    )
    path = find_path(start, goal, minefield)
    assert path is None, "Should return None when no path exists"


def test_find_path_uses_cardinal_moves_only():
    start = Position(10, 10)
    goal = Position(12, 12)
    minefield = Minefield(
        width=PLAYABLE_WIDTH, height=PLAYABLE_HEIGHT, mines=frozenset()
    )
    path = find_path(start, goal, minefield)
    assert path is not None, "Should find path"
    for i in range(len(path) - 1):
        curr = path[i]
        next_pos = path[i + 1]
        dx = abs(next_pos.x - curr.x)
        dy = abs(next_pos.y - curr.y)
        assert dx + dy == 1, f"Each step should be cardinal: {curr} -> {next_pos}"


def test_find_path_avoids_mines():
    start = Position(10, 10)
    goal = Position(10, 12)
    mines = [Position(10, 11)]
    minefield = Minefield(
        width=PLAYABLE_WIDTH, height=PLAYABLE_HEIGHT, mines=frozenset(mines)
    )
    path = find_path(start, goal, minefield)
    assert path is not None, "Should find path around mine"
    for pos in path:
        assert pos not in mines, f"Path should not go through mine at {pos}"


def test_find_path_single_step():
    start = Position(10, 10)
    goal = Position(10, 11)
    minefield = Minefield(
        width=PLAYABLE_WIDTH, height=PLAYABLE_HEIGHT, mines=frozenset()
    )
    path = find_path(start, goal, minefield)
    assert path is not None, "Should find path"
    assert len(path) == 2, "Path should have 2 positions (start and goal)"
    assert path == [start, goal], "Path should be direct"


def test_find_path_same_position():
    start = Position(10, 10)
    goal = Position(10, 10)
    minefield = Minefield(
        width=PLAYABLE_WIDTH, height=PLAYABLE_HEIGHT, mines=frozenset()
    )
    path = find_path(start, goal, minefield)
    assert path is not None, "Should return path when start equals goal"
    assert len(path) == 1, "Path should contain single position"
    assert path[0] == start, "Path should contain start position"


def test_find_path_returns_shortest_path():
    start = Position(10, 10)
    goal = Position(10, 15)
    minefield = Minefield(
        width=PLAYABLE_WIDTH, height=PLAYABLE_HEIGHT, mines=frozenset()
    )
    path = find_path(start, goal, minefield)
    assert path is not None, "Should find path"
    expected_length = abs(goal.y - start.y) + 1
    assert len(path) == expected_length, (
        f"BFS should find shortest path of length {expected_length}"
    )
