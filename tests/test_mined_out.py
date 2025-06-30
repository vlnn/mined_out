import pytest
from unittest.mock import patch
from mined_out.common import CellType, Direction, Position, Explosion
from mined_out.grid_operations import (
    create_empty_grid, is_valid_position, find_cell_position,
    count_cells_of_type, count_adjacent_mines, has_adjacent_mines,
    is_safe_player_position, can_move_to_cell
)
from mined_out.grid_builder import (
    add_borders_to_grid, calculate_mine_count, calculate_item_count,
    place_random_cells
)
from mined_out.level_generation import create_level_state
from mined_out.game_logic import (
    can_exit_level, should_advance_level, should_win_game,
    move_position
)
from mined_out.game_state import GameState


class TestPositionOperations:
    """Test position-related pure functions."""

    def test_move_position_up(self):
        pos = Position(5, 5)
        new_pos = move_position(pos, Direction.UP)
        assert new_pos == Position(5, 4)

    def test_move_position_down(self):
        pos = Position(5, 5)
        new_pos = move_position(pos, Direction.DOWN)
        assert new_pos == Position(5, 6)

    def test_move_position_left(self):
        pos = Position(5, 5)
        new_pos = move_position(pos, Direction.LEFT)
        assert new_pos == Position(4, 5)

    def test_move_position_right(self):
        pos = Position(5, 5)
        new_pos = move_position(pos, Direction.RIGHT)
        assert new_pos == Position(6, 5)


class TestGridOperations:
    """Test grid-related pure functions."""

    def test_create_empty_grid_dimensions(self):
        grid = create_empty_grid(3, 2)
        assert len(grid) == 2  # height
        assert len(grid[0]) == 3  # width
        assert all(cell == CellType.EMPTY for row in grid for cell in row)

    def test_is_valid_position_within_bounds(self):
        assert is_valid_position(Position(0, 0), 5, 5)
        assert is_valid_position(Position(4, 4), 5, 5)
        assert is_valid_position(Position(2, 3), 5, 5)

    def test_is_valid_position_outside_bounds(self):
        assert not is_valid_position(Position(-1, 0), 5, 5)
        assert not is_valid_position(Position(0, -1), 5, 5)
        assert not is_valid_position(Position(5, 0), 5, 5)
        assert not is_valid_position(Position(0, 5), 5, 5)

    def test_find_cell_position_exists(self):
        grid = create_empty_grid(3, 3)
        grid[1][2] = CellType.PLAYER
        pos = find_cell_position(grid, CellType.PLAYER, 3, 3)
        assert pos == Position(2, 1)

    def test_find_cell_position_not_exists(self):
        grid = create_empty_grid(3, 3)
        pos = find_cell_position(grid, CellType.PLAYER, 3, 3)
        assert pos == Position(1, 1)  # default fallback

    def test_count_cells_of_type_empty_grid(self):
        grid = create_empty_grid(3, 3)
        count = count_cells_of_type(grid, CellType.MINE)
        assert count == 0

    def test_count_cells_of_type_with_mines(self):
        grid = create_empty_grid(3, 3)
        grid[0][0] = CellType.MINE
        grid[1][1] = CellType.MINE
        grid[2][2] = CellType.MINE
        count = count_cells_of_type(grid, CellType.MINE)
        assert count == 3

    def test_count_adjacent_mines_center_position(self):
        grid = create_empty_grid(3, 3)
        grid[0][0] = CellType.MINE  # adjacent
        grid[0][1] = CellType.MINE  # adjacent
        grid[2][2] = CellType.MINE  # adjacent
        grid[1][1] = CellType.PLAYER  # center

        count = count_adjacent_mines(grid, Position(1, 1), 3, 3)
        assert count == 3

    def test_count_adjacent_mines_edge_position(self):
        grid = create_empty_grid(3, 3)
        grid[0][1] = CellType.MINE  # adjacent
        grid[1][1] = CellType.MINE  # adjacent

        count = count_adjacent_mines(grid, Position(0, 0), 3, 3)
        assert count == 2

    def test_has_adjacent_mines_true(self):
        grid = create_empty_grid(3, 3)
        grid[0][1] = CellType.MINE

        assert has_adjacent_mines(grid, Position(0, 0), 3, 3)

    def test_has_adjacent_mines_false(self):
        grid = create_empty_grid(3, 3)

        assert not has_adjacent_mines(grid, Position(1, 1), 3, 3)

    def test_is_safe_player_position_safe(self):
        grid = create_empty_grid(3, 3)

        assert is_safe_player_position(grid, Position(1, 1), 3, 3)

    def test_is_safe_player_position_near_mine(self):
        grid = create_empty_grid(3, 3)
        grid[0][0] = CellType.MINE

        assert not is_safe_player_position(grid, Position(1, 1), 3, 3)

    def test_is_safe_player_position_occupied(self):
        grid = create_empty_grid(3, 3)
        grid[1][1] = CellType.WALL

        assert not is_safe_player_position(grid, Position(1, 1), 3, 3)

    def test_can_move_to_cell_empty(self):
        grid = create_empty_grid(3, 3)

        assert can_move_to_cell(grid, Position(1, 1), 3, 3)

    def test_can_move_to_cell_wall(self):
        grid = create_empty_grid(3, 3)
        grid[1][1] = CellType.WALL

        assert not can_move_to_cell(grid, Position(1, 1), 3, 3)

    def test_can_move_to_cell_mine(self):
        grid = create_empty_grid(3, 3)
        grid[1][1] = CellType.MINE

        assert can_move_to_cell(grid, Position(1, 1), 3, 3)  # Can move to mine (will trigger reveal)

    def test_can_move_to_cell_out_of_bounds(self):
        grid = create_empty_grid(3, 3)

        assert not can_move_to_cell(grid, Position(-1, 0), 3, 3)
        assert not can_move_to_cell(grid, Position(3, 0), 3, 3)


