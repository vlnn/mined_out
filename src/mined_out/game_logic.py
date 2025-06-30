from mined_out.common import Direction, CellType, Position, Explosion, MAX_LEVEL, move_position
from mined_out.game_state import GameState
from mined_out.audio_operations import play_item_collect, play_explosion
from mined_out.grid_operations import count_adjacent_mines, can_move_to_cell
from mined_out.level_generation import create_level_state

def can_exit_level(items_collected: int, total_items: int) -> bool:
    """Check if player can exit current level."""
    return items_collected >= total_items

def should_advance_level(state: GameState) -> bool:
    """Check if player should advance to next level."""
    player_cell = state.grid[state.player_pos.y][state.player_pos.x]
    return player_cell == CellType.EXIT and can_exit_level(state.items_collected, state.total_items)

def should_win_game(level: int) -> bool:
    """Check if player has won the game."""
    return level > MAX_LEVEL

def handle_cell_interaction(state: GameState, cell_type: CellType) -> None:
    """Handle player interaction with cell."""
    if cell_type == CellType.ITEM:
        state.items_collected += 1
        play_item_collect()

def move_player_to_position(state: GameState, new_pos: Position, width: int, height: int) -> None:
    """Move player to new position and update state."""
    old_pos = state.player_pos
    if state.grid[old_pos.y][old_pos.x] == CellType.PLAYER:
        state.grid[old_pos.y][old_pos.x] = CellType.VISITED

    state.player_pos = new_pos
    state.grid[new_pos.y][new_pos.x] = CellType.PLAYER
    state.mine_count_nearby = count_adjacent_mines(state.grid, state.player_pos, width, height)

def start_mine_reveal(state: GameState, mine_pos: Position) -> None:
    """Start mine reveal sequence."""
    state.grid[mine_pos.y][mine_pos.x] = CellType.REVEALED_MINE
    state.revealing_mine_pos = mine_pos
    state.mine_reveal_timer = 5

def explode_mine(state: GameState, mine_pos: Position) -> None:
    """Trigger mine explosion."""
    state.explosion = Explosion(mine_pos)
    state.game_over = True
    play_explosion()

def try_player_move(state: GameState, direction: Direction, width: int, height: int) -> None:
    """Attempt to move player in direction."""
    new_pos = move_position(state.player_pos, direction)

    if not can_move_to_cell(state.grid, new_pos, width, height):
        return

    cell = state.grid[new_pos.y][new_pos.x]

    if cell == CellType.MINE:
        start_mine_reveal(state, new_pos)
    else:
        move_player_to_position(state, new_pos, width, height)
        handle_cell_interaction(state, cell)

        if should_advance_level(state):
            if should_win_game(state.level):
                state.won = True
                state.game_over = True
            else:
                new_state = create_level_state(state.level + 1, width, height)
                state.__dict__.update(new_state.__dict__)
                state.mine_count_nearby = count_adjacent_mines(state.grid, state.player_pos, width, height)

def update_game_timers(state: GameState) -> None:
    """Update all game timers."""
    if state.explosion:
        state.explosion.frame += 1
        if state.explosion.frame >= 80:
            state.explosion = None

    if state.mine_reveal_timer > 0:
        state.mine_reveal_timer -= 1
        if state.mine_reveal_timer == 0 and state.revealing_mine_pos:
            explode_mine(state, state.revealing_mine_pos)
            state.revealing_mine_pos = None
