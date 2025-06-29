from typing import List

from mined_out.common import CellType,Position

class MovementHandler:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height

    def is_valid_move(self, pos: Position, grid: List[List[CellType]]) -> bool:
        if not self._is_within_bounds(pos):
            return False
        cell = grid[pos.y][pos.x]
        return cell != CellType.WALL

    def _is_within_bounds(self, pos: Position) -> bool:
        return 0 <= pos.x < self.width and 0 <= pos.y < self.height
