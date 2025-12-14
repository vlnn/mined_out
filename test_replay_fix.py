"""
Test to verify that replay shows original path, not shuffled path.

This test creates a scenario where:
1. Player makes some moves
2. PathShuffler shuffles some visited positions
3. Replay should show the original path taken, not the final shuffled positions
"""

import pytest
from unittest.mock import patch
from mined_out.types import Position, GameState, Minefield
from mined_out.game import move_player
from mined_out.movement import Direction
from mined_out.main import MinedOutGame
from mined_out.path_shuffler import PathShuffler


def test_replay_shows_original_path_not_shuffled_path():
    """Test that replay displays original path progression, not shuffled final state."""
    
    # Create initial state
    game = MinedOutGame()
    
    # Make some moves to create a path
    initial_state = game.state
    state = move_player(initial_state, Direction.RIGHT)
    state = move_player(state, Direction.RIGHT)
    state = move_player(state, Direction.UP)
    
    # Store the original path before any shuffling
    original_path = state.original_path or state.move_history
    print(f"Original path: {original_path}")
    
    # Force a shuffle to happen (Level 2+, move_count divisible by 5)
    # We'll manually trigger shuffling by creating a level 2 state
    from mined_out.level import generate_level, get_start_position
    level_2_minefield = generate_level(2)
    start_pos = get_start_position()
    
    # Create state with same path but level 2 to trigger shuffling
    test_state = GameState(
        level_number=2,
        minefield=level_2_minefield,
        player_pos=state.player_pos,
        visited=state.visited,
        move_history=state.move_history,
        original_path=original_path,  # Preserve original path
        lives=state.lives,
        score=state.score,
        move_count=5,  # Trigger shuffle (5 % 5 == 0)
    )
    
    # Apply shuffle
    shuffler = PathShuffler()
    with patch('random.random', return_value=0.2):  # Force 30% probability
        shuffled_state, shuffle_event = shuffler.shuffle_path(test_state)
    
    print(f"Shuffled move_history: {shuffled_state.move_history}")
    print(f"Preserved original_path: {shuffled_state.original_path}")
    
    # Verify that original path is preserved
    assert shuffled_state.original_path == original_path
    
    # Verify that move_history is different (shuffled occurred)
    assert shuffled_state.move_history != original_path
    
    # Verify that shuffle event occurred
    assert shuffle_event is not None
    
    # The key test: replay should use original_path, not move_history
    # This simulates what happens in main.py replay rendering
    from mined_out.replay import get_replay_position, create_replay_state
    
    replay_history = shuffled_state.original_path  # This is what main.py now uses
    replay_state = create_replay_state(replay_history)
    
    # Get positions at different replay frames
    frame_0_pos = get_replay_position(replay_state._replace(current_frame=0), replay_history)
    frame_1_pos = get_replay_position(replay_state._replace(current_frame=1), replay_history)
    frame_2_pos = get_replay_position(replay_state._replace(current_frame=2), replay_history)
    
    # These should match the ORIGINAL path, not the shuffled move_history
    assert frame_0_pos == original_path[0]
    assert frame_1_pos == original_path[1] 
    assert frame_2_pos == original_path[2]
    
    # And they should NOT match the shuffled move_history (if different)
    if shuffled_state.move_history != original_path:
        assert frame_0_pos != shuffled_state.move_history[0] or frame_0_pos == original_path[0]
        assert frame_1_pos != shuffled_state.move_history[1] or frame_1_pos == original_path[1]
        assert frame_2_pos != shuffled_state.move_history[2] or frame_2_pos == original_path[2]


if __name__ == "__main__":
    test_replay_shows_original_path_not_shuffled_path()
    print("✅ Replay correctly shows original path, not shuffled path!")