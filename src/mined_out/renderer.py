import pyxel
from typing import Tuple
from mined_out.types import Position, GameState
from mined_out.config import (
    TILE_SIZE,
    SCREEN_WIDTH_TILES,
    SCREEN_HEIGHT_TILES,
    STATUS_BAR_ROW,
    TOP_WALL_ROW,
    BOTTOM_WALL_ROW,
    TRANSIENT_INFO_ROW,
    PLAYAREA_START_ROW,
    PLAYAREA_END_ROW,
    WALL_COLOR,
    PLAYER_COLOR,
    MINE_COLOR,
    COLOR_BLACK,
    COLOR_WHITE,
    COLOR_DARK_GRAY,
)
from mined_out.proximity import count_adjacent_mines
from mined_out.level import get_level_colors


def position_to_pixel(position: Position) -> Tuple[int, int]:
    return (position.x * TILE_SIZE, position.y * TILE_SIZE)


def draw_tile(position: Position, color: int) -> None:
    x, y = position_to_pixel(position)
    pyxel.rect(x, y, TILE_SIZE, TILE_SIZE, color)


def draw_wall() -> None:
    screen_width = SCREEN_WIDTH_TILES * TILE_SIZE

    for x in range(SCREEN_WIDTH_TILES):
        draw_tile(Position(x, TOP_WALL_ROW), WALL_COLOR)
        draw_tile(Position(x, BOTTOM_WALL_ROW), WALL_COLOR)


def draw_player(position: Position) -> None:
    x, y = position_to_pixel(position)
    pyxel.rect(x, y, TILE_SIZE, TILE_SIZE, PLAYER_COLOR)


def draw_mine(position: Position) -> None:
    x, y = position_to_pixel(position)
    center_x = x + TILE_SIZE // 2
    center_y = y + TILE_SIZE // 2
    radius = TILE_SIZE // 3
    pyxel.circ(center_x, center_y, MINE_COLOR, radius)


def draw_path_line(from_pos: Position, to_pos: Position) -> None:
    from_x, from_y = position_to_pixel(from_pos)
    to_x, to_y = position_to_pixel(to_pos)

    from_center_x = from_x + TILE_SIZE // 2
    from_center_y = from_y + TILE_SIZE // 2
    to_center_x = to_x + TILE_SIZE // 2
    to_center_y = to_y + TILE_SIZE // 2

    pyxel.line(from_center_x, from_center_y, to_center_x, to_center_y, COLOR_DARK_GRAY)


def draw_status_bar(state: GameState, proximity: int) -> None:
    y = STATUS_BAR_ROW * TILE_SIZE + 1

    pyxel.text(2, y, f"LEVEL:{state.level_number}", COLOR_WHITE)
    pyxel.text(50, y, f"MOVES:{state.move_count}", COLOR_WHITE)
    pyxel.text(110, y, f"SCORE:{state.score}", COLOR_WHITE)
    pyxel.text(180, y, f"LIVES:{state.lives}", COLOR_WHITE)
    pyxel.text(220, y, f"MINES:{proximity}", COLOR_WHITE)


def draw_transient_info(message: str) -> None:
    y = TRANSIENT_INFO_ROW * TILE_SIZE + 1
    x = (SCREEN_WIDTH_TILES * TILE_SIZE - len(message) * 4) // 2
    pyxel.text(x, y, message, COLOR_WHITE)


def draw_game_state(state: GameState, show_mines: bool = False) -> None:
    pyxel.cls(COLOR_BLACK)

    unvisited_color, visited_color = get_level_colors(state.level_number)

    for x in range(1, 31):
        for y in range(PLAYAREA_START_ROW, PLAYAREA_END_ROW + 1):
            pos = Position(x, y)
            if pos in state.visited:
                draw_tile(pos, visited_color)
            else:
                draw_tile(pos, unvisited_color)

    draw_wall()

    if show_mines:
        for mine_pos in state.minefield.mines:
            draw_mine(mine_pos)

    for i in range(len(state.move_history) - 1):
        current_pos = state.move_history[i]
        next_pos = state.move_history[i + 1]
        draw_path_line(current_pos, next_pos)

    draw_player(state.player_pos)

    proximity = count_adjacent_mines(state.player_pos, state.minefield)
    draw_status_bar(state, proximity)
