import pyxel
from typing import Optional

from mined_out.common import Direction

def get_direction_from_input() -> Optional[Direction]:
    """Get direction from current input state."""
    if pyxel.btnp(pyxel.KEY_UP) or pyxel.btnp(pyxel.KEY_W):
        return Direction.UP
    elif pyxel.btnp(pyxel.KEY_DOWN) or pyxel.btnp(pyxel.KEY_S):
        return Direction.DOWN
    elif pyxel.btnp(pyxel.KEY_LEFT) or pyxel.btnp(pyxel.KEY_A):
        return Direction.LEFT
    elif pyxel.btnp(pyxel.KEY_RIGHT) or pyxel.btnp(pyxel.KEY_D):
        return Direction.RIGHT
    return None

def is_restart_pressed() -> bool:
    """Check if restart key is pressed."""
    return pyxel.btnp(pyxel.KEY_R)
