from typing import Tuple
from mined_out.types import Position, LevelConfig, Minefield
from mined_out.config import (
    PLAYABLE_WIDTH,
    PLAYABLE_HEIGHT,
    ENTRY_DOOR_COLS,
    EXIT_DOOR_COLS,
    START_POSITION_ROW,
    EXIT_DOOR_ROW,
    COLOR_YELLOW,
    COLOR_ORANGE,
    COLOR_GREEN,
    COLOR_CYAN,
    COLOR_PINK,
)
from mined_out.minefield import calculate_mine_count, create_minefield
from mined_out.pathfinding import has_path


LEVEL_COLORS = [
    COLOR_YELLOW,
    COLOR_ORANGE,
    COLOR_GREEN,
    COLOR_CYAN,
    COLOR_PINK,
]


def get_level_colors(level_number: int) -> Tuple[int, int]:
    color_index = (level_number - 1) % len(LEVEL_COLORS)
    color = LEVEL_COLORS[color_index]
    return (color, color)


def get_start_position() -> Position:
    return Position(ENTRY_DOOR_COLS[0], START_POSITION_ROW)


def get_exit_position() -> Position:
    return Position(EXIT_DOOR_COLS[0], EXIT_DOOR_ROW + 1)


def create_level_config(level_number: int) -> LevelConfig:
    unvisited_color, visited_color = get_level_colors(level_number)
    mine_count = calculate_mine_count(level_number)
    start_position = get_start_position()

    return LevelConfig(
        level_number=level_number,
        width=PLAYABLE_WIDTH,
        height=PLAYABLE_HEIGHT,
        mine_count=mine_count,
        unvisited_color=unvisited_color,
        visited_color=visited_color,
        entry_door_cols=ENTRY_DOOR_COLS,
        exit_door_cols=EXIT_DOOR_COLS,
        start_position=start_position,
    )


def generate_level(level_number: int, max_attempts: int = 100) -> Minefield:
    start = get_start_position()
    exit_pos = get_exit_position()

    for attempt in range(max_attempts):
        minefield = create_minefield(level_number)
        if has_path(start, exit_pos, minefield):
            return minefield

    raise Exception(f"Could not generate solvable level after {max_attempts} attempts")
