import socket
import json
from multiprocessing import Queue
from external_com.tr_interfaces.reciever_transmitter_interfaces import Reciever
import time
import paho.mqtt.client as mqtt


class MQTT_Reciever(Reciever):
    def __init__(self, broker: str, port: int, topic: str, packet_queue: Queue) -> None:
        self.broker = broker
        self.port = port
        self.topic = topic
        self.packet_queue = packet_queue
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(self.broker, self.port, 60)

    def on_connect(self, client, userdata, flags, rc) -> None:
        print('Connected with result code {rc}')
        client.subscribe(self.topic)

    def on_message(self, client, userdata, msg) -> None:
        message = json.loads(msg.payload)
        self.packet_queue.put(message)

    def start_receiving(self)-> None:
        self.client.loop_forever()

    def __del__(self) -> None:
        self.client.disconnect()


if __name__ == '__main__':
    test_queue = Queue()
    my_receiver = MQTT_Reciever('localhost&apos', 1883, 'mytopic', test_queue)
    my_receiver.start_receiving()