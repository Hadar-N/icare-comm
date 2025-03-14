import re

is_state_re = re.compile("^game/word/[^/]+/state$")
is_select_re = re.compile("^game/word/[^/]+/select$")

class Topics:
    CONTROL="game/control"
    STATE="game/state"
    # TODO: deprecated! should be removed!!!
    DATA="game/data"

    @staticmethod
    def word_state(word: str = '+'):
        return f'game/word/{word}/state'
    @staticmethod
    def is_word_state(topicname: str):
        return bool(re.search(is_state_re,topicname))
    
    @staticmethod
    def word_select(word: str = '+'):
        return f'game/word/{word}/select'
    @staticmethod
    def is_word_select(topicname: str):
        return bool(re.search(is_state_re,topicname))
