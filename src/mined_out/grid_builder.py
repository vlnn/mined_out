from typing import List
import random

from mined_out.common import CellType, Position
from mined_out.grid_operations import is_border_position, get_random_interior_position, is_safe_player_position


def add_borders_to_grid(grid: List[List[CellType]], width: int, height: int) -> None:
    """Add walls around grid perimeter."""
    for y in range(height):
        for x in range(width):
            if is_border_position(x, y, width, height):
                grid[y][x] = CellType.WALL

def place_wall_cluster(grid: List[List[CellType]], x: int, y: int) -> None:
    """Place a small cluster of walls at position."""
    grid[y][x] = CellType.WALL
    if random.random() < 0.5:
        grid[y][x + 1] = CellType.WALL
    if random.random() < 0.5:
        grid[y + 1][x] = CellType.WALL

def add_walls_to_grid(grid: List[List[CellType]], level_num: int, width: int, height: int) -> None:
    """Add walls to grid based on level difficulty."""
    density = min(0.1 + level_num * 0.05, 0.3)
    for y in range(2, height - 2, 2):
        for x in range(2, width - 2, 2):
            if random.random() < density:
                place_wall_cluster(grid, x, y)

def place_random_cells(grid: List[List[CellType]], cell_type: CellType, count: int, width: int, height: int) -> int:
    """Place random cells of given type, return number actually placed."""
    placed = 0
    attempts = 0
    max_attempts = count * 10

    while placed < count and attempts < max_attempts:
        pos = get_random_interior_position(width, height)
        if grid[pos.y][pos.x] == CellType.EMPTY:
            grid[pos.y][pos.x] = cell_type
            placed += 1
        attempts += 1

    return placed

def place_player_safely(grid: List[List[CellType]], width: int, height: int) -> bool:
    """Place player in safe position, return True if successful."""
    for y in range(1, height - 1):
        for x in range(1, width - 1):
            pos = Position(x, y)
            if is_safe_player_position(grid, pos, width, height):
                grid[y][x] = CellType.PLAYER
                return True
    return False

def place_exit_in_grid(grid: List[List[CellType]], width: int, height: int) -> bool:
    """Place exit in grid, return True if successful."""
    for y in range(height - 3, 0, -1):
        for x in range(width - 3, 0, -1):
            if grid[y][x] == CellType.EMPTY:
                grid[y][x] = CellType.EXIT
                return True
    return False

def calculate_mine_count(level_num: int) -> int:
    """Calculate number of mines for level."""
    return min(5 + level_num * 3, 25)

def calculate_item_count(level_num: int) -> int:
    """Calculate number of items for level."""
    return max(3, 8 - level_num)
