from dataclasses import dataclass
from typing import FrozenSet, Tuple, Optional, TYPE_CHECKING, Any


@dataclass(frozen=True)
class Position:
    x: int
    y: int

    def __add__(self, other: "Position") -> "Position":
        return Position(self.x + other.x, self.y + other.y)


@dataclass(frozen=True)
class LevelConfig:
    level_number: int
    width: int
    height: int
    mine_count: int
    unvisited_color: int
    visited_color: int
    entry_door_cols: Tuple[int, int, int]
    exit_door_cols: Tuple[int, int, int]
    start_position: Position


@dataclass(frozen=True)
class Minefield:
    width: int
    height: int
    mines: FrozenSet[Position]

    def has_mine_at(self, pos: Position) -> bool:
        return pos in self.mines


@dataclass(frozen=True)
class GameState:
    level_number: int
    minefield: Minefield
    player_pos: Position
    visited: FrozenSet[Position]
    move_history: Tuple[Position, ...]
    lives: int
    score: int
    move_count: int
    original_path: Optional[Tuple[Position, ...]] = None  # Original path before shuffling for replay
    is_replay: bool = False
    shuffle_count: int = 0
    last_shuffle_event: Optional[Any] = None
    
    def _replace(self, **kwargs):
        """Create a new GameState with replaced fields."""
        return GameState(
            level_number=kwargs.get('level_number', self.level_number),
            minefield=kwargs.get('minefield', self.minefield),
            player_pos=kwargs.get('player_pos', self.player_pos),
            visited=kwargs.get('visited', self.visited),
            move_history=kwargs.get('move_history', self.move_history),
            original_path=kwargs.get('original_path', self.original_path),
            lives=kwargs.get('lives', self.lives),
            score=kwargs.get('score', self.score),
            move_count=kwargs.get('move_count', self.move_count),
            is_replay=kwargs.get('is_replay', self.is_replay),
            shuffle_count=kwargs.get('shuffle_count', self.shuffle_count),
            last_shuffle_event=kwargs.get('last_shuffle_event', self.last_shuffle_event),
        )


@dataclass(frozen=True)
class ReplayState:
    current_frame: int
    total_frames: int
    speed_multiplier: float
