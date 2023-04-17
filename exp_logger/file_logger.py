from datetime import datetime
import time
import csv
import os

class Logger:
    def __init__(self,path: str,file_name:str = "sensors") -> None:
        path = os.path.join(path,f'{file_name}_{datetime.now().strftime("%m-%d-%Y_%H:%M:%S")}.csv')
        self.data_file = open(path, 'w')
        self.writer = csv.writer(self.data_file)
        self.header = False

    def log(self, data:dict) -> None:
        if not self.header:
            self.header = True
            self.writer.writerow(data.keys())
        self.writer.writerow(data.values())

    def close_file(self) -> None:
        self.data_file.close()
    
    def __dell__(self):
        self.close_file()

if __name__ == "__main__":
    logger = Logger('raw_data','action')
    driving_mode = 1
    packet = {"prediction":driving_mode,"timestamp": time.time()}
    while True:
        logger.log(packet)
        time.sleep(1)