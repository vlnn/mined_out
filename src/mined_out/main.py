import pyxel
from enum import Enum
from typing import Optional
from mined_out.types import GameState, ReplayState
from mined_out.config import SCREEN_WIDTH, SCREEN_HEIGHT, REPLAY_AUTO_ADVANCE_TIMEOUT
from mined_out.game import (
    create_initial_game_state,
    move_player,
    is_on_mine,
    is_at_exit,
    handle_death,
    handle_level_complete,
)
from mined_out.movement import Direction
from mined_out.replay import (
    create_replay_state,
    advance_replay,
    is_replay_complete,
    get_replay_position,
    skip_to_end,
)
from mined_out.renderer import draw_game_state, draw_transient_info


class GameMode(Enum):
    PLAYING = 1
    REPLAY = 2
    WAITING = 3
    GAME_OVER = 4


class MinedOutGame:
    def __init__(self):
        pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT, title="Mined-Out", fps=60)

        self.state: Optional[GameState] = create_initial_game_state()
        self.mode: GameMode = GameMode.PLAYING
        self.replay_state: Optional[ReplayState] = None
        self.replay_history: tuple = ()
        self.replay_frame_counter: int = 0
        self.wait_timer: float = 0.0
        self.final_score: int = 0

        pyxel.run(self.update, self.draw)

    def update(self):
        if self.mode == GameMode.PLAYING:
            self._update_playing()
        elif self.mode == GameMode.REPLAY:
            self._update_replay()
        elif self.mode == GameMode.WAITING:
            self._update_waiting()
        elif self.mode == GameMode.GAME_OVER:
            self._update_game_over()

    def _update_playing(self):
        if self.state is None:
            return

        direction = None
        if pyxel.btnp(pyxel.KEY_UP):
            direction = Direction.UP
        elif pyxel.btnp(pyxel.KEY_DOWN):
            direction = Direction.DOWN
        elif pyxel.btnp(pyxel.KEY_LEFT):
            direction = Direction.LEFT
        elif pyxel.btnp(pyxel.KEY_RIGHT):
            direction = Direction.RIGHT

        if direction:
            self.state = move_player(self.state, direction)

            if is_on_mine(self.state):
                print(f"DEBUG: Hit mine at {self.state.player_pos}")
                self._start_replay("MINE!")
            elif is_at_exit(self.state):
                print(f"DEBUG: Reached exit at {self.state.player_pos}")
                self._start_replay("LEVEL COMPLETE!")

    def _update_replay(self):
        if self.replay_state is None:
            return

        if self._any_key_pressed():
            self.replay_state = skip_to_end(self.replay_state)

        if not is_replay_complete(self.replay_state):
            self.replay_state = advance_replay(self.replay_state)

        if is_replay_complete(self.replay_state):
            self._start_waiting()

    def _update_waiting(self):
        self.wait_timer += 1.0 / 60.0

        if self._any_key_pressed() or self.wait_timer >= REPLAY_AUTO_ADVANCE_TIMEOUT:
            self._advance_after_replay()

    def _update_game_over(self):
        if pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.KEY_RETURN):
            self.state = create_initial_game_state()
            self.mode = GameMode.PLAYING

    def _start_replay(self, message: str):
        if self.state is None:
            return

        self.replay_history = self.state.move_history
        self.replay_state = create_replay_state(self.replay_history)
        self.mode = GameMode.REPLAY

    def _start_waiting(self):
        self.wait_timer = 0.0
        self.mode = GameMode.WAITING

    def _advance_after_replay(self):
        if self.state is None:
            return

        if is_on_mine(self.state):
            new_state = handle_death(self.state)
            if new_state is None:
                self.final_score = self.state.score
                self.mode = GameMode.GAME_OVER
            else:
                self.state = new_state
                self.mode = GameMode.PLAYING
        elif is_at_exit(self.state):
            self.state = handle_level_complete(self.state)
            self.mode = GameMode.PLAYING

    def _any_key_pressed(self) -> bool:
        for key in range(256):
            if pyxel.btnp(key):
                return True
        return False

    def draw(self):
        if self.mode == GameMode.PLAYING:
            if self.state:
                draw_game_state(self.state, show_mines=False)

        elif self.mode == GameMode.REPLAY:
            if self.state and self.replay_state:
                replay_pos = get_replay_position(self.replay_state, self.replay_history)
                if replay_pos:
                    visited_up_to_now = frozenset(
                        self.replay_history[: self.replay_state.current_frame + 1]
                    )
                    replay_render_state = GameState(
                        level_number=self.state.level_number,
                        minefield=self.state.minefield,
                        player_pos=replay_pos,
                        visited=visited_up_to_now,
                        move_history=self.replay_history,
                        lives=self.state.lives,
                        score=self.state.score,
                        move_count=self.replay_state.current_frame,
                        is_replay=True,
                    )
                    draw_game_state(replay_render_state, show_mines=True)
                    draw_transient_info("ACTION REPLAY")

        elif self.mode == GameMode.WAITING:
            if self.state:
                draw_game_state(self.state, show_mines=True)
                draw_transient_info("Press any key to continue...")

        elif self.mode == GameMode.GAME_OVER:
            if self.state:
                draw_game_state(self.state, show_mines=True)
            draw_transient_info(f"GAME OVER - Score: {self.final_score} - Press SPACE")


def main():
    MinedOutGame()


# Alias for package entry point
MinedOut = MinedOutGame


if __name__ == "__main__":
    main()
