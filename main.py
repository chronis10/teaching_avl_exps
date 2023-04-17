from multiprocessing import Lock, Process, Queue, current_process,Event
from external_com.UDP_bytes.reciever import UDP_Reciever
from external_com.UDP_bytes.transmiter import UDP_Transmitter
from external_com.tr_interfaces.reciever_transmitter_interfaces import Transmitter,Reciever
from data_converter.converter import MC_Converter
from exp_logger.file_logger import Logger
import time
import random
import argparse


def data_reciever_service(reciever: Reciever) -> None:
    reciever.start_receiving()

def get_last_data(incoming_queue: Queue,logger: Logger = None) -> dict:
    data = None
    if not incoming_queue.empty():
        while not incoming_queue.empty():
            data = incoming_queue.get()
            if logger is not None:
                logger.log(data)
    return data

def load_drivers(drivers_path:str ) -> dict:
    import yaml
    with open(drivers_path, 'r') as file:
        drivers_profiles = yaml.safe_load(file)
    return drivers_profiles

def manual_control(incoming_queue: Queue,transmiter: Transmitter,term_event: Event, logger: bool = False) -> None:
    from pyjoycon import ButtonEventJoyCon, get_R_id

    if logger:
        sensor_logger = Logger('raw_data','sensor')
        action_logger = Logger('raw_data','action')
        
    else:
        sensor_logger = None
        action_logger = None

    joycon_id = get_R_id()
    joycon = ButtonEventJoyCon(*joycon_id)
    driving_mode = 1
    delay = 0.1
    timestart = 0
    transmiter.send({"handshake":0,"timestamp": time.time()})
   
    while True:
        data = get_last_data(incoming_queue,sensor_logger)
        if data is not None:
            print(f'Incoming data: {data}')
        for event_type, status in joycon.events():
            if time.time() - timestart > delay:
                print(event_type, status)
                timestart = time.time()
                if event_type == 'right_sr' and status == 1:
                    driving_mode += 1
                    driving_mode = min(driving_mode,2)
                    packet = {"prediction":driving_mode,"timestamp": time.time()}
                    if action_logger is not None:
                        action_logger.log(packet)
                    transmiter.send(packet)
                if event_type == 'right_sl' and status == 1:
                    driving_mode -= 1
                    driving_mode = max(driving_mode,0)
                    packet = {"prediction":driving_mode,"timestamp": time.time()}
                    if action_logger is not None:
                        action_logger.log(packet)
                    transmiter.send(packet)
                print(f"Driving mode : {driving_mode}")
        if term_event.is_set():
            action_logger.close_file()
            sensor_logger.close_file()
            break


def test_coms(incoming_queue: Queue,transmiter: Transmitter) -> None:
    transmiter.send({"handshake":0,"timestamp": time.time()})
    while True:
        data = get_last_data(incoming_queue)
        if data is not None:
            print(f'Incoming data: {data}')
            try:
                prediction = random.randint(0,3)
                packet = {"prediction":prediction,"timestamp": time.time()}
                transmiter.send(packet)
                print(f'Transimited: {packet}')
            except Exception as error_message:
                print(error_message)


def predictor_service(incoming_queue: Queue,transmiter: Transmitter,current_driver: int,  profiles_path:str, term_event: Event, logger: bool = False  ) -> None:
    drivers_profiles = load_drivers(profiles_path)
    from ai_module.personalization import Personalization_Model
    per_model = Personalization_Model(drivers_profiles[f'driver{current_driver}']['model_path'])
    transmiter.send({"handshake":0,"timestamp": time.time()})
    if logger:
        sensor_logger = Logger('raw_data','sensor')
        action_logger = Logger('raw_data','action')
    else:
        sensor_logger = None
        action_logger = None
    
    while True:
        data = get_last_data(incoming_queue,sensor_logger)
        if data is not None:
            print(f'Incoming data: {data}')
            try:
                prediction = per_model.prediction(data)
                packet = {"prediction":prediction,"timestamp": time.time()}
                if action_logger is not None:
                    action_logger.log(packet)
                transmiter.send(packet)
                print(f'Transimited: {packet}')
            except Exception as error_message:
                print(error_message)
        if term_event.is_set():
            action_logger.close_file()
            sensor_logger.close_file()
            break

