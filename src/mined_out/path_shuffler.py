import random
from typing import Tuple, Optional, List, Set
from dataclasses import dataclass

from mined_out.types import Position, GameState, Minefield
from mined_out.config import (
    TILE_SIZE,
    PLAYABLE_WIDTH,
    PLAYABLE_HEIGHT,
    PLAYAREA_START_ROW,
    PLAYAREA_END_ROW,
    TOP_WALL_ROW,
    BOTTOM_WALL_ROW,
)
from mined_out.movement import is_valid_position


@dataclass(frozen=True)
class ShuffleEvent:
    """Represents a single path shuffling event."""
    old_position: Position
    new_position: Position
    timestamp: int
    
    def _replace(self, **kwargs):
        """Create a new ShuffleEvent with replaced fields."""
        return ShuffleEvent(
            old_position=kwargs.get('old_position', self.old_position),
            new_position=kwargs.get('new_position', self.new_position),
            timestamp=kwargs.get('timestamp', self.timestamp),
        )


class PathShuffler:
    """Handles path shuffling mechanics for Level 2+."""
    
    def __init__(self, shuffle_frequency: int = 5):
        self.shuffle_frequency = shuffle_frequency
    
    def should_shuffle(self, state: GameState) -> bool:
        """Check if shuffling should occur based on game state."""
        return (
            state.level_number >= 2 and 
            state.move_count % self.shuffle_frequency == 0 and
            state.move_count > 0
        )
    
    def get_shuffle_distance(self) -> int:
        """Get shuffle distance with weighted distribution."""
        rand = random.random()
        if rand < 0.7:      # 70% chance: 1-3 tiles
            return random.randint(1, 3)
        elif rand < 0.9:    # 20% chance: 4-6 tiles
            return random.randint(4, 6)
        else:                 # 10% chance: 7-10 tiles
            return random.randint(7, 10)
    
    def _find_valid_targets(self, state: GameState, from_pos: Position, max_distance: int) -> List[Position]:
        """Find valid target positions within distance range."""
        valid_targets = []
        
        for dx in range(-max_distance, max_distance + 1):
            for dy in range(-max_distance, max_distance + 1):
                # Skip the origin position
                if dx == 0 and dy == 0:
                    continue
                
                # Calculate actual distance
                actual_distance = max(abs(dx), abs(dy))
                if actual_distance > max_distance:
                    continue
                
                target_pos = Position(from_pos.x + dx, from_pos.y + dy)
                
                # Safety checks
                if not self._is_valid_shuffle_target(state, target_pos):
                    continue
                
                valid_targets.append(target_pos)
        
        return valid_targets
    
    def _is_valid_shuffle_target(self, state: GameState, pos: Position) -> bool:
        """Check if position is valid for shuffling."""
        # Must be within playable area
        if not (1 <= pos.x <= 30 and PLAYAREA_START_ROW <= pos.y <= PLAYAREA_END_ROW):
            return False
        
        # Must be valid position (not walls)
        if not is_valid_position(pos):
            return False
        
        # Cannot shuffle into player position
        if pos == state.player_pos:
            return False
        
        return True
    
    def shuffle_path(self, state: GameState) -> Tuple[GameState, Optional[ShuffleEvent]]:
        """Perform path shuffling and return new state with shuffle event."""
        visited_positions = list(state.visited)
        if not visited_positions:
            return state, None
        
        # Select random visited position to shuffle
        old_pos = random.choice(visited_positions)
        distance = self.get_shuffle_distance()
        
        # Find valid target positions within distance
        valid_targets = self._find_valid_targets(state, old_pos, distance)
        
        if not valid_targets:
            return state, None
        
        new_pos = random.choice(valid_targets)
        
        # Create new visited set with swapped positions
        new_visited = set(state.visited)
        new_visited.remove(old_pos)
        new_visited.add(new_pos)
        
        # Update move history to reflect the shuffle
        new_move_history = tuple(
            new_pos if pos == old_pos else pos 
            for pos in state.move_history
        )
        
        # Create new game state
        new_state = GameState(
            level_number=state.level_number,
            minefield=state.minefield,
            player_pos=state.player_pos,
            visited=frozenset(new_visited),
            move_history=new_move_history,
            lives=state.lives,
            score=state.score,
            move_count=state.move_count,
            is_replay=state.is_replay
        )
        
        # Create shuffle event for visual feedback
        shuffle_event = ShuffleEvent(
            old_position=old_pos,
            new_position=new_pos,
            timestamp=0  # Will be set by caller
        )
        
        return new_state, shuffle_event