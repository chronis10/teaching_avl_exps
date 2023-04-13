from multiprocessing import Lock, Process, Queue, current_process
from external_com.UDP_bytes.reciever import UDP_Reciever
from external_com.UDP_bytes.transmiter import UDP_Transmitter
from external_com.tr_interfaces.reciever_transmitter_interfaces import Transmitter,Reciever
from data_converter.converter import MC_Converter
import time
import random



def data_reciever_service(reciever: Reciever) -> None:
    reciever.start_receiving()

def sensor_transmiter_service(incoming_queue: Queue,transmiter: Transmitter) -> None:
    print('Started')
    while True:
        if not incoming_queue.empty():
            data = incoming_queue.get()
            print(f'Recieved {data}')
        sensors = {'acclat': 9.999, 'acclong': random.uniform(0, 50), 'accpitch': random.uniform(0, 50), 'accroll': random.uniform(0, 50),
                    'accvert': random.uniform(0, 50), 'accyaw': random.uniform(0, 50), 'asteer': random.uniform(0, 50), 'battery_state_of_charge': random.uniform(0, 50),
                    'commandid': random.uniform(0, 50), 'datalen': random.uniform(0, 50), 'messageidx': random.uniform(0, 50), 'msteer': random.uniform(0, 50), 'ngear': random.uniform(0, 50),
                    'nwheelspeedfl': random.uniform(0, 50), 'nwheelspeedfr': random.uniform(0, 50), 'nwheelspeedrl': random.uniform(0, 50), 'nwheelspeedrr': random.uniform(0, 50),
                    'pls_state': random.uniform(0, 50), 'ratepitch': random.uniform(0, 50), 'rateroll': random.uniform(0, 50), 'rateyaw': random.uniform(0, 50), 'rbrake': random.uniform(0, 50),
                    'rbrakebias': random.uniform(0, 50), 'rclutch': random.uniform(0, 50), 'rthrottle': random.uniform(0, 50), 'rwheelslipfl': random.uniform(0, 50), 'rwheelslipfr': random.uniform(0, 50),
                    'rwheelsliprl': random.uniform(0, 50), 'rwheelsliprr': random.uniform(0, 50), 'rwingrear': random.uniform(0, 50), 'spare01': random.uniform(0, 50), 'spare02': random.uniform(0, 50),
                    'spare03': random.uniform(0, 50), 'spare04': random.uniform(0, 50), 'spare05': random.uniform(0, 50), 'spare06': random.uniform(0, 50), 'spare07': random.uniform(0, 50), 'spare08': random.uniform(0, 50),
                    'spare09': random.uniform(0, 50), 'spare10': random.uniform(0, 50), 'telapsedtime': random.uniform(0, 50), 'timestamp': random.uniform(0, 50), 'vcar': random.uniform(0, 50), 'wengine': random.uniform(0, 50)}
            
       
        #print(sensors)
        transmiter.send(sensors)
       
        
if __name__ == '__main__':

    bytes_converter = MC_Converter("example.ini")
    incoming_queue = Queue() 
    reciever = UDP_Reciever("127.0.0.1", 20002, incoming_queue, bytes_converter)
    transmiter = UDP_Transmitter("127.0.0.1", 20001, bytes_converter)
    reciever_process = Process(target=data_reciever_service, args=(reciever,),daemon=True)
    sensor_transmiter = Process(target=sensor_transmiter_service, args=(incoming_queue,transmiter,),daemon=True)
    reciever_process.start()
    sensor_transmiter.start()
    sensor_transmiter.join()
    reciever_process.join()