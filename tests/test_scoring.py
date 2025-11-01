import pytest
from mined_out.config import BASE_SCORE_PER_LEVEL, DEATH_PENALTY, EFFICIENCY_BONUS_MAX
from mined_out.scoring import (
    calculate_base_score,
    calculate_efficiency_bonus,
    calculate_level_score,
    apply_death_penalty,
)


@pytest.mark.parametrize(
    "level_number,expected_base",
    [
        (1, 100),
        (2, 200),
        (5, 500),
        (10, 1000),
        (20, 2000),
    ],
)
def test_calculate_base_score_returns_correct_value(level_number, expected_base):
    result = calculate_base_score(level_number)
    assert result == expected_base, (
        f"Level {level_number} should have base score {expected_base}"
    )


def test_calculate_base_score_scales_linearly():
    score_1 = calculate_base_score(1)
    score_2 = calculate_base_score(2)
    assert score_2 == score_1 * 2, "Base score should scale linearly with level"


@pytest.mark.parametrize(
    "moves,optimal_moves,expected_bonus",
    [
        (10, 10, 1.5),
        (15, 10, 1.0),
        (20, 10, 0.5),
        (25, 10, 0.0),
        (30, 10, 0.0),
        (5, 10, 1.5),
    ],
)
def test_calculate_efficiency_bonus_returns_correct_value(
    moves, optimal_moves, expected_bonus
):
    result = calculate_efficiency_bonus(moves, optimal_moves)
    assert result == pytest.approx(expected_bonus), (
        f"{moves} moves vs {optimal_moves} optimal should give bonus {expected_bonus}"
    )


def test_calculate_efficiency_bonus_perfect_play_gives_max_bonus():
    result = calculate_efficiency_bonus(10, 10)
    assert result == EFFICIENCY_BONUS_MAX, (
        "Perfect play should give maximum efficiency bonus"
    )


def test_calculate_efficiency_bonus_better_than_optimal_gives_max_bonus():
    result = calculate_efficiency_bonus(5, 10)
    assert result == EFFICIENCY_BONUS_MAX, (
        "Better than optimal should still give max bonus"
    )


def test_calculate_efficiency_bonus_poor_play_gives_zero():
    result = calculate_efficiency_bonus(100, 10)
    assert result == 0.0, "Very poor play should give zero bonus"


def test_calculate_efficiency_bonus_never_negative():
    result = calculate_efficiency_bonus(1000, 10)
    assert result >= 0.0, "Efficiency bonus should never be negative"


@pytest.mark.parametrize(
    "moves,optimal,expected_min,expected_max",
    [
        (10, 10, 1.5, 1.5),
        (11, 10, 1.4, 1.5),
        (12, 10, 1.3, 1.4),
        (15, 10, 1.0, 1.0),
        (20, 10, 0.5, 0.5),
    ],
)
def test_calculate_efficiency_bonus_decreases_with_more_moves(
    moves, optimal, expected_min, expected_max
):
    result = calculate_efficiency_bonus(moves, optimal)
    assert expected_min <= result <= expected_max, (
        f"Bonus should be between {expected_min} and {expected_max}"
    )


@pytest.mark.parametrize(
    "level_number,moves,optimal_moves,expected_score",
    [
        (1, 10, 10, 150),
        (1, 15, 10, 100),
        (1, 20, 10, 50),
        (1, 25, 10, 0),
        (2, 10, 10, 300),
        (5, 20, 20, 750),
        (10, 50, 50, 1500),
    ],
)
def test_calculate_level_score_returns_correct_value(
    level_number, moves, optimal_moves, expected_score
):
    result = calculate_level_score(level_number, moves, optimal_moves)
    assert result == pytest.approx(expected_score), (
        f"Level {level_number} with {moves}/{optimal_moves} moves should score {expected_score}"
    )


def test_calculate_level_score_perfect_play():
    level = 5
    optimal = 30
    result = calculate_level_score(level, optimal, optimal)
    expected = BASE_SCORE_PER_LEVEL * level * EFFICIENCY_BONUS_MAX
    assert result == pytest.approx(expected), "Perfect play should give max score"


def test_calculate_level_score_poor_play_gives_zero():
    result = calculate_level_score(1, 100, 10)
    assert result == 0, "Very poor play should give zero score"


def test_calculate_level_score_never_negative():
    result = calculate_level_score(10, 1000, 10)
    assert result >= 0, "Score should never be negative"


def test_calculate_level_score_higher_levels_worth_more():
    moves = 20
    optimal = 20
    score_1 = calculate_level_score(1, moves, optimal)
    score_5 = calculate_level_score(5, moves, optimal)
    score_10 = calculate_level_score(10, moves, optimal)
    assert score_1 < score_5 < score_10, "Higher levels should be worth more points"


@pytest.mark.parametrize(
    "current_score,expected_score",
    [
        (100, 50),
        (200, 150),
        (50, 0),
        (25, 0),
        (0, 0),
        (1000, 950),
    ],
)
def test_apply_death_penalty_reduces_score_correctly(current_score, expected_score):
    result = apply_death_penalty(current_score)
    assert result == expected_score, (
        f"Score {current_score} minus death penalty should be {expected_score}"
    )


def test_apply_death_penalty_uses_correct_penalty():
    initial = 1000
    result = apply_death_penalty(initial)
    assert result == initial - DEATH_PENALTY, "Should subtract DEATH_PENALTY constant"


def test_apply_death_penalty_never_goes_negative():
    result = apply_death_penalty(10)
    assert result >= 0, "Score should never go negative from death penalty"


def test_apply_death_penalty_zero_score_stays_zero():
    result = apply_death_penalty(0)
    assert result == 0, "Zero score should stay zero"


def test_apply_death_penalty_multiple_deaths():
    score = 1000
    score = apply_death_penalty(score)
    score = apply_death_penalty(score)
    score = apply_death_penalty(score)
    expected = max(0, 1000 - 3 * DEATH_PENALTY)
    assert score == expected, "Multiple deaths should stack penalties"


@pytest.mark.parametrize(
    "level,moves,optimal",
    [
        (1, 10, 10),
        (5, 25, 20),
        (10, 50, 40),
    ],
)
def test_scoring_integration_full_flow(level, moves, optimal):
    base = calculate_base_score(level)
    bonus = calculate_efficiency_bonus(moves, optimal)
    score = calculate_level_score(level, moves, optimal)

    expected = int(base * bonus)
    assert score == expected, "Full scoring flow should calculate correctly"


def test_scoring_with_death_scenario():
    level = 1
    optimal = 10
    moves = 15
    initial_score = 0

    level_score = calculate_level_score(level, moves, optimal)
    initial_score += level_score

    initial_score = apply_death_penalty(initial_score)

    assert initial_score >= 0, "Score should remain valid after death"
    assert initial_score < level_score, "Death should reduce total score"
