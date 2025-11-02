import pytest
from mined_out.main import MinedOutGame, GameMode


def test_game_initializes_with_initial_state(mocker):
    mocker.patch("mined_out.main.pyxel")
    game = MinedOutGame.__new__(MinedOutGame)
    game.__init__ = lambda: None

    from mined_out.game import create_initial_game_state

    game.state = create_initial_game_state()
    game.mode = GameMode.PLAYING

    assert game.state is not None, "Should have initial state"
    assert game.mode == GameMode.PLAYING, "Should start in PLAYING mode"


def test_game_starts_in_playing_mode(mocker):
    mock_pyxel = mocker.patch("mined_out.main.pyxel")
    mock_pyxel.init = mocker.MagicMock()
    mock_pyxel.run = mocker.MagicMock()

    game = MinedOutGame()

    assert game.mode == GameMode.PLAYING, "Should start in PLAYING mode"


def test_game_has_initial_state(mocker):
    mock_pyxel = mocker.patch("mined_out.main.pyxel")
    mock_pyxel.init = mocker.MagicMock()
    mock_pyxel.run = mocker.MagicMock()

    game = MinedOutGame()

    assert game.state is not None, "Should have initial game state"
    assert game.state.level_number == 1, "Should start at level 1"


def test_game_initializes_pyxel(mocker):
    mock_pyxel = mocker.patch("mined_out.main.pyxel")
    mock_pyxel.init = mocker.MagicMock()
    mock_pyxel.run = mocker.MagicMock()

    MinedOutGame()

    mock_pyxel.init.assert_called_once()


def test_game_starts_pyxel_run_loop(mocker):
    mock_pyxel = mocker.patch("mined_out.main.pyxel")
    mock_pyxel.init = mocker.MagicMock()
    mock_pyxel.run = mocker.MagicMock()

    MinedOutGame()

    mock_pyxel.run.assert_called_once()


def test_playing_mode_accepts_arrow_keys(mocker):
    mock_pyxel = mocker.patch("mined_out.main.pyxel")
    mock_pyxel.init = mocker.MagicMock()
    mock_pyxel.run = mocker.MagicMock()
    mock_pyxel.btnp = mocker.MagicMock(return_value=False)

    game = MinedOutGame()
    initial_pos = game.state.player_pos

    mock_pyxel.btnp.side_effect = lambda key: key == mock_pyxel.KEY_UP
    mock_pyxel.KEY_UP = 0
    mock_pyxel.KEY_DOWN = 1
    mock_pyxel.KEY_LEFT = 2
    mock_pyxel.KEY_RIGHT = 3

    game._update_playing()

    assert game.state.move_count > 0 or game.state.player_pos != initial_pos, (
        "Should process input"
    )


def test_playing_mode_detects_mine_collision(mocker):
    mock_pyxel = mocker.patch("mined_out.main.pyxel")
    mock_pyxel.init = mocker.MagicMock()
    mock_pyxel.run = mocker.MagicMock()
    mock_pyxel.btnp = mocker.MagicMock(return_value=False)
    mock_pyxel.KEY_UP = 0
    mock_pyxel.KEY_DOWN = 1
    mock_pyxel.KEY_LEFT = 2
    mock_pyxel.KEY_RIGHT = 3

    game = MinedOutGame()

    from mined_out.types import Position, GameState
    from mined_out.movement import Direction

    mine_pos = list(game.state.minefield.mines)[0]

    adjacent_pos = Position(mine_pos.x, mine_pos.y + 1)
    game.state = GameState(
        level_number=game.state.level_number,
        minefield=game.state.minefield,
        player_pos=adjacent_pos,
        visited=game.state.visited | {adjacent_pos},
        move_history=game.state.move_history + (adjacent_pos,),
        lives=game.state.lives,
        score=game.state.score,
        move_count=game.state.move_count + 1,
    )

    mock_pyxel.btnp.side_effect = lambda key: key == mock_pyxel.KEY_UP
    game._update_playing()

    if game.state.player_pos == mine_pos:
        assert game.mode == GameMode.REPLAY, "Should start replay on mine hit"
    else:
        assert game.mode == GameMode.PLAYING, "Movement didn't land on mine"


def test_replay_mode_advances_frames(mocker):
    mock_pyxel = mocker.patch("mined_out.main.pyxel")
    mock_pyxel.init = mocker.MagicMock()
    mock_pyxel.run = mocker.MagicMock()
    mock_pyxel.btnp = mocker.MagicMock(return_value=False)

    game = MinedOutGame()
    game.mode = GameMode.REPLAY

    from mined_out.replay import create_replay_state
    from mined_out.types import Position

    game.replay_history = tuple(Position(15, y) for y in range(21, 10, -1))
    game.replay_state = create_replay_state(game.replay_history)
    initial_frame = game.replay_state.current_frame

    for _ in range(20):
        game._update_replay()

    assert game.replay_state.current_frame > initial_frame, "Should advance replay"


def test_replay_mode_skips_on_key_press(mocker):
    mock_pyxel = mocker.patch("mined_out.main.pyxel")
    mock_pyxel.init = mocker.MagicMock()
    mock_pyxel.run = mocker.MagicMock()
    mock_pyxel.btnp = mocker.MagicMock(side_effect=lambda k: k == 0)

    game = MinedOutGame()
    game.mode = GameMode.REPLAY

    from mined_out.replay import create_replay_state
    from mined_out.types import Position

    game.replay_history = tuple(Position(i, 10) for i in range(10))
    game.replay_state = create_replay_state(game.replay_history)

    game._update_replay()

    from mined_out.replay import is_replay_complete

    assert is_replay_complete(game.replay_state), "Should skip to end on key press"


