class Clue:

    def __init__(self, position, answer_length, clue=None):
        self.clue = clue
        self.position = position
        self.answer_length = answer_length

    def __str__(self):
        return f"{self.clue} ({self.answer_length}), at {self.position}"
