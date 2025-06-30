import pyxel

def setup_sounds() -> None:
    """Initialize game sounds."""
    pyxel.sounds[0].set("c2e2g2c3", "p", "7", "f", 10)  # Explosion
    pyxel.sounds[1].set("g3c4e4g4", "p", "7", "f", 8)   # Item collect

def play_explosion() -> None:
    """Play explosion sound."""
    pyxel.play(0, 0)

def play_item_collect() -> None:
    """Play item collection sound."""
    pyxel.play(0, 1)
