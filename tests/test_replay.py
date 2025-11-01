import pytest
from mined_out.types import Position, ReplayState
from mined_out.config import REPLAY_SPEED_MULTIPLIER
from mined_out.replay import (
    create_replay_state,
    advance_replay,
    is_replay_complete,
    get_replay_position,
    skip_to_end,
)


@pytest.mark.parametrize(
    "move_history,expected_total",
    [
        ((Position(15, 21),), 1),
        ((Position(15, 21), Position(15, 20)), 2),
        ((Position(15, 21), Position(15, 20), Position(15, 19)), 3),
        (tuple(Position(x, 10) for x in range(1, 11)), 10),
    ],
)
def test_create_replay_state_has_correct_total_frames(move_history, expected_total):
    replay = create_replay_state(move_history)
    assert replay.total_frames == expected_total, (
        f"Should have {expected_total} total frames"
    )


def test_create_replay_state_starts_at_frame_zero():
    move_history = (Position(15, 21), Position(15, 20))
    replay = create_replay_state(move_history)
    assert replay.current_frame == 0, "Should start at frame 0"


def test_create_replay_state_uses_correct_speed_multiplier():
    move_history = (Position(15, 21),)
    replay = create_replay_state(move_history)
    assert replay.speed_multiplier == REPLAY_SPEED_MULTIPLIER, (
        f"Should use speed multiplier {REPLAY_SPEED_MULTIPLIER}"
    )


def test_create_replay_state_empty_history():
    move_history = ()
    replay = create_replay_state(move_history)
    assert replay.total_frames == 0, "Empty history should have 0 frames"
    assert replay.current_frame == 0, "Should start at frame 0"


@pytest.mark.parametrize(
    "current_frame,total_frames",
    [
        (0, 10),
        (5, 10),
        (9, 10),
    ],
)
def test_advance_replay_increments_frame(current_frame, total_frames):
    replay = ReplayState(current_frame, total_frames, REPLAY_SPEED_MULTIPLIER)
    next_replay = advance_replay(replay)
    assert next_replay.current_frame == current_frame + 1, "Should increment frame by 1"


def test_advance_replay_preserves_total_frames():
    replay = ReplayState(5, 10, REPLAY_SPEED_MULTIPLIER)
    next_replay = advance_replay(replay)
    assert next_replay.total_frames == 10, "Should preserve total frames"


def test_advance_replay_preserves_speed_multiplier():
    replay = ReplayState(5, 10, REPLAY_SPEED_MULTIPLIER)
    next_replay = advance_replay(replay)
    assert next_replay.speed_multiplier == REPLAY_SPEED_MULTIPLIER, (
        "Should preserve speed multiplier"
    )


def test_advance_replay_at_end_stays_at_end():
    replay = ReplayState(10, 10, REPLAY_SPEED_MULTIPLIER)
    next_replay = advance_replay(replay)
    assert next_replay.current_frame == 10, "Should not advance past total frames"


def test_advance_replay_multiple_times():
    replay = ReplayState(0, 5, REPLAY_SPEED_MULTIPLIER)
    for i in range(1, 6):
        replay = advance_replay(replay)
        expected = min(i, 5)
        assert replay.current_frame == expected, (
            f"After {i} advances, should be at frame {expected}"
        )


@pytest.mark.parametrize(
    "current_frame,total_frames,expected",
    [
        (0, 10, False),
        (5, 10, False),
        (9, 10, False),
        (10, 10, True),
        (11, 10, True),
        (0, 0, True),
    ],
)
def test_is_replay_complete_returns_correct_value(
    current_frame, total_frames, expected
):
    replay = ReplayState(current_frame, total_frames, REPLAY_SPEED_MULTIPLIER)
    result = is_replay_complete(replay)
    assert result == expected, (
        f"Frame {current_frame}/{total_frames} should be {'complete' if expected else 'incomplete'}"
    )


def test_is_replay_complete_empty_replay():
    replay = ReplayState(0, 0, REPLAY_SPEED_MULTIPLIER)
    assert is_replay_complete(replay), "Empty replay should be complete"


