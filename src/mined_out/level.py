from typing import Tuple
from mined_out.types import Position, LevelConfig, Minefield
from mined_out.config import (
    PLAYABLE_WIDTH,
    PLAYABLE_HEIGHT,
    ENTRY_DOOR_COLS,
    EXIT_DOOR_COLS,
    START_POSITION_ROW,
    EXIT_DOOR_ROW,
    COLOR_DARK_BLUE,
    COLOR_DARK_GREEN,
    COLOR_DARK_PURPLE,
    COLOR_BROWN,
    COLOR_DARK_GRAY,
    COLOR_LIGHT_GRAY,
    COLOR_WHITE,
    COLOR_RED,
    COLOR_ORANGE,
    COLOR_YELLOW,
    COLOR_GREEN,
    COLOR_CYAN,
    COLOR_LIGHT_BLUE,
    COLOR_LAVENDER,
    COLOR_PINK,
)
from mined_out.minefield import calculate_mine_count, create_minefield
from mined_out.pathfinding import has_path


# Base colors for levels (darker versions)
LEVEL_COLORS = [
    COLOR_DARK_BLUE,      # Level 1
    COLOR_DARK_GREEN,      # Level 2
    COLOR_DARK_PURPLE,      # Level 3
    COLOR_BROWN,           # Level 4
    COLOR_DARK_GRAY,        # Level 5
    COLOR_RED,             # Level 6
    COLOR_ORANGE,          # Level 7
    COLOR_YELLOW,          # Level 8
    COLOR_GREEN,           # Level 9
    COLOR_CYAN,            # Level 10+
]


def get_level_colors(level_number: int) -> Tuple[int, int]:
    """Return (unvisited_color, visited_color) for the given level."""
    color_index = (level_number - 1) % len(LEVEL_COLORS)
    base_color = LEVEL_COLORS[color_index]
    lighter_color = get_lighter_color(base_color)
    return (base_color, lighter_color)


def get_lighter_color(base_color: int) -> int:
    """Return a lighter version of the given color for visited tiles."""
    # Map each base color to its lighter counterpart
    lighter_map = {
        COLOR_DARK_BLUE: COLOR_LIGHT_BLUE,
        COLOR_DARK_GREEN: COLOR_GREEN,
        COLOR_DARK_PURPLE: COLOR_LAVENDER,
        COLOR_BROWN: COLOR_ORANGE,
        COLOR_DARK_GRAY: COLOR_WHITE,
        COLOR_RED: COLOR_PINK,
        COLOR_ORANGE: COLOR_YELLOW,
        COLOR_YELLOW: COLOR_CYAN,
        COLOR_GREEN: COLOR_LIGHT_BLUE,
        COLOR_CYAN: COLOR_LAVENDER,
    }
    return lighter_map.get(base_color, base_color)


def get_start_position() -> Position:
    return Position(ENTRY_DOOR_COLS[1], START_POSITION_ROW)


def get_exit_position() -> Position:
    return Position(EXIT_DOOR_COLS[1], EXIT_DOOR_ROW)


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
