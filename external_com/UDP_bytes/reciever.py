import socket
import json
from multiprocessing import Queue
from external_com.tr_interfaces.reciever_transmitter_interfaces import Reciever
import time
from data_converter.converter import MC_Converter

class UDP_Reciever(Reciever):

    def __init__(self, ip: str, port: int, packet_queue: Queue,converter: MC_Converter) -> None:
        self.ip = ip
        self.port = port
        self.bufferSize = 1024
        self.packet_queue = packet_queue
        self.UDPClientSocket  = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.UDPClientSocket.bind((self.ip, self.port))
        self.converter = converter
        print("UDP Reciever up and listening")

    def start_receiving(self)-> None:
        while(True):
            msgFromServer = self.UDPClientSocket.recvfrom(self.bufferSize)
            message = self.converter.decode(msgFromServer[0])
            self.packet_queue.put(message)
            

    def __del__(self) -> None:
        self.UDPClientSocket.close()
