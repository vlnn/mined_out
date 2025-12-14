import pytest
from mined_out.types import Position, GameState, Minefield
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
    COLOR_GREEN,
    COLOR_RED,
    COLOR_WHITE,
    COLOR_DARK_GRAY,
    COLOR_LIGHT_GRAY,
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
    draw_entry_door,
    draw_exit_door,
    draw_path_line,
    draw_path_marker,
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

    # Player sprite now draws multiple rectangles for head, body, arms, legs
    assert mock_rect.call_count >= 6, "Should draw multiple rectangles for player sprite"


def test_draw_player_uses_player_color(mocker):
    mock_rect = mocker.patch("mined_out.renderer.pyxel.rect")

    draw_player(Position(10, 10))

    args = mock_rect.call_args[0]
    assert args[4] == PLAYER_COLOR, "Should use PLAYER_COLOR"


def test_draw_mine_calls_pyxel_circ(mocker):
    mock_circ = mocker.patch("mined_out.renderer.pyxel.circ")
    mock_rect = mocker.patch("mined_out.renderer.pyxel.rect")

    draw_mine(Position(10, 10))

    mock_circ.assert_called_once()
    # Mine now also draws spike rectangles
    assert mock_rect.call_count >= 8, "Should draw mine center and spikes"


def test_draw_mine_uses_mine_color(mocker):
    mock_circ = mocker.patch("mined_out.renderer.pyxel.circ")
    mock_rect = mocker.patch("mined_out.renderer.pyxel.rect")

    draw_mine(Position(5, 5))

    args = mock_circ.call_args[0]
    assert args[3] == MINE_COLOR, "Should use MINE_COLOR"


def test_draw_status_bar_calls_pyxel_text(mocker):
    mock_text = mocker.patch("mined_out.renderer.pyxel.text")
    mock_rect = mocker.patch("mined_out.renderer.pyxel.rect")
    from mined_out.game import create_initial_game_state

    state = create_initial_game_state()
    draw_status_bar(state, proximity=2)

    assert mock_text.call_count >= 4, "Should draw multiple status elements"
    mock_rect.assert_called_once(), "Should draw status bar background"


def test_draw_status_bar_shows_level(mocker):
    mock_text = mocker.patch("mined_out.renderer.pyxel.text")
    mock_rect = mocker.patch("mined_out.renderer.pyxel.rect")
    from mined_out.game import create_initial_game_state

    state = create_initial_game_state()
    draw_status_bar(state, proximity=0)

    level_calls = [
        call for call in mock_text.call_args_list if "L" in str(call[0][2]) and len(call[0][2]) <= 4
    ]
    assert len(level_calls) > 0, "Should display level"


def test_draw_status_bar_shows_score(mocker):
    mock_text = mocker.patch("mined_out.renderer.pyxel.text")
    mock_rect = mocker.patch("mined_out.renderer.pyxel.rect")
    from mined_out.game import create_initial_game_state

    state = create_initial_game_state()
    draw_status_bar(state, proximity=0)

    score_calls = [
        call for call in mock_text.call_args_list if "S:" in str(call[0][2])
    ]
    assert len(score_calls) > 0, "Should display score"


