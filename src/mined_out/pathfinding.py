from collections import deque
from typing import List, Optional, Set
from mined_out.types import Position, Minefield
from mined_out.movement import get_next_position, is_valid_position, Direction


CARDINAL_DIRECTIONS = [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT]


def has_path(start: Position, goal: Position, minefield: Minefield) -> bool:
    if start == goal:
        return True

    visited: Set[Position] = {start}
    queue = deque([start])

    while queue:
        current = queue.popleft()

        for direction in CARDINAL_DIRECTIONS:
            next_pos = get_next_position(current, direction)

            if next_pos == goal:
                return True

            if (
                next_pos not in visited
                and is_valid_position(next_pos)
                and not minefield.has_mine_at(next_pos)
            ):
                visited.add(next_pos)
                queue.append(next_pos)

    return False


def find_path(
    start: Position, goal: Position, minefield: Minefield
) -> Optional[List[Position]]:
    if start == goal:
        return [start]

    visited: Set[Position] = {start}
    queue = deque([(start, [start])])

    while queue:
        current, path = queue.popleft()

        for direction in CARDINAL_DIRECTIONS:
            next_pos = get_next_position(current, direction)

            if next_pos == goal:
                return path + [goal]

            if (
                next_pos not in visited
                and is_valid_position(next_pos)
                and not minefield.has_mine_at(next_pos)
            ):
                visited.add(next_pos)
                queue.append((next_pos, path + [next_pos]))

    return None
