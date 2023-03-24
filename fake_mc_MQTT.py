from multiprocessing import Lock, Process, Queue, current_process
from external_com.MQTT_com.reciever import MQTT_Reciever
from external_com.MQTT_com.transmitter import MQTT_Transmitter
from external_com.tr_interfaces.reciever_transmitter_interfaces import Transmitter,Reciever
import time
import random

def data_reciever_service(reciever: Reciever) -> None:
    reciever.start_receiving()

def sensor_transmiter_service(incoming_queue: Queue,transmiter: Transmitter) -> None:
    while True:
        if not incoming_queue.empty():
            data = incoming_queue.get()
            print(f'Recieved {data}')
        sensors = {'timestamp': time.time(),
                        'Ego_Acceleration_y' : random.uniform(0, 50),
                        'Ego_VehicleSpeed' : random.uniform(0, 180),
                        'Ego_YawRate' : random.uniform(0, 50),
                        'Vehicle.Heading' : random.uniform(0, 360),
                        'Ego_Acceleration_x' : random.uniform(0, 50),
                        'Ego_SteeringWheelAngle' : random.uniform(0, 360),
                        'Vehicle.Engine.Engine Speed' : random.uniform(0, 180),
                        'Vehicle.Engine.Engine Torque' : random.uniform(0, 180),
                        'Vehicle.Acceleration Vertical' : random.uniform(0, 50),
                        'Speed_limit' : random.uniform(0, 50),
                        'Lat': random.uniform(0, 90),
                        'Long': random.uniform(0, 90) }
        #print(sensors)
        transmiter.send(sensors)
        print('Transmited sensors data')
        
if __name__ == '__main__':
    incoming_queue = Queue() 
    reciever = MQTT_Reciever("127.0.0.1", 1883,'ai_predictions', incoming_queue)
    transmiter = MQTT_Transmitter("127.0.0.1", 1883,'sensors')
    reciever_process = Process(target=data_reciever_service, args=(reciever,),daemon=True)
    sensor_transmiter = Process(target=sensor_transmiter_service, args=(incoming_queue,transmiter,),daemon=True)
    reciever_process.start()
    sensor_transmiter.start()
    sensor_transmiter.join()
    reciever_process.join()

    