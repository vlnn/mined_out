import pyxel
from mined_out.constants import GRID_WIDTH, GRID_HEIGHT, CELL_SIZE
from mined_out.level_generator import LevelGenerator
from mined_out.input_handler import InputHandler
from mined_out.game_renderer import GameRenderer
from mined_out.game_logic import GameLogic

class MinedOut:

    def __init__(self):
        self.width = GRID_WIDTH * CELL_SIZE
        self.height = GRID_HEIGHT * CELL_SIZE

        pyxel.init(self.width, self.height, title="Mined-Out!")
        pyxel.mouse(False)

        self.level_gen = LevelGenerator(GRID_WIDTH, GRID_HEIGHT)
        self.input_handler = InputHandler()
        self.renderer = GameRenderer(self.width, self.height, CELL_SIZE)
        self.game_logic = GameLogic(GRID_WIDTH, GRID_HEIGHT)

        self.state = self.level_gen.create_level(1)
        self.game_logic._update_mine_count(self.state)

        pyxel.run(self.update, self.draw)

    def update(self) -> None:
        self.game_logic.update_timers(self.state)

        if self.state.game_over:
            if self.input_handler.should_restart():
                self._reset_game()
            return

        if self.state.mine_reveal_timer > 0:
            return

        direction = self.input_handler.get_direction()
        if direction:
            self.game_logic.try_move_player(self.state, direction)

    def draw(self) -> None:
        self.renderer.draw_game(self.state)

    def _reset_game(self) -> None:
        self.state = self.level_gen.create_level(1)
        self.game_logic._update_mine_count(self.state)


if __name__ == "__main__":
    MinedOut()
