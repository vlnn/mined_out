from enum import Enum
from dataclasses import dataclass

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


@dataclass
class Position:
    x: int
    y: int

    def move(self, direction: Direction) -> 'Position':
        dx, dy = direction.value
        return Position(self.x + dx, self.y + dy)


@dataclass
class Explosion:
    pos: Position
    frame: int = 0
