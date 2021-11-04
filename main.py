#!/usr/bin/python

import sys
import cv2.cv2 as cv2

from image_to_crossword import CrosswordImageProcessor
from json_to_crossword import CrosswordJsonProcessor


def main(argv):

    grid_img = cv2.imread("test_images/8_grid.png")
    across_img = cv2.imread("test_images/8_clues_across.png")
    down_img = cv2.imread("test_images/8_clues_down.png")
    image_puzzle = CrosswordImageProcessor.crossword_from_images(
        tesseract_path=r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe",
        grid_img=grid_img,
        across_clues_img=across_img,
        down_clues_img=down_img,
        rows=9,
        cols=7
    )

    image_puzzle.print_data()

    # test_data = """
    # {
    #     "grid": [
    #         ["1", "1", "1", "1", "1", "1"],
    #         ["0", "0", "1", "0", "0", "0"],
    #         ["0", "0", "1", "0", "0", "0"],
    #         ["0", "0", "1", "0", "0", "0"],
    #         ["0", "0", "1", "0", "0", "0"],
    #         ["0", "0", "0", "0", "0", "0"]
    #     ],
    #     "across": {
    #         "1": {
    #             "clue": "Example",
    #             "length": [6]
    #         }
    #     },
    #     "down": {
    #         "2": {
    #             "clue": "Example2",
    #             "length": [1,1,1,1,1]
    #         }
    #     }
    # }
    # """
    # json_puzzle = CrosswordJsonProcessor.crossword_from_json(test_data)
    # json_puzzle.solve_clue(1, True, "Answer")
    # json_puzzle.print_data()


if __name__ == '__main__':
    main(sys.argv[1:])
