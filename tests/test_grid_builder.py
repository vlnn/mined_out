from typing import List

from mined_out.common import CellType, Position
from mined_out.grid_operations import is_valid_position, find_cell_position, count_cells_of_type, count_adjacent_mines, has_adjacent_mines, is_safe_player_position, get_random_interior_position, can_move_to_cell
from mined_out.grid_utils import add_borders_to_grid

class TestGridBuilder():
    def test_add_borders_to_grid(self):
        width, height = 5, 5
        grid = [[CellType.EMPTY for _ in range(width)] for _ in range(height)]
        add_borders_to_grid(grid, width, height)
        expected_border_cells = [
            (0, 0), (0, 1), (0, 2), (0, 3), (0, 4),
            (1, 0), (4, 0),
            (1, 4), (4, 4),
            (1, 1), (1, 2), (1, 3),
            (2, 1), (2, 2), (2, 3),
            (3, 1), (3, 2), (3, 3),
        ]
        for y in range(height):
            for x in range(width):
                if (x, y) in expected_border_cells:
                    assert grid[y][x] == CellType.WALL
                else:
                    assert grid[y][x] == CellType.EMPTY

    def test_place_wall_cluster(self):
        width, height = 5, 5
        grid = [[CellType.EMPTY for _ in range(width)] for _ in range(height)]
        x, y = 2, 2
        place_wall_cluster(grid, x, y)
        self.assertEqual(grid[y][x], CellType.WALL)
        self.assertIn((x + 1, y), [(x + 1, y) for y in range(height)])
        self.assertIn((x, y + 1), [(x, y + 1) for x in range(width)])

    def test_add_walls_to_grid(self):
        width, height = 5, 5
        grid = [[CellType.EMPTY for _ in range(width)] for _ in range(height)]
        level_num = 2
        add_walls_to_grid(grid, level_num, width, height)
        wall_cells = sum(row.count(CellType.WALL) for row in grid)
        self.assertGreater(wall_cells, 0)

    def test_calculate_mine_count(self):
        level_num = 3
        mine_count = calculate_mine_count(level_num)
        self.assertEqual(mine_count, min(5 + level_num * 3, 25))

    def test_calculate_item_count(self):
        level_num = 3
        item_count = calculate_item_count(level_num)
        self.assertEqual(item_count, max(3, 8 - level_num))
