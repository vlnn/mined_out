from enum import Enum
from dataclasses import dataclass

MAX_LEVEL = 5

class CellType(Enum):
    EMPTY = "empty"
    WALL = "wall"
    MINE = "mine"
    PLAYER = "player"
    ITEM = "item"
    EXIT = "exit"
    REVEALED_MINE = "revealed_mine"
    VISITED = "visited"

class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

@dataclass(frozen=True)
class Position:
    x: int
    y: int

@dataclass
class Explosion:
    pos: Position
    frame: int = 0

def move_position(pos: Position, direction: Direction) -> Position:
    """Move position in given direction."""
    dx, dy = direction.value
    return Position(pos.x + dx, pos.y + dy)
