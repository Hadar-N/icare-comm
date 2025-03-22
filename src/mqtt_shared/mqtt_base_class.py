import os
import paho.mqtt.client as mqtt
from logging import Logger
import json
from dataclasses import dataclass

from .mqtt_body import BodyForTopic, BodyObject

@dataclass
class MQTTInitialData:
    port: str
    host: str
    username: str
    password: str

class MQTTBaseClass:
    def __init__(self, base: MQTTInitialData, logger: Logger, topics: list[str], handle_message: callable):        
        self.__logger = logger
        self.__topics = topics
        self.__handle_message = handle_message

        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self.__on_connect
        self.client.on_publish = self.__on_publish
        self.client.on_message = self.__on_message
        try:
            self.client.username_pw_set(username=base.username,password=base.password)
            self.client.connect(base.host, int(base.port))
            self.client.loop_start()
        except Exception as e:
            print("mqtt connection failed! error: ", e)

    def __on_connect(self, client, userdata, flags, rc, props):
        self.__logger.info("Connected with result code "+str(rc))
        print("Connected with result code "+str(rc))
        for topic in self.__topics:
            client.subscribe(topic)

    def close_client(self):
        self.client.disconnect()
        self.client.loop_stop()

    def __on_publish(self, client, userdata, mid, reason_code, properties):
        try:
            self.__logger.info('message published status: '+ str(reason_code))
            # TODO: error handling
        except KeyError:
            print(KeyError)

    def __on_message(self, client, userdata, msg):
        asstr= msg.payload.decode()
        self.__logger.info('message received: ' + asstr)
        data = BodyForTopic(msg.topic, asstr)
        self.__handle_message(msg.topic, data)
    
    def publish_message(self, topic: str, msg: BodyObject):
        msg_final = msg.parseToMsg()
        if not self.client.is_connected():
            self.__logger.error("Client disconnected")
            return
        msg_info = self.client.publish(topic, msg_final, qos=1)
        msg_info.wait_for_publish(timeout=1)
        self.__logger.info(f'publishing status {msg_info.is_published()} for topic: {topic} message: {msg_final}')
