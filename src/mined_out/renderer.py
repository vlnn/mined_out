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
    COLOR_LIGHT_GRAY,
    COLOR_GREEN,
    COLOR_RED,
    COLOR_YELLOW,
    ENTRY_DOOR_COLS,
    EXIT_DOOR_COLS,
    ENTRY_DOOR_ROW,
    EXIT_DOOR_ROW,
)
from mined_out.proximity import count_adjacent_mines
from mined_out.level import get_level_colors


def position_to_pixel(position: Position) -> Tuple[int, int]:
    return (position.x * TILE_SIZE, position.y * TILE_SIZE)


def draw_tile(position: Position, color: int, add_texture: bool = False) -> None:
    x, y = position_to_pixel(position)
    pyxel.rect(x, y, TILE_SIZE, TILE_SIZE, color)
    
    # Add subtle texture for better visual distinction
    if add_texture:
        # Add a small dot pattern for texture
        pyxel.rect(x + 3, y + 3, 2, 2, COLOR_DARK_GRAY)


def draw_wall() -> None:
    # Draw top wall with exit door gap and texture
    for x in range(SCREEN_WIDTH_TILES):
        if x not in EXIT_DOOR_COLS:
            draw_tile(Position(x, TOP_WALL_ROW), WALL_COLOR)
            # Add brick pattern texture
            if x % 2 == 0:
                pyxel.rect(x * TILE_SIZE + 2, TOP_WALL_ROW * TILE_SIZE + 2, 2, 2, COLOR_DARK_GRAY)
    
    # Draw bottom wall with entry door gap and texture
    for x in range(SCREEN_WIDTH_TILES):
        if x not in ENTRY_DOOR_COLS:
            draw_tile(Position(x, BOTTOM_WALL_ROW), WALL_COLOR)
            # Add brick pattern texture
            if x % 2 == 1:
                pyxel.rect(x * TILE_SIZE + 2, BOTTOM_WALL_ROW * TILE_SIZE + 2, 2, 2, COLOR_DARK_GRAY)


def draw_entry_door() -> None:
    # Draw entry door at bottom with green color
    for x in ENTRY_DOOR_COLS:
        draw_tile(Position(x, ENTRY_DOOR_ROW), COLOR_GREEN)
        # Add door frame effect
        if x == ENTRY_DOOR_COLS[0]:
            pyxel.rect(x * TILE_SIZE, ENTRY_DOOR_ROW * TILE_SIZE, 1, TILE_SIZE, WALL_COLOR)
        elif x == ENTRY_DOOR_COLS[-1]:  # Rightmost door
            pyxel.rect((x + 1) * TILE_SIZE - 1, ENTRY_DOOR_ROW * TILE_SIZE, 1, TILE_SIZE, WALL_COLOR)


def draw_exit_door() -> None:
    # Draw exit door at top with red color
    for x in EXIT_DOOR_COLS:
        draw_tile(Position(x, EXIT_DOOR_ROW), COLOR_RED)
        # Add door frame effect
        if x == EXIT_DOOR_COLS[0]:
            pyxel.rect(x * TILE_SIZE, EXIT_DOOR_ROW * TILE_SIZE, 1, TILE_SIZE, WALL_COLOR)
        elif x == EXIT_DOOR_COLS[-1]:  # Rightmost door
            pyxel.rect((x + 1) * TILE_SIZE - 1, EXIT_DOOR_ROW * TILE_SIZE, 1, TILE_SIZE, WALL_COLOR)


def draw_player(position: Position) -> None:
    x, y = position_to_pixel(position)
    # Draw a distinctive player character - a simple person sprite
    # Head
    pyxel.rect(x + 2, y + 1, 4, 2, PLAYER_COLOR)
    # Body
    pyxel.rect(x + 3, y + 3, 2, 3, PLAYER_COLOR)
    # Arms
    pyxel.rect(x + 1, y + 4, 1, 1, PLAYER_COLOR)
    pyxel.rect(x + 6, y + 4, 1, 1, PLAYER_COLOR)
    # Legs
    pyxel.rect(x + 2, y + 6, 1, 2, PLAYER_COLOR)
    pyxel.rect(x + 5, y + 6, 1, 2, PLAYER_COLOR)


