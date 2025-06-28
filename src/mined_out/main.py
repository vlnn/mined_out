import pyxel
from random import randint

# CONSTANTS
# TODO: move to constants.py in future
X = 160
Y = 120

### Logic func

def rnd_around(center, epsilon):
    """Return random coordinate around center with maximum distance = epsilon."""
    return randint(center-epsilon, center+epsilon)

### Preparation of pyxel.run
pyxel.init(X, Y)

def update():
    if pyxel.btnp(pyxel.KEY_Q):
        pyxel.quit()

def draw():
    pyxel.cls(0)
    pyxel.rect(rnd_around(0,5), rnd_around(0,5), rnd_around(20,10), rnd_around(30,10), pyxel.COLOR_GREEN)

### Main cycle
pyxel.run(update, draw)
