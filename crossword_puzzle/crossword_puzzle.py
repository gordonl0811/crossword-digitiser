from .utils import Grid, Clue, ClueMetadata
from .exceptions import *

from collections import OrderedDict


class CrosswordPuzzle:

    def __init__(self):
        self._grid: Grid = Grid()
        self._clues_across_map: OrderedDict[int, Clue] = OrderedDict()
        self._clues_down_map: OrderedDict[int, Clue] = OrderedDict()

    def print_data(self):
        """
        Pretty prints the data stored in this class
        """
        print("\n============== GRID ==============\n")
        print(self._grid)
        print("\n============== CLUES ==============\n")
        print("ACROSS:\n")
        print('\n'.join([f"{pos}. {clue}" for pos, clue in self._clues_across_map.items()]))
        print("\nDOWN:\n")
        print('\n'.join([f"{pos}. {clue}" for pos, clue in self._clues_down_map.items()]))

    def set_grid(self, rows: int, cols: int):
        """
        Sets up the grid for the crossword clue
        :param rows: number of rows in the grid
        :param cols: number of cols in the grid
        """
        self._grid.create_grid(rows, cols)

    def add_clue(self, clue_no: int, is_across: bool, clue_text: str, answer_len: list[int]):
        """
        Adds a clue to the crossword puzzle
        :param clue_no: clue number
        :param is_across: across or down clue
        :param clue_text: the provided clue
        :param answer_len: length of the answer
        """

        new_clue = Clue(clue_text, answer_len, (-1, -1))

        clues_map = self._clues_across_map if is_across else self._clues_down_map

        if clue_no in clues_map:
            raise ClueAlreadyExistsError(clue_no, is_across)

        clues_map[clue_no] = new_clue

    def remove_clue(self, clue_no: int, is_across: bool):
        """
        Removes a clue from the crossword puzzle
        :param clue_no: clue number
        :param is_across: across or down clue
        """

        clues_map = self._clues_across_map if is_across else self._clues_down_map

        if clue_no not in clues_map:
            raise ClueDoesNotExistError(clue_no, is_across)

        del clues_map[clue_no]

    def solve_clue(self, clue_no: int, is_across: bool, answer: str):
        """
        Fills in a grid with a given answer to a clue
        :param clue_no: clue number
        :param is_across: True if across clue, False if down clue
        :param answer: answer
        """

        answer = answer.upper()

        clue_map = self._clues_across_map if is_across else self._clues_down_map

        if clue_no not in clue_map:
            raise ClueDoesNotExistError(clue_no, is_across)

        answer_len = len(answer)
        expected_answer_len = sum(clue_map[clue_no].answer_len)

        if answer_len != expected_answer_len:
            raise AnswerDoesNotFitError(answer, expected_answer_len, len(answer))

        clue_pos_row, clue_pos_col = clue_map[clue_no].pos

        for i, char in enumerate(answer):

            current_row = clue_pos_row
            current_col = clue_pos_col

            if is_across:
                current_col += i
            else:
                current_row += i

            try:

                self.fill_cell(current_row, current_col, char)

            except InputClashesWithExistingEntryError:

                # Revert the answer that was being inputted
                for j in range(i):

                    current_row = clue_pos_row
                    current_col = clue_pos_col

                    if is_across:
                        current_col += j
                    else:
                        current_row += j

                    self.clear_cell(current_row, current_col)

                # Relay that the answer didn't work
                raise AnswerHasConflictingCharacter(clue_no, is_across, answer, i)

    def fill_cell(self, row: int, col: int, char: str):
        """
        Fills a cell in the grid
        :param row: row in the crossword
        :param col: column in the crossword
        :param char: character to fill in the grid
        """

        # Verify that the input is a single character
        if not (len(char) == 1 and char.isalpha()):
            raise AnswerFormatError(char, row, col)

        char = char.upper()

        current_cell_value = self._grid.get_grid_cell(row, col)

        if current_cell_value == '1':
            # Cell is available: fill it in
            self._grid.fill_grid_cell(row, col, char)
        elif current_cell_value == '0':
            # Cell isn't meant to have a character - programmer error
            raise BlackCellModificationError(row, col)
        elif current_cell_value != char:
            # A character is already in the grid, and this answer won't work with it
            raise InputClashesWithExistingEntryError(char, current_cell_value)

        # Character is already in the grid and aligns with the provided answer - no action

    def clear_cell(self, row: int, col: int):
        """
        Clears a cell in the grid
        :param row: row in the crossword
        :param col: column in the crossword
        """

        current_cell_value = self._grid.get_grid_cell(row, col)

        if current_cell_value == '0':
            # Cell isn't meant to have a character - programmer error
            raise BlackCellModificationError(row, col)

        self._grid.clear_grid_cell(row, col)

    def turn_cell_white(self, row: int, col: int):
        """
        Turns a cell in the grid white (available)
        :param row: row in the crossword
        :param col: column in the crossword
        """
        self._grid.set_grid_cell(row, col)

    def turn_cell_black(self, row: int, col: int):
        """
        Turns a cell in the grid white (unavailable)
        :param row: row in the crossword
        :param col: column in the crossword
        """
        self._grid.clear_grid_cell(row, col)

    def verify_and_sync(self):
        """
        Verifies that the grid structure matches the clues stored inside the puzzle.
        If successful, updates the clues to store information on where they are in the grid.
        """

        across_clues_metadata, down_clues_metadata = self.__get_metadata_all()

        self.__verify_clues(self._clues_across_map, across_clues_metadata, is_across=True)
        self.__verify_clues(self._clues_down_map, down_clues_metadata, is_across=False)

    def __get_metadata_all(self):
        """
        Uses the grid to fill out the across/down maps with Clue objects with their
        corresponding metadata (position and length)
        :return: metadata for across and down clues
        """

        across_metadata = self.__get_metadata_set(is_across=True)
        down_metadata = self.__get_metadata_set(is_across=False)

        # Create and enumerate the clues

        clue_no = 1
        enumerated_across_metadata = {}
        enumerated_down_metadata = {}

        while across_metadata or down_metadata:

            # Assign the rest of the clue numbers
            if not across_metadata:
                while down_metadata:
                    enumerated_down_metadata[clue_no] = down_metadata.pop(0)
                    clue_no += 1
            elif not down_metadata:
                while across_metadata:
                    enumerated_across_metadata[clue_no] = across_metadata.pop(0)
                    clue_no += 1
            # Compare the positions of the across and down clues
            elif across_metadata[0] < down_metadata[0]:
                enumerated_across_metadata[clue_no] = across_metadata.pop(0)
                clue_no += 1
            elif across_metadata[0] > down_metadata[0]:
                enumerated_down_metadata[clue_no] = down_metadata.pop(0)
                clue_no += 1
            else:
                enumerated_across_metadata[clue_no] = across_metadata.pop(0)
                enumerated_down_metadata[clue_no] = down_metadata.pop(0)
                clue_no += 1

        return enumerated_across_metadata, enumerated_down_metadata

    def __get_metadata_set(self, is_across: bool):
        """
        Generates a list of ClueMetadata based on the layout of a grid
        :param is_across: indicate metadata generation for either Across or Down clues
        :return: list of ClueMetadata
        """

        metadata_set = []

        if is_across:
            row_length = self._grid.length_cols()
            grid_data = self._grid.data
        else:
            row_length = self._grid.length_rows()
            grid_data = map(list, zip(*self._grid.data))

        for i, row in enumerate(grid_data):

            # Two pointers
            p1 = p2 = 0

            while p1 < row_length:
                if p1 == p2:
                    # Searching for a new word
                    if row[p1] != '0':
                        # 1st pointer is on a white cell
                        p2 += 1
                    else:
                        # 1st pointer is on a black cell
                        p1 += 1
                        p2 += 1
                else:
                    if p2 == row_length:
                        # End of row
                        word_length = p2 - p1
                        if word_length > 1:
                            # We've got a word, store the information
                            position = (i, p1)
                            metadata_set.append(ClueMetadata(position, word_length))
                        # 1st pointer set to 2nd (ending loop)
                        p1 = p2
                    else:
                        # Check if we have a white cell
                        if row[p2] != '0':
                            # White cell found
                            p2 += 1
                        else:
                            # End of row
                            word_length = p2 - p1
                            if word_length > 1:
                                # We've got a word, store the information
                                position = (i, p1)
                                metadata_set.append(ClueMetadata(position, word_length))

                            # 1st pointer set to 2nd
                            p1 = p2

        # Down clues will have their position flipped which must be corrected
        # i.e. position = (p1, i) instead of (i, p1)
        if not is_across:
            for metadata in metadata_set:
                metadata.pos = tuple(reversed(metadata.pos))

        # Sort metadata by position
        metadata_set.sort()

        return metadata_set

    @staticmethod
    def __verify_clues(clues_map, clues_metadata, is_across):
        """
        Checks if a map of enumerated Clues matches a map of enumerated ClueMetadata,
        and updates the Clues' positions if successful
        :param clues_map: map of clue numbers to clues
        :param clues_metadata: map of clue numbers to clue metadata
        """

        for clue_no, clue in clues_map.items():

            # Check if the grid expects a clue
            if clue_no not in clues_metadata:
                raise UnexpectedClueError(clue_no, is_across, clue.clue_text)

            clue_metadata = clues_metadata[clue_no]

            # Check if the grid and clue have matching lengths
            total_length = sum(clue.answer_len)
            if total_length != clue_metadata.length:
                raise ClueLengthDoesNotMatchError(clue_no, is_across, total_length, clue_metadata.length)

            # Clue is verified - sync the clue by storing its position from the metadata
            clue.pos = clue_metadata.pos
