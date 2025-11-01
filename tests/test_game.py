import pytest
from mined_out.types import Position, GameState
from mined_out.config import INITIAL_LIVES
from mined_out.movement import Direction
from mined_out.game import (
    create_initial_game_state,
    move_player,
    is_on_mine,
    is_at_exit,
    start_new_level,
    handle_death,
    handle_level_complete,
)


def test_create_initial_game_state_has_correct_level():
    state = create_initial_game_state()
    assert state.level_number == 1, "Should start at level 1"


def test_create_initial_game_state_has_initial_lives():
    state = create_initial_game_state()
    assert state.lives == INITIAL_LIVES, f"Should start with {INITIAL_LIVES} lives"


def test_create_initial_game_state_has_zero_score():
    state = create_initial_game_state()
    assert state.score == 0, "Should start with 0 score"


def test_create_initial_game_state_has_zero_move_count():
    state = create_initial_game_state()
    assert state.move_count == 0, "Should start with 0 moves"


def test_create_initial_game_state_player_at_start():
    state = create_initial_game_state()
    from mined_out.level import get_start_position

    expected_start = get_start_position()
    assert state.player_pos == expected_start, "Player should be at start position"


def test_create_initial_game_state_has_valid_minefield():
    state = create_initial_game_state()
    from mined_out.pathfinding import has_path
    from mined_out.level import get_start_position, get_exit_position

    assert has_path(get_start_position(), get_exit_position(), state.minefield), (
        "Initial minefield should be solvable"
    )


def test_create_initial_game_state_visited_includes_start():
    state = create_initial_game_state()
    assert state.player_pos in state.visited, "Start position should be visited"


def test_create_initial_game_state_move_history_has_start():
    state = create_initial_game_state()
    assert len(state.move_history) == 1, "Move history should have start position"
    assert state.move_history[0] == state.player_pos, (
        "First move should be start position"
    )


def test_create_initial_game_state_not_replay():
    state = create_initial_game_state()
    assert not state.is_replay, "Should not be in replay mode"


@pytest.mark.parametrize(
    "direction", [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT]
)
def test_move_player_updates_position(direction):
    state = create_initial_game_state()
    from mined_out.movement import get_next_position, can_move_to

    next_pos = get_next_position(state.player_pos, direction)
    if can_move_to(next_pos):
        new_state = move_player(state, direction)
        assert new_state.player_pos == next_pos, f"Player should move {direction.name}"


def test_move_player_increments_move_count():
    state = create_initial_game_state()
    new_state = move_player(state, Direction.UP)
    assert new_state.move_count == state.move_count + 1, "Move count should increment"


def test_move_player_adds_to_visited():
    state = create_initial_game_state()
    new_state = move_player(state, Direction.UP)
    assert new_state.player_pos in new_state.visited, "New position should be visited"


def test_move_player_adds_to_move_history():
    state = create_initial_game_state()
    new_state = move_player(state, Direction.UP)
    assert len(new_state.move_history) == 2, "Move history should grow"
    assert new_state.move_history[-1] == new_state.player_pos, (
        "Last move should be current position"
    )


def test_move_player_preserves_other_fields():
    state = create_initial_game_state()
    new_state = move_player(state, Direction.UP)
    assert new_state.level_number == state.level_number, "Should preserve level number"
    assert new_state.lives == state.lives, "Should preserve lives"
    assert new_state.score == state.score, "Should preserve score"
    assert new_state.minefield == state.minefield, "Should preserve minefield"


def test_move_player_invalid_move_returns_same_state():
    state = create_initial_game_state()
    from mined_out.movement import get_next_position, can_move_to

    for direction in [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT]:
        next_pos = get_next_position(state.player_pos, direction)
        if not can_move_to(next_pos):
            new_state = move_player(state, direction)
            assert new_state == state, (
                f"Invalid move {direction.name} should return same state"
            )
            break


def test_is_on_mine_returns_true_when_on_mine():
    state = create_initial_game_state()

    if len(state.minefield.mines) > 0:
        mine_pos = list(state.minefield.mines)[0]
        test_state = GameState(
            level_number=state.level_number,
            minefield=state.minefield,
            player_pos=mine_pos,
            visited=state.visited,
            move_history=state.move_history,
            lives=state.lives,
            score=state.score,
            move_count=state.move_count,
        )
        assert is_on_mine(test_state), "Should detect mine at player position"