@pytest.mark.parametrize(
    "frame,move_history,expected_pos",
    [
        (0, (Position(15, 21), Position(15, 20)), Position(15, 21)),
        (1, (Position(15, 21), Position(15, 20)), Position(15, 20)),
        (0, (Position(10, 10), Position(11, 10), Position(12, 10)), Position(10, 10)),
        (1, (Position(10, 10), Position(11, 10), Position(12, 10)), Position(11, 10)),
        (2, (Position(10, 10), Position(11, 10), Position(12, 10)), Position(12, 10)),
    ],
)
def test_get_replay_position_returns_correct_position(
    frame, move_history, expected_pos
):
    replay = ReplayState(frame, len(move_history), REPLAY_SPEED_MULTIPLIER)
    result = get_replay_position(replay, move_history)
    assert result == expected_pos, f"Frame {frame} should show position {expected_pos}"


def test_get_replay_position_at_end_returns_last_position():
    move_history = (Position(15, 21), Position(15, 20), Position(15, 19))
    replay = ReplayState(3, 3, REPLAY_SPEED_MULTIPLIER)
    result = get_replay_position(replay, move_history)
    assert result == Position(15, 19), "Should return last position when at end"


def test_get_replay_position_beyond_end_returns_last_position():
    move_history = (Position(15, 21), Position(15, 20))
    replay = ReplayState(5, 2, REPLAY_SPEED_MULTIPLIER)
    result = get_replay_position(replay, move_history)
    assert result == Position(15, 20), "Should return last position when beyond end"


def test_get_replay_position_empty_history_returns_none():
    move_history = ()
    replay = ReplayState(0, 0, REPLAY_SPEED_MULTIPLIER)
    result = get_replay_position(replay, move_history)
    assert result is None, "Empty history should return None"


def test_skip_to_end_sets_frame_to_total():
    replay = ReplayState(3, 10, REPLAY_SPEED_MULTIPLIER)
    result = skip_to_end(replay)
    assert result.current_frame == 10, "Should set current frame to total frames"


def test_skip_to_end_preserves_total_frames():
    replay = ReplayState(3, 10, REPLAY_SPEED_MULTIPLIER)
    result = skip_to_end(replay)
    assert result.total_frames == 10, "Should preserve total frames"


def test_skip_to_end_preserves_speed_multiplier():
    replay = ReplayState(3, 10, REPLAY_SPEED_MULTIPLIER)
    result = skip_to_end(replay)
    assert result.speed_multiplier == REPLAY_SPEED_MULTIPLIER, (
        "Should preserve speed multiplier"
    )


def test_skip_to_end_already_at_end():
    replay = ReplayState(10, 10, REPLAY_SPEED_MULTIPLIER)
    result = skip_to_end(replay)
    assert result.current_frame == 10, "Should remain at end"


def test_replay_full_sequence():
    move_history = tuple(Position(15, y) for y in range(21, 16, -1))
    replay = create_replay_state(move_history)

    assert not is_replay_complete(replay), "Should not be complete at start"

    positions = []
    while not is_replay_complete(replay):
        pos = get_replay_position(replay, move_history)
        positions.append(pos)
        replay = advance_replay(replay)

    assert len(positions) == 5, "Should have 5 positions"
    assert positions == list(move_history), "Should replay all positions in order"


def test_replay_with_skip():
    move_history = tuple(Position(15, y) for y in range(21, 11, -1))
    replay = create_replay_state(move_history)

    replay = advance_replay(replay)
    replay = advance_replay(replay)
    assert replay.current_frame == 2, "Should be at frame 2"

    replay = skip_to_end(replay)
    assert is_replay_complete(replay), "Should be complete after skip"

    pos = get_replay_position(replay, move_history)
    assert pos == Position(15, 12), "Should show last position after skip"


@pytest.mark.parametrize(
    "total_frames",
    [1, 5, 10, 20, 100],
)
def test_replay_completes_after_exact_advances(total_frames):
    move_history = tuple(Position(i, i) for i in range(total_frames))
    replay = create_replay_state(move_history)

    for _ in range(total_frames):
        replay = advance_replay(replay)

    assert is_replay_complete(replay), (
        f"Should be complete after {total_frames} advances"
    )
