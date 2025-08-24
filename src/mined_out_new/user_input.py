import pyxel


def key_quit():
    if pyxel.btnp(pyxel.KEY_Q):
        pyxel.quit()
