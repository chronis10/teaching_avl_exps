import socket
import time
import json
from external_com.tr_interfaces.reciever_transmitter_interfaces import Transmitter
from data_converter.converter import MC_Converter

class UDP_Transmitter(Transmitter):

    def __init__(self, ip: str, port: int, converter: MC_Converter) -> None:
        self.ip = ip
        self.port = port
        self.bufferSize = 1024
        self.UDPClientSocket  = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.converter = converter
        
    def send(self,message: dict)-> None:
        #print(f'Transmit {message}')
        bytesToSend = self.converter.encode(message)
        self.UDPClientSocket.sendto(bytesToSend, (self.ip,self.port))

    def __del__(self) -> None:
        self.UDPClientSocket.close()
