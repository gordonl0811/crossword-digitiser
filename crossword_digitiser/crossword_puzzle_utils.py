class Grid:

    def __init__(self):
        self._data = None

    def __str__(self):
        return "\n".join(map(" ".join, self._data))

    def create_grid(self, rows: int, cols: int):
        """
        Creates an empty grid with specified dimensions
        :param rows: number of rows in the grid
        :param cols: number of columns in the grid
        """
        self._data = [['0'] * cols for _ in range(rows)]

    @property
    def data(self):
        return self._data

    def get_grid_cell(self, row: int, col: int):
        """
        Gets the value in a cell in the crossword grid
        :param row: row number in the grid
        :param col: column number in the grid
        :return: the value stored in the cell
        """
        return self._data[row][col]

    def set_grid_cell(self, row: int, col: int):
        """
        Sets a cell in the crossword grid to 1 (white cell)
        :param row: row number in the grid
        :param col: column number in the grid
        """
        self._data[row][col] = '1'

    def clear_grid_cell(self, row: int, col: int):
        """
        Sets a cell in the crossword grid to 0 (black cell)
        :param row: row number in the grid
        :param col: column number in the grid
        """
        self._data[row][col] = '0'

    def fill_grid_cell(self, row: int, col: int, value: str):
        """
        Fills in a cell in the crossword grid using the given value
        :param row: row number in the grid
        :param col: column number in the grid
        :param value: a single character to be placed in the cell
        """
        assert len(value) == 1 and value.isalpha()
        self._data[row][col] = value.upper()

    def length_rows(self):
        """
        Returns the number of rows in the grid
        :return: Number of rows in the grid
        """
        assert self._data is not None
        return len(self._data)

    def length_cols(self):
        """
        Returns the number of columns in the grid
        :return: Number of columns in the grid
        """
        assert self._data is not None
        return len(self._data[0])


class Clue:

    def __init__(self, clue_text: str, answer_len: list[int], pos: tuple[int, int]):
        self.clue_text = clue_text
        self.answer_len = answer_len
        self.pos = pos

    def __str__(self):
        return f"{self.clue_text} ({','.join(map(str, self.answer_len))}), at {self.pos}"

    def __lt__(self, other):
        return self.pos < other.pos


class ClueMetadata:

    def __init__(self, pos: tuple[int, int], length: int):
        self.pos = pos
        self.length = length

    def __lt__(self, other):
        return self.pos < other.pos
