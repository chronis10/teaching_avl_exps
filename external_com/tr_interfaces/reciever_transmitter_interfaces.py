from abc import ABC,abstractmethod 


class Transmitter(ABC):

    @abstractmethod     
    def send(self,message: dict)-> None:
        pass

class Reciever:

    @abstractmethod  
    def start_receiving(self)-> None:
        pass
