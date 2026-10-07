"""Entry point. Only parses CLI options; game logic lives in game/board/rules."""

import argparse

from game import DotsAndBoxes


def build_parser():
    parser = argparse.ArgumentParser(description="Play Dots and Boxes.")
    parser.add_argument("--rows", type=int, default=2, help="board rows (1-9)")
    parser.add_argument("--cols", type=int, default=2, help="board columns (1-9)")
    return parser


if __name__ == "__main__":
    args = build_parser().parse_args()
    try:
        DotsAndBoxes(rows=args.rows, cols=args.cols).run()
    except ValueError as exc:
        print(f"Cannot start game: {exc}")
