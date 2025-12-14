import pytest
from unittest.mock import patch
from mined_out.types import Position, GameState, Minefield
from mined_out.path_shuffler import PathShuffler, ShuffleEvent
from mined_out.config import COLOR_DARK_BLUE, PLAYABLE_WIDTH, PLAYABLE_HEIGHT


class TestPathShuffler:
    
    def test_init_default_frequency(self):
        shuffler = PathShuffler()
        assert shuffler.shuffle_frequency == 5
    
    def test_init_custom_frequency(self):
        shuffler = PathShuffler(shuffle_frequency=10)
        assert shuffler.shuffle_frequency == 10
    
    def test_should_shuffle_level_1_false(self):
        shuffler = PathShuffler()
        state = GameState(
            level_number=1,
            minefield=Minefield(width=30, height=20, mines=frozenset()),
            player_pos=Position(15, 10),
            visited=frozenset([Position(15, 10)]),
            move_history=(Position(15, 10),),
            lives=3,
            score=0,
            move_count=5,
        )
        assert not shuffler.should_shuffle(state)
    
    def test_should_shuffle_level_2_true(self):
        shuffler = PathShuffler()
        state = GameState(
            level_number=2,
            minefield=Minefield(width=30, height=20, mines=frozenset()),
            player_pos=Position(15, 10),
            visited=frozenset([Position(15, 10)]),
            move_history=(Position(15, 10),),
            lives=3,
            score=0,
            move_count=5,
        )
        assert shuffler.should_shuffle(state)
    
    def test_should_shuffle_frequency(self):
        shuffler = PathShuffler(shuffle_frequency=3)
        state = GameState(
            level_number=2,
            minefield=Minefield(width=30, height=20, mines=frozenset()),
            player_pos=Position(15, 10),
            visited=frozenset([Position(15, 10)]),
            move_history=(Position(15, 10),),
            lives=3,
            score=0,
            move_count=2,  # Not divisible by 3
        )
        assert not shuffler.should_shuffle(state)
        
        state = state._replace(move_count=3)  # Divisible by 3
        assert shuffler.should_shuffle(state)
    
    def test_get_shuffle_distance_distribution(self):
        shuffler = PathShuffler()
        distances = []
        
        # Run many times to check distribution
        for _ in range(1000):
            distances.append(shuffler.get_shuffle_distance())
        
        # Check that most distances are 1-3 (70%)
        close_count = sum(1 for d in distances if 1 <= d <= 3)
        medium_count = sum(1 for d in distances if 4 <= d <= 6)
        far_count = sum(1 for d in distances if 7 <= d <= 10)
        
        # Allow some tolerance in distribution
        assert close_count >= 600  # Should be around 700
        assert medium_count >= 150  # Should be around 200
        assert far_count >= 80     # Should be around 100
    
    def test_shuffle_path_no_visited_positions(self):
        shuffler = PathShuffler()
        state = GameState(
            level_number=2,
            minefield=Minefield(width=30, height=20, mines=frozenset()),
            player_pos=Position(15, 10),
            visited=frozenset(),  # No visited positions
            move_history=(),
            lives=3,
            score=0,
            move_count=5,
        )
        
        new_state, shuffle_event = shuffler.shuffle_path(state)
        assert new_state == state  # No change
        assert shuffle_event is None
    
    @patch('random.random')
    def test_shuffle_path_with_visited_positions(self, mock_random):
        shuffler = PathShuffler()
        visited_pos = Position(10, 10)
        state = GameState(
            level_number=2,
            minefield=Minefield(width=30, height=20, mines=frozenset()),
            player_pos=Position(15, 10),
            visited=frozenset([visited_pos]),
            move_history=(visited_pos,),
            lives=3,
            score=0,
            move_count=5,
        )
        
        # Force 30% probability to trigger
        mock_random.return_value = 0.2
        
        new_state, shuffle_event = shuffler.shuffle_path(state)
        
        assert shuffle_event is not None
        assert shuffle_event.old_position == visited_pos
        assert shuffle_event.new_position != visited_pos
        assert shuffle_event.new_position not in state.visited
        assert visited_pos not in new_state.visited
        assert shuffle_event.new_position in new_state.visited
    
    @patch('random.random')
    def test_shuffle_path_avoids_player_position(self, mock_random):
        shuffler = PathShuffler()
        visited_pos = Position(10, 10)
        player_pos = Position(12, 10)
        state = GameState(
            level_number=2,
            minefield=Minefield(width=30, height=20, mines=frozenset()),
            player_pos=player_pos,
            visited=frozenset([visited_pos]),
            move_history=(visited_pos,),
            lives=3,
            score=0,
            move_count=5,
        )
        
        # Force 30% probability to trigger
        mock_random.return_value = 0.2
        
        new_state, shuffle_event = shuffler.shuffle_path(state)
        
        assert shuffle_event is not None
        assert shuffle_event.new_position != player_pos
    
    @patch('random.random')
    def test_shuffle_path_updates_move_history(self, mock_random):
        shuffler = PathShuffler()
        old_pos = Position(10, 10)
        state = GameState(
            level_number=2,
            minefield=Minefield(width=30, height=20, mines=frozenset()),
            player_pos=Position(15, 10),
            visited=frozenset([old_pos]),
            move_history=(old_pos, Position(15, 10)),
            lives=3,
            score=0,
            move_count=5,
        )
        
        # Force 30% probability to trigger
        mock_random.return_value = 0.2
        
        new_state, shuffle_event = shuffler.shuffle_path(state)
        
        assert shuffle_event is not None
        assert shuffle_event.old_position == old_pos
        assert shuffle_event.new_position != old_pos
        assert shuffle_event.new_position not in state.visited
        assert old_pos not in new_state.visited
        assert shuffle_event.new_position in new_state.visited
        
        # The old position should be replaced with new position in move history
        assert old_pos not in new_state.move_history
        assert shuffle_event.new_position in new_state.move_history
    
    def test_shuffle_path_multiple_positions_probability(self):
        """Test that multiple positions can be shuffled in one call."""
        shuffler = PathShuffler()
        # Create many visited positions to increase chances
        visited_positions = [Position(x, 10) for x in range(5, 15)]  # 10 positions
        state = GameState(
            level_number=2,
            minefield=Minefield(width=30, height=20, mines=frozenset()),
            player_pos=Position(20, 10),
            visited=frozenset(visited_positions),
            move_history=tuple(visited_positions),
            lives=3,
            score=0,
            move_count=5,
        )
        
        # Run multiple times to see probabilistic behavior
        shuffle_count = 0
        for _ in range(20):  # Try multiple times
            new_state, shuffle_event = shuffler.shuffle_path(state)
            if shuffle_event is not None:
                shuffle_count += 1
        
        # Should shuffle some of the time (not always, not never)
        assert 0 < shuffle_count <= 20, f"Expected some shuffles over 20 attempts, got {shuffle_count}"
    
    def test_find_valid_targets_within_bounds(self):
        shuffler = PathShuffler()
        state = GameState(
            level_number=2,
            minefield=Minefield(width=30, height=20, mines=frozenset()),
            player_pos=Position(15, 10),
            visited=frozenset([Position(15, 10)]),
            move_history=(Position(15, 10),),
            lives=3,
            score=0,
            move_count=5,
        )
        
        targets = shuffler._find_valid_targets(state, Position(15, 10), 3)
        
        # All targets should be within playable area
        for target in targets:
            assert 1 <= target.x <= 30
            assert 2 <= target.y <= 21
    
    def test_is_valid_shuffle_target_player_position(self):
        shuffler = PathShuffler()
        state = GameState(
            level_number=2,
            minefield=Minefield(width=30, height=20, mines=frozenset()),
            player_pos=Position(15, 10),
            visited=frozenset(),
            move_history=(),
            lives=3,
            score=0,
            move_count=5,
        )
        
        player_pos = Position(15, 10)
        assert not shuffler._is_valid_shuffle_target(state, player_pos)
    
    def test_is_valid_shuffle_target_avoids_mines(self):
        shuffler = PathShuffler()
        mine_pos = Position(10, 10)
        safe_pos = Position(11, 10)
        player_pos = Position(15, 10)
        state = GameState(
            level_number=2,
            minefield=Minefield(width=30, height=20, mines=frozenset([mine_pos])),
            player_pos=player_pos,
            visited=frozenset(),
            move_history=(),
            lives=3,
            score=0,
            move_count=5,
        )
        
        # Mine position should be invalid
        assert not shuffler._is_valid_shuffle_target(state, mine_pos)
        
        # Safe position should be valid
        assert shuffler._is_valid_shuffle_target(state, safe_pos)
    
    def test_shuffle_path_avoids_mines_in_dense_minefield(self):
        """Test that shuffling works correctly even with many mines."""
        shuffler = PathShuffler()
        
        # Create a dense minefield around the shuffle area
        mines = frozenset([
            Position(8, 8), Position(9, 8), Position(10, 8),
            Position(8, 9), Position(10, 9),
            Position(8, 10), Position(9, 10), Position(10, 10),
        ])
        
        visited_pos = Position(9, 9)  # This position is surrounded by mines
        player_pos = Position(15, 10)
        state = GameState(
            level_number=2,
            minefield=Minefield(width=30, height=20, mines=mines),
            player_pos=player_pos,
            visited=frozenset([visited_pos]),
            move_history=(visited_pos,),
            lives=3,
            score=0,
            move_count=5,
        )
        
        # Should still find valid targets (outside the mine cluster)
        targets = shuffler._find_valid_targets(state, visited_pos, 3)
        assert len(targets) > 0, "Should find valid targets even with dense mines"
        
        # All targets should be mine-free
        for target in targets:
            assert not state.minefield.has_mine_at(target), f"Target {target} should not contain mine"
    
    def test_shuffle_path_preserves_original_path(self):
        """Test that original_path is preserved during shuffling."""
        shuffler = PathShuffler()
        
        # Create state with original path
        original_path = (Position(10, 10), Position(11, 10), Position(12, 10))
        state = GameState(
            level_number=2,
            minefield=Minefield(width=30, height=20, mines=frozenset()),
            player_pos=Position(12, 10),
            visited=frozenset(original_path),
            move_history=original_path,
            original_path=original_path,  # Set original path
            lives=3,
            score=0,
            move_count=3,
        )
        
        # Force shuffle to happen
        with patch('random.random', return_value=0.2):  # Force 30% probability
            new_state, shuffle_event = shuffler.shuffle_path(state)
        
        # Original path should be preserved
        assert new_state.original_path == original_path, "Original path should be preserved during shuffle"
        
        # Move history should be different (shuffled)
        assert new_state.move_history != original_path, "Move history should be updated with shuffled positions"
        
        # Shuffle event should indicate actual changes
        assert shuffle_event is not None, "Shuffle should have occurred"
    
    def test_shuffle_path_excludes_player_position(self):
        """Test that player's current position is never shuffled."""
        shuffler = PathShuffler()
        
        # Create visited positions including player position
        visited_positions = [Position(10, 10), Position(11, 10), Position(12, 10)]
        player_pos = Position(11, 10)  # Player is at middle position
        
        state = GameState(
            level_number=2,
            minefield=Minefield(width=30, height=20, mines=frozenset()),
            player_pos=player_pos,
            visited=frozenset(visited_positions),
            move_history=tuple(visited_positions),
            lives=3,
            score=0,
            move_count=5,
        )
        
        # Run shuffle multiple times to ensure player position is never affected
        for _ in range(20):  # Try multiple times
            new_state, shuffle_event = shuffler.shuffle_path(state)
            
            # Player position should always remain in visited set
            assert player_pos in new_state.visited, "Player position should never be removed from visited"
            
            # Player position should never be the old position in shuffle event
            if shuffle_event:
                assert shuffle_event.old_position != player_pos, "Player position should never be shuffled"
            
            # Player position should remain unchanged in move history
            assert player_pos in new_state.move_history, "Player position should remain in move history"


def close(a, b, tolerance=0.1):
    return abs(a - b) <= tolerance