import cv2
import pytesseract

from clue import Clue

from collections import OrderedDict
import re


class Grid:

    def __init__(self):
        self.grid = None
        self.clues_across_map = OrderedDict()
        self.clues_down_map = OrderedDict()

    def create_grid(self, rows: int, cols: int):
        """
        Creates an empty grid with specified dimensions
        :param rows: number of rows in the grid
        :param cols: number of columns in the grid
        :return: None
        """
        self.grid = [['0'] * cols for _ in range(rows)]

    def get_grid_cell(self, row: int, col: int):
        """
        Gets the value in a cell in the crossword grid
        :param row: row number in the grid
        :param col: column number in the grid
        :return: the value stored in the cell
        """
        return self.grid[row][col]

    def set_grid_cell(self, row: int, col: int):
        """
        Sets a cell in the crossword grid to 1 (white cell)
        :param row: row number in the grid
        :param col: column number in the grid
        :return:
        """
        self.grid[row][col] = '1'

    def clear_grid_cell(self, row: int, col: int):
        """
        Sets a cell in the crossword grid to 0 (black cell)
        :param row: row number in the grid
        :param col: column number in the grid
        :return:
        """
        self.grid[row][col] = '0'

    def fill_grid_cell(self, row: int, col: int, value: str):
        """
        Fills in a cell in the crossword grid using the given value
        :param row: row number in the grid
        :param col: column number in the grid
        :param value: a single character to be placed in the cell
        :return:
        """
        assert len(value) == 1 and value.isalpha()
        self.grid[row][col] = value.upper()

    def solve_clue(self, clue_no: int, is_across: bool, answer: str):

        answer = answer.upper()

        clue_map = self.clues_across_map if is_across else self.clues_down_map

        if clue_no not in clue_map:
            raise ValueError(f"This crossword puzzle doesn't have {clue_no} " + ("ACROSS" if is_across else "DOWN"))

        answer_len = len(answer)
        expected_answer_len = sum(clue_map[clue_no].answer_len)

        if answer_len != expected_answer_len:
            raise ValueError(f"Your answer {answer} doesn't fit in the grid. "
                             f"Expected: {expected_answer_len} "
                             f"Received: {len(answer)}")

        clue_pos_row, clue_pos_col = clue_map[clue_no].position

        for i, char in enumerate(answer):

            current_row = clue_pos_row
            current_col = clue_pos_col

            if is_across:
                current_col += i
            else:
                current_row += i

            current_cell_value = self.get_grid_cell(current_row, current_col)

            if current_cell_value == '1':
                # Cell is available: fill it in
                self.fill_grid_cell(current_row, current_col, char)
            elif current_cell_value == '0':
                # Cell isn't meant to have a character - programmer error
                raise ValueError(f"Attempted to fill black cell at Row {current_row}, Col {current_col} ")
            elif current_cell_value != char:
                # A character is already in the grid, and this answer won't work with it
                raise ValueError(f"Answer collision: proposed answer clashes with existing grid")

            # Character is already in the grid and aligns with the provided answer

    def length_rows(self):
        """
        Returns the number of rows in the grid
        :return: Rows in the grid
        """
        assert self.grid is not None
        return len(self.grid)

    def length_cols(self):
        """
        Returns the number of columns in the grid
        :return: Columns in the grid
        """
        assert self.grid is not None
        return len(self.grid[0])

    def print_data(self):
        """
        Pretty prints the data stored in this class
        :return:
        """
        print("============== GRID ==============")
        for row in self.grid:
            print(row)
        print("============== CLUES ==============")
        print("ACROSS:")
        print('\n'.join(
            [f"{pos}. {clue}" for pos, clue in self.clues_across_map.items()]
        ))
        print("DOWN:")
        print('\n'.join(
            [f"{pos}. {clue}" for pos, clue in self.clues_down_map.items()]
        ))

    def upload_grid(self, img_path: str, rows: int, cols: int):
        """
        Take an image with a crossword grid and store it in the class
        :param img_path: path to the image file
        :param rows: number of rows in the grid
        :param cols: number of columns in the grid
        :return:
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
        self.create_grid(rows, cols)

        # Iterate through each cell, treating it as empty if more than 50 pixels are white
        for i in range(rows):
            for j in range(cols):
                box = cross_rect[i * 10:(i + 1) * 10, j * 10:(j + 1) * 10]
                if cv2.countNonZero(box) > 50:
                    self.set_grid_cell(i, j)

        self.__get_clue_metadata()

    def upload_clues(self, img_path: str, is_across: bool):
        """
        Uploads a column of clues to the data structure using regexes and string manipulation
        :param img_path: path to the image file
        :param is_across: True if the clues are from the across column, False otherwise
        :return:
        """

        pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

        img = cv2.imread(img_path)

        # TODO: Image preprocessing

        # Convert the image to a string
        text = pytesseract.image_to_string(
            img,
            lang='eng',
            config=f'--psm 6'
        )

        # TODO: Text post processing

        # Remove Across/Down if needed
        text = re.sub('^across' if is_across else '^down', '', text, flags=re.IGNORECASE)

        # Change vertical bars to "I"
        text = text.replace('|', 'I')

        # Replace newlines with spaces
        text = text.replace('\n', ' ')

        # TODO: Get clues

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
                clues_map = self.clues_across_map if is_across else self.clues_down_map

                # Verify that the answer length matches what the grid has
                if sum(answer_len) != sum(clues_map[clue_no].answer_len):

                    raise ValueError(
                        f"Answer length of {answer_len} != grid structure of {clues_map[clue_no].answer_len}\n"
                        f"CLUE: {clue_no}"
                    )
                else:
                    # Reassign the actual clue length
                    clues_map[clue_no].answer_len = answer_len

                # Store the clue in the grid's map,
                clues_map[clue_no].clue = clue_text

    def __get_clue_metadata(self):
        """
        Uses the grid to fill out the across/down maps with Clue objects with their
        corresponding metadata (position and length)
        :return:
        """

        num_rows = self.length_rows()
        num_cols = self.length_cols()

        across_clues = []
        down_clues = []

        # Get all "across" clues
        for i, row in enumerate(self.grid):

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
                            across_clues.append((position, [word_length]))
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
                                across_clues.append((position, [word_length]))
                            # 1st pointer set to 2nd
                            p1 = p2

        # Get all "down" clues using a similar algorithm but with a transposed grid
        for j, col in enumerate(map(list, zip(*self.grid))):

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
                            down_clues.append((position, [word_length]))
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
                                down_clues.append((position, [word_length]))
                            # 1st pointer set to 2nd
                            p1 = p2

        # Sort "down" clues
        down_clues.sort()

        # Create and enumerate the clues

        clue_no = 1

        while across_clues or down_clues:

            # Assign the rest of the clue numbers
            if not across_clues:
                while down_clues:
                    clue_data = down_clues.pop(0)
                    self.clues_down_map[clue_no] = Clue(clue_data[0], clue_data[1])
                    clue_no += 1
            elif not down_clues:
                while across_clues:
                    clue_data = across_clues.pop(0)
                    self.clues_across_map[clue_no] = Clue(clue_data[0], clue_data[1])
                    clue_no += 1
            # Compare the positions of the across and down clues
            elif across_clues[0][0] < down_clues[0][0]:
                clue_data = across_clues.pop(0)
                self.clues_across_map[clue_no] = Clue(clue_data[0], clue_data[1])
                clue_no += 1
            elif across_clues[0][0] > down_clues[0][0]:
                clue_data = down_clues.pop(0)
                self.clues_down_map[clue_no] = Clue(clue_data[0], clue_data[1])
                clue_no += 1
            else:
                clue_data = across_clues.pop(0)
                self.clues_across_map[clue_no] = Clue(clue_data[0], clue_data[1])
                clue_data = down_clues.pop(0)
                self.clues_down_map[clue_no] = Clue(clue_data[0], clue_data[1])
                clue_no += 1


if __name__ == '__main__':
    grid = Grid()
    print("Uploading grid...")
    grid.upload_grid('test_images/6_grid.jpg', 15, 15)
    print("Uploading across clues...")
    grid.upload_clues('test_images/6_clues_across.jpg', is_across=True)
    print("Uploading down clues...")
    grid.upload_clues('test_images/6_clues_down.jpg', is_across=False)

    grid.solve_clue(1, True, "ANSWER")
    grid.solve_clue(1, False, "ANSWERED")
    grid.print_data()
