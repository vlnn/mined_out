import pytest
from mined_out.types import Position, Minefield
from mined_out.config import (
    PLAYABLE_WIDTH,
    PLAYABLE_HEIGHT,
    PLAYABLE_AREA,
    MINE_BASE_DENSITY,
    MINE_DENSITY_MAX_MULTIPLIER,
    ENTRY_DOOR_COLS,
    EXIT_DOOR_COLS,
    EXIT_DOOR_ROW,
    START_POSITION_ROW,
)
from mined_out.minefield import (
    calculate_mine_count,
    get_forbidden_positions,
    is_position_in_buffer_zone,
    generate_valid_mine_positions,
    create_minefield,
)


def test_calculate_mine_count_respects_max_multiplier():
    very_high_level = 100
    mine_count = calculate_mine_count(very_high_level)
    max_possible = int(PLAYABLE_AREA * MINE_BASE_DENSITY * MINE_DENSITY_MAX_MULTIPLIER)
    assert mine_count <= max_possible, (
        f"Mine count should not exceed maximum density cap of {max_possible}"
    )


def test_calculate_mine_count_increases_with_level():
    counts = [calculate_mine_count(level) for level in range(1, 11)]
    for i in range(len(counts) - 1):
        assert counts[i] <= counts[i + 1], (
            f"Mine count should increase or stay same as level increases"
        )


class TestIsPositionInBufferZone:
    @pytest.mark.parametrize(
        "position,door_positions,expected",
        [
            (Position(15, 20), [Position(15, 21), Position(16, 21)], True),
            (Position(16, 20), [Position(15, 21), Position(16, 21)], True),
            (Position(14, 21), [Position(15, 21), Position(16, 21)], True),
            (Position(17, 21), [Position(15, 21), Position(16, 21)], True),
            (Position(15, 19), [Position(15, 21), Position(16, 21)], False),
            (Position(13, 21), [Position(15, 21), Position(16, 21)], False),
            (Position(20, 20), [Position(15, 21), Position(16, 21)], False),
        ],
    )
    def test_is_position_in_buffer_zone(self, position, door_positions, expected):
        result = is_position_in_buffer_zone(position, door_positions)
        assert result == expected, (
            f"Position {position} should {'be' if expected else 'not be'} in buffer zone of doors"
        )

    def test_is_position_in_buffer_zone_uses_chebyshev_distance(self):
        door = Position(10, 10)
        assert is_position_in_buffer_zone(Position(9, 10), [door]), (
            "Should be in buffer zone (horizontal distance 1)"
        )
        assert is_position_in_buffer_zone(Position(11, 10), [door]), (
            "Should be in buffer zone (horizontal distance 1)"
        )
        assert is_position_in_buffer_zone(Position(10, 9), [door]), (
            "Should be in buffer zone (vertical distance 1)"
        )
        assert is_position_in_buffer_zone(Position(10, 11), [door]), (
            "Should be in buffer zone (vertical distance 1)"
        )
        assert is_position_in_buffer_zone(Position(9, 9), [door]), (
            "Should be in buffer zone (diagonal distance 1)"
        )
        assert is_position_in_buffer_zone(Position(11, 11), [door]), (
            "Should be in buffer zone (diagonal distance 1)"
        )
        assert not is_position_in_buffer_zone(Position(8, 10), [door]), (
            "Should not be in buffer zone (distance 2)"
        )
        assert not is_position_in_buffer_zone(Position(8, 8), [door]), (
            "Should not be in buffer zone (distance 2)"
        )


class TestGetForbiddenPositions:
    def test_get_forbidden_positions_includes_walls(self):
        forbidden = get_forbidden_positions()
        assert Position(0, 10) in forbidden, "Left wall should be forbidden"
        assert Position(31, 10) in forbidden, "Right wall should be forbidden"

    def test_get_forbidden_positions_includes_buffer_around_entry_door(self):
        forbidden = get_forbidden_positions()
        for col in ENTRY_DOOR_COLS:
            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    pos = Position(col + dx, START_POSITION_ROW + dy)
                    assert pos in forbidden, (
                        f"Position {pos} should be in entry door buffer zone"
                    )

    def test_get_forbidden_positions_includes_buffer_around_exit_door(self):
        forbidden = get_forbidden_positions()
        exit_row = EXIT_DOOR_ROW + 1
        for col in EXIT_DOOR_COLS:
            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    pos = Position(col + dx, exit_row + dy)
                    assert pos in forbidden, (
                        f"Position {pos} should be in exit door buffer zone"
                    )

    def test_get_forbidden_positions_includes_border_tiles(self):
        forbidden = get_forbidden_positions()
        assert Position(1, 2) in forbidden, "Top border should be forbidden"
        assert Position(1, 21) in forbidden, "Bottom border should be forbidden"
        assert Position(1, 10) in forbidden, "Left border should be forbidden"
        assert Position(30, 10) in forbidden, "Right border should be forbidden"

    def test_get_forbidden_positions_allows_interior_positions(self):
        forbidden = get_forbidden_positions()
        assert Position(10, 10) not in forbidden, (
            "Interior position should not be forbidden"
        )
        assert Position(20, 15) not in forbidden, (
            "Interior position should not be forbidden"
        )


