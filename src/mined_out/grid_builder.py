from typing import List
import random

from mined_out.common import CellType, Position
from mined_out.grid_operations import get_random_interior_position

def calculate_mine_count(level_num: int) -> int:
    """Calculate the number of mines based on level progression."""
    base_mines = 5  # minimum number of mines per level
    mine_increase = (level_num * 3)  # increase in mines for each subsequent level
    total_mines = min(base_mines + mine_increase, 25)  # cap at 25 mines
    return total_mines

def calculate_item_count(level_num: int) -> int:
    """Calculate the number of items based on level progression."""
    base_items = 3   # minimum number of items per level
    item_increase = max((8 - level_num), 0)   # decrease in items for each subsequent level
    total_items = min(base_items + item_increase, 25)   # cap at 25 items
    return total_items

def place_random_cells(grid: List[List[CellType]], cell_type: CellType, count: int, width: int, height: int) -> int:
    """Place random cells of the given type in the grid."""
    placed = 0
    while placed < count:
        x = random.randint(1, width - 2)
        y = random.randint(1, height - 2)
        if grid[y][x] == CellType.EMPTY:
            grid[y][x] = cell_type
            placed += 1
    return placed

def place_exit_in_grid(grid: List[List[CellType]], width: int, height: int) -> Position:
    """Place exit in a random interior position without checking for emptiness."""
    pos = get_random_interior_position(width, height)
    grid[pos.y][pos.x] = CellType.EXIT
    return pos


def place_player_safely(grid: List[List[CellType]], width: int, height: int) -> Position:
    """Place the player safely at an empty cell in the grid."""
    while True:  # Keep trying until we find a safe position
        x = random.randint(1, width-2)
        y = random.randint(1, height-2)
        if grid[y][x] == CellType.EMPTY:
            grid[y][x] = CellType.PLAYER  # Assuming you have a PLAYER cell type
            return Position(x, y)   # Return the position of the player
