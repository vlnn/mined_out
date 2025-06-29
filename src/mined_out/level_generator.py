from typing import List

from mined_out.common import CellType
from mined_out.grid_builder import GridBuilder
from mined_out.grid_analyzer import GridAnalyzer
from mined_out.game_state import GameState

class LevelGenerator:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.builder = GridBuilder(width, height)

    def create_level(self, level_num: int) -> GameState:
        grid = self._generate_grid(level_num)
        analyzer = GridAnalyzer(grid, self.width, self.height)

        player_pos = analyzer.find_cell_position(CellType.PLAYER)
        total_items = analyzer.count_cells(CellType.ITEM)

        return GameState(
            player_pos=player_pos,
            grid=grid,
            items_collected=0,
            total_items=total_items,
            level=level_num
        )

    def _generate_grid(self, level_num: int) -> List[List[CellType]]:
        grid = self.builder.create_empty_grid()

        self.builder.add_borders(grid)
        self.builder.add_walls(grid, level_num)
        self._add_mines(grid, level_num)
        self._add_items(grid, level_num)
        self.builder.place_player_safely(grid)
        self.builder.place_exit(grid)

        return grid

    def _add_mines(self, grid: List[List[CellType]], level_num: int) -> None:
        count = min(5 + level_num * 3, 25)
        self.builder.place_random_cells(grid, CellType.MINE, count)

    def _add_items(self, grid: List[List[CellType]], level_num: int) -> None:
        count = max(3, 8 - level_num)
        self.builder.place_random_cells(grid, CellType.ITEM, count)
