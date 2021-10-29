from image_to_crossword import grid_from_image, clues_from_image
from crossword_puzzle_utils import Grid, Clue, ClueMetadata

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

    def add_clue(self, clue_no: int, is_across: bool, clue: str, answer_len: list[int]):
        # TODO: Implement
        pass

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
            raise ValueError(f"This crossword puzzle doesn't have {clue_no} " + ("ACROSS" if is_across else "DOWN"))

        answer_len = len(answer)
        expected_answer_len = sum(clue_map[clue_no].answer_len)

        if answer_len != expected_answer_len:
            raise ValueError(f"Your answer {answer} doesn't fit in the grid. "
                             f"Expected: {expected_answer_len} "
                             f"Received: {len(answer)}")

        clue_pos_row, clue_pos_col = clue_map[clue_no].pos

        for i, char in enumerate(answer):

            current_row = clue_pos_row
            current_col = clue_pos_col

            if is_across:
                current_col += i
            else:
                current_row += i

            current_cell_value = self._grid.get_grid_cell(current_row, current_col)

            if current_cell_value == '1':
                # Cell is available: fill it in
                self._grid.fill_grid_cell(current_row, current_col, char)
            elif current_cell_value == '0':
                # Cell isn't meant to have a character - programmer error
                raise ValueError(f"Attempted to fill black cell at Row {current_row}, Col {current_col} ")
            elif current_cell_value != char:
                # A character is already in the grid, and this answer won't work with it
                raise ValueError(f"Answer collision: proposed answer clashes with existing grid")

            # Character is already in the grid and aligns with the provided answer

    def upload_from_images(self, grid_path: str, across_clues_path: str, down_clues_path: str, rows: int, cols: int):
        """
        Function that takes in a picture of a grid, across and down clues,
        and verifying that the clues match the grid
        :param grid_path: path to the picture of the grid
        :param across_clues_path: path to the picture of the Across clues
        :param down_clues_path: path to the picture of the Down clues
        :param rows: number of rows in the grid
        :param cols: number of columns in the grid
        """

        print("Uploading grid...")
        grid_from_image(grid=self._grid, img_path=grid_path, rows=rows, cols=cols)

        print("Uploading across clues...")
        clues_from_image(clues_map=self._clues_across_map, img_path=across_clues_path, is_across=True)

        print("Uploading down clues...")
        clues_from_image(clues_map=self._clues_down_map, img_path=down_clues_path, is_across=False)

        print("Verifying puzzle state...")
        self.__verify_and_sync()

    def __verify_and_sync(self):
        """
        Gets a set of metadata from the grid and verifies the stored clues against it
        """

        across_clues_metadata, down_clues_metadata = self.__get_metadata_all()

        self.__verify_clues(self._clues_across_map, across_clues_metadata)
        self.__verify_clues(self._clues_down_map, down_clues_metadata)

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
    def __verify_clues(clues_map, clues_metadata):
        """
        Checks if a map of enumerated Clues matches a map of enumerated ClueMetadata,
        and updates the Clues' positions if successful
        :param clues_map: map of clue numbers to clues
        :param clues_metadata: map of clue numbers to clue metadata
        """

        for clue_no, clue in clues_map.items():

            # Check if the grid expects a clue
            if clue_no not in clues_metadata:
                raise ValueError(f"Clue {clue_no} ({clue.clue_text}) not found in grid")

            clue_metadata = clues_metadata[clue_no]

            # Check if the grid and clue have matching lengths
            if sum(clue.answer_len) != clue_metadata.length:
                raise ValueError(
                    f"CLUE: {clue_no}\n"
                    f"Answer's Expected Length: {clue.answer_len}\n"
                    f"Grid's Expected Length: {clue_metadata.length}"
                )

            # Clue is verified - sync the clue by storing its position from the metadata
            clue.pos = clue_metadata.pos


if __name__ == '__main__':

    crossword_puzzle = CrosswordPuzzle()

    crossword_puzzle.upload_from_images(
        grid_path="test_images/6_grid.jpg",
        across_clues_path="test_images/6_clues_across.jpg",
        down_clues_path="test_images/6_clues_down.jpg",
        rows=15,
        cols=15
    )

    crossword_puzzle.solve_clue(1, True, "ANSWER")
    crossword_puzzle.solve_clue(1, False, "ANSWERED")

    crossword_puzzle.print_data()
