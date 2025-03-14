import json
from dataclasses import dataclass

@dataclass
class VocabOption:
    word: str
    is_attempted: bool

class VocabItem():
    def __init__(self, word: str, meaning: str, options: list[VocabOption]= [], is_solved: bool = False, timestamp:float = None):
        self.word = word
        self.meaning = meaning
        self.options = options
        self.is_solved = is_solved
        self.timestamp = timestamp

    def asDict(self, removed_args: list[str] = []):
        return {key: value for key, value in self.__dict__.items() if key not in removed_args}
