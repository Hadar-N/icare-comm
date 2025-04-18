from logging import Logger
import threading
import queue

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

    def get_current_game_status(self) -> GAME_STATUS: return self.__game_status
    
    def get_matched_list(self) -> list: return self.__matched_words

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

        cls.__matched_words = []
        cls.__read_queue = {}
        cls.__game_status = GAME_STATUS.HALTED

        cls.__mqtt_instance = MQTTBaseClass(
            base,
            cls.__logger,
            Topics.topics_per_role(cls.__role),
            instance.__handle_message
        )
        cls.__initialized = True

        return instance
                
    @classmethod
    def close_connection(cls) -> None:
        instance = cls.get_instance()
        if instance: cls.__mqtt_instance.close_client()

    def register_device(self, device_id: str):
        self.__read_queue[device_id] = queue.Queue()
        
    def is_initialized(self):
        return self.__initialized

    def publish_message(self, topic: str, msg: dict) -> None:
        body = BodyForTopic(topic, msg)
        self.__mqtt_instance.publish_message(topic, body)

    def __update_status(self, new_status: GAME_STATUS, timestamp: float = None):
        self.__game_status = new_status
        if self.__game_status == GAME_STATUS.ACTIVE:
            self.__read_queue = {}
            self.__matched_words = []

    def __handle_message(self, topic:str, data: BodyObject):
        asdict = data.bodyToDict()
        if topic == Topics.STATE:
            self.__update_status(data.state)
        elif Topics.is_word_state(topic):
            for d_id in self.__read_queue:
                self.__read_queue[d_id].put(asdict)
            if data.type == MQTT_DATA_ACTIONS.MATCHED: self.__matched_words.append(asdict)

        if self.__outer_handle_messages: self.__outer_handle_messages(topic = topic, data = asdict)
    
    def get_device_msg(self, device_id):
        res= None
        if device_id in self.__read_queue:
            try:
                res= self.__read_queue[device_id].get()
            except queue.Empty:
                pass
        else:
            raise ValueError(device_id)
        return res
    