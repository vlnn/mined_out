import pyxel
from typing import Optional

from mined_out.common import Direction



class InputHandler:
    def get_direction(self) -> Optional[Direction]:
        if pyxel.btnp(pyxel.KEY_UP) or pyxel.btnp(pyxel.KEY_W):
            return Direction.UP
        elif pyxel.btnp(pyxel.KEY_DOWN) or pyxel.btnp(pyxel.KEY_S):
            return Direction.DOWN
        elif pyxel.btnp(pyxel.KEY_LEFT) or pyxel.btnp(pyxel.KEY_A):
            return Direction.LEFT
        elif pyxel.btnp(pyxel.KEY_RIGHT) or pyxel.btnp(pyxel.KEY_D):
            return Direction.RIGHT
        return None

    def should_restart(self) -> bool:
        return pyxel.btnp(pyxel.KEY_R)
