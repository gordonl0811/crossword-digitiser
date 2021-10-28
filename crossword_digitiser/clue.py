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
