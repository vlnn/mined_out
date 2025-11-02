import pytest
from mined_out.types import Position
from mined_out.config import (
    TILE_SIZE,
    SCREEN_WIDTH_TILES,
    SCREEN_HEIGHT_TILES,
    STATUS_BAR_ROW,
    TOP_WALL_ROW,
    BOTTOM_WALL_ROW,
    TRANSIENT_INFO_ROW,
    WALL_COLOR,
    PLAYER_COLOR,
    MINE_COLOR,
)
from mined_out.renderer import (
    position_to_pixel,
    draw_tile,
    draw_wall,
    draw_player,
    draw_mine,
    draw_status_bar,
    draw_transient_info,
    draw_game_state,
)


@pytest.mark.parametrize(
    "position,expected_x,expected_y",
    [
        (Position(0, 0), 0, 0),
        (Position(1, 0), 8, 0),
        (Position(0, 1), 0, 8),
        (Position(5, 10), 40, 80),
        (Position(15, 21), 120, 168),
    ],
)
def test_position_to_pixel_converts_correctly(position, expected_x, expected_y):
    x, y = position_to_pixel(position)
    assert x == expected_x, f"X coordinate should be {expected_x}"
    assert y == expected_y, f"Y coordinate should be {expected_y}"


def test_position_to_pixel_uses_tile_size():
    pos = Position(1, 1)
    x, y = position_to_pixel(pos)
    assert x == TILE_SIZE, f"X should be {TILE_SIZE}"
    assert y == TILE_SIZE, f"Y should be {TILE_SIZE}"


def test_draw_tile_calls_pyxel_rect(mocker):
    mock_rect = mocker.patch("mined_out.renderer.pyxel.rect")

    draw_tile(Position(5, 10), color=7)

    mock_rect.assert_called_once_with(40, 80, TILE_SIZE, TILE_SIZE, 7)


def test_draw_tile_uses_correct_color(mocker):
    mock_rect = mocker.patch("mined_out.renderer.pyxel.rect")

    draw_tile(Position(0, 0), color=11)

    args = mock_rect.call_args[0]
    assert args[4] == 11, "Should use specified color"


def test_draw_wall_draws_horizontal_line(mocker):
    mock_rect = mocker.patch("mined_out.renderer.pyxel.rect")

    draw_wall()

    top_wall_calls = [
        call
        for call in mock_rect.call_args_list
        if call[0][1] == TOP_WALL_ROW * TILE_SIZE
    ]
    assert len(top_wall_calls) > 0, "Should draw top wall"

    bottom_wall_calls = [
        call
        for call in mock_rect.call_args_list
        if call[0][1] == BOTTOM_WALL_ROW * TILE_SIZE
    ]
    assert len(bottom_wall_calls) > 0, "Should draw bottom wall"


def test_draw_wall_uses_wall_color(mocker):
    mock_rect = mocker.patch("mined_out.renderer.pyxel.rect")

    draw_wall()

    for call in mock_rect.call_args_list:
        assert call[0][4] == WALL_COLOR, "Should use WALL_COLOR"


def test_draw_player_calls_pyxel_rect(mocker):
    mock_rect = mocker.patch("mined_out.renderer.pyxel.rect")

    draw_player(Position(15, 21))

    mock_rect.assert_called_once()


def test_draw_player_uses_player_color(mocker):
    mock_rect = mocker.patch("mined_out.renderer.pyxel.rect")

    draw_player(Position(10, 10))

    args = mock_rect.call_args[0]
    assert args[4] == PLAYER_COLOR, "Should use PLAYER_COLOR"


def test_draw_mine_calls_pyxel_circ(mocker):
    mock_circ = mocker.patch("mined_out.renderer.pyxel.circ")

    draw_mine(Position(10, 10))

    mock_circ.assert_called_once()


def test_draw_mine_uses_mine_color(mocker):
    mock_circ = mocker.patch("mined_out.renderer.pyxel.circ")

    draw_mine(Position(5, 5))

    args = mock_circ.call_args[0]
    assert args[2] == MINE_COLOR, "Should use MINE_COLOR"


def test_draw_status_bar_calls_pyxel_text(mocker):
    mock_text = mocker.patch("mined_out.renderer.pyxel.text")
    from mined_out.game import create_initial_game_state

    state = create_initial_game_state()
    draw_status_bar(state, proximity=2)

    assert mock_text.call_count >= 4, "Should draw multiple status elements"


