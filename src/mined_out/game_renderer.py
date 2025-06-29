import pyxel
from typing import List,Optional

from mined_out.common import CellType,Explosion
from mined_out.game_state import GameState

class GameRenderer:
    def __init__(self, width: int, height: int, cell_size: int):
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.grid_width = width // cell_size
        self.grid_height = height // cell_size

    def draw_game(self, state: GameState) -> None:
        pyxel.cls(4)
        self._draw_grid(state.grid)

        if not state.game_over:
            self._draw_mine_indicator(state)

        self._draw_explosion(state.explosion)

        if state.game_over:
            self._draw_game_over_screen(state.won)
        else:
            self._draw_ui(state)

    def _draw_grid(self, grid: List[List[CellType]]) -> None:
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                cell = grid[y][x]
                if cell != CellType.EMPTY:
                    self._draw_cell(x, y, cell)

    def _draw_cell(self, x: int, y: int, cell_type: CellType) -> None:
        sx, sy = x * self.cell_size, y * self.cell_size

        if cell_type == CellType.WALL:
            pyxel.rect(sx, sy, self.cell_size, self.cell_size, 6)
        elif cell_type == CellType.VISITED:
            pyxel.rect(sx, sy, self.cell_size, self.cell_size, pyxel.COLOR_CYAN)
        elif cell_type == CellType.REVEALED_MINE:
            pyxel.circb(sx + 3, sy + 3, 2, 8)
        elif cell_type == CellType.PLAYER:
            pyxel.rect(sx + 1, sy + 1, 6, 6, 11)
        elif cell_type == CellType.ITEM:
            pyxel.rect(sx + 2, sy + 2, 4, 4, 10)
        elif cell_type == CellType.EXIT:
            pyxel.rectb(sx, sy, self.cell_size, self.cell_size, pyxel.COLOR_GREEN)

    def _draw_mine_indicator(self, state: GameState) -> None:
        count = state.mine_count_nearby
        color = self._get_danger_color(count)

        px = state.player_pos.x * self.cell_size
        py = state.player_pos.y * self.cell_size

        tx = max(1, min(px - 6, self.width - 8))
        ty = max(1, min(py - 6, self.height - 8))

        pyxel.circb(tx + 2, ty + 2, 3, 7)
        pyxel.text(tx, ty, str(count), color)

    def _draw_explosion(self, explosion: Optional[Explosion]) -> None:
        if not explosion:
            return

        progress = explosion.frame / 30  # EXPLOSION_FRAMES
        radius = int(12 * progress)

        sx = explosion.pos.x * self.cell_size + 4
        sy = explosion.pos.y * self.cell_size + 4

        color = self._get_explosion_color(progress)

        if radius > 0:
            pyxel.circb(sx, sy, radius, color)
            if radius > 2:
                pyxel.circb(sx, sy, radius - 2, color)

        if progress < 0.8:
            self._draw_explosion_sparks(sx, sy, radius, color, explosion.frame)

    def _draw_explosion_sparks(self, sx: int, sy: int, radius: int, color: int, frame: int) -> None:
        for i in range(8):
            spark_x = sx + int(radius * 0.7 * pyxel.cos(i * 45))
            spark_y = sy + int(radius * 0.7 * pyxel.sin(i * 45))
            if frame % 3 == i % 3:
                pyxel.pset(spark_x, spark_y, color)

    def _draw_game_over_screen(self, won: bool) -> None:
        pyxel.rect(0, self.height // 2 - 15, self.width, 30, 0)
        message = "YOU WON!" if won else "GAME OVER"
        color = 11 if won else 8
        x = (self.width - len(message) * 4) // 2
        pyxel.text(x, self.height // 2 - 10, message, color)
        pyxel.text(x - 20, self.height // 2, "Press R to restart", 7)

    def _draw_ui(self, state: GameState) -> None:
        pyxel.text(2, 2, f"Level: {state.level}", 7)
        pyxel.text(2, 10, f"Items: {state.items_collected}/{state.total_items}", 7)
        pyxel.text(2, 18, f"Mines nearby: {state.mine_count_nearby}",
                  self._get_danger_color(state.mine_count_nearby))

        if state.items_collected >= state.total_items:
            pyxel.text(2, self.height - 16, "Find the exit!", 11)
        else:
            pyxel.text(2, self.height - 16, "Collect all items!", 7)
        pyxel.text(2, self.height - 8, "Mines are hidden!", 8)

    def _get_danger_color(self, count: int) -> int:
        if count == 0:
            return pyxel.COLOR_GREEN
        elif count <= 2:
            return pyxel.COLOR_YELLOW
        elif count <= 8:
            return pyxel.COLOR_RED
        else:
            return pyxel.COLOR_GRAY

    def _get_explosion_color(self, progress: float) -> int:
        if progress < 0.3:
            return 7  # White
        elif progress < 0.6:
            return 9  # Orange
        else:
            return 8  # Red
