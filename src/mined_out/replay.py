from typing import Tuple, Optional
from mined_out.types import Position, ReplayState
from mined_out.config import REPLAY_SPEED_MULTIPLIER


def create_replay_state(move_history: Tuple[Position, ...]) -> ReplayState:
    return ReplayState(
        current_frame=0,
        total_frames=len(move_history),
        speed_multiplier=REPLAY_SPEED_MULTIPLIER,
    )


def advance_replay(replay: ReplayState) -> ReplayState:
    next_frame = min(replay.current_frame + 1, replay.total_frames)
    return ReplayState(
        current_frame=next_frame,
        total_frames=replay.total_frames,
        speed_multiplier=replay.speed_multiplier,
    )


def is_replay_complete(replay: ReplayState) -> bool:
    return replay.current_frame >= replay.total_frames


def get_replay_position(
    replay: ReplayState, move_history: Tuple[Position, ...]
) -> Optional[Position]:
    if len(move_history) == 0:
        return None

    frame_index = min(replay.current_frame, len(move_history) - 1)
    return move_history[frame_index]


def skip_to_end(replay: ReplayState) -> ReplayState:
    return ReplayState(
        current_frame=replay.total_frames,
        total_frames=replay.total_frames,
        speed_multiplier=replay.speed_multiplier,
    )
