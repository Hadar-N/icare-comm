import json
from random import sample, randint
from dataclasses import dataclass, asdict

@dataclass
class VocabOption:
    word: str
    is_attempted: bool

class VocabItem():
    def __init__(self, word: str, meaning: str, **kwargs):
        self.word = word
        self.meaning = meaning
        self.options = []
        if "options" in kwargs: self.optionsFromOptions(kwargs["options"])
        elif "similar" in kwargs: self.optionsFromSimilar(kwargs["similar"])
        self.is_solved = False if "is_solved" not in kwargs else kwargs["is_solved"]

    def optionsFromOptions(self, options):
        self.options = [o if isinstance(o, VocabOption) else VocabOption(**o) for o in options]

    def optionsFromSimilar(self, similar: list[str]):
        temp = sample(similar, 2)
        ix = randint(0,2)
        temp.insert(ix, self.meaning)
        self.options = [VocabOption(word= t, is_attempted=False) for t in temp]

    def asDict(self, removed_args: list[str] = []):
        temp = {key: value for key, value in self.__dict__.items() if key not in removed_args}
        if "options" in temp and len(temp["options"]): temp["options"] = [asdict(v) for v in temp["options"]]
        return temp
