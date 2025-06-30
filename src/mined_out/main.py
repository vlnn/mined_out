import pyxel

from mined_out.constants import GRID_WIDTH, GRID_HEIGHT, CELL_SIZE
from mined_out.audio_operations import setup_sounds
from mined_out.level_generation import create_level_state
from mined_out.grid_operations import count_adjacent_mines
from mined_out.rendering_operations import draw_grid, draw_mine_indicator, draw_explosion, draw_game_over_screen, draw_ui
from mined_out.game_logic import try_player_move, update_game_timers, try_player_move
from mined_out.input_operations import is_restart_pressed, get_direction_from_input

class MinedOut:
    """Main game class - minimal state container for Pyxel integration."""

    def __init__(self):
        self._initialize_display()
        self._initialize_game()
        setup_sounds()
        pyxel.run(self.update, self.draw)

    def _initialize_display(self) -> None:
        """Set up the game window."""
        self.width = GRID_WIDTH * CELL_SIZE
        self.height = GRID_HEIGHT * CELL_SIZE
        pyxel.init(self.width, self.height, title="Mined-Out!")
        pyxel.mouse(False)

    def _initialize_game(self) -> None:
        """Create initial game state."""
        self.state = create_level_state(1, GRID_WIDTH, GRID_HEIGHT)
        self.state.mine_count_nearby = count_adjacent_mines(
            self.state.grid, self.state.player_pos, GRID_WIDTH, GRID_HEIGHT
        )

    def _restart_game(self) -> None:
        """Restart game from level 1."""
        self._initialize_game()

    def update(self) -> None:
        """Main game update loop."""
        update_game_timers(self.state)

        if self.state.game_over:
            if is_restart_pressed():
                self._restart_game()
            return

        if self.state.mine_reveal_timer > 0:
            return

        direction = get_direction_from_input()
        if direction:
            try_player_move(self.state, direction, GRID_WIDTH, GRID_HEIGHT)

    def draw(self) -> None:
        """Render the current game state."""
        pyxel.cls(4)
        draw_grid(self.state.grid, GRID_WIDTH, GRID_HEIGHT, CELL_SIZE)

        if not self.state.game_over:
            draw_mine_indicator(self.state.player_pos, self.state.mine_count_nearby, CELL_SIZE, self.width, self.height)

        if self.state.explosion:
            draw_explosion(self.state.explosion, CELL_SIZE)

        if self.state.game_over:
            draw_game_over_screen(self.state.won, self.width, self.height)
        else:
            draw_ui(self.state.level, self.state.items_collected, self.state.total_items,
                   self.state.mine_count_nearby, self.height)


if __name__ == "__main__":
    MinedOut()
