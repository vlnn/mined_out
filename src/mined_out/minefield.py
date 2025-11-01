import random
from typing import List, Set
from mined_out.types import Position, Minefield
from mined_out.config import (
    PLAYABLE_WIDTH,
    PLAYABLE_HEIGHT,
    PLAYABLE_AREA,
    MINE_BASE_DENSITY,
    MINE_DENSITY_INCREASE_PER_LEVEL,
    MINE_DENSITY_MAX_MULTIPLIER,
    BUFFER_ZONE_RADIUS,
    ENTRY_DOOR_COLS,
    EXIT_DOOR_COLS,
    EXIT_DOOR_ROW,
    START_POSITION_ROW,
    PLAYAREA_START_ROW,
    PLAYAREA_END_ROW,
)


def calculate_mine_count(level_number: int) -> int:
    multiplier = 1.0 + (level_number - 1) * MINE_DENSITY_INCREASE_PER_LEVEL
    multiplier = min(multiplier, MINE_DENSITY_MAX_MULTIPLIER)
    return int(PLAYABLE_AREA * MINE_BASE_DENSITY * multiplier)


def is_position_in_buffer_zone(
    position: Position, door_positions: List[Position]
) -> bool:
    for door_pos in door_positions:
        dx = abs(position.x - door_pos.x)
        dy = abs(position.y - door_pos.y)
        distance = max(dx, dy)
        if distance <= BUFFER_ZONE_RADIUS:
            return True
    return False


def get_forbidden_positions() -> Set[Position]:
    forbidden = set()

    for x in range(32):
        for y in range(24):
            if x == 0 or x == 31:
                forbidden.add(Position(x, y))

    for x in range(1, 31):
        for y in range(24):
            if y < PLAYAREA_START_ROW or y > PLAYAREA_END_ROW:
                forbidden.add(Position(x, y))
            elif x == 1 or x == 30:
                forbidden.add(Position(x, y))
            elif y == PLAYAREA_START_ROW or y == PLAYAREA_END_ROW:
                forbidden.add(Position(x, y))

    entry_door_positions = [
        Position(col, START_POSITION_ROW) for col in ENTRY_DOOR_COLS
    ]
    exit_door_positions = [Position(col, EXIT_DOOR_ROW + 1) for col in EXIT_DOOR_COLS]

    for x in range(1, 31):
        for y in range(1, 23):
            pos = Position(x, y)
            if is_position_in_buffer_zone(pos, entry_door_positions):
                forbidden.add(pos)
            if is_position_in_buffer_zone(pos, exit_door_positions):
                forbidden.add(pos)

    return forbidden


def generate_valid_mine_positions(mine_count: int) -> List[Position]:
    forbidden = get_forbidden_positions()
    valid_positions = []

    for x in range(1, 31):
        for y in range(PLAYAREA_START_ROW, PLAYAREA_END_ROW + 1):
            pos = Position(x, y)
            if pos not in forbidden:
                valid_positions.append(pos)

    return random.sample(valid_positions, mine_count)


def create_minefield(level_number: int) -> Minefield:
    mine_count = calculate_mine_count(level_number)
    mine_positions = generate_valid_mine_positions(mine_count)

    return Minefield(
        width=PLAYABLE_WIDTH,
        height=PLAYABLE_HEIGHT,
        mines=frozenset(mine_positions),
    )
