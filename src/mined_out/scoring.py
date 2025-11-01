from mined_out.config import BASE_SCORE_PER_LEVEL, DEATH_PENALTY, EFFICIENCY_BONUS_MAX


def calculate_base_score(level_number: int) -> int:
    return BASE_SCORE_PER_LEVEL * level_number


def calculate_efficiency_bonus(moves: int, optimal_moves: int) -> float:
    if moves <= optimal_moves:
        return EFFICIENCY_BONUS_MAX

    extra_moves = moves - optimal_moves
    penalty = extra_moves / optimal_moves
    bonus = EFFICIENCY_BONUS_MAX - penalty
    return max(0.0, bonus)


def calculate_level_score(level_number: int, moves: int, optimal_moves: int) -> int:
    base = calculate_base_score(level_number)
    bonus = calculate_efficiency_bonus(moves, optimal_moves)
    return int(base * bonus)


def apply_death_penalty(current_score: int) -> int:
    return max(0, current_score - DEATH_PENALTY)
