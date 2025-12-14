# Architecture Overview

## Project Structure

Mined-Out is a retro puzzle game port implemented using functional programming principles with immutable state management. The architecture follows a clean separation of concerns with each module handling a specific domain.

## Core Architecture Principles

### Functional Programming with Immutable State
- **Frozen Dataclasses**: All state objects use `@dataclass(frozen=True)` to ensure immutability
- **Pure Functions**: Game logic functions transform state objects without side effects
- **State Transitions**: Game state changes return new state objects rather than mutating existing ones

### Modular Design
- **Single Responsibility**: Each module handles one specific domain (movement, rendering, scoring, etc.)
- **Loose Coupling**: Modules communicate through well-defined interfaces and data structures
- **High Cohesion**: Related functionality is grouped together

## Module Architecture

### Core Data Layer (`types.py`)
```python
@dataclass(frozen=True)
class GameState:
    level_number: int
    minefield: Minefield
    player_pos: Position
    visited: FrozenSet[Position]
    move_history: Tuple[Position, ...]
    lives: int
    score: int
    move_count: int
    is_replay: bool = False
```

### Game Logic Layer (`game.py`)
- **State Management**: Core game state transitions and initialization
- **Player Actions**: Movement, death handling, level completion
- **Game Flow**: Manages transitions between playing, replay, waiting, game over

### Movement System (`movement.py`)
- **Direction Handling**: Cardinal directions with position offsets
- **Position Validation**: Boundary checking and movement validation
- **Next Position Calculation**: Pure functions for position math

### Level Generation (`level.py`, `minefield.py`)
- **Procedural Generation**: Creates solvable minefields
- **Pathfinding Validation**: Ensures every level has a solution
- **Difficulty Scaling**: Progressive mine density with level advancement

### Rendering System (`renderer.py`)
- **Pixel-Perfect Drawing**: Tile-based rendering with Pyxel
- **Visual Feedback**: Player sprites, mine graphics, path visualization
- **UI Elements**: Status bar, transient messages, door graphics

### Input Handling (`main.py`)
- **Game Loop**: Pyxel's update/draw cycle
- **Input Processing**: Keyboard input with mode-specific handling
- **State Machine**: Manages game modes (playing, replay, waiting, game over)

## Data Flow

```
Input → Game Logic → State Update → Rendering → Display
  ↓           ↓              ↓           ↓
Keyboard → move_player() → GameState → draw_game_state() → Screen
```

### State Transformation Pipeline
1. **Input Capture**: Raw keyboard input
2. **Action Processing**: Convert to game actions (movement, menu navigation)
3. **State Transition**: Apply action to current state → new state
4. **Collision Detection**: Check for mines, exit, boundaries
5. **Game Logic**: Handle death, level completion, scoring
6. **Render Preparation**: Prepare visual representation
7. **Display Output**: Draw to screen via Pyxel

## Key Design Patterns

### Command Pattern
- **Game Actions**: Movement, death, level completion as commands
- **Replay System**: Recorded moves as replayable command sequence
- **State Restoration**: Replay system restores exact game states

### Strategy Pattern
- **Level Generation**: Different strategies for minefield generation
- **Pathfinding**: BFS algorithm for solvability validation
- **Scoring**: Configurable scoring strategies per level

### Observer Pattern
- **Rendering Pipeline**: State changes trigger visual updates
- **UI Updates**: Status bar reflects current game state
- **Event System**: Game events (death, completion) trigger appropriate responses

## Performance Considerations

### Efficient Data Structures
- **Frozen Sets**: O(1) membership tests for visited positions
- **Tuples**: Immutable move history for memory efficiency
- **Position Objects**: Cached coordinate calculations

### Rendering Optimization
- **Dirty Rectangle**: Only redraw changed portions when possible
- **Tile Caching**: Pre-computed tile positions
- **Batch Drawing**: Group similar drawing operations

## Testing Architecture

### Unit Testing
- **Pure Function Testing**: Each game logic function tested independently
- **State Validation**: Verify state transitions maintain invariants
- **Edge Case Coverage**: Boundary conditions, error states

### Integration Testing
- **Game Flow Testing**: Complete gameplay scenarios
- **Rendering Testing**: Visual output verification with mocks
- **Performance Testing**: Frame rate and memory usage validation

### Test Organization
```
tests/
├── test_game.py      # Core game logic
├── test_movement.py  # Movement and position
├── test_level.py    # Level generation
├── test_renderer.py  # Visual rendering
├── test_scoring.py  # Score calculation
└── test_*.py       # Other domain-specific tests
```

## Technology Stack

### Core Framework
- **Pyxel**: Retro game engine with 16-color palette, 4-channel audio
- **Python 3.13+**: Modern Python with type hints
- **UV**: Fast Python package manager

### Development Tools
- **pytest**: Testing framework with mocking support
- **loguru**: Structured logging with performance optimization
- **hatchling**: Modern Python build backend

## Configuration Management

### Game Configuration (`config.py`)
- **Screen Dimensions**: Tile-based layout (32x24 tiles, 8px tiles)
- **Color Palette**: ZX Spectrum-inspired retro colors
- **Game Balance**: Mine density, scoring multipliers, lives

### Level Progression
- **Dynamic Difficulty**: Mine density increases with level
- **Feature Introduction**: New mechanics at specific levels
- **Score Scaling**: Exponential scoring for higher levels

## Extensibility

### Modular Expansion Points
- **New Game Modes**: Add new game states in `main.py`
- **Additional Mechanics**: Extend game logic in `game.py`
- **Visual Themes**: Modify rendering in `renderer.py`
- **Level Types**: Extend generation in `level.py`

### Plugin Architecture
- **Component System**: Graphics and logic as interchangeable components
- **Event Bus**: Decoupled communication between systems
- **Resource Loading**: External assets and configuration

## Security and Reliability

### Error Handling
- **Graceful Degradation**: Continue gameplay despite non-critical errors
- **State Validation**: Ensure game state consistency
- **Recovery Mechanisms**: Handle corrupted save files, network issues

### Performance Monitoring
- **Frame Rate Tracking**: Maintain consistent 60 FPS
- **Memory Profiling**: Monitor for memory leaks
- **Logging**: Structured logging for debugging and analytics

## Future Architecture Considerations

### Scalability
- **Network Play**: Multiplayer support with state synchronization
- **Level Editor**: Built-in level creation and sharing
- **Mod Support**: Community content integration

### Code Evolution
- **Type Safety**: Gradual migration to stricter typing
- **Async Support**: Non-blocking I/O for network features
- **Caching**: Strategic caching for performance optimization

This architecture provides a solid foundation for the retro Mined-Out game while maintaining clean, testable, and extensible code that follows modern Python best practices.