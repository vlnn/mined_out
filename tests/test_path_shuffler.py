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
    
    def test_shuffle_path_with_visited_positions(self):
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
        
        new_state, shuffle_event = shuffler.shuffle_path(state)
        
        assert shuffle_event is not None
        assert shuffle_event.old_position == visited_pos
        assert shuffle_event.new_position != visited_pos
        assert shuffle_event.new_position not in state.visited
        assert visited_pos not in new_state.visited
        assert shuffle_event.new_position in new_state.visited
    
    def test_shuffle_path_avoids_player_position(self):
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
        
        new_state, shuffle_event = shuffler.shuffle_path(state)
        
        assert shuffle_event is not None
        assert shuffle_event.new_position != player_pos
    
    def test_shuffle_path_updates_move_history(self):
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


def close(a, b, tolerance=0.1):
    return abs(a - b) <= tolerance