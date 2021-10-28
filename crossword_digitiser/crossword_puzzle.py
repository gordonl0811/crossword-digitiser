import cv2
import pytesseract

from grid import Grid
from clue import Clue, ClueMetadata

from collections import OrderedDict
import re


class CrosswordPuzzle:

    def __init__(self):
        self._grid = Grid()
        self._clues_across_map = OrderedDict()
        self._clues_down_map = OrderedDict()

    def print_data(self):
        """
        Pretty prints the data stored in this class
        :return:
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
        :return:
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
        self.__upload_grid(img_path=grid_path, rows=rows, cols=cols)

        print("Uploading across clues...")
        self.__upload_clues(img_path=across_clues_path, is_across=True)

        print("Uploading down clues...")
        self.__upload_clues(img_path=down_clues_path, is_across=False)

        print("Verifying puzzle state...")
        self.__verify_and_sync()

    def __upload_grid(self, img_path: str, rows: int, cols: int):
        """
        Take an image with a crossword grid and store it in the class
        :param img_path: path to the image file
        :param rows: number of rows in the grid
        :param cols: number of columns in the grid
        """

        # Read the image and convert it to grayscale
        img = cv2.imread(img_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Thresholding
        ret, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)
        thresh2 = cv2.bitwise_not(thresh)

        # Find contours in the image
        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, 1)

        max_area = -1
        max_cnt = -1

        # Locate the grid by finding the square with the largest area
        for cnt in contours:
            # Get the approximated contour
            approx = cv2.approxPolyDP(cnt, 0.02 * cv2.arcLength(cnt, True), True)
            if len(approx) == 4 and cv2.contourArea(cnt) > max_area:
                # Found largest rectangle, store this information
                max_area = cv2.contourArea(cnt)
                max_cnt = cnt

        # Extract the crossword region, and resize it to a standard size
        x, y, w, h = cv2.boundingRect(max_cnt)
        cross_rect = thresh2[y:y + h, x:x + w]
        cross_rect = cv2.resize(cross_rect, (rows * 10, cols * 10))

        # Initialise the grid as a 2D array with zeroes
        self._grid.create_grid(rows, cols)

        # Iterate through each cell, treating it as empty if more than 50 pixels are white
        for i in range(rows):
            for j in range(cols):
                box = cross_rect[i * 10:(i + 1) * 10, j * 10:(j + 1) * 10]
                if cv2.countNonZero(box) > 50:
                    self._grid.set_grid_cell(i, j)

        self.__get_clue_metadata()

    def __upload_clues(self, img_path: str, is_across: bool):
        """
        Uploads a column of clues to the data structure using regexes and string manipulation
        Clue objects will be missing a "position" field, which is updated in __verify_and_sync()
        :param img_path: path to the image file
        :param is_across: True if the clues are from the across column, False otherwise
        :return:
        """

        pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

        img = cv2.imread(img_path)

        # TODO: IMAGE PREPROCESSING

        # Convert the image to a string
        text = pytesseract.image_to_string(img, lang='eng', config=f'--psm 6')

        # TEXT POST PROCESSING

        # Remove Across/Down if needed
        text = re.sub('^across' if is_across else '^down', '', text, flags=re.IGNORECASE)

        # Change vertical bars to "I"
        text = text.replace('|', 'I')

        # Replace newlines with spaces
        text = text.replace('\n', ' ')

        # EXTRACT THE CLUES

        # Split text based on the answer length found at the end of a clue
        split_text = re.split(r'(\([1-9][0-9]?(, ?[1-9][0-9]?)*\))', text)

        # The above regex uses two capture groups, and .split() returns both
        # in the result (returning None if the 2nd capture group isn't invoked)
        del split_text[2::3]

        # Group each clue with its answer length (the element succeeding the clue in the list
        split_text_iter = iter(split_text)
        clue_length_tuples = list(zip(split_text_iter, split_text_iter))

        # Process each clue
        for clue, length in clue_length_tuples:

            # Search for the 2 digit number in the clue after removing extra whitespace
            clue_no_search = re.match(r'([1-9][0-9]?)\.?(.*)', clue.lstrip().rstrip())

            # Search for the actual value of the length
            length_val_search = re.match(r'\((.*)\)', length)

            # Check that matches were successful
            if not clue_no_search:

                raise ValueError(f"Couldn't detect the clue number from the image for {clue}")

            elif not length_val_search:

                raise ValueError(f"Couldn't detect the answer length from the image for {clue}")

            else:

                # Convert to relevant types and remove whitespace at start/end
                clue_no = int(clue_no_search.group(1))
                clue_text = clue_no_search.group(2).lstrip().rstrip()

                length_val_match = length_val_search.group(1)

                # Remove whitespace
                length_val_match = length_val_match.replace(" ", "")

                if ',' in length_val_match:
                    word_lengths = length_val_match.split(',')
                    answer_len = list(map(int, word_lengths))
                else:
                    answer_len = [int(length_val_match)]

                # The map being used is dependent on the across_clues flag given
                clues_map = self._clues_across_map if is_across else self._clues_down_map

                # Store the clue in the respective grid's map
                clues_map[clue_no] = Clue(clue_text, answer_len, None)

    def __verify_and_sync(self):
        """
        Gets a set of metadata from the grid and verifies the stored clues against it
        """

        across_clues_metadata, down_clues_metadata = self.__get_clue_metadata()

        self.__verify_clues(self._clues_across_map, across_clues_metadata)
        self.__verify_clues(self._clues_down_map, down_clues_metadata)

    def __get_clue_metadata(self):
        """
        Uses the grid to fill out the across/down maps with Clue objects with their
        corresponding metadata (position and length)
        :return: metadata for across and down clues
        """

        num_rows = self._grid.length_rows()
        num_cols = self._grid.length_cols()

        across_metadata = []
        down_metadata = []

        # Get all "across" clues
        for i, row in enumerate(self._grid.data):

            # Two pointers
            p1 = p2 = 0

            # Find Across

            while p1 < num_cols:

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
                    if p2 == num_cols:
                        # End of row
                        word_length = p2 - p1
                        if word_length > 1:
                            # We've got a word, store the information
                            position = (i, p1)
                            across_metadata.append(ClueMetadata(position, word_length))
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
                                across_metadata.append(ClueMetadata(position, word_length))
                            # 1st pointer set to 2nd
                            p1 = p2

        # Get all "down" clues using a similar algorithm but with a transposed grid
        for j, col in enumerate(map(list, zip(*self._grid.data))):

            # Two pointers
            p1 = p2 = 0

            while p1 < num_rows:

                if p1 == p2:
                    # Searching for a new word
                    if col[p1] != '0':
                        # 1st pointer is on a white cell
                        p2 += 1
                    else:
                        # 1st pointer is on a black cell
                        p1 += 1
                        p2 += 1
                else:
                    if p2 == num_rows:
                        # End of column
                        word_length = p2 - p1
                        if word_length > 1:
                            # We've got a word, store the information
                            position = (p1, j)
                            down_metadata.append(ClueMetadata(position, word_length))
                        # 1st pointer set to 2nd (ending loop)
                        p1 = p2
                    else:
                        # Check if we have a white cell
                        if col[p2] != '0':
                            # White cell found
                            p2 += 1
                        else:
                            # End of column
                            word_length = p2 - p1
                            if word_length > 1:
                                # We've got a word, store the information
                                position = (p1, j)
                                down_metadata.append(ClueMetadata(position, word_length))
                            # 1st pointer set to 2nd
                            p1 = p2

        # Sort "down" clues
        down_metadata.sort()

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
