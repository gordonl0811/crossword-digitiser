class Clue:

    def __init__(self, position: tuple[int, int], answer_len: int, clue: str = None):
        self.clue = clue
        self.position = position
        self.answer_len = answer_len

    def __str__(self):
        return f"{self.clue} ({self.answer_len}), at {self.position}"
