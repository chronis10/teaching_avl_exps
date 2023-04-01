from multiprocessing import Lock, Process, Queue, current_process
from external_com.UDP_bytes.reciever import UDP_Reciever
from external_com.UDP_bytes.transmiter import UDP_Transmitter
from external_com.tr_interfaces.reciever_transmitter_interfaces import Transmitter,Reciever
from data_converter.converter import MC_Converter
import time
import random

def data_reciever_service(reciever: Reciever) -> None:
    reciever.start_receiving()

def predictor_service(incoming_queue: Queue,transmiter: Transmitter,model_path:str) -> None:
    if not TEST_COMS:
        from ai_module.personalization import Personalization_Model
        per_model = Personalization_Model(model_path)
    while True:        
        if not incoming_queue.empty():
            #FIXME I don't know a better way
            while not incoming_queue.empty():        
                data = incoming_queue.get()
            print(f'Incoming data: {data}')
            if data is not None:
                try:
                    if TEST_COMS:
                        prediction = random.randint(0,3)
                    else:
                        prediction = per_model.prediction(data)
                    packet = {"prediction":prediction,"timestamp": time.time()}
                    transmiter.send(packet)
                    print(f'Transimited: {packet}')
                except Exception as e:
                    print(e)
            
def main(sensors_address: dict,mc_address:dict,model_path:str,ini_path:str) -> None:

    bytes_converter = MC_Converter(ini_path)
    incoming_queue = Queue() 
    reciever = UDP_Reciever(sensors_address['ip'], sensors_address['port'], incoming_queue,bytes_converter)
    transmiter = UDP_Transmitter(mc_address['ip'], mc_address['port'],bytes_converter)

    reciever_process = Process(target=data_reciever_service, args=(reciever,),daemon=True)
    model_path='pers_hua.h5'
    predictor_process = Process(target=predictor_service, args=(incoming_queue,transmiter,model_path,),daemon=True)
    reciever_process.start()
    predictor_process.start()
    
    predictor_process.join()
    print('Predictor Terminated')
    reciever_process.join()
    print('Reciever Terminated')
 
if __name__ == '__main__':
    TEST_COMS = True
    sensors_address = {'ip':"127.0.0.1",'port':20001} #Data input from MC
    mc_address = {'ip':"127.0.0.1",'port':20002} #Prediciton output to MC
    model_path = 'pers_hua.h5'
    ini_path = 'example.ini'
    main(sensors_address,mc_address,model_path,ini_path)