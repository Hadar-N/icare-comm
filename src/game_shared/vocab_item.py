from dataclasses import dataclass

@dataclass
class VocabOption:
    word: str
    is_attempted: bool

class VocabItem():
    def __init__(self, word: str, meaning: str, options: list[VocabOption]= [], is_solved: bool = False, timestamp:float = None):
        self.__word = word
        self.__meaning = meaning
        self.__options = options
        self.__is_solved = is_solved
        self.__timestamp = timestamp