class TestGridBuilder:
    """Test grid building pure functions."""

    def test_add_borders_to_grid(self):
        grid = create_empty_grid(5, 5)
        add_borders_to_grid(grid, 5, 5)

        # Check corners
        assert grid[0][0] == CellType.WALL
        assert grid[0][4] == CellType.WALL
        assert grid[4][0] == CellType.WALL
        assert grid[4][4] == CellType.WALL

        # Check edges
        assert grid[0][2] == CellType.WALL  # top
        assert grid[4][2] == CellType.WALL  # bottom
        assert grid[2][0] == CellType.WALL  # left
        assert grid[2][4] == CellType.WALL  # right

        # Check interior remains empty
        assert grid[2][2] == CellType.EMPTY

    def test_calculate_mine_count_progression(self):
        assert calculate_mine_count(1) == 8   # 5 + 1*3
        assert calculate_mine_count(2) == 11  # 5 + 2*3
        assert calculate_mine_count(5) == 20  # 5 + 5*3
        assert calculate_mine_count(10) == 25 # capped at 25

    def test_calculate_item_count_progression(self):
        assert calculate_item_count(1) == 7   # 8 - 1
        assert calculate_item_count(3) == 5   # 8 - 3
        assert calculate_item_count(6) == 3   # min 3
        assert calculate_item_count(10) == 3  # min 3

    @patch('mined_out.grid_builder.random.randint')
    def test_place_random_cells_success(self, mock_randint):
        grid = create_empty_grid(5, 5)
        add_borders_to_grid(grid, 5, 5)

        # Mock random to always return valid interior positions
        mock_randint.side_effect = [2, 2, 1, 1, 3, 3]  # x, y pairs

        placed = place_random_cells(grid, CellType.MINE, 3, 5, 5)

        assert placed == 3
        assert grid[2][2] == CellType.MINE
        assert grid[1][1] == CellType.MINE
        assert grid[3][3] == CellType.MINE


class TestGameLogic:
    """Test game logic pure functions."""

    def test_can_exit_level_sufficient_items(self):
        assert can_exit_level(5, 5)
        assert can_exit_level(6, 5)

    def test_can_exit_level_insufficient_items(self):
        assert not can_exit_level(4, 5)
        assert not can_exit_level(0, 5)

    def test_should_win_game_final_level(self):
        assert should_win_game(6)  # MAX_LEVEL + 1
        assert should_win_game(10)

    def test_should_win_game_not_final_level(self):
        assert not should_win_game(1)
        assert not should_win_game(5)  # MAX_LEVEL

    def test_should_advance_level_at_exit_with_items(self):
        grid = create_empty_grid(3, 3)
        grid[1][1] = CellType.EXIT

        state = GameState(
            player_pos=Position(1, 1),
            grid=grid,
            items_collected=3,
            total_items=3,
            level=1
        )

        assert should_advance_level(state)

    def test_should_advance_level_at_exit_without_items(self):
        grid = create_empty_grid(3, 3)
        grid[1][1] = CellType.EXIT

        state = GameState(
            player_pos=Position(1, 1),
            grid=grid,
            items_collected=2,
            total_items=3,
            level=1
        )

        assert not should_advance_level(state)

    def test_should_advance_level_not_at_exit(self):
        grid = create_empty_grid(3, 3)
        grid[1][1] = CellType.PLAYER

        state = GameState(
            player_pos=Position(1, 1),
            grid=grid,
            items_collected=3,
            total_items=3,
            level=1
        )

        assert not should_advance_level(state)