def test_draw_status_bar_shows_level(mocker):
    mock_text = mocker.patch("mined_out.renderer.pyxel.text")
    from mined_out.game import create_initial_game_state

    state = create_initial_game_state()
    draw_status_bar(state, proximity=0)

    level_calls = [
        call for call in mock_text.call_args_list if "LEVEL" in str(call[0][2]).upper()
    ]
    assert len(level_calls) > 0, "Should display level"


def test_draw_status_bar_shows_score(mocker):
    mock_text = mocker.patch("mined_out.renderer.pyxel.text")
    from mined_out.game import create_initial_game_state

    state = create_initial_game_state()
    draw_status_bar(state, proximity=0)

    score_calls = [
        call for call in mock_text.call_args_list if "SCORE" in str(call[0][2]).upper()
    ]
    assert len(score_calls) > 0, "Should display score"


def test_draw_status_bar_shows_lives(mocker):
    mock_text = mocker.patch("mined_out.renderer.pyxel.text")
    from mined_out.game import create_initial_game_state

    state = create_initial_game_state()
    draw_status_bar(state, proximity=0)

    lives_calls = [
        call
        for call in mock_text.call_args_list
        if "LIVES" in str(call[0][2]).upper() or "❤" in str(call[0][2])
    ]
    assert len(lives_calls) > 0, "Should display lives"


def test_draw_transient_info_calls_pyxel_text(mocker):
    mock_text = mocker.patch("mined_out.renderer.pyxel.text")

    draw_transient_info("TEST MESSAGE")

    mock_text.assert_called_once()


def test_draw_transient_info_shows_message(mocker):
    mock_text = mocker.patch("mined_out.renderer.pyxel.text")

    message = "ACTION REPLAY"
    draw_transient_info(message)

    args = mock_text.call_args[0]
    assert message in args[2], "Should display the message"


def test_draw_game_state_draws_walls(mocker):
    mocker.patch("mined_out.renderer.pyxel.cls")
    mocker.patch("mined_out.renderer.pyxel.rect")
    mocker.patch("mined_out.renderer.pyxel.text")
    mocker.patch("mined_out.renderer.pyxel.circ")
    mock_draw_wall = mocker.patch("mined_out.renderer.draw_wall")
    from mined_out.game import create_initial_game_state

    state = create_initial_game_state()
    draw_game_state(state, show_mines=False)

    mock_draw_wall.assert_called_once()


def test_draw_game_state_draws_player(mocker):
    mocker.patch("mined_out.renderer.pyxel.cls")
    mocker.patch("mined_out.renderer.pyxel.rect")
    mocker.patch("mined_out.renderer.pyxel.text")
    mocker.patch("mined_out.renderer.pyxel.circ")
    mock_draw_player = mocker.patch("mined_out.renderer.draw_player")
    from mined_out.game import create_initial_game_state

    state = create_initial_game_state()
    draw_game_state(state, show_mines=False)

    mock_draw_player.assert_called_once_with(state.player_pos)


def test_draw_game_state_draws_status_bar(mocker):
    mocker.patch("mined_out.renderer.pyxel.cls")
    mocker.patch("mined_out.renderer.pyxel.rect")
    mocker.patch("mined_out.renderer.pyxel.text")
    mocker.patch("mined_out.renderer.pyxel.circ")
    mock_draw_status = mocker.patch("mined_out.renderer.draw_status_bar")
    from mined_out.game import create_initial_game_state

    state = create_initial_game_state()
    draw_game_state(state, show_mines=False)

    mock_draw_status.assert_called_once()


def test_draw_game_state_shows_mines_when_requested(mocker):
    mocker.patch("mined_out.renderer.pyxel.cls")
    mocker.patch("mined_out.renderer.pyxel.rect")
    mocker.patch("mined_out.renderer.pyxel.text")
    mocker.patch("mined_out.renderer.pyxel.circ")
    mock_draw_mine = mocker.patch("mined_out.renderer.draw_mine")
    from mined_out.game import create_initial_game_state

    state = create_initial_game_state()
    draw_game_state(state, show_mines=True)

    assert mock_draw_mine.call_count > 0, "Should draw mines when show_mines=True"


def test_draw_game_state_hides_mines_when_not_requested(mocker):
    mocker.patch("mined_out.renderer.pyxel.cls")
    mocker.patch("mined_out.renderer.pyxel.rect")
    mocker.patch("mined_out.renderer.pyxel.text")
    mocker.patch("mined_out.renderer.pyxel.circ")
    mock_draw_mine = mocker.patch("mined_out.renderer.draw_mine")
    from mined_out.game import create_initial_game_state

    state = create_initial_game_state()
    draw_game_state(state, show_mines=False)

    mock_draw_mine.assert_not_called()