class TestGenerateValidMinePositions:
    def test_generate_valid_mine_positions_returns_correct_count(self):
        mine_count = 50
        positions = generate_valid_mine_positions(mine_count)
        assert len(positions) == mine_count, (
            f"Should generate exactly {mine_count} mine positions"
        )

    def test_generate_valid_mine_positions_avoids_forbidden_zones(self):
        mine_count = 50
        positions = generate_valid_mine_positions(mine_count)
        forbidden = get_forbidden_positions()
        for pos in positions:
            assert pos not in forbidden, (
                f"Mine at {pos} should not be in forbidden zone"
            )

    def test_generate_valid_mine_positions_all_unique(self):
        mine_count = 50
        positions = generate_valid_mine_positions(mine_count)
        assert len(positions) == len(set(positions)), (
            "All mine positions should be unique"
        )

    def test_generate_valid_mine_positions_within_bounds(self):
        mine_count = 50
        positions = generate_valid_mine_positions(mine_count)
        for pos in positions:
            assert 1 <= pos.x <= 30, (
                f"Mine x coordinate {pos.x} should be within bounds"
            )
            assert 2 <= pos.y <= 21, (
                f"Mine y coordinate {pos.y} should be within bounds"
            )

    def test_generate_valid_mine_positions_different_on_repeated_calls(self):
        mine_count = 20
        positions1 = set(generate_valid_mine_positions(mine_count))
        positions2 = set(generate_valid_mine_positions(mine_count))
        assert positions1 != positions2, (
            "Multiple calls should generate different mine layouts"
        )


class TestCreateMinefield:
    def test_create_minefield_returns_minefield_with_correct_dimensions(self):
        level = 1
        minefield = create_minefield(level)
        assert minefield.width == PLAYABLE_WIDTH, (
            f"Minefield width should be {PLAYABLE_WIDTH}"
        )
        assert minefield.height == PLAYABLE_HEIGHT, (
            f"Minefield height should be {PLAYABLE_HEIGHT}"
        )

    def test_create_minefield_has_correct_mine_count(self):
        level = 1
        minefield = create_minefield(level)
        expected_count = calculate_mine_count(level)
        assert len(minefield.mines) == expected_count, (
            f"Level {level} should have {expected_count} mines"
        )

    def test_create_minefield_mines_are_frozen_set(self):
        level = 1
        minefield = create_minefield(level)
        assert isinstance(minefield.mines, frozenset), (
            "Mines should be stored as frozenset"
        )

    def test_create_minefield_different_levels_different_mine_counts(self):
        minefield_1 = create_minefield(1)
        minefield_5 = create_minefield(5)
        assert len(minefield_1.mines) < len(minefield_5.mines), (
            "Higher levels should have more mines"
        )

    def test_create_minefield_uses_valid_positions(self):
        level = 1
        minefield = create_minefield(level)
        forbidden = get_forbidden_positions()
        for mine_pos in minefield.mines:
            assert mine_pos not in forbidden, (
                f"Mine at {mine_pos} should not be in forbidden zone"
            )

    @pytest.mark.parametrize("level", [1, 2, 5, 10])
    def test_create_minefield_for_multiple_levels(self, level):
        minefield = create_minefield(level)
        expected_count = calculate_mine_count(level)
        assert len(minefield.mines) == expected_count, (
            f"Level {level} should have {expected_count} mines"
        )
        assert minefield.width == PLAYABLE_WIDTH, (
            f"Level {level} minefield should have correct width"
        )
        assert minefield.height == PLAYABLE_HEIGHT, (
            f"Level {level} minefield should have correct height"
        )


class TestMinefieldHasMineAt:
    def test_has_mine_at_returns_true_for_mine_positions(self):
        mine_positions = [Position(5, 5), Position(10, 10), Position(15, 15)]
        minefield = Minefield(
            width=PLAYABLE_WIDTH,
            height=PLAYABLE_HEIGHT,
            mines=frozenset(mine_positions),
        )
        for pos in mine_positions:
            assert minefield.has_mine_at(pos), f"Should detect mine at position {pos}"

    def test_has_mine_at_returns_false_for_empty_positions(self):
        mine_positions = [Position(5, 5), Position(10, 10)]
        minefield = Minefield(
            width=PLAYABLE_WIDTH,
            height=PLAYABLE_HEIGHT,
            mines=frozenset(mine_positions),
        )
        empty_pos = Position(20, 20)
        assert not minefield.has_mine_at(empty_pos), (
            f"Should not detect mine at empty position {empty_pos}"
        )
