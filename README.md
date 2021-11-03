# Crossword Digitiser

Digitises a crossword puzzle from images, using scripts provided in the `image_to_crossword.py` module.

Puzzle data is stored in a CrosswordPuzzle object, with exposed methods that can manipulate the grid and clues stored.

## Usage and Documentation

Running `main.py` will run a demo of the digitiser using images from the `crossword_digitiser/test_images` folder.

Public method documentation can primarily be found in the docstrings.

Run `pydoc -b` to browse the available methods in a legible format.

## Exceptions
User-defined Exceptions have been created for easier debugging/handling. The exception hierarchy can be found below.

```
CrosswordPuzzleError
├── PuzzleDevelopmentError
│   ├── ClueAlreadyExistsError
│   ├── ClueDoesNotExistError
│   └── BlackCellModificationError
├── GridVerificationError
│   ├── UnexpectedClueError
│   └── ClueLengthDoesNotMatchError
└── AnswerInputError
    ├── AnswerDoesNotFitError
    ├── AnswerFormatError
    └── InputClashesWithExistingEntryError
```

## CrosswordPuzzle Lifecycle

The CrosswordPuzzle object holds onto a Grid (2D list of characters), and two maps of numbers to Clue objects (representing a list of across/down clues in the puzzle).

Ensure that the stages below are followed to fully utilise the CrosswordPuzzle object.

### Initialising the Grid

Initialise the CrosswordPuzzle object using its constructor `CrosswordPuzzle()`.

Use `.set_grid(x, y)` method to set up an empty grid with `x` rows and `y` columns.

`.turn_cell_white(x, y)` and `.turn_cell_black(x, y)` should then be used to manipulate the grid into the desired structure.

### Loading the Clues

`.add_clue(clue_no, is_across, clue_text, answer_len)` should be used to add clues to the puzzle. It takes the following parameters:
- `clue_no (int)`: corresponding to the number of the clue
- `is_across (bool)`: indicating whether the clue is across or down (therefore adding it to the corresponding map)
- `clue_text (str)`: the clue itself (e.g. "companion shredded corset")
- `answer_len (list[int])`: a list of integers indicating the answer structure (e.g. [10] or [3, 7])

### Verifying the Grid structure and synchronising Clue positions

At this point, a Grid has been built and the clues are stored within their respective maps. However, the Clue info does not include their positions in the grid.

It is essential that the method `.verify_and_sync()` is called to update the positions of the clues.
The number and length of clues can be identified by analysing just the grid - an algorithm has been implemented to do this, and will check that the Clues stored in the object match the Grid's expectations.

Failure to do so will result in a `GridVerificationError` being raised (see the section `Exceptions` for more information).

### Solving Clues and filling the Grid

Finally, the Grid can be manipulated to fill in cells and solve clues using `.fill_cell(row, col, char)` and `.solve_clue(clue_no, is_across, answer)` respectively.

Naturally, attempts to fill in the grid may not work. `AnswerInputError`s will be raised, corresponding to the type of issue arising when solving the grid.