def draw_mine(position: Position) -> None:
    x, y = position_to_pixel(position)
    center_x = x + TILE_SIZE // 2
    center_y = y + TILE_SIZE // 2
    
    # Draw a mine with spikes pattern like classic minesweeper
    # Center circle
    pyxel.circ(center_x, center_y, 2, MINE_COLOR)
    # Spikes pointing outwards (8 directions)
    for dx, dy in [(0, -3), (2, -2), (3, 0), (2, 2), (0, 3), (-2, 2), (-3, 0), (-2, -2)]:
        pyxel.rect(center_x + dx, center_y + dy, 1, 1, MINE_COLOR)


def draw_path_line(from_pos: Position, to_pos: Position) -> None:
    from_x, from_y = position_to_pixel(from_pos)
    to_x, to_y = position_to_pixel(to_pos)

    # Draw light path between tiles using empty rectangles
    # This creates a "trampled" look that's lighter than the field color
    from_center_x = from_x + TILE_SIZE // 2
    from_center_y = from_y + TILE_SIZE // 2
    to_center_x = to_x + TILE_SIZE // 2
    to_center_y = to_y + TILE_SIZE // 2
    
    # Draw a light gray line (lighter than field colors)
    pyxel.line(from_center_x, from_center_y, to_center_x, to_center_y, COLOR_LIGHT_GRAY)
    
    # Add stumpy feet sprites at path points for better visibility
    draw_path_marker(from_pos)
    draw_path_marker(to_pos)


def draw_path_marker(position: Position) -> None:
    """Draw a small stumpy feet marker at path position"""
    x, y = position_to_pixel(position)
    
    # Draw two small rectangles representing feet
    # Left foot
    pyxel.rect(x + 1, y + 5, 2, 1, COLOR_LIGHT_GRAY)
    # Right foot  
    pyxel.rect(x + 5, y + 5, 2, 1, COLOR_LIGHT_GRAY)


def draw_shuffle_feedback(shuffle_event) -> None:
    """Draw visual feedback for path shuffling."""
    if not shuffle_event:
        return
    
    # Calculate animation progress (0.5 second duration = 30 frames at 60 FPS)
    import pyxel
    frames_since_shuffle = pyxel.frame_count - shuffle_event.timestamp
    if frames_since_shuffle > 30:
        return
    
    # Draw yellow border around affected positions
    for pos in [shuffle_event.old_position, shuffle_event.new_position]:
        x, y = position_to_pixel(pos)
        # Draw border effect
        pyxel.rectb(x-1, y-1, TILE_SIZE+2, TILE_SIZE+2, COLOR_YELLOW)


def draw_status_bar(state: GameState, proximity: int) -> None:
    y = STATUS_BAR_ROW * TILE_SIZE + 1
    
    # Draw status bar background for better visibility
    pyxel.rect(0, 0, SCREEN_WIDTH_TILES * TILE_SIZE, TILE_SIZE, COLOR_DARK_GRAY)
    
    # Layout information more like the original Mined-Out
    pyxel.text(2, y, f"L{state.level_number:02d}", COLOR_WHITE)
    pyxel.text(40, y, f"M:{state.move_count:03d}", COLOR_WHITE)
    pyxel.text(80, y, f"S:{state.score:05d}", COLOR_WHITE)
    pyxel.text(140, y, f"LIVES:{state.lives}", COLOR_WHITE)
    pyxel.text(200, y, f"MINES:{proximity}", COLOR_WHITE)


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
                draw_tile(pos, visited_color, add_texture=True)
            else:
                draw_tile(pos, unvisited_color)

    draw_wall()
    draw_entry_door()
    draw_exit_door()

    if show_mines:
        for mine_pos in state.minefield.mines:
            draw_mine(mine_pos)

    draw_player(state.player_pos)
    
    # Draw proximity number on player position like original Mined-Out
    proximity = count_adjacent_mines(state.player_pos, state.minefield)
    if proximity > 0:
        x, y = position_to_pixel(state.player_pos)
        # Draw number in bottom-right corner of player tile
        pyxel.text(x + 1, y + 5, str(proximity), COLOR_BLACK)
    
    # Draw shuffle feedback if available
    if hasattr(state, 'last_shuffle_event') and state.last_shuffle_event:
        draw_shuffle_feedback(state.last_shuffle_event)
    
    draw_status_bar(state, proximity)