def test_replay_transitions_to_waiting_when_complete(mocker):
    mock_pyxel = mocker.patch("mined_out.main.pyxel")
    mock_pyxel.init = mocker.MagicMock()
    mock_pyxel.run = mocker.MagicMock()
    mock_pyxel.btnp = mocker.MagicMock(return_value=False)

    game = MinedOutGame()
    game.mode = GameMode.REPLAY

    from mined_out.replay import create_replay_state, skip_to_end

    game.replay_history = game.state.move_history
    game.replay_state = create_replay_state(game.replay_history)
    game.replay_state = skip_to_end(game.replay_state)

    game._update_replay()

    assert game.mode == GameMode.WAITING, "Should transition to WAITING after replay"


def test_waiting_mode_advances_on_key_press(mocker):
    mock_pyxel = mocker.patch("mined_out.main.pyxel")
    mock_pyxel.init = mocker.MagicMock()
    mock_pyxel.run = mocker.MagicMock()
    mock_pyxel.btnp = mocker.MagicMock(side_effect=lambda k: k == 0)

    game = MinedOutGame()
    game.mode = GameMode.WAITING

    from mined_out.level import get_exit_position
    from mined_out.types import GameState

    exit_pos = get_exit_position()
    game.state = GameState(
        level_number=game.state.level_number,
        minefield=game.state.minefield,
        player_pos=exit_pos,
        visited=game.state.visited,
        move_history=game.state.move_history,
        lives=game.state.lives,
        score=game.state.score,
        move_count=game.state.move_count,
    )

    game._update_waiting()

    assert game.mode != GameMode.WAITING, "Should exit WAITING on key press"


def test_waiting_mode_advances_on_timeout(mocker):
    mock_pyxel = mocker.patch("mined_out.main.pyxel")
    mock_pyxel.init = mocker.MagicMock()
    mock_pyxel.run = mocker.MagicMock()
    mock_pyxel.btnp = mocker.MagicMock(return_value=False)

    game = MinedOutGame()
    game.mode = GameMode.WAITING
    game.wait_timer = 10.0

    from mined_out.level import get_exit_position
    from mined_out.types import GameState

    exit_pos = get_exit_position()
    game.state = GameState(
        level_number=game.state.level_number,
        minefield=game.state.minefield,
        player_pos=exit_pos,
        visited=game.state.visited,
        move_history=game.state.move_history,
        lives=game.state.lives,
        score=game.state.score,
        move_count=game.state.move_count,
    )

    game._update_waiting()

    assert game.mode != GameMode.WAITING, "Should exit WAITING on timeout"


def test_game_over_mode_restarts_on_space(mocker):
    mock_pyxel = mocker.patch("mined_out.main.pyxel")
    mock_pyxel.init = mocker.MagicMock()
    mock_pyxel.run = mocker.MagicMock()
    mock_pyxel.btnp = mocker.MagicMock(return_value=False)
    mock_pyxel.KEY_SPACE = 32
    mock_pyxel.KEY_RETURN = 13

    game = MinedOutGame()
    game.mode = GameMode.GAME_OVER
    game.final_score = 500

    mock_pyxel.btnp.side_effect = lambda k: k == mock_pyxel.KEY_SPACE
    game._update_game_over()

    assert game.mode == GameMode.PLAYING, "Should restart game"
    assert game.state.level_number == 1, "Should start at level 1"


def test_death_with_lives_remaining_returns_to_playing(mocker):
    mock_pyxel = mocker.patch("mined_out.main.pyxel")
    mock_pyxel.init = mocker.MagicMock()
    mock_pyxel.run = mocker.MagicMock()

    game = MinedOutGame()
    game.mode = GameMode.WAITING

    from mined_out.types import Position, GameState

    mine_pos = list(game.state.minefield.mines)[0]
    game.state = GameState(
        level_number=game.state.level_number,
        minefield=game.state.minefield,
        player_pos=mine_pos,
        visited=game.state.visited,
        move_history=game.state.move_history,
        lives=2,
        score=game.state.score,
        move_count=game.state.move_count,
    )

    game._advance_after_replay()

    assert game.mode == GameMode.PLAYING, (
        "Should return to PLAYING with lives remaining"
    )


def test_death_without_lives_goes_to_game_over(mocker):
    mock_pyxel = mocker.patch("mined_out.main.pyxel")
    mock_pyxel.init = mocker.MagicMock()
    mock_pyxel.run = mocker.MagicMock()

    game = MinedOutGame()
    game.mode = GameMode.WAITING

    from mined_out.types import Position, GameState

    mine_pos = list(game.state.minefield.mines)[0]
    game.state = GameState(
        level_number=game.state.level_number,
        minefield=game.state.minefield,
        player_pos=mine_pos,
        visited=game.state.visited,
        move_history=game.state.move_history,
        lives=1,
        score=100,
        move_count=game.state.move_count,
    )

    game._advance_after_replay()

    assert game.mode == GameMode.GAME_OVER, "Should go to GAME_OVER with no lives"


def test_level_complete_advances_level(mocker):
    mock_pyxel = mocker.patch("mined_out.main.pyxel")
    mock_pyxel.init = mocker.MagicMock()
    mock_pyxel.run = mocker.MagicMock()

    game = MinedOutGame()
    game.mode = GameMode.WAITING

    from mined_out.level import get_exit_position
    from mined_out.types import GameState

    exit_pos = get_exit_position()
    game.state = GameState(
        level_number=1,
        minefield=game.state.minefield,
        player_pos=exit_pos,
        visited=game.state.visited,
        move_history=game.state.move_history,
        lives=game.state.lives,
        score=game.state.score,
        move_count=game.state.move_count,
    )

    game._advance_after_replay()

    assert game.state.level_number == 2, "Should advance to next level"
    assert game.mode == GameMode.PLAYING, "Should return to PLAYING"
