import pytest
from mined_out.types import Position, LevelConfig, Minefield
from mined_out.config import (
    PLAYABLE_WIDTH,
    PLAYABLE_HEIGHT,
    ENTRY_DOOR_COLS,
    EXIT_DOOR_COLS,
    START_POSITION_ROW,
    EXIT_DOOR_ROW,
    COLOR_YELLOW,
    COLOR_ORANGE,
    COLOR_GREEN,
    COLOR_CYAN,
    COLOR_PINK,
)
from mined_out.level import (
    create_level_config,
    generate_level,
    get_level_colors,
    get_start_position,
    get_exit_position,
)
from mined_out.minefield import calculate_mine_count


@pytest.mark.parametrize(
    "level_number,expected_colors",
    [
        (1, (COLOR_YELLOW, COLOR_YELLOW)),
        (2, (COLOR_ORANGE, COLOR_ORANGE)),
        (3, (COLOR_GREEN, COLOR_GREEN)),
        (4, (COLOR_CYAN, COLOR_CYAN)),
        (5, (COLOR_PINK, COLOR_PINK)),
        (6, (COLOR_YELLOW, COLOR_YELLOW)),
    ],
)
def test_get_level_colors_cycles_through_palette(level_number, expected_colors):
    unvisited, visited = get_level_colors(level_number)
    assert (unvisited, visited) == expected_colors, (
        f"Level {level_number} should have colors {expected_colors}"
    )


def test_get_level_colors_returns_different_colors_for_different_levels():
    colors_1 = get_level_colors(1)
    colors_2 = get_level_colors(2)
    assert colors_1 != colors_2, "Different levels should have different colors"


def test_get_start_position_returns_entry_door_position():
    start = get_start_position()
    assert start.y == START_POSITION_ROW, "Start should be at entry door row"
    assert start.x in ENTRY_DOOR_COLS, "Start should be at one of entry door columns"


def test_get_exit_position_returns_exit_door_position():
    exit_pos = get_exit_position()
    assert exit_pos.y == EXIT_DOOR_ROW + 1, "Exit should be just inside exit door"
    assert exit_pos.x in EXIT_DOOR_COLS, "Exit should be at one of exit door columns"


@pytest.mark.parametrize("level_number", [1, 2, 5, 10, 20])
def test_create_level_config_returns_valid_config(level_number):
    config = create_level_config(level_number)
    assert config.level_number == level_number, (
        "Config should have correct level number"
    )
    assert config.width == PLAYABLE_WIDTH, "Config should have correct width"
    assert config.height == PLAYABLE_HEIGHT, "Config should have correct height"
    assert config.mine_count == calculate_mine_count(level_number), (
        "Config should have correct mine count"
    )
    assert config.entry_door_cols == ENTRY_DOOR_COLS, (
        "Config should have entry door cols"
    )
    assert config.exit_door_cols == EXIT_DOOR_COLS, "Config should have exit door cols"


def test_create_level_config_has_valid_colors():
    config = create_level_config(1)
    assert config.unvisited_color >= 0, "Unvisited color should be valid"
    assert config.visited_color >= 0, "Visited color should be valid"


def test_create_level_config_has_valid_start_position():
    config = create_level_config(1)
    assert config.start_position.y == START_POSITION_ROW, (
        "Start position should be at entry"
    )
    assert config.start_position.x in ENTRY_DOOR_COLS, (
        "Start position should be at entry door"
    )


def test_create_level_config_different_levels_different_colors():
    config1 = create_level_config(1)
    config2 = create_level_config(2)
    assert config1.unvisited_color != config2.unvisited_color, (
        "Different levels should have different colors"
    )


@pytest.mark.parametrize("level_number", [1, 2, 5, 10])
def test_generate_level_returns_valid_minefield(level_number):
    minefield = generate_level(level_number)
    assert isinstance(minefield, Minefield), "Should return Minefield instance"
    assert minefield.width == PLAYABLE_WIDTH, "Minefield should have correct width"
    assert minefield.height == PLAYABLE_HEIGHT, "Minefield should have correct height"
    expected_mine_count = calculate_mine_count(level_number)
    assert len(minefield.mines) == expected_mine_count, (
        f"Level {level_number} should have {expected_mine_count} mines"
    )


def test_generate_level_creates_solvable_minefield():
    from mined_out.pathfinding import has_path

    minefield = generate_level(1)
    start = get_start_position()
    exit_pos = get_exit_position()
    assert has_path(start, exit_pos, minefield), "Generated level should be solvable"


def test_generate_level_different_calls_produce_different_minefields():
    minefield1 = generate_level(1)
    minefield2 = generate_level(1)
    assert minefield1.mines != minefield2.mines, (
        "Should generate different mine layouts"
    )


def test_generate_level_retries_until_solvable():
    level_number = 1
    minefield = generate_level(level_number, max_attempts=5)
    from mined_out.pathfinding import has_path

    start = get_start_position()
    exit_pos = get_exit_position()
    assert has_path(start, exit_pos, minefield), (
        "Should eventually generate solvable level"
    )


def test_generate_level_raises_error_if_cannot_generate_solvable(mocker):
    mocker.patch("mined_out.level.has_path", return_value=False)

    with pytest.raises(
        Exception, match="Could not generate solvable level after .* attempts"
    ):
        generate_level(1, max_attempts=3)


@pytest.mark.parametrize("level_number", [1, 5, 10, 15, 20])
def test_generate_level_higher_levels_have_more_mines(level_number):
    minefield = generate_level(level_number)
    expected_count = calculate_mine_count(level_number)
    assert len(minefield.mines) == expected_count, (
        f"Level {level_number} should have {expected_count} mines"
    )


def test_generate_level_respects_max_attempts(mocker):
    call_count = 0

    def mock_has_path(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        return False

    mocker.patch("mined_out.level.has_path", side_effect=mock_has_path)

    max_attempts = 5
    try:
        generate_level(1, max_attempts=max_attempts)
    except Exception:
        pass

    assert call_count == max_attempts, f"Should attempt exactly {max_attempts} times"
