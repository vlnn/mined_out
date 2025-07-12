from typing import List
import random

from mined_out.common import CellType, Position

def add_borders_to_grid(grid: List[List[CellType]], width: int, height: int) -> None:
    """Add borders to grid."""
    for y in range(height):
        for x in range(width):
            if (x == 0 or x == width - 1 or y == 0 or y == height - 1) and grid[y][x] != CellType.WALL:
                grid[y][x] = CellType.WALL

def add_walls_to_grid(grid: List[List[CellType]], level_num: int, width: int, height: int) -> None:
    """Add walls to the grid based on the level number."""
    wall_chance = 0.1 + 0.2 * (level_num // 5)   # Increase chance with each fifth level
    for y in range(height):
        for x in range(width):
            if random.random() < wall_chance and grid[y][x] == CellType.EMPTY:
                grid[y][x] = CellType.WALL
