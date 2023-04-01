import socket
import time
import json
from external_com.tr_interfaces.reciever_transmitter_interfaces import Transmitter

class UDP_Transmitter(Transmitter):

    def __init__(self, ip: str, port: int) -> None:
        self.ip = ip
        self.port = port
        self.bufferSize = 1024
        self.UDPClientSocket  = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        
    def send(self,message: dict)-> None:
        #print(f'Transmit {message}')
        bytesToSend = str.encode(json.dumps(message))
        self.UDPClientSocket.sendto(bytesToSend, (self.ip,self.port))

    def __del__(self) -> None:
        self.UDPClientSocket.close()

if __name__ == '__main__':
    my_transmiter = UDP_Transmitter("127.0.0.1", 20001)
    i = 0
    while True:
        packet = {'timestap': time.time(), 'source': 'ai','value': i }
        my_transmiter.send(packet)
        i+=1
        time.sleep(0.5)