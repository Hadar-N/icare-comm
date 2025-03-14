from logging import Logger
import threading
import time

from game_shared import *
from .mqtt_base_class import MQTTInitialData, MQTTBaseClass
from .mqtt_topics import Topics
from .mqtt_body import BodyObject

class ConnectionManager:

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args):
        with cls._lock:
            if not cls._instance:
                cls._instance = super(ConnectionManager, cls).__new__(cls)
                cls.__initialized = False
        return cls._instance

    def __init__(self, base: MQTTInitialData, role: DEVICE_TYPE, logger: Logger, handle_message:callable):
        if self.__initialized:
            return

        self.__logger = logger
        self.__role = role
        self.__outer_handle_messages = handle_message

        # TODO: Old system- Remove!
        self.__messages = []
        self.__last_start_index = 0

        # TODO: New system- Activate!!
        self.__active_words = {}
        self.__game_status = GAME_STATUS.HALTED
        self.__start_timestamp = 0

        self.__mqtt_instance = MQTTBaseClass(base,
            self.__logger,
            self.subscribed_topics,
            self.__handle_message
        )

    @property
    def subscribed_topics(self) -> list[str]:
        if (self.__role == DEVICE_TYPE.CONTROL):
            return [ Topics.STATE, Topics.word_state(), Topics.DATA ]
        else: return [ Topics.CONTROL, Topics.word_select() ]

    @property
    def current_game_status(self) -> GAME_STATUS:
        return self.__game_status

    def close_connection(self) -> None:
        self.__mqtt_instance.__on_close()

    def publish_message(self, topic: str, msg: BodyObject):
        if topic == Topics.CONTROL and msg.command == MQTT_COMMANDS.START:
            self.__last_start_index = len(self.__messages)
        self.__mqtt_instance.publish_message(topic, msg)

    def __update_status(self, new_status: GAME_STATUS, timestamp: float = None):
        self.__game_status = new_status
        if new_status == GAME_STATUS.ACTIVE:
            self.__start_timestamp = timestamp

    def __handle_message(self, topic:str, data: BodyObject):
        if Topics.is_word_state(topic):
            """TODO: add word to active"""
        elif topic == Topics.STATE:
            self.__update_status(data.status)
        elif topic == Topics.DATA:
            self.__messages.append(data)

        self.__outer_handle_messages(topic, data)
    
    def get_words(self):
        # return [v for k,v in self.__active_words.items() if v.timestamp > self.__start_timestamp]
        return self.__messages[self.__last_start_index:]
    