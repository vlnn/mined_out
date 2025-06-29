from typing import List

from mined_out.common import Position,CellType


class GridAnalyzer:
    def __init__(self, grid: List[List[CellType]], width: int, height: int):
        self.grid = grid
        self.width = width
        self.height = height

    def find_cell_position(self, cell_type: CellType) -> Position:
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == cell_type:
                    return Position(x, y)
        return Position(1, 1)

    def count_cells(self, cell_type: CellType) -> int:
        return sum(row.count(cell_type) for row in self.grid)

    def count_adjacent_mines(self, pos: Position) -> int:
        count = 0
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                x, y = pos.x + dx, pos.y + dy
                if self._is_valid_position(x, y) and self.grid[y][x] == CellType.MINE:
                    count += 1
        return count

    def _is_valid_position(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height
