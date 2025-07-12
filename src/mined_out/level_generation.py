from typing import List

from mined_out.common import CellType
from mined_out.grid_builder import place_random_cells
from mined_out.game_state import GameState
from mined_out.grid_operations import create_empty_grid, find_cell_position, count_cells_of_type
from mined_out.grid_builder import calculate_mine_count, calculate_item_count
from mined_out.grid_utils import add_borders_to_grid, add_walls_to_grid
from mined_out.grid_builder import place_player_safely, place_exit_in_grid

def generate_level_grid(level_num: int, width: int, height: int) -> List[List[CellType]]:
    """Generate complete grid for level."""
    grid = create_empty_grid(width, height)

    add_borders_to_grid(grid, width, height)
    add_walls_to_grid(grid, level_num, width, height)

    mine_count = calculate_mine_count(level_num)
    place_random_cells(grid, CellType.MINE, mine_count, width, height)

    item_count = calculate_item_count(level_num)
    place_random_cells(grid, CellType.ITEM, item_count, width, height)

    place_player_safely(grid, width, height)
    place_exit_in_grid(grid, width, height)

    return grid

from mined_out.common import Position
from mined_out.grid_operations import get_random_interior_position

def create_level_state(level_num: int, width: int, height: int) -> GameState:
    """Create complete game state for level."""
    grid = generate_level_grid(level_num, width, height)

    # Set player position to the center of the lowest row
    player_pos = Position(x=width // 2, y=height - 1)
    while grid[player_pos.y][player_pos.x] != CellType.EMPTY:
        player_pos = get_random_interior_position(width, height)

    # Place exit using place_exit_in_grid function without checking for emptiness
    exit_pos = place_exit_in_grid(grid, width, height)

    return GameState(
        player_pos=player_pos,
        grid=grid,
        items_collected=0,
        total_items=count_cells_of_type(grid, CellType.ITEM),
        level=level_num,
        exit_pos=exit_pos
    )