class TestLevelGeneration:
    """Test level generation functions."""

    def test_create_level_state_structure(self):
        state = create_level_state(1, 10, 8)

        assert state.level == 1
        assert state.items_collected == 0
        assert state.total_items > 0
        assert not state.game_over
        assert not state.won
        assert len(state.grid) == 8  # height
        assert len(state.grid[0]) == 10  # width

    def test_create_level_state_has_player(self):
        state = create_level_state(1, 10, 8)

        # Should find player in grid
        player_found = False
        for row in state.grid:
            if CellType.PLAYER in row:
                player_found = True
                break

        assert player_found
        assert state.grid[state.player_pos.y][state.player_pos.x] == CellType.PLAYER

    def test_create_level_state_has_borders(self):
        state = create_level_state(1, 10, 8)

        # Check all border positions have walls
        for x in range(10):
            assert state.grid[0][x] == CellType.WALL  # top
            assert state.grid[7][x] == CellType.WALL  # bottom

        for y in range(8):
            assert state.grid[y][0] == CellType.WALL  # left
            assert state.grid[y][9] == CellType.WALL  # right

    def test_create_level_state_has_items_and_mines(self):
        state = create_level_state(2, 10, 8)

        mine_count = count_cells_of_type(state.grid, CellType.MINE)
        item_count = count_cells_of_type(state.grid, CellType.ITEM)

        assert mine_count > 0
        assert item_count > 0
        assert item_count == state.total_items


class TestGameState:
    """Test game state management."""

    def test_game_state_initialization(self):
        grid = create_empty_grid(3, 3)
        state = GameState(
            player_pos=Position(1, 1),
            grid=grid,
            items_collected=0,
            total_items=5,
            level=1
        )

        assert state.player_pos == Position(1, 1)
        assert state.items_collected == 0
        assert state.total_items == 5
        assert state.level == 1
        assert state.mine_count_nearby == 0
        assert not state.game_over
        assert not state.won
        assert state.explosion is None
        assert state.mine_reveal_timer == 0
        assert state.revealing_mine_pos is None

    def test_explosion_dataclass(self):
        pos = Position(5, 5)
        explosion = Explosion(pos)

        assert explosion.pos == pos
        assert explosion.frame == 0

        explosion.frame = 10
        assert explosion.frame == 10


class TestIntegration:
    """Integration tests for complete game scenarios."""

    def test_complete_level_generation_and_validation(self):
        """Test that generated levels are always valid and playable."""
        for level_num in range(1, 6):
            state = create_level_state(level_num, 20, 15)

            # Basic validation
            assert state.level == level_num
            assert state.total_items > 0
            assert 0 <= state.player_pos.x < 20
            assert 0 <= state.player_pos.y < 15

            # Player should exist in grid
            player_count = count_cells_of_type(state.grid, CellType.PLAYER)
            assert player_count == 1, f"Expected 1 player, found {player_count}"

            # Player position should match grid content
            actual_cell = state.grid[state.player_pos.y][state.player_pos.x]
            assert actual_cell == CellType.PLAYER, f"Expected PLAYER at {state.player_pos}, found {actual_cell}"

            # Player should be in safe position (level generation should ensure this)
            # Note: We check this but allow for the possibility that level generation
            # had to remove some mines to make a safe position
            mine_count_near_player = count_adjacent_mines(state.grid, state.player_pos, 20, 15)
            assert mine_count_near_player == 0, f"Player at {state.player_pos} has {mine_count_near_player} adjacent mines"

            # Should have exit
            exit_count = count_cells_of_type(state.grid, CellType.EXIT)
            assert exit_count == 1, f"Expected 1 exit, found {exit_count}"

            # Should have reasonable number of mines (may be less than target due to safety constraints)
            mine_count = count_cells_of_type(state.grid, CellType.MINE)
            expected_mine_count = calculate_mine_count(level_num)
            assert mine_count <= expected_mine_count, f"Too many mines: {mine_count} > {expected_mine_count}"
            assert mine_count > 0, "Should have at least some mines"

    @patch('pyxel.play')
    def test_player_movement_sequence(self, mock_play):
        """Test a sequence of valid player movements."""
        grid = create_empty_grid(5, 5)
        add_borders_to_grid(grid, 5, 5)
        grid[2][2] = CellType.PLAYER
        grid[1][2] = CellType.ITEM
        grid[3][2] = CellType.EXIT

        state = GameState(
            player_pos=Position(2, 2),
            grid=grid,
            items_collected=0,
            total_items=1,
            level=1
        )

        from mined_out.game_logic import move_player_to_position, handle_cell_interaction
        new_pos = move_position(state.player_pos, Direction.UP)
        old_cell = state.grid[new_pos.y][new_pos.x]
        move_player_to_position(state, new_pos, 5, 5)
        handle_cell_interaction(state, old_cell)

        assert state.player_pos == Position(2, 1)
        assert state.items_collected == 1
        assert state.grid[1][2] == CellType.PLAYER  # grid[y][x] not grid[x][y]
        assert state.grid[2][2] == CellType.VISITED

        # Move down twice to reach exit
        new_pos = move_position(state.player_pos, Direction.DOWN)
        move_player_to_position(state, new_pos, 5, 5)

        new_pos = move_position(state.player_pos, Direction.DOWN)
        move_player_to_position(state, new_pos, 5, 5)

        assert state.player_pos == Position(2, 3)