def preferences_based(incoming_queue: Queue,transmiter: Transmitter,current_driver: int,profiles_path:str, term_event: Event, logger: bool = False) -> None:
    
    drivers_profiles = load_drivers(profiles_path)
    max_speed = drivers_profiles[f'driver{current_driver}']['speed']
    max_angv = drivers_profiles[f'driver{current_driver}']['angv']
    normal = drivers_profiles[f'driver{current_driver}']['normal']
    turns = drivers_profiles[f'driver{current_driver}']['turns']
    transmiter.send({"handshake":0,"timestamp": time.time()})
    if logger:
        sensor_logger = Logger('raw_data','sensor')
        action_logger = Logger('raw_data','action')
    else:
        sensor_logger = None
        action_logger = None

    while True:
        data = get_last_data(incoming_queue,sensor_logger)
        if data is not None:
            print(f'Incoming data: {data}')
            try:
                if data['angv'] > max_angv:
                    prediction = turns
                elif data['speed'] > max_speed:
                    prediction = normal
                packet = {"prediction":prediction,"timestamp": time.time()}
                if action_logger is not None:
                    action_logger.log(packet)
                transmiter.send(packet)
                print(f'Transimited: {packet}')
            except Exception as error_message:
                print(error_message)
        if term_event.is_set():
            action_logger.close_file()
            sensor_logger.close_file()
            break

if __name__ == '__main__':    
    argParser = argparse.ArgumentParser()
    term_event = Event()
    argParser.add_argument("--mode", required=True, help="0 TEST COMS , 1 PERS HUA , 2 MANUAL CONTROL 3 PREFERENCES BASED")
    argParser.add_argument("--ini", default='example.ini', help="MC ini file path")
    argParser.add_argument("--profiles", default='drivers.yaml', help="Drivers info and models")
    argParser.add_argument("--driver", default=1, help="Current driver")
    argParser.add_argument("--logger", default=0, help="Save logs: 0 False 1 True")
    args = vars(argParser.parse_args())
    mode = int(args['mode'])
    driver = int(args['driver'])
    profiles_path = args['profiles']
    logger = bool(int(args['logger']))

    sensors_address = {'ip':"127.0.0.1",'port':20001} #Data input from MC
    mc_address = {'ip':"127.0.0.1",'port':20002} #Prediciton output to MC
    
    ini_path = args['ini']
    bytes_converter = MC_Converter(ini_path)
    incoming_queue = Queue()
    reciever = UDP_Reciever(sensors_address['ip'], sensors_address['port'], incoming_queue,bytes_converter)
    transmiter = UDP_Transmitter(mc_address['ip'], mc_address['port'],bytes_converter)
    
    
    try:
        reciever_process = Process(target=data_reciever_service, args=(reciever,),daemon=False)
        reciever_process.start()

        if mode == 0:
            actions_process = Process(target=test_coms, args=(incoming_queue,transmiter,),daemon=False)

        elif mode == 1:
            actions_process = Process(target=predictor_service, args=(incoming_queue,transmiter,driver,profiles_path,term_event,logger,),daemon=False)

        elif mode == 2:
            actions_process = Process(target=manual_control, args=(incoming_queue,transmiter,term_event,logger,),daemon=False)

        elif mode == 3:
            actions_process = Process(target=preferences_based, args=(incoming_queue,transmiter,driver,profiles_path,term_event, logger,),daemon=False)

        actions_process.start()

        actions_process.join()
        reciever_process.join()
        
    except KeyboardInterrupt:
        print("Keyboard interrupt")
    finally:
        term_event.set()
        # reciever_process.terminate()
        print('Reciever Process Terminated')
        # actions_process.terminate()
        print('Action Process Terminated')
    

