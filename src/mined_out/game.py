from typing import Optional
from mined_out.types import Position, GameState
from mined_out.config import INITIAL_LIVES
from mined_out.movement import Direction, get_next_position, can_move_to
from mined_out.level import generate_level, get_start_position, get_exit_position
from mined_out.pathfinding import find_path
from mined_out.scoring import calculate_level_score, apply_death_penalty


def create_initial_game_state() -> GameState:
    level_number = 1
    minefield = generate_level(level_number)
    start_pos = get_start_position()

    return GameState(
        level_number=level_number,
        minefield=minefield,
        player_pos=start_pos,
        visited=frozenset([start_pos]),
        move_history=(start_pos,),
        lives=INITIAL_LIVES,
        score=0,
        move_count=0,
        is_replay=False,
    )


def move_player(state: GameState, direction: Direction) -> GameState:
    next_pos = get_next_position(state.player_pos, direction)

    if not can_move_to(next_pos):
        return state

    return GameState(
        level_number=state.level_number,
        minefield=state.minefield,
        player_pos=next_pos,
        visited=state.visited | {next_pos},
        move_history=state.move_history + (next_pos,),
        lives=state.lives,
        score=state.score,
        move_count=state.move_count + 1,
        is_replay=state.is_replay,
    )


def is_on_mine(state: GameState) -> bool:
    return state.minefield.has_mine_at(state.player_pos)


def is_at_exit(state: GameState) -> bool:
    return state.player_pos == get_exit_position()


def start_new_level(level_number: int, score: int, lives: int) -> GameState:
    minefield = generate_level(level_number)
    start_pos = get_start_position()

    return GameState(
        level_number=level_number,
        minefield=minefield,
        player_pos=start_pos,
        visited=frozenset([start_pos]),
        move_history=(start_pos,),
        lives=lives,
        score=score,
        move_count=0,
        is_replay=False,
    )


def handle_death(state: GameState) -> Optional[GameState]:
    new_lives = state.lives - 1

    if new_lives <= 0:
        return None

    new_score = apply_death_penalty(state.score)

    return start_new_level(state.level_number, new_score, new_lives)


def handle_level_complete(state: GameState) -> GameState:
    path = find_path(get_start_position(), get_exit_position(), state.minefield)
    optimal_moves = len(path) - 1 if path else state.move_count

    level_score = calculate_level_score(
        state.level_number, state.move_count, optimal_moves
    )

    new_score = state.score + level_score
    next_level = state.level_number + 1

    return start_new_level(next_level, new_score, state.lives)
