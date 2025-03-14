import re
from game_shared import DEVICE_TYPE

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
    
    @staticmethod
    def topics_per_role(role: DEVICE_TYPE) -> list[str]:
        if (role == DEVICE_TYPE.CONTROL):
            return [ Topics.STATE, Topics.word_state(), Topics.DATA ]
        else: return [ Topics.CONTROL, Topics.word_select() ]


