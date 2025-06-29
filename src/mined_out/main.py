import pyxel
from mined_out.constants import GRID_WIDTH, GRID_HEIGHT, CELL_SIZE
from mined_out.level_generator import LevelGenerator
from mined_out.input_handler import InputHandler
from mined_out.game_renderer import GameRenderer
from mined_out.game_logic import GameLogic


class MinedOut:
    def __init__(self):
        self._initialize_display()
        self._initialize_components()
        self._start_new_game()
        pyxel.run(self.update, self.draw)

    def _initialize_display(self) -> None:
        """Set up the game window and display settings."""
        self.width = GRID_WIDTH * CELL_SIZE
        self.height = GRID_HEIGHT * CELL_SIZE
        pyxel.init(self.width, self.height, title="Mined-Out!")
        pyxel.mouse(False)

    def _initialize_components(self) -> None:
        """Initialize all game components and systems."""
        self.level_gen = LevelGenerator(GRID_WIDTH, GRID_HEIGHT)
        self.input_handler = InputHandler()
        self.renderer = GameRenderer(self.width, self.height, CELL_SIZE)
        self.game_logic = GameLogic(GRID_WIDTH, GRID_HEIGHT)

    def _start_new_game(self) -> None:
        """Create initial game state for a new game."""
        self.state = self.level_gen.create_level(1)
        self.game_logic._update_mine_count(self.state)

    def _should_handle_game_over(self) -> bool:
        """Check if game is over and handle restart input."""
        if not self.state.game_over:
            return False

        if self.input_handler.should_restart():
            self._start_new_game()
        return True

    def _should_skip_input(self) -> bool:
        """Check if player input should be ignored during mine reveal."""
        return self.state.mine_reveal_timer > 0

    def _handle_player_input(self) -> None:
        """Process player movement input."""
        direction = self.input_handler.get_direction()
        if direction:
            self.game_logic.try_move_player(self.state, direction)

    def update(self) -> None:
        """Main game update loop called by pyxel."""
        self.game_logic.update_timers(self.state)

        if self._should_handle_game_over():
            return

        if self._should_skip_input():
            return

        self._handle_player_input()

    def _should_handle_game_over(self) -> bool:
        """Check if game is over and handle restart input."""
        if not self.state.game_over:
            return False

        if self.input_handler.should_restart():
            self._start_new_game()
        return True

    def _should_skip_input(self) -> bool:
        """Check if player input should be ignored during mine reveal."""
        return self.state.mine_reveal_timer > 0

    def _handle_player_input(self) -> None:
        """Process player movement input."""
        direction = self.input_handler.get_direction()
        if direction:
            self.game_logic.try_move_player(self.state, direction)

    def draw(self) -> None:
        """Render the current game state."""
        self.renderer.draw_game(self.state)


def main() -> None:
    """Entry point for the game."""
    MinedOut()


if __name__ == "__main__":
    main()
