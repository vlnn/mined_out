from typing import List
import random

from mined_out.common import CellType, Position

def create_empty_grid(width: int, height: int) -> List[List[CellType]]:
    """Create empty grid filled with EMPTY cells."""
    return [[CellType.EMPTY for _ in range(width)] for _ in range(height)]

def is_valid_position(pos: Position, width: int, height: int) -> bool:
    """Check if position is within grid bounds."""
    return 0 <= pos.x < width and 0 <= pos.y < height

def is_border_position(x: int, y: int, width: int, height: int) -> bool:
    """Check if position is on grid border."""
    return x == 0 or x == width - 1 or y == 0 or y == height - 1

def find_cell_position(grid: List[List[CellType]], cell_type: CellType, width: int, height: int) -> Position:
    """Find first occurrence of cell type in grid."""
    for y in range(height):
        for x in range(width):
            if grid[y][x] == cell_type:
                return Position(x, y)
    return Position(1, 1)

def count_cells_of_type(grid: List[List[CellType]], cell_type: CellType) -> int:
    """Count total number of cells of given type."""
    return sum(row.count(cell_type) for row in grid)

def count_adjacent_mines(grid: List[List[CellType]], pos: Position, width: int, height: int) -> int:
    """Count mines adjacent to position (including diagonals)."""
    count = 0
    for dy in [-1, 0, 1]:
        for dx in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue
            adj_pos = Position(pos.x + dx, pos.y + dy)
            if is_valid_position(adj_pos, width, height) and grid[adj_pos.y][adj_pos.x] == CellType.MINE:
                count += 1
    return count

def has_adjacent_mines(grid: List[List[CellType]], pos: Position, width: int, height: int) -> bool:
    """Check if position has any adjacent mines."""
    return count_adjacent_mines(grid, pos, width, height) > 0

def is_safe_player_position(grid: List[List[CellType]], pos: Position, width: int, height: int) -> bool:
    """Check if position is safe for player placement."""
    if not is_valid_position(pos, width, height):
        return False
    if grid[pos.y][pos.x] != CellType.EMPTY:
        return False
    return not has_adjacent_mines(grid, pos, width, height)

def get_random_interior_position(width: int, height: int) -> Position:
    """Get random position inside grid borders."""
    x = random.randint(1, width - 2)
    y = random.randint(1, height - 2)
    return Position(x, y)

def can_move_to_cell(grid: List[List[CellType]], pos: Position, width: int, height: int) -> bool:
    """Check if player can move to given position."""
    if not is_valid_position(pos, width, height):
        return False
    cell = grid[pos.y][pos.x]
    return cell != CellType.WALL