def test_is_on_mine_returns_false_when_not_on_mine():
    state = create_initial_game_state()
    assert not is_on_mine(state), "Start position should not have mine"


def test_is_at_exit_returns_true_at_exit():
    from mined_out.level import get_exit_position

    state = create_initial_game_state()
    exit_pos = get_exit_position()

    test_state = GameState(
        level_number=state.level_number,
        minefield=state.minefield,
        player_pos=exit_pos,
        visited=state.visited,
        move_history=state.move_history,
        lives=state.lives,
        score=state.score,
        move_count=state.move_count,
    )
    assert is_at_exit(test_state), "Should detect player at exit"


def test_is_at_exit_returns_false_when_not_at_exit():
    state = create_initial_game_state()
    assert not is_at_exit(state), "Start position should not be exit"


@pytest.mark.parametrize("level_number", [1, 2, 5, 10])
def test_start_new_level_creates_valid_state(level_number):
    state = start_new_level(level_number, score=100, lives=2)
    assert state.level_number == level_number, f"Should be level {level_number}"
    assert state.score == 100, "Should preserve score"
    assert state.lives == 2, "Should preserve lives"


def test_start_new_level_has_solvable_minefield():
    state = start_new_level(5, score=0, lives=3)
    from mined_out.pathfinding import has_path
    from mined_out.level import get_start_position, get_exit_position

    assert has_path(get_start_position(), get_exit_position(), state.minefield), (
        "New level should be solvable"
    )


def test_start_new_level_resets_move_count():
    state = start_new_level(1, score=500, lives=2)
    assert state.move_count == 0, "Move count should reset"


def test_start_new_level_resets_visited():
    state = start_new_level(1, score=500, lives=2)
    assert len(state.visited) == 1, "Visited should only have start position"


def test_start_new_level_resets_move_history():
    state = start_new_level(1, score=500, lives=2)
    assert len(state.move_history) == 1, "Move history should only have start position"


def test_handle_death_decrements_lives():
    state = create_initial_game_state()
    new_state = handle_death(state)
    assert new_state.lives == state.lives - 1, "Should lose a life"


def test_handle_death_applies_score_penalty():
    state = create_initial_game_state()
    initial_score = 200
    state = GameState(
        level_number=state.level_number,
        minefield=state.minefield,
        player_pos=state.player_pos,
        visited=state.visited,
        move_history=state.move_history,
        lives=state.lives,
        score=initial_score,
        move_count=state.move_count,
    )
    new_state = handle_death(state)
    assert new_state.score < initial_score, "Score should decrease"


def test_handle_death_resets_level_for_retry():
    state = create_initial_game_state()
    new_state = handle_death(state)
    assert new_state.level_number == state.level_number, "Should retry same level"
    assert new_state.move_count == 0, "Move count should reset"


def test_handle_death_returns_none_on_game_over():
    state = create_initial_game_state()
    state = GameState(
        level_number=state.level_number,
        minefield=state.minefield,
        player_pos=state.player_pos,
        visited=state.visited,
        move_history=state.move_history,
        lives=1,
        score=state.score,
        move_count=state.move_count,
    )
    new_state = handle_death(state)
    assert new_state is None, "Should return None when out of lives"


def test_handle_level_complete_increments_level():
    state = create_initial_game_state()
    new_state = handle_level_complete(state)
    assert new_state.level_number == state.level_number + 1, (
        "Should advance to next level"
    )


def test_handle_level_complete_increases_score():
    state = create_initial_game_state()
    initial_score = state.score
    new_state = handle_level_complete(state)
    assert new_state.score > initial_score, "Score should increase"


def test_handle_level_complete_resets_move_count():
    state = create_initial_game_state()

    state = move_player(state, Direction.UP)
    state = move_player(state, Direction.UP)

    new_state = handle_level_complete(state)
    assert new_state.move_count == 0, "Move count should reset for new level"


def test_handle_level_complete_preserves_lives():
    state = create_initial_game_state()
    new_state = handle_level_complete(state)
    assert new_state.lives == state.lives, "Should preserve lives"


def test_handle_level_complete_creates_new_minefield():
    state = create_initial_game_state()
    new_state = handle_level_complete(state)
    assert new_state.minefield != state.minefield, "Should have new minefield"
