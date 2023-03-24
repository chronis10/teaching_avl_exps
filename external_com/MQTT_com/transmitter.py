import paho.mqtt.client as mqtt
import time
import json
from external_com.tr_interfaces.reciever_transmitter_interfaces import Transmitter


class MQTT_Transmitter(Transmitter):
    def __init__(self, broker: str, port: int, topic: str)-> None:
        self.broker = broker
        self.port = port
        self.topic = topic
        self.client = mqtt.Client()
        self.client.connect(self.broker, self.port, 60)

    def send(self, message: dict) -> None:
        self.client.publish(self.topic, json.dumps(message))

    def __del__(self) -> None:
        self.client.disconnect()


if __name__ == '__main__':
    my_transmiter = MQTT_Transmitter('localhost', 1883, 'mytopic')
    i = 0
    while True:
        packet = {'timestap': time.time(), 'source': 'ai','value': i }
        my_transmiter.send(packet)
        i+=1
        time.sleep(0.5)