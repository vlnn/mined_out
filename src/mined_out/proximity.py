from typing import List
from mined_out.types import Position, Minefield
from mined_out.movement import Direction, get_next_position, is_valid_position


CARDINAL_DIRECTIONS = [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT]


def get_adjacent_positions(position: Position) -> List[Position]:
    return [get_next_position(position, direction) for direction in CARDINAL_DIRECTIONS]


def count_adjacent_mines(position: Position, minefield: Minefield) -> int:
    adjacent_positions = get_adjacent_positions(position)
    count = 0
    for adj_pos in adjacent_positions:
        if is_valid_position(adj_pos) and minefield.has_mine_at(adj_pos):
            count += 1
    return count
