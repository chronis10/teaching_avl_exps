import socket
import json
from multiprocessing import Queue
from external_com.tr_interfaces.reciever_transmitter_interfaces import Reciever
import time

class UDP_Reciever(Reciever):

    def __init__(self, ip: str, port: int, packet_queue: Queue) -> None:
        self.ip = ip
        self.port = port
        self.bufferSize = 1024
        self.packet_queue = packet_queue
        self.UDPClientSocket  = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.UDPClientSocket.bind((self.ip, self.port))
        print("UDP Reciever up and listening")

    def start_receiving(self)-> None:
        while(True):
            msgFromServer = self.UDPClientSocket.recvfrom(self.bufferSize)
            message = json.loads(msgFromServer[0])
            self.packet_queue.put(message)
            #print(message)

    def __del__(self) -> None:
        self.UDPClientSocket.close()

if __name__ == '__main__':
    test_queue = Queue()
    my_reciever = UDP_Reciever("127.0.0.1", 20001,test_queue)
    my_reciever.start_receiving()