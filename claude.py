import pyxel
from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple, Optional, Set
import random


class CellType(Enum):
    EMPTY = 0
    WALL = 1
    MINE = 2
    PLAYER = 3
    ITEM = 4
    EXIT = 5


class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)


@dataclass
class Position:
    x: int
    y: int
    
    def __add__(self, direction: Direction) -> 'Position':
        dx, dy = direction.value
        return Position(self.x + dx, self.y + dy)
    
    def __eq__(self, other) -> bool:
        return self.x == other.x and self.y == other.y


@dataclass
class GameState:
    player_pos: Position
    level_grid: List[List[CellType]]
    items_collected: int
    total_items: int
    level_number: int
    game_over: bool = False
    won: bool = False


class MinedOutGame:
    def __init__(self):
        self.width = 160
        self.height = 120
        self.grid_width = 20
        self.grid_height = 15
        self.cell_size = 8
        
        pyxel.init(self.width, self.height, title="Mined-Out!")
        pyxel.mouse(True)
        
        self.game_state = self._create_initial_game_state()
        
        pyxel.run(self.update, self.draw)
    
    def _create_initial_game_state(self) -> GameState:
        """Initialize the first level of the game."""
        level_grid = self._generate_level(1)
        player_pos = self._find_player_start_position(level_grid)
        total_items = self._count_items_in_level(level_grid)
        
        return GameState(
            player_pos=player_pos,
            level_grid=level_grid,
            items_collected=0,
            total_items=total_items,
            level_number=1
        )
    
    def _generate_level(self, level_num: int) -> List[List[CellType]]:
        """Generate a level layout based on level number."""
        grid = [[CellType.EMPTY for _ in range(self.grid_width)] 
                for _ in range(self.grid_height)]
        
        # Create walls around the border
        self._add_border_walls(grid)
        
        # Add internal walls and obstacles
        self._add_internal_walls(grid, level_num)
        
        # Place mines strategically
        self._place_mines(grid, level_num)
        
        # Place collectible items
        self._place_items(grid, level_num)
        
        # Place player start position
        self._place_player_start(grid)
        
        # Place exit
        self._place_exit(grid)
        
        return grid
    
    def _add_border_walls(self, grid: List[List[CellType]]) -> None:
        """Add walls around the level border."""
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                if (x == 0 or x == self.grid_width - 1 or 
                    y == 0 or y == self.grid_height - 1):
                    grid[y][x] = CellType.WALL
    
    def _add_internal_walls(self, grid: List[List[CellType]], level_num: int) -> None:
        """Add internal walls to create maze-like structure."""
        wall_density = min(0.1 + (level_num * 0.05), 0.3)
        
        for y in range(2, self.grid_height - 2, 2):
            for x in range(2, self.grid_width - 2, 2):
                if random.random() < wall_density:
                    grid[y][x] = CellType.WALL
                    # Add connecting walls
                    if random.random() < 0.5:
                        grid[y][x + 1] = CellType.WALL
                    if random.random() < 0.5:
                        grid[y + 1][x] = CellType.WALL
    
    def _place_mines(self, grid: List[List[CellType]], level_num: int) -> None:
        """Place mines throughout the level."""
        mine_count = min(5 + level_num * 3, 25)
        placed = 0
        
        while placed < mine_count:
            x = random.randint(1, self.grid_width - 2)
            y = random.randint(1, self.grid_height - 2)
            
            if grid[y][x] == CellType.EMPTY:
                grid[y][x] = CellType.MINE
                placed += 1
    
    def _place_items(self, grid: List[List[CellType]], level_num: int) -> None:
        """Place collectible items in the level."""
        item_count = max(3, 8 - level_num)
        placed = 0
        
        while placed < item_count:
            x = random.randint(1, self.grid_width - 2)
            y = random.randint(1, self.grid_height - 2)
            
            if grid[y][x] == CellType.EMPTY:
                grid[y][x] = CellType.ITEM
                placed += 1
    
    def _place_player_start(self, grid: List[List[CellType]]) -> None:
        """Place player starting position."""
        # Find a safe starting position
        for y in range(1, self.grid_height - 1):
            for x in range(1, self.grid_width - 1):
                if (grid[y][x] == CellType.EMPTY and 
                    self._is_safe_starting_position(grid, x, y)):
                    grid[y][x] = CellType.PLAYER
                    return
    
    def _place_exit(self, grid: List[List[CellType]]) -> None:
        """Place the level exit."""
        # Place exit in bottom-right area
        for y in range(self.grid_height - 3, 0, -1):
            for x in range(self.grid_width - 3, 0, -1):
                if grid[y][x] == CellType.EMPTY:
                    grid[y][x] = CellType.EXIT
                    return
    
    def _is_safe_starting_position(self, grid: List[List[CellType]], x: int, y: int) -> bool:
        """Check if position is safe for player start (no adjacent mines)."""
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                nx, ny = x + dx, y + dy
                if (0 <= nx < self.grid_width and 0 <= ny < self.grid_height and
                    grid[ny][nx] == CellType.MINE):
                    return False
        return True
    
    def _find_player_start_position(self, grid: List[List[CellType]]) -> Position:
        """Find the player's starting position in the grid."""
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                if grid[y][x] == CellType.PLAYER:
                    return Position(x, y)
        return Position(1, 1)  # Fallback
    
    def _count_items_in_level(self, grid: List[List[CellType]]) -> int:
        """Count total collectible items in the level."""
        return sum(row.count(CellType.ITEM) for row in grid)
    
    def _get_movement_direction(self) -> Optional[Direction]:
        """Get movement direction from player input."""
        if pyxel.btnp(pyxel.KEY_UP) or pyxel.btnp(pyxel.KEY_W):
            return Direction.UP
        elif pyxel.btnp(pyxel.KEY_DOWN) or pyxel.btnp(pyxel.KEY_S):
            return Direction.DOWN
        elif pyxel.btnp(pyxel.KEY_LEFT) or pyxel.btnp(pyxel.KEY_A):
            return Direction.LEFT
        elif pyxel.btnp(pyxel.KEY_RIGHT) or pyxel.btnp(pyxel.KEY_D):
            return Direction.RIGHT
        return None
    
    def _is_valid_position(self, pos: Position) -> bool:
        """Check if position is within grid bounds."""
        return (0 <= pos.x < self.grid_width and 
                0 <= pos.y < self.grid_height)
    
    def _can_move_to_position(self, pos: Position) -> bool:
        """Check if player can move to the given position."""
        if not self._is_valid_position(pos):
            return False
        
        cell = self.game_state.level_grid[pos.y][pos.x]
        return cell not in [CellType.WALL, CellType.MINE]
    
    def _handle_player_movement(self, direction: Direction) -> None:
        """Process player movement in the given direction."""
        new_pos = self.game_state.player_pos + direction
        
        if not self._can_move_to_position(new_pos):
            return
        
        # Check what's at the new position
        cell_type = self.game_state.level_grid[new_pos.y][new_pos.x]
        
        if cell_type == CellType.MINE:
            self._trigger_game_over()
        elif cell_type == CellType.ITEM:
            self._collect_item(new_pos)
        elif cell_type == CellType.EXIT:
            self._try_exit_level()
        
        # Move player
        self._move_player_to_position(new_pos)
    
    def _move_player_to_position(self, new_pos: Position) -> None:
        """Move player to new position and update grid."""
        # Clear old position
        old_pos = self.game_state.player_pos
        self.game_state.level_grid[old_pos.y][old_pos.x] = CellType.EMPTY
        
        # Set new position
        self.game_state.player_pos = new_pos
        self.game_state.level_grid[new_pos.y][new_pos.x] = CellType.PLAYER
    
    def _collect_item(self, pos: Position) -> None:
        """Handle item collection."""
        self.game_state.items_collected += 1
        self.game_state.level_grid[pos.y][pos.x] = CellType.EMPTY
    
    def _try_exit_level(self) -> None:
        """Try to exit the current level."""
        if self._all_items_collected():
            self._advance_to_next_level()
        else:
            # Maybe show a message that all items must be collected
            pass
    
    def _all_items_collected(self) -> bool:
        """Check if all items have been collected."""
        return self.game_state.items_collected >= self.game_state.total_items
    
    def _advance_to_next_level(self) -> None:
        """Advance to the next level."""
        next_level = self.game_state.level_number + 1
        
        if next_level > 5:  # Win condition
            self.game_state.won = True
            self.game_state.game_over = True
        else:
            # Generate next level
            level_grid = self._generate_level(next_level)
            player_pos = self._find_player_start_position(level_grid)
            total_items = self._count_items_in_level(level_grid)
            
            self.game_state = GameState(
                player_pos=player_pos,
                level_grid=level_grid,
                items_collected=0,
                total_items=total_items,
                level_number=next_level
            )
    
    def _trigger_game_over(self) -> None:
        """Trigger game over state."""
        self.game_state.game_over = True
        self.game_state.won = False
    
    def _reset_game(self) -> None:
        """Reset the game to initial state."""
        self.game_state = self._create_initial_game_state()
    
    def update(self) -> None:
        """Main game update loop."""
        if self.game_state.game_over:
            if pyxel.btnp(pyxel.KEY_R):
                self._reset_game()
            return
        
        movement_direction = self._get_movement_direction()
        if movement_direction:
            self._handle_player_movement(movement_direction)
    
    def _get_cell_color(self, cell_type: CellType) -> int:
        """Get the color for a given cell type."""
        color_map = {
            CellType.EMPTY: 0,      # Black
            CellType.WALL: 6,       # Light Blue
            CellType.MINE: 8,       # Red
            CellType.PLAYER: 11,    # Yellow
            CellType.ITEM: 10,      # Green
            CellType.EXIT: 12       # Light Blue
        }
        return color_map.get(cell_type, 0)
    
    def _draw_cell(self, x: int, y: int, cell_type: CellType) -> None:
        """Draw a single cell at the given grid position."""
        screen_x = x * self.cell_size
        screen_y = y * self.cell_size
        color = self._get_cell_color(cell_type)
        
        if cell_type == CellType.EMPTY:
            return  # Don't draw empty cells
        elif cell_type == CellType.WALL:
            pyxel.rect(screen_x, screen_y, self.cell_size, self.cell_size, color)
        elif cell_type == CellType.MINE:
            pyxel.circb(screen_x + 3, screen_y + 3, 2, color)
        elif cell_type == CellType.PLAYER:
            pyxel.rect(screen_x + 1, screen_y + 1, 6, 6, color)
        elif cell_type == CellType.ITEM:
            pyxel.rect(screen_x + 2, screen_y + 2, 4, 4, color)
        elif cell_type == CellType.EXIT:
            pyxel.rectb(screen_x, screen_y, self.cell_size, self.cell_size, color)
    
    def _draw_game_grid(self) -> None:
        """Draw the entire game grid."""
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                cell_type = self.game_state.level_grid[y][x]
                self._draw_cell(x, y, cell_type)
    
    def _draw_ui_text(self) -> None:
        """Draw UI text (score, level, etc.)."""
        # Draw level info
        pyxel.text(2, 2, f"Level: {self.game_state.level_number}", 7)
        
        # Draw items collected
        items_text = f"Items: {self.game_state.items_collected}/{self.game_state.total_items}"
        pyxel.text(2, 10, items_text, 7)
        
        # Draw instructions
        if self._all_items_collected():
            pyxel.text(2, self.height - 16, "Find the exit!", 11)
        else:
            pyxel.text(2, self.height - 16, "Collect all items!", 7)
    
    def _draw_game_over_screen(self) -> None:
        """Draw the game over screen."""
        pyxel.cls(0)
        
        if self.game_state.won:
            message = "YOU WON!"
            color = 11
        else:
            message = "GAME OVER"
            color = 8
        
        # Center the message
        text_width = len(message) * 4
        x = (self.width - text_width) // 2
        y = self.height // 2 - 10
        
        pyxel.text(x, y, message, color)
        pyxel.text(x - 20, y + 20, "Press R to restart", 7)
    
    def draw(self) -> None:
        """Main draw function."""
        pyxel.cls(0)
        
        if self.game_state.game_over:
            self._draw_game_over_screen()
        else:
            self._draw_game_grid()
            self._draw_ui_text()


if __name__ == "__main__":
    MinedOutGame()
