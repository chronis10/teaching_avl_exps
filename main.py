from multiprocessing import Lock, Process, Queue, current_process
from external_com.UDP_bytes.reciever import UDP_Reciever
from external_com.UDP_bytes.transmiter import UDP_Transmitter
from external_com.tr_interfaces.reciever_transmitter_interfaces import Transmitter,Reciever
from data_converter.converter import MC_Converter
import time
import random
import argparse


def data_reciever_service(reciever: Reciever) -> None:
    reciever.start_receiving()


def manual_control(incoming_queue: Queue,transmiter: Transmitter) -> None:
    from pyjoycon import ButtonEventJoyCon, get_R_id
    joycon_id = get_R_id()
    joycon = ButtonEventJoyCon(*joycon_id)
    driving_mode = 1
    delay = 0.5
    timestart = 0
    transmiter.send({"handshake":0,"timestamp": time.time()})
    while True:
        if not incoming_queue.empty():
            #FIXME I don't know a better way
            while not incoming_queue.empty():
                data = incoming_queue.get()
            print(f'Incoming data: {data}')
        for event_type, status in joycon.events():
            
            
            if time.time() - timestart > delay:
                print(event_type, status)
                timestart = time.time()
                if event_type == 'right_sr' and status == 1:
                    driving_mode += 1
                    driving_mode = min(driving_mode,2)
                    packet = {"prediction":driving_mode,"timestamp": time.time()}
                    transmiter.send(packet)
                if event_type == 'right_sl' and status == 1:
                    driving_mode -= 1
                    driving_mode = max(driving_mode,0)
                    packet = {"prediction":driving_mode,"timestamp": time.time()}
                    transmiter.send(packet)
                print(f"Driving mode : {driving_mode}")

def test_coms(incoming_queue: Queue,transmiter: Transmitter) -> None:
    transmiter.send({"handshake":0,"timestamp": time.time()})
    while True:
        if not incoming_queue.empty():
            #FIXME I don't know a better way
            while not incoming_queue.empty():
                data = incoming_queue.get()
            print(f'Incoming data: {data}')
            if data is not None:
                try:
                    prediction = random.randint(0,3)
                    packet = {"prediction":prediction,"timestamp": time.time()}
                    transmiter.send(packet)
                    print(f'Transimited: {packet}')
                except Exception as error_message:
                    print(error_message)


def predictor_service(incoming_queue: Queue,transmiter: Transmitter,model_path:str ) -> None:
    from ai_module.personalization import Personalization_Model
    per_model = Personalization_Model(model_path)
    transmiter.send({"handshake":0,"timestamp": time.time()})
    while True:       
        if not incoming_queue.empty():
            #FIXME I don't know a better way
            while not incoming_queue.empty():
                data = incoming_queue.get()
            print(f'Incoming data: {data}')
            if data is not None:
                try:
                    prediction = per_model.prediction(data)
                    packet = {"prediction":prediction,"timestamp": time.time()}
                    transmiter.send(packet)
                    print(f'Transimited: {packet}')
                except Exception as error_message:
                    print(error_message)
            

if __name__ == '__main__':    
    argParser = argparse.ArgumentParser()
    argParser.add_argument("--mode", required=True, help="0 TEST COMS , 1 PERS HUA , 2 MANUAL CONTROL")
    argParser.add_argument("--ini", default='example.ini', help="MC ini file path")
    argParser.add_argument("--model", default='pers_hua.h5', help="Model path for personalization model")
    args = vars(argParser.parse_args())
    mode = int(args['mode'])

    sensors_address = {'ip':"127.0.0.1",'port':20001} #Data input from MC
    mc_address = {'ip':"127.0.0.1",'port':20002} #Prediciton output to MC
    
    ini_path = args['ini']
    bytes_converter = MC_Converter(ini_path)
    incoming_queue = Queue()
    reciever = UDP_Reciever(sensors_address['ip'], sensors_address['port'], incoming_queue,bytes_converter)
    transmiter = UDP_Transmitter(mc_address['ip'], mc_address['port'],bytes_converter)
    reciever_process = Process(target=data_reciever_service, args=(reciever,),daemon=True)
    reciever_process.start()

    if mode == 0:
        test_process = Process(target=test_coms, args=(incoming_queue,transmiter),daemon=True)
        test_process.start()
        test_process.join()
        print('Test Coms Terminated')
    elif mode == 1:
        
        model_path = args['model']
        predictor_process = Process(target=predictor_service, args=(incoming_queue,transmiter,model_path),daemon=True)
        predictor_process.start()
        predictor_process.join()
        print('Predictor Terminated')

    elif mode == 2:
        
        manual_control_process = Process(target=manual_control, args=(incoming_queue,transmiter,),daemon=True)
        manual_control_process.start()
        manual_control_process.join()
        print('Manual Control Terminated')

    reciever_process.join()
    print('Reciever Terminated')


