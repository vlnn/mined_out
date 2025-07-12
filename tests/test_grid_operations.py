import unittest
from typing import List

from mined_out.common import CellType, Position
from src.mined_out.grid_operations import (
    create_empty_grid,
    is_valid_position,
    is_border_position,
    find_cell_position,
    count_cells_of_type,
    count_adjacent_mines,
    has_adjacent_mines,
    is_safe_player_position,
    get_random_interior_position,
    can_move_to_cell,
)

class TestGridOperations(unittest.TestCase):
    def test_create_empty_grid(self):
        width, height = 5, 5
        grid = create_empty_grid(width, height)
        self.assertEqual(len(grid), height)
        for row in grid:
            self.assertEqual(len(row), width)
            self.assertTrue(all(cell == CellType.EMPTY for cell in row))

    def test_is_valid_position(self):
        width, height = 5, 5
        pos = Position(2, 3)
        self.assertTrue(is_valid_position(pos, width, height))
        pos = Position(-1, 0)
        self.assertFalse(is_valid_position(pos, width, height))
        pos = Position(5, 0)
        self.assertFalse(is_valid_position(pos, width, height))
        pos = Position(2, -1)
        self.assertFalse(is_valid_position(pos, width, height))
        pos = Position(2, 5)
        self.assertFalse(is_valid_position(pos, width, height))

    def test_is_border_position(self):
        width, height = 5, 5
        self.assertTrue(is_border_position(0, 0, width, height))
        self.assertTrue(is_border_position(4, 0, width, height))
        self.assertTrue(is_border_position(0, 4, width, height))
        self.assertTrue(is_border_position(4, 4, width, height))
        self.assertFalse(is_border_position(1, 1, width, height))

    def test_find_cell_position(self):
        width, height = 5, 5
        grid = [
            [CellType.EMPTY, CellType.EMPTY, CellType.MINE, CellType.EMPTY, CellType.EMPTY],
            [CellType.EMPTY, CellType.WALL, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY],
            [CellType.EMPTY, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY],
        ]
        pos = find_cell_position(grid, CellType.MINE, width, height)
        self.assertEqual(pos, Position(2, 0))
        pos = find_cell_position(grid, CellType.WALL, width, height)
        self.assertEqual(pos, Position(1, 1))

    def test_count_cells_of_type(self):
        width, height = 5, 5
        grid = [
            [CellType.EMPTY, CellType.EMPTY, CellType.MINE, CellType.EMPTY, CellType.EMPTY],
            [CellType.EMPTY, CellType.WALL, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY],
            [CellType.EMPTY, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY],
        ]
        count = count_cells_of_type(grid, CellType.MINE)
        self.assertEqual(count, 1)
        count = count_cells_of_type(grid, CellType.WALL)
        self.assertEqual(count, 1)

    def test_count_adjacent_mines(self):
        width, height = 5, 5
        grid = [
            [CellType.EMPTY, CellType.EMPTY, CellType.MINE, CellType.EMPTY, CellType.EMPTY],
            [CellType.EMPTY, CellType.WALL, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY],
            [CellType.EMPTY, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY],
        ]
        pos = Position(2, 1)
        count = count_adjacent_mines(grid, pos, width, height)
        self.assertEqual(count, 0)

    def test_has_adjacent_mines(self):
        width, height = 5, 5
        grid = [
            [CellType.EMPTY, CellType.EMPTY, CellType.MINE, CellType.EMPTY, CellType.EMPTY],
            [CellType.EMPTY, CellType.WALL, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY],
            [CellType.EMPTY, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY],
        ]
        pos = Position(2, 1)
        self.assertFalse(has_adjacent_mines(grid, pos, width, height))

    def test_is_safe_player_position(self):
        width, height = 5, 5
        grid = [
            [CellType.EMPTY, CellType.EMPTY, CellType.MINE, CellType.EMPTY, CellType.EMPTY],
            [CellType.EMPTY, CellType.WALL, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY],
            [CellType.EMPTY, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY],
        ]
        pos = Position(2, 1)
        self.assertFalse(is_safe_player_position(grid, pos, width, height))
        pos = Position(0, 0)
        self.assertTrue(is_safe_player_position(grid, pos, width, height))

    def test_get_random_interior_position(self):
        width, height = 5, 5
        pos = get_random_interior_position(width, height)
        self.assertTrue(1 <= pos.x < width - 1)
        self.assertTrue(1 <= pos.y < height - 1)

    def test_can_move_to_cell(self):
        width, height = 5, 5
        grid = [
            [CellType.EMPTY, CellType.EMPTY, CellType.MINE, CellType.EMPTY, CellType.EMPTY],
            [CellType.EMPTY, CellType.WALL, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY],
            [CellType.EMPTY, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY, CellType.EMPTY],
        ]
        pos = Position(2, 1)
        self.assertFalse(can_move_to_cell(grid, pos, width, height))
        pos = Position(0, 0)
        self.assertTrue(can_move_to_cell(grid, pos, width, height))

if __name__ == '__main__':
    unittest.main()
