import json
import time
from dataclasses import is_dataclass, asdict
from enum import Enum
from game_shared import GAME_LEVELS, GAME_MODES, MQTT_COMMANDS, GAME_STATUS, VocabItem, MQTT_DATA_ACTIONS
from .mqtt_topics import Topics

# def is_property_obj(obj, property):
#     return property in obj and type(obj[property]) == dict

class BodyObject:
    def __init__(self, **kwargs):
        self._parsed_msg = self.timestamp = None
        if len(kwargs) == 1 and "msg" in kwargs:
            self._parsed_msg = json.loads(kwargs["msg"])
            if "timestamp" in self._parsed_msg: self.timestamp = self._parsed_msg["timestamp"]

    def bodyToDict(self):
        attrs = {key: self.__valueToMsg(value) for key, value in self.__dict__.items() if not key.startswith('_')}
        return attrs

    def parseToMsg(self):
        attrs = self.bodyToDict()
        if not next((k for k in attrs.keys() if k not in ["timestamp", "items"]), None):
            attrs = attrs["items"]
        return json.dumps(attrs)
    
    def __valueToMsg(self, item):
        val = item
        if isinstance(item, Enum): val = item.value
        elif is_dataclass(item): val = asdict(item)
        elif hasattr(item, "asDict"): val = item.asDict()
        elif isinstance(item, list): val = [self.__valueToMsg(i) for i in item]
        return val 

class ControlCommandBody(BodyObject):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.command=self.payload=None
        if self._parsed_msg: self.__parseFromMsg()
        else: self.__parseFromArgs(**kwargs)
        
    def __parseFromMsg(self):
        try:
            self.command = MQTT_COMMANDS(self._parsed_msg["command"])
            self.payload= None
            if self._parsed_msg["payload"]:
                if self.command == MQTT_COMMANDS.START:
                    self.payload = {
                        "level": GAME_LEVELS[self._parsed_msg["payload"]["level"]],
                        "mode": GAME_MODES[self._parsed_msg["payload"]["mode"]]
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
        self.items=[]
        if self._parsed_msg: self.__parseFromMsg()
        else: self.__parseFromArgs(**kwargs)

    def __parseFromMsg(self):
        self.items = [WordStateBody(**i) for i in self._parsed_msg]

    def __parseFromArgs(self, **kwargs):
        self.items = [WordStateBody(**i) for i in kwargs["items"]]

class GameStateBody(BodyObject):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.state=self._parsed_msg["state"] if self._parsed_msg else kwargs["state"]

class WordStateBody(BodyObject):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = self.word= None
        if self._parsed_msg: self.__parseFromMsg()
        else: self.__parseFromArgs(**kwargs)

    def __parseFromMsg(self):
        self.type= MQTT_DATA_ACTIONS(self._parsed_msg["type"])
        self.word= self._parsed_msg["word"] if isinstance(self._parsed_msg["word"], VocabItem) else VocabItem(**self._parsed_msg["word"])

    def __parseFromArgs(self, **kwargs):
        self.type= kwargs["type"] if isinstance(kwargs["type"], MQTT_DATA_ACTIONS) else MQTT_DATA_ACTIONS(kwargs["type"])
        self.word= kwargs["word"] if isinstance(kwargs["word"], VocabItem) else VocabItem(**kwargs["word"])

    def asDict(self):
        return {
            "type": self.type.value if isinstance(self.type, MQTT_DATA_ACTIONS) else self.type,
            "word": self.word.asDict()
        }

class WordSelectBody(BodyObject):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.word=self._parsed_msg["word"] if self._parsed_msg else kwargs["word"]
        self.selected=self._parsed_msg["selected"] if self._parsed_msg else kwargs["selected"]

class GameContoursBody(BodyObject):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.contours=self._parsed_msg["contours"] if self._parsed_msg else kwargs["contours"]

topic_body = {
    Topics.CONTROL : ControlCommandBody,
    Topics.STATE : GameStateBody,
    Topics.CONTOURS : GameContoursBody,
    Topics.word_state() : WordStateBody,
    Topics.word_select() : WordSelectBody,
}

def BodyForTopic(topic: str, payload: dict | str | list) -> BodyObject:
    res= None
    body_class = topic_body[Topics.get_generic_topicname(topic)]

    if isinstance(payload, str): res = body_class(msg=payload)
    elif isinstance(payload, list):
        res = body_class(items=payload)
    elif isinstance(payload, dict):
        res = body_class(**payload)

    if hasattr(res, "timestamp"): 
        res.timestamp = time.time()
    return res
