from mined_out.common import Direction,CellType,Position,Explosion
from mined_out.game_state import GameState
from mined_out.movement_handler import MovementHandler
from mined_out.grid_analyzer import GridAnalyzer
from mined_out.level_generator import LevelGenerator
from mined_out.sound_manager import SoundManager


class GameLogic:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.movement = MovementHandler(width, height)
        self.sounds = SoundManager()

    def try_move_player(self, state: GameState, direction: Direction) -> None:
        new_pos = state.player_pos.move(direction)

        if not self.movement.is_valid_move(new_pos, state.grid):
            return

        cell = state.grid[new_pos.y][new_pos.x]

        if cell == CellType.MINE:
            self._start_mine_reveal(state, new_pos)
        else:
            self._move_player_to(state, new_pos)
            self._handle_cell_interaction(state, cell)

    def _move_player_to(self, state: GameState, new_pos: Position) -> None:
        old_pos = state.player_pos
        if state.grid[old_pos.y][old_pos.x] == CellType.PLAYER:
            state.grid[old_pos.y][old_pos.x] = CellType.VISITED

        state.player_pos = new_pos
        state.grid[new_pos.y][new_pos.x] = CellType.PLAYER
        self._update_mine_count(state)

    def _handle_cell_interaction(self, state: GameState, cell: CellType) -> None:
        if cell == CellType.ITEM:
            self._collect_item(state)
        elif cell == CellType.EXIT and self._can_exit(state):
            self._advance_level(state)

    def _collect_item(self, state: GameState) -> None:
        state.items_collected += 1
        self.sounds.play_item_collect()

    def _can_exit(self, state: GameState) -> bool:
        return state.items_collected >= state.total_items

    def _advance_level(self, state: GameState) -> None:
        if state.level >= 5:
            state.won = True
            state.game_over = True
        else:
            level_gen = LevelGenerator(self.width, self.height)
            new_state = level_gen.create_level(state.level + 1)
            state.__dict__.update(new_state.__dict__)
            self._update_mine_count(state)

    def _start_mine_reveal(self, state: GameState, mine_pos: Position) -> None:
        state.grid[mine_pos.y][mine_pos.x] = CellType.REVEALED_MINE
        state.revealing_mine_pos = mine_pos
        state.mine_reveal_timer = 15  # MINE_REVEAL_FRAMES

    def _explode_mine(self, state: GameState, mine_pos: Position) -> None:
        state.explosion = Explosion(mine_pos)
        state.game_over = True
        self.sounds.play_explosion()

    def _update_mine_count(self, state: GameState) -> None:
        analyzer = GridAnalyzer(state.grid, self.width, self.height)
        state.mine_count_nearby = analyzer.count_adjacent_mines(state.player_pos)

    def update_timers(self, state: GameState) -> None:
        if state.explosion:
            state.explosion.frame += 1
            if state.explosion.frame >= 30:  # EXPLOSION_FRAMES
                state.explosion = None

        if state.mine_reveal_timer > 0:
            state.mine_reveal_timer -= 1
            if state.mine_reveal_timer == 0 and state.revealing_mine_pos:
                self._explode_mine(state, state.revealing_mine_pos)
                state.revealing_mine_pos = None
