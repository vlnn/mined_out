from typing import List
import random

from mined_out.common import CellType
from mined_out.game_state import GameState


class GridBuilder:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height

    def create_empty_grid(self) -> List[List[CellType]]:
        return [[CellType.EMPTY for _ in range(self.width)]
                for _ in range(self.height)]

    def add_borders(self, grid: List[List[CellType]]) -> None:
        for y in range(self.height):
            for x in range(self.width):
                if self._is_border_position(x, y):
                    grid[y][x] = CellType.WALL

    def add_walls(self, grid: List[List[CellType]], level_num: int) -> None:
        density = min(0.1 + level_num * 0.05, 0.3)
        for y in range(2, self.height - 2, 2):
            for x in range(2, self.width - 2, 2):
                if random.random() < density:
                    self._place_wall_cluster(grid, x, y)

    def place_random_cells(self, grid: List[List[CellType]], cell_type: CellType, count: int) -> None:
        placed = 0
        while placed < count:
            x, y = self._random_interior_position()
            if grid[y][x] == CellType.EMPTY:
                grid[y][x] = cell_type
                placed += 1

    def place_player_safely(self, grid: List[List[CellType]]) -> None:
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                if self._is_safe_player_position(grid, x, y):
                    grid[y][x] = CellType.PLAYER
                    return

    def place_exit(self, grid: List[List[CellType]]) -> None:
        for y in range(self.height - 3, 0, -1):
            for x in range(self.width - 3, 0, -1):
                if grid[y][x] == CellType.EMPTY:
                    grid[y][x] = CellType.EXIT
                    return

    def _is_border_position(self, x: int, y: int) -> bool:
        return x == 0 or x == self.width - 1 or y == 0 or y == self.height - 1

    def _place_wall_cluster(self, grid: List[List[CellType]], x: int, y: int) -> None:
        grid[y][x] = CellType.WALL
        if random.random() < 0.5:
            grid[y][x + 1] = CellType.WALL
        if random.random() < 0.5:
            grid[y + 1][x] = CellType.WALL

    def _random_interior_position(self) -> tuple[int, int]:
        x = random.randint(1, self.width - 2)
        y = random.randint(1, self.height - 2)
        return x, y

    def _is_safe_player_position(self, grid: List[List[CellType]], x: int, y: int) -> bool:
        if grid[y][x] != CellType.EMPTY:
            return False
        return not self._has_adjacent_mines(grid, x, y)

    def _has_adjacent_mines(self, grid: List[List[CellType]], x: int, y: int) -> bool:
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                nx, ny = x + dx, y + dy
                if self._is_valid_position(nx, ny) and grid[ny][nx] == CellType.MINE:
                    return True
        return False

    def _is_valid_position(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height
