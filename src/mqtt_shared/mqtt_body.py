import json
from enum import Enum
from game_shared import GAME_LEVELS, GAME_MODES, MQTT_COMMANDS, GAME_STATUS, VocabItem
from .mqtt_topics import Topics

# def is_property_obj(obj, property):
#     return property in obj and type(obj[property]) == dict

def BodyForTopic(topic, payload):
    res= None
    if (topic == Topics.CONTROL): res = ControlCommandBody(msg=payload)
    elif (topic == Topics.DATA): res = GameDataBody(msg=payload) #TODO: remove
    elif (topic == Topics.STATE): res = GameStateBody(msg=payload)
    elif (Topics.is_word_state(topic)): res = WordStateBody(msg=payload)
    elif (Topics.is_word_select(topic)): res = WordSelectBody(msg=payload)

    return res

class BodyObject:
    def __init__(self, **kwargs):
        self._parsed_msg = json.loads(kwargs["msg"]) if len(kwargs) == 1 and "msg" in kwargs else None

    def __parseFromMsg(self): raise NotImplementedError("method '__parseFromMsg' not implemented!")
    def __parseFromArgs(self): raise NotImplementedError("method '__parseFromArgs' not implemented!")

    def parseToMsg(self):
        attrs = {key: value.value if isinstance(value, Enum) else value for key, value in self.__dict__.items() if not key.startswith('_')}
        return json.dumps(attrs)

class ControlCommandBody(BodyObject):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # self.command=self.level=self.mode=self.coords=None
        if self._parsed_msg: self.__parseFromMsg()
        if not self._parsed_msg: self.__parseFromArgs(**kwargs)
        
    def __parseFromMsg(self):
        try:
            self.command = MQTT_COMMANDS(self._parsed_msg["command"])
            if self.command == MQTT_COMMANDS.START:
                self.level =  GAME_LEVELS[self._parsed_msg["payload"]["level"]]
                self.mode = GAME_MODES[self._parsed_msg["payload"]["option"]]
            elif self.command == MQTT_COMMANDS.RESET_DISPLAY:
                self.coords= self._parsed_msg["payload"]
        except:
            raise("Invalid parameters!", self._parsed_msg)
        
    def __parseFromArgs(self, **kwargs):
        # TODO: who makes it into Enum values??
        self.command = kwargs["command"]
        if "level" in kwargs: self.level = kwargs["level"]
        if "mode" in kwargs: self.mode = kwargs["mode"]
        if "coords" in kwargs: self.coords = kwargs["coords"]

class GameDataBody(BodyObject):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for i in self._parsed_msg: print(i, type(i))
        self.items = [{"type": i["type"], "word": VocabItem(**i["word"])} for i in self._parsed_msg]

class GameStateBody(BodyObject):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.state=self._parsed_msg["state"] if self._parsed_msg else kwargs["state"]
        self.timestamp=self._parsed_msg["timestamp"] if self._parsed_msg else kwargs["timestamp"]

class WordStateBody(BodyObject):
    """TODO"""

class WordSelectBody(BodyObject):
    """TODO"""