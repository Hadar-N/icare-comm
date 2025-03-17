from logging import Logger
import threading

from game_shared import *
from .mqtt_base_class import MQTTInitialData, MQTTBaseClass
from .mqtt_topics import Topics
from .mqtt_body import BodyObject, BodyForTopic

class ConnectionManager:

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if not cls._instance:
                cls._instance = super(ConnectionManager, cls).__new__(cls)
                cls.__initialized = False
        return cls._instance

    def __init__(self):
        if self.__initialized:
            return

        self.__initialized = False

    @property
    def current_game_status(self) -> GAME_STATUS:
        return self.__game_status
    
    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance
        
    @classmethod    
    def initialize(cls, base: MQTTInitialData, role: DEVICE_TYPE, logger: Logger, handle_message:callable = None):
        instance = cls.get_instance()
        if cls.__initialized:
            return instance
        
        cls.__logger = logger
        cls.__role = role
        cls.__outer_handle_messages = handle_message

        # TODO: Old system- Remove!
        cls.__messages = []
        cls.__last_start_index = 0

        # TODO: New system- Activate!!
        cls.__active_words = {}
        cls.__game_status = GAME_STATUS.HALTED
        cls.__start_timestamp = 0

        cls.__mqtt_instance = MQTTBaseClass(
            base,
            cls.__logger,
            Topics.topics_per_role(cls.__role),
            instance.__handle_message
        )
        cls.__initialized = True

        return instance
    
    def is_initialized(self):
        return self.__initialized

    def close_connection(self) -> None:
        self.__mqtt_instance.__on_close()

    def publish_message(self, topic: str, msg: dict):
        body = BodyForTopic(topic, msg)
        if topic == Topics.CONTROL and body.command == MQTT_COMMANDS.START:
            self.__last_start_index = len(self.__messages)
        self.__mqtt_instance.publish_message(topic, body)

    def __update_status(self, new_status: GAME_STATUS, timestamp: float = None):
        self.__game_status = new_status
        if new_status == GAME_STATUS.ACTIVE:
            self.__start_timestamp = timestamp

    def __handle_message(self, topic:str, data: BodyObject):
        if Topics.is_word_state(topic):
            """TODO: add word to active"""
        elif topic == Topics.STATE:
            self.__update_status(data.state)
        elif topic == Topics.DATA:
            self.__messages.append(data.items)

        if self.__outer_handle_messages: self.__outer_handle_messages(topic = topic, data = data)
    
    def get_words(self):
        # return [v for k,v in self.__active_words.items() if v.timestamp > self.__start_timestamp]
        return self.__messages[self.__last_start_index:]
    