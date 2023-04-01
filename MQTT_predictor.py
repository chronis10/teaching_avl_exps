from multiprocessing import Lock, Process, Queue, current_process
from external_com.MQTT_com.reciever import MQTT_Reciever
from external_com.MQTT_com.transmitter import MQTT_Transmitter
from ai_module.personalization import Personalization_Model
from external_com.tr_interfaces.reciever_transmitter_interfaces import Transmitter,Reciever
import time


def data_reciever_service(reciever: Reciever) -> None:
    reciever.start_receiving()

def predictor_service(incoming_queue: Queue,transmiter: Transmitter,model_path:str) -> None:
    per_model = Personalization_Model(model_path)
    while True:        
        if not incoming_queue.empty():
            #FIXME I dont know a better way
            while not incoming_queue.empty():        
                data = incoming_queue.get()
            print(data)
            if data is not None:
                try:
                    prediction = per_model.prediction(data)
                    transmiter.send(prediction)
                    print(f'Transimited {prediction}')
                except Exception as e:
                    print(e)
            
def main(sensors_address: dict,mc_address:dict,model_path:str) -> None:
    incoming_queue = Queue() 
    reciever = MQTT_Reciever(sensors_address['ip'], sensors_address['port'],sensors_address['sensors_topic'], incoming_queue)
    transmiter = MQTT_Transmitter(mc_address['ip'], mc_address['port'],mc_address['predictions_topic'])

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
    sensors_broker = {'ip':"127.0.0.1",'port':1883,'sensors_topic':'sensors'}
    mc_broker = {'ip':"127.0.0.1",'port':1883,'predictions_topic':'ai_predictions'}
    model_path = 'pers_hua.h5'
    main(sensors_broker,mc_broker,model_path)