import pyxel
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional
import random


class CellType(Enum):
    EMPTY = 0
    WALL = 1
    MINE = 2
    PLAYER = 3
    ITEM = 4
    EXIT = 5
    REVEALED_MINE = 6


class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)


@dataclass
class Position:
    x: int
    y: int

    def move(self, direction: Direction) -> 'Position':
        dx, dy = direction.value
        return Position(self.x + dx, self.y + dy)


@dataclass
class Explosion:
    pos: Position
    frame: int = 0


@dataclass
class GameState:
    player_pos: Position
    grid: List[List[CellType]]
    items_collected: int
    total_items: int
    level: int
    mine_count_nearby: int = 0
    game_over: bool = False
    won: bool = False
    explosion: Optional[Explosion] = None
    mine_reveal_timer: int = 0
    revealing_mine_pos: Optional[Position] = None


class MinedOutGame:
    GRID_WIDTH = 20
    GRID_HEIGHT = 15
    CELL_SIZE = 8
    MINE_REVEAL_FRAMES = 15
    EXPLOSION_FRAMES = 30

    def __init__(self):
        self.width = self.GRID_WIDTH * self.CELL_SIZE
        self.height = self.GRID_HEIGHT * self.CELL_SIZE

        pyxel.init(self.width, self.height, title="Mined-Out!")
        pyxel.sounds[0].set("c2e2g2c3", "p", "7", "f", 10)  # Explosion
        pyxel.sounds[1].set("g3c4e4g4", "p", "7", "f", 8)   # Item collect
        pyxel.mouse(False)

        self.state = self._create_level(1)
        self._update_mine_count()

        pyxel.run(self.update, self.draw)

    def _create_level(self, level_num: int) -> GameState:
        grid = self._generate_grid(level_num)
        player_pos = self._find_cell_position(grid, CellType.PLAYER)
        total_items = self._count_cells(grid, CellType.ITEM)

        return GameState(
            player_pos=player_pos,
            grid=grid,
            items_collected=0,
            total_items=total_items,
            level=level_num
        )

    def _generate_grid(self, level_num: int) -> List[List[CellType]]:
        grid = [[CellType.EMPTY for _ in range(self.GRID_WIDTH)]
                for _ in range(self.GRID_HEIGHT)]

        self._add_borders(grid)
        self._add_walls(grid, level_num)
        self._add_mines(grid, level_num)
        self._add_items(grid, level_num)
        self._add_player(grid)
        self._add_exit(grid)

        return grid

    def _add_borders(self, grid: List[List[CellType]]) -> None:
        for y in range(self.GRID_HEIGHT):
            for x in range(self.GRID_WIDTH):
                if x == 0 or x == self.GRID_WIDTH - 1 or y == 0 or y == self.GRID_HEIGHT - 1:
                    grid[y][x] = CellType.WALL

    def _add_walls(self, grid: List[List[CellType]], level_num: int) -> None:
        density = min(0.1 + level_num * 0.05, 0.3)
        for y in range(2, self.GRID_HEIGHT - 2, 2):
            for x in range(2, self.GRID_WIDTH - 2, 2):
                if random.random() < density:
                    grid[y][x] = CellType.WALL
                    if random.random() < 0.5:
                        grid[y][x + 1] = CellType.WALL
                    if random.random() < 0.5:
                        grid[y + 1][x] = CellType.WALL

    def _add_mines(self, grid: List[List[CellType]], level_num: int) -> None:
        count = min(5 + level_num * 3, 25)
        self._place_random_cells(grid, CellType.MINE, count)

    def _add_items(self, grid: List[List[CellType]], level_num: int) -> None:
        count = max(3, 8 - level_num)
        self._place_random_cells(grid, CellType.ITEM, count)

    def _add_player(self, grid: List[List[CellType]]) -> None:
        for y in range(1, self.GRID_HEIGHT - 1):
            for x in range(1, self.GRID_WIDTH - 1):
                if grid[y][x] == CellType.EMPTY and self._is_safe_position(grid, x, y):
                    grid[y][x] = CellType.PLAYER
                    return

    def _add_exit(self, grid: List[List[CellType]]) -> None:
        for y in range(self.GRID_HEIGHT - 3, 0, -1):
            for x in range(self.GRID_WIDTH - 3, 0, -1):
                if grid[y][x] == CellType.EMPTY:
                    grid[y][x] = CellType.EXIT
                    return

    def _place_random_cells(self, grid: List[List[CellType]], cell_type: CellType, count: int) -> None:
        placed = 0
        while placed < count:
            x = random.randint(1, self.GRID_WIDTH - 2)
            y = random.randint(1, self.GRID_HEIGHT - 2)
            if grid[y][x] == CellType.EMPTY:
                grid[y][x] = cell_type
                placed += 1

    def _is_safe_position(self, grid: List[List[CellType]], x: int, y: int) -> bool:
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                nx, ny = x + dx, y + dy
                if (0 <= nx < self.GRID_WIDTH and 0 <= ny < self.GRID_HEIGHT and
                    grid[ny][nx] == CellType.MINE):
                    return False
        return True

    def _find_cell_position(self, grid: List[List[CellType]], cell_type: CellType) -> Position:
        for y in range(self.GRID_HEIGHT):
            for x in range(self.GRID_WIDTH):
                if grid[y][x] == cell_type:
                    return Position(x, y)
        return Position(1, 1)

    def _count_cells(self, grid: List[List[CellType]], cell_type: CellType) -> int:
        return sum(row.count(cell_type) for row in grid)

    def _is_valid_move(self, pos: Position) -> bool:
        if not (0 <= pos.x < self.GRID_WIDTH and 0 <= pos.y < self.GRID_HEIGHT):
            return False
        cell = self.state.grid[pos.y][pos.x]
        return cell not in [CellType.WALL]

    def _count_adjacent_mines(self, pos: Position) -> int:
        count = 0
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                x, y = pos.x + dx, pos.y + dy
                if (0 <= x < self.GRID_WIDTH and 0 <= y < self.GRID_HEIGHT and
                    self.state.grid[y][x] == CellType.MINE):
                    count += 1
        return count

    def _update_mine_count(self) -> None:
        self.state.mine_count_nearby = self._count_adjacent_mines(self.state.player_pos)

    def _get_input_direction(self) -> Optional[Direction]:
        if pyxel.btnp(pyxel.KEY_UP) or pyxel.btnp(pyxel.KEY_W):
            return Direction.UP
        elif pyxel.btnp(pyxel.KEY_DOWN) or pyxel.btnp(pyxel.KEY_S):
            return Direction.DOWN
        elif pyxel.btnp(pyxel.KEY_LEFT) or pyxel.btnp(pyxel.KEY_A):
            return Direction.LEFT
        elif pyxel.btnp(pyxel.KEY_RIGHT) or pyxel.btnp(pyxel.KEY_D):
            return Direction.RIGHT
        return None

    def _try_move_player(self, direction: Direction) -> None:
        new_pos = self.state.player_pos.move(direction)

        if not self._is_valid_move(new_pos):
            return

        cell = self.state.grid[new_pos.y][new_pos.x]

        if cell == CellType.MINE:
            self._start_mine_reveal(new_pos)
        else:
            self._move_player_to(new_pos)
            if cell == CellType.ITEM:
                self._collect_item()
            elif cell == CellType.EXIT and self.state.items_collected >= self.state.total_items:
                self._advance_level()

    def _move_player_to(self, new_pos: Position) -> None:
        self.state.grid[self.state.player_pos.y][self.state.player_pos.x] = CellType.EMPTY
        self.state.player_pos = new_pos
        self.state.grid[new_pos.y][new_pos.x] = CellType.PLAYER
        self._update_mine_count()

    def _collect_item(self) -> None:
        self.state.items_collected += 1
        pyxel.play(0, 1)

    def _advance_level(self) -> None:
        if self.state.level >= 5:
            self.state.won = True
            self.state.game_over = True
        else:
            self.state = self._create_level(self.state.level + 1)
            self._update_mine_count()

    def _start_mine_reveal(self, mine_pos: Position) -> None:
        self.state.grid[mine_pos.y][mine_pos.x] = CellType.REVEALED_MINE
        self.state.revealing_mine_pos = mine_pos
        self.state.mine_reveal_timer = self.MINE_REVEAL_FRAMES

    def _explode_mine(self, mine_pos: Position) -> None:
        self.state.explosion = Explosion(mine_pos)
        self.state.game_over = True
        pyxel.play(0, 0)

    def _reset_game(self) -> None:
        self.state = self._create_level(1)
        self._update_mine_count()

    def update(self) -> None:
        if self.state.explosion:
            self.state.explosion.frame += 1
            if self.state.explosion.frame >= self.EXPLOSION_FRAMES:
                self.state.explosion = None

        if self.state.mine_reveal_timer > 0:
            self.state.mine_reveal_timer -= 1
            if self.state.mine_reveal_timer == 0 and self.state.revealing_mine_pos:
                self._explode_mine(self.state.revealing_mine_pos)
                self.state.revealing_mine_pos = None

        if self.state.game_over:
            if pyxel.btnp(pyxel.KEY_R):
                self._reset_game()
            return

        if self.state.mine_reveal_timer > 0:
            return

        direction = self._get_input_direction()
        if direction:
            self._try_move_player(direction)

    def _get_danger_color(self, count: int) -> int:
        if count == 0:
            return 11  # Yellow
        elif count <= 2:
            return 10  # Green
        elif count <= 4:
            return 9   # Orange
        else:
            return 8   # Red

    def _draw_cell(self, x: int, y: int, cell_type: CellType) -> None:
        sx, sy = x * self.CELL_SIZE, y * self.CELL_SIZE

        if cell_type == CellType.WALL:
            pyxel.rect(sx, sy, self.CELL_SIZE, self.CELL_SIZE, 6)
        elif cell_type == CellType.REVEALED_MINE:
            pyxel.circb(sx + 3, sy + 3, 2, 8)
        elif cell_type == CellType.PLAYER:
            pyxel.rect(sx + 1, sy + 1, 6, 6, 11)
        elif cell_type == CellType.ITEM:
            pyxel.rect(sx + 2, sy + 2, 4, 4, 10)
        elif cell_type == CellType.EXIT:
            pyxel.rectb(sx, sy, self.CELL_SIZE, self.CELL_SIZE, 12)

    def _draw_explosion(self) -> None:
        if not self.state.explosion:
            return

        exp = self.state.explosion
        progress = exp.frame / self.EXPLOSION_FRAMES
        radius = int(12 * progress)

        sx = exp.pos.x * self.CELL_SIZE + 4
        sy = exp.pos.y * self.CELL_SIZE + 4

        if progress < 0.3:
            color = 7  # White
        elif progress < 0.6:
            color = 9  # Orange
        else:
            color = 8  # Red

        if radius > 0:
            pyxel.circb(sx, sy, radius, color)
            if radius > 2:
                pyxel.circb(sx, sy, radius - 2, color)

        if progress < 0.8:
            for i in range(8):
                spark_x = sx + int(radius * 0.7 * pyxel.cos(i * 45))
                spark_y = sy + int(radius * 0.7 * pyxel.sin(i * 45))
                if exp.frame % 3 == i % 3:
                    pyxel.pset(spark_x, spark_y, color)

    def _draw_mine_indicator(self) -> None:
        count = self.state.mine_count_nearby
        color = self._get_danger_color(count)

        px = self.state.player_pos.x * self.CELL_SIZE
        py = self.state.player_pos.y * self.CELL_SIZE

        tx = max(1, min(px - 6, self.width - 8))
        ty = max(1, min(py - 6, self.height - 8))

        pyxel.circb(tx + 2, ty + 2, 3, 7)
        pyxel.text(tx, ty, str(count), color)

    def draw(self) -> None:
        pyxel.cls(0)

        # Draw grid
        for y in range(self.GRID_HEIGHT):
            for x in range(self.GRID_WIDTH):
                cell = self.state.grid[y][x]
                if cell not in [CellType.EMPTY, CellType.MINE]:
                    self._draw_cell(x, y, cell)

        if not self.state.game_over:
            self._draw_mine_indicator()

        self._draw_explosion()

        if self.state.game_over:
            # Draw game over overlay
            pyxel.rect(0, self.height // 2 - 15, self.width, 30, 0)
            message = "YOU WON!" if self.state.won else "GAME OVER"
            color = 11 if self.state.won else 8
            x = (self.width - len(message) * 4) // 2
            pyxel.text(x, self.height // 2 - 10, message, color)
            pyxel.text(x - 20, self.height // 2, "Press R to restart", 7)
        else:
            # Draw UI
            pyxel.text(2, 2, f"Level: {self.state.level}", 7)
            pyxel.text(2, 10, f"Items: {self.state.items_collected}/{self.state.total_items}", 7)
            pyxel.text(2, 18, f"Mines nearby: {self.state.mine_count_nearby}",
                      self._get_danger_color(self.state.mine_count_nearby))

            if self.state.items_collected >= self.state.total_items:
                pyxel.text(2, self.height - 16, "Find the exit!", 11)
            else:
                pyxel.text(2, self.height - 16, "Collect all items!", 7)
            pyxel.text(2, self.height - 8, "Mines are hidden!", 8)


if __name__ == "__main__":
    MinedOutGame()
