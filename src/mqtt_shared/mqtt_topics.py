import re
from game_shared import DEVICE_TYPE

is_state_re = re.compile("^game/word/[^/]+/state$")
is_select_re = re.compile("^game/word/[^/]+/select$")

class Topics:
    CONTROL="game/control"
    STATE="game/state"
    CONTOURS="game/contours"

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
        return bool(re.search(is_select_re,topicname))
    
    @staticmethod
    def get_relevant_topicname(topicname:str, is_simplify:bool, word:str = None):
        res= None
        if Topics.is_word_state(topicname):
            if is_simplify: res = Topics.word_state()
            elif word: res = Topics.word_state(word)
            else: raise Exception("word required for word state")
        elif Topics.is_word_select(topicname): 
            if is_simplify: res = Topics.word_select()
            elif word: res = Topics.word_select(word)
            else: raise Exception("word required for word selection")
        elif topicname in [Topics.CONTROL, Topics.STATE, Topics.CONTOURS]: res = topicname
        else: raise Exception("invalid topic name")
        return res
    
    @staticmethod
    def topics_per_role(role: DEVICE_TYPE) -> list[str]:
        if (role == DEVICE_TYPE.CONTROL):
            return [ Topics.STATE, Topics.word_state(), Topics.CONTOURS ]
        else: return [ Topics.CONTROL, Topics.word_select() ]


