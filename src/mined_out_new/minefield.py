import pyxel


def _draw_chessboard(height, width):
    """Testing graphics output to the minefield."""
    for row in range(height):
        for col in range(width):
            color = _get_square_color(row, col)
            pyxel.rect(row, col, 1, 1, color)


def _get_square_color(row, col):
    return pyxel.COLOR_LIGHT_BLUE if (row + col) % 2 == 0 else pyxel.COLOR_GRAY


def init_minefield(app, h, w):
    pyxel.init(h, w, title="Mined Out")
    _draw_chessboard(h, w)
    pyxel.run(app.update, app.draw)


def redraw_minefield(h, w): ...
