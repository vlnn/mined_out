# AGENTS.md

## Build/Test Commands
- **Run all tests**: `uv run pytest`  
- **Run single test**: `uv run pytest tests/test_game.py::test_create_initial_game_state_has_correct_level`
- **Run tests with coverage**: `uv run pytest --cov=mined_out`
- **Run game**: `uv run mined_out`

## Code Style Guidelines
- **Imports**: Group standard library, third-party, and local imports. Use absolute imports for local modules.
- **Types**: Use type hints consistently. Frozen dataclasses for immutable state. Optional[T] for nullable fields.
- **Naming**: snake_case for functions/variables, PascalCase for classes, UPPER_CASE for constants.
- **Error Handling**: Return None for failure states in game logic. Use assertions in tests.
- **Structure**: Functional programming style - pure functions transform immutable state objects.
- **Testing**: Comprehensive parametrized tests. One assertion per test function where possible.
- **Logging**: Use loguru for all logging. Use structured logging with placeholders (`logger.debug("Message {}", var)`) instead of f-strings. Use appropriate log levels (debug, info, warning, error).