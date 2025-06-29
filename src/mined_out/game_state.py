from dataclasses import dataclass
from typing import List, Optional

from mined_out.common import Position,CellType,Explosion

@dataclass
class GameState:
    player_pos: Position
    grid: List[List[CellType]]
    items_collected: int
    total_items: int
    level: int
    mine_count_nearby: int = 0
    game_over: bool = False
    won: bool = False
    explosion: Optional[Explosion] = None
    mine_reveal_timer: int = 0
    revealing_mine_pos: Optional[Position] = None
