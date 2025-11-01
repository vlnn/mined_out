from dataclasses import dataclass
from typing import FrozenSet, Tuple


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
    entry_door_cols: Tuple[int, int]
    exit_door_cols: Tuple[int, int]
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
    is_replay: bool = False


@dataclass(frozen=True)
class ReplayState:
    current_frame: int
    total_frames: int
    speed_multiplier: float
