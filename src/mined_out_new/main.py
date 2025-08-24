from minefield import init_minefield, redraw_minefield
import user_input

HEIGHT = 25
WIDTH = 20


class mined_out:
    def __init__(self):
        init_minefield(self, HEIGHT, WIDTH)

    def update(self):
        user_input.key_quit()

    def draw(self):
        redraw_minefield(HEIGHT, WIDTH)


def main():
    mined_out()


if __name__ == "__main__":
    main()
