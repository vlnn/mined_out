from enum import Enum
from mined_out.types import Position
from mined_out.config import PLAYAREA_START_ROW, PLAYAREA_END_ROW


class Direction(Enum):
    UP = Position(0, -1)
    DOWN = Position(0, 1)
    LEFT = Position(-1, 0)
    RIGHT = Position(1, 0)

    @property
    def offset(self) -> Position:
        return self.value


def get_next_position(current: Position, direction: Direction) -> Position:
    return current + direction.offset


def is_valid_position(position: Position) -> bool:
    return (
        1 <= position.x <= 30 and PLAYAREA_START_ROW <= position.y <= PLAYAREA_END_ROW
    )


def can_move_to(position: Position) -> bool:
    return is_valid_position(position)
