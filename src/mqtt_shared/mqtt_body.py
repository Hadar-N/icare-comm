import json
from enum import Enum
from game_shared import GAME_LEVELS, GAME_MODES, MQTT_COMMANDS, GAME_STATUS, VocabItem
from .mqtt_topics import Topics

# def is_property_obj(obj, property):
#     return property in obj and type(obj[property]) == dict

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
        self.command=self.payload=None
        if self._parsed_msg: self.__parseFromMsg()
        if not self._parsed_msg: self.__parseFromArgs(**kwargs)
        
    def __parseFromMsg(self):
        try:
            self.command = MQTT_COMMANDS(self._parsed_msg["command"])
            self.payload= None
            if self.command == MQTT_COMMANDS.START:
                self.payload = {
                    "level": GAME_LEVELS[self._parsed_msg["payload"]["level"]],
                    "mode": GAME_MODES[self._parsed_msg["payload"]["option"]]
                }
            elif self.command == MQTT_COMMANDS.RESET_DISPLAY:
                self.payload= self._parsed_msg["payload"]
        except:
            raise("Invalid parameters!", self._parsed_msg)
        
    def __parseFromArgs(self, **kwargs):
        # TODO: who makes it into Enum values??
        self.command = kwargs["command"]
        self.payload = {}
        if "coords" in kwargs: self.payload = kwargs["coords"]
        else:
            if "level" in kwargs: self.payload["level"] = kwargs["level"]
            if "mode" in kwargs: self.payload["mode"] = kwargs["mode"]

class GameDataBody(BodyObject):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.items = [{"type": i["type"],
                       "word": i["word"] if type(i["word"]) == str else VocabItem(**i["word"]).asDict()
                       } for i in self._parsed_msg]

class GameStateBody(BodyObject):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.state=self._parsed_msg["state"] if self._parsed_msg else kwargs["state"]
        self.timestamp=self._parsed_msg["timestamp"] if self._parsed_msg else kwargs["timestamp"]

class WordStateBody(BodyObject):
    """TODO"""

class WordSelectBody(BodyObject):
    """TODO"""

def BodyForTopic(topic, payload) -> BodyObject:
    res= None
    body_class = None
    if topic == Topics.CONTROL: body_class = ControlCommandBody
    elif topic == Topics.DATA: body_class = GameDataBody #TODO: remove
    elif topic == Topics.STATE: body_class = GameStateBody
    elif Topics.is_word_state(topic): body_class = WordStateBody
    elif Topics.is_word_select(topic): body_class = WordSelectBody

    if isinstance(payload, str): return body_class(msg=payload)
    elif isinstance(payload, dict): return body_class(**payload)

    return res
