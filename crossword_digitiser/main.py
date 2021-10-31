#!/usr/bin/python

import sys

from image_to_crossword import CrosswordImageProcessor


def main(argv):

    puzzle = CrosswordImageProcessor.crossword_from_images(
        grid_path="test_images/6_grid.jpg",
        across_clues_path="test_images/6_clues_across.jpg",
        down_clues_path="test_images/6_clues_down.jpg",
        rows=15,
        cols=15
    )

    puzzle.solve_clue(1, True, "ANSWER")
    puzzle.solve_clue(1, False, "ANSWERED")
    puzzle.print_data()


if __name__ == '__main__':
    main(sys.argv[1:])