def test_draw_status_bar_shows_lives(mocker):
    mock_text = mocker.patch("mined_out.renderer.pyxel.text")
    mock_rect = mocker.patch("mined_out.renderer.pyxel.rect")
    from mined_out.game import create_initial_game_state

    state = create_initial_game_state()
    draw_status_bar(state, proximity=0)

    lives_calls = [
        call
        for call in mock_text.call_args_list
        if "LIVES" in str(call[0][2]).upper()
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
    mocker.patch("mined_out.renderer.pyxel.line")
    mock_draw_mine = mocker.patch("mined_out.renderer.draw_mine")
    from mined_out.game import create_initial_game_state

    state = create_initial_game_state()
    draw_game_state(state, show_mines=False)

    mock_draw_mine.assert_not_called()





def test_draw_entry_door_calls_pyxel_rect(mocker):
    mock_rect = mocker.patch("mined_out.renderer.pyxel.rect")

    draw_entry_door()

    # Should draw green door tiles
    green_calls = [call for call in mock_rect.call_args_list if call[0][4] == COLOR_GREEN]
    assert len(green_calls) >= 2, "Should draw multiple green door tiles"


def test_draw_exit_door_calls_pyxel_rect(mocker):
    mock_rect = mocker.patch("mined_out.renderer.pyxel.rect")

    draw_exit_door()

    # Should draw red door tiles
    red_calls = [call for call in mock_rect.call_args_list if call[0][4] == COLOR_RED]
    assert len(red_calls) >= 2, "Should draw multiple red door tiles"


def test_draw_entry_door_uses_green_color(mocker):
    mock_rect = mocker.patch("mined_out.renderer.pyxel.rect")

    draw_entry_door()

    # Check that green color is used for door tiles
    green_calls = [call for call in mock_rect.call_args_list if call[0][4] == COLOR_GREEN]
    assert len(green_calls) > 0, "Should use green color for entry door"


def test_draw_exit_door_uses_red_color(mocker):
    mock_rect = mocker.patch("mined_out.renderer.pyxel.rect")

    draw_exit_door()

    # Check that red color is used for door tiles
    red_calls = [call for call in mock_rect.call_args_list if call[0][4] == COLOR_RED]
    assert len(red_calls) > 0, "Should use red color for exit door"


def test_draw_game_state_shows_proximity_number_when_mines_nearby(mocker):
    mock_rect = mocker.patch("mined_out.renderer.pyxel.rect")
    mock_line = mocker.patch("mined_out.renderer.pyxel.line")
    mock_circ = mocker.patch("mined_out.renderer.pyxel.circ")
    mock_text = mocker.patch("mined_out.renderer.pyxel.text")
    mock_cls = mocker.patch("mined_out.renderer.pyxel.cls")
    from mined_out.game import create_initial_game_state
    from mined_out.types import Position, Minefield

    state = create_initial_game_state()
    # Create a state with mines near player
    nearby_mine = Position(state.player_pos.x + 1, state.player_pos.y)
    state = GameState(
        level_number=state.level_number,
        minefield=Minefield(width=30, height=20, mines=frozenset([nearby_mine])),
        player_pos=state.player_pos,
        visited=state.visited,
        move_history=state.move_history,
        lives=state.lives,
        score=state.score,
        move_count=state.move_count,
    )

    draw_game_state(state)

    # Should draw proximity number when mines are nearby
    proximity_calls = [call for call in mock_text.call_args_list if call[0][2].isdigit()]
    assert len(proximity_calls) > 0, "Should display proximity number when mines are nearby"


def test_draw_game_state_does_not_show_proximity_when_no_mines_nearby(mocker):
    mock_rect = mocker.patch("mined_out.renderer.pyxel.rect")
    mock_line = mocker.patch("mined_out.renderer.pyxel.line")
    mock_circ = mocker.patch("mined_out.renderer.pyxel.circ")
    mock_text = mocker.patch("mined_out.renderer.pyxel.text")
    mock_cls = mocker.patch("mined_out.renderer.pyxel.cls")
    from mined_out.game import create_initial_game_state

    state = create_initial_game_state()
    draw_game_state(state)

    # Should not draw proximity number when no mines are nearby (start position)
    proximity_calls = [call for call in mock_text.call_args_list if call[0][2].isdigit() and len(call[0][2]) == 1]
    assert len(proximity_calls) == 0, "Should not display proximity number when no mines nearby"


def test_draw_tile_with_texture_adds_texture_dot(mocker):
    mock_rect = mocker.patch("mined_out.renderer.pyxel.rect")

    draw_tile(Position(5, 5), COLOR_WHITE, add_texture=True)

    # Should draw main tile and texture dot
    assert mock_rect.call_count == 2, "Should draw tile and texture"
    
    # Check that texture dot uses dark gray color
    texture_calls = [call for call in mock_rect.call_args_list if call[0][4] == COLOR_DARK_GRAY]
    assert len(texture_calls) == 1, "Should draw one texture dot"


def test_draw_tile_without_texture_no_extra_calls(mocker):
    mock_rect = mocker.patch("mined_out.renderer.pyxel.rect")

    draw_tile(Position(5, 5), COLOR_WHITE, add_texture=False)

    # Should draw only main tile
    assert mock_rect.call_count == 1, "Should draw only tile when no texture"


def test_wall_with_texture_uses_brick_pattern(mocker):
    mock_rect = mocker.patch("mined_out.renderer.pyxel.rect")

    draw_wall()

    # Should draw wall tiles and texture bricks
    dark_gray_calls = [call for call in mock_rect.call_args_list if call[0][4] == COLOR_DARK_GRAY]
    assert len(dark_gray_calls) >= 10, "Should draw multiple brick texture dots"


def test_draw_path_line_uses_light_color(mocker):
    mock_line = mocker.patch("mined_out.renderer.pyxel.line")
    mock_rect = mocker.patch("mined_out.renderer.pyxel.rect")

    draw_path_line(Position(5, 5), Position(6, 5))

    # Should draw light gray line for path
    args = mock_line.call_args[0]
    assert args[4] == COLOR_LIGHT_GRAY, "Should use light gray for path"


def test_draw_path_line_draws_feet_markers(mocker):
    mock_line = mocker.patch("mined_out.renderer.pyxel.line")
    mock_rect = mocker.patch("mined_out.renderer.pyxel.rect")

    draw_path_line(Position(5, 5), Position(6, 5))

    # Should draw feet markers (two small rectangles per position)
    light_gray_calls = [call for call in mock_rect.call_args_list if call[0][4] == COLOR_LIGHT_GRAY]
    assert len(light_gray_calls) >= 4, "Should draw at least 4 feet rectangles (2 per position)"


def test_draw_path_marker_draws_feet(mocker):
    mock_rect = mocker.patch("mined_out.renderer.pyxel.rect")

    draw_path_marker(Position(5, 5))

    # Should draw two small rectangles for feet
    assert mock_rect.call_count == 2, "Should draw exactly 2 foot rectangles"
    
    # Check both feet use light gray color
    for call in mock_rect.call_args_list:
        assert call[0][4] == COLOR_LIGHT_GRAY, "Both feet should use light gray color"


def test_draw_path_marker_positions_feet_correctly(mocker):
    mock_rect = mocker.patch("mined_out.renderer.pyxel.rect")

    draw_path_marker(Position(10, 10))

    # Check foot positions within tile bounds
    calls = mock_rect.call_args_list
    
    # Left foot should be at x+1, y+5
    left_foot = calls[0][0]
    assert left_foot[0] == 81, "Left foot x position should be x*8 + 1"
    assert left_foot[1] == 85, "Left foot y position should be y*8 + 5"
    assert left_foot[2] == 2, "Left foot should be 2 pixels wide"
    assert left_foot[3] == 1, "Left foot should be 1 pixel tall"
    
    # Right foot should be at x+5, y+5  
    right_foot = calls[1][0]
    assert right_foot[0] == 85, "Right foot x position should be x*8 + 5"
    assert right_foot[1] == 85, "Right foot y position should be y*8 + 5"
    assert right_foot[2] == 2, "Right foot should be 2 pixels wide"
    assert right_foot[3] == 1, "Right foot should be 1 pixel tall"
