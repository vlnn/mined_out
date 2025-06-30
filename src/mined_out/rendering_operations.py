import pyxel
from typing import List

from mined_out.common import CellType, Position, Explosion

def get_danger_color(mine_count: int) -> int:
    """Get color based on mine danger level."""
    if mine_count == 0:
        return pyxel.COLOR_GREEN
    elif mine_count <= 2:
        return pyxel.COLOR_YELLOW
    elif mine_count <= 8:
        return pyxel.COLOR_RED
    else:
        return pyxel.COLOR_GRAY

def get_explosion_color(progress: float) -> int:
    """Get explosion color based on animation progress."""
    if progress < 0.3:
        return 7  # White
    elif progress < 0.6:
        return 9  # Orange
    else:
        return 8  # Red

def draw_cell(x: int, y: int, cell_type: CellType, cell_size: int) -> None:
    """Draw single cell at grid position."""
    sx, sy = x * cell_size, y * cell_size

    if cell_type == CellType.WALL:
        pyxel.rect(sx, sy, cell_size, cell_size, 6)
    elif cell_type == CellType.VISITED:
        pyxel.rect(sx, sy, cell_size, cell_size, pyxel.COLOR_CYAN)
    elif cell_type == CellType.REVEALED_MINE:
        pyxel.circb(sx + 3, sy + 3, 2, 8)
    elif cell_type == CellType.PLAYER:
        pyxel.rect(sx + 1, sy + 1, 6, 6, 11)
    elif cell_type == CellType.ITEM:
        pyxel.rect(sx + 2, sy + 2, 4, 4, 10)
    elif cell_type == CellType.EXIT:
        pyxel.rectb(sx, sy, cell_size, cell_size, pyxel.COLOR_GREEN)

def draw_grid(grid: List[List[CellType]], grid_width: int, grid_height: int, cell_size: int) -> None:
    """Draw entire grid."""
    for y in range(grid_height):
        for x in range(grid_width):
            cell = grid[y][x]
            if cell != CellType.EMPTY:
                draw_cell(x, y, cell, cell_size)

def draw_mine_indicator(player_pos: Position, mine_count: int, cell_size: int, screen_width: int, screen_height: int) -> None:
    """Draw mine count indicator near player."""
    color = get_danger_color(mine_count)
    px = player_pos.x * cell_size
    py = player_pos.y * cell_size

    tx = max(1, min(px - 6, screen_width - 8))
    ty = max(1, min(py - 6, screen_height - 8))

    pyxel.circb(tx + 2, ty + 2, 3, 7)
    pyxel.text(tx, ty, str(mine_count), color)

def draw_explosion_sparks(sx: int, sy: int, radius: int, color: int, frame: int) -> None:
    """Draw explosion sparks around center point."""
    for i in range(8):
        spark_x = sx + int(radius * 0.7 * pyxel.cos(i * 45))
        spark_y = sy + int(radius * 0.7 * pyxel.sin(i * 45))
        if frame % 3 == i % 3:
            pyxel.pset(spark_x, spark_y, color)

def draw_explosion(explosion: Explosion, cell_size: int) -> None:
    """Draw explosion animation."""
    progress = explosion.frame / 30
    radius = int(12 * progress)

    sx = explosion.pos.x * cell_size + 4
    sy = explosion.pos.y * cell_size + 4

    color = get_explosion_color(progress)

    if radius > 0:
        pyxel.circb(sx, sy, radius, color)
        if radius > 2:
            pyxel.circb(sx, sy, radius - 2, color)

    if progress < 0.8:
        draw_explosion_sparks(sx, sy, radius, color, explosion.frame)

def draw_game_over_screen(won: bool, screen_width: int, screen_height: int) -> None:
    """Draw game over overlay."""
    pyxel.rect(0, screen_height // 2 - 15, screen_width, 30, 0)
    message = "YOU WON!" if won else "GAME OVER"
    color = 11 if won else 8
    x = (screen_width - len(message) * 4) // 2
    pyxel.text(x, screen_height // 2 - 10, message, color)
    pyxel.text(x - 20, screen_height // 2, "Press R to restart", 7)

def draw_ui(level: int, items_collected: int, total_items: int, mine_count: int, screen_height: int) -> None:
    """Draw game UI elements."""
    pyxel.text(2, 2, f"Level: {level}", 7)
    pyxel.text(2, 10, f"Items: {items_collected}/{total_items}", 7)
    pyxel.text(2, 18, f"Mines nearby: {mine_count}", get_danger_color(mine_count))

    if items_collected >= total_items:
        pyxel.text(2, screen_height - 16, "Find the exit!", 11)
    else:
        pyxel.text(2, screen_height - 16, "Collect all items!", 7)
    pyxel.text(2, screen_height - 8, "Mines are hidden!", 8)
