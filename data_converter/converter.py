
import configparser
import struct

class MC_Converter:
    def __init__(self, conf_file: str):
        self.conf_file = conf_file
        self.cofig = configparser.ConfigParser()
        self.cofig.read(conf_file)
        self.inputs = self.cofig.items('INPUT')
        self.outputs = self.cofig.items('OUTPUT')
        self.input_dict,self.output_dict = self.input_output_dict()

    def input_output_dict(self):
        input_dict = {}
        for data in self.inputs:
            input_dict[data[0].split('data_type')[0].replace('\t0','').strip()] = 0.0
        output_dict = {}
        for data in self.outputs:
            output_dict[data[0].split('data_type')[0].replace('\t0','').strip()] = 0.0

        myKeys = list(input_dict.keys())
        myKeys.sort()
        input_dict = {i: input_dict[i] for i in myKeys}

        myKeys = list(output_dict.keys())
        myKeys.sort()
        output_dict = {i: output_dict[i] for i in myKeys}

        return input_dict,output_dict

   
    def encode(self, data: dict):
        byte_array = b""
        for val in data.values():
            byte_array += struct.pack("f", val)
        
        return byte_array
    
    def decode(self, data: bytes):
        

        decoded_data = self.input_dict.copy()
        float_list = []
        for i in range(0, len(data), 4):
            f = struct.unpack('f', data[i:i+4])[0]
            float_list.append(f)
        if len(data) == 8:
            decoded_data = {"timestamp": 0.0, "prediction": 0.0}
        for i,key in enumerate(decoded_data.keys()):
            decoded_data[key] = float_list[i]

        return decoded_data


if __name__ == '__main__':
    my_converter = MC_Converter('example.ini')
    data = {'acclat': 0.9, 'acclong': 0.0, 'accpitch': 0.0, 'accroll': 0.0, 'accvert': 0.0, 'accyaw': 0.0, 'asteer': 0.0, 'battery_state_of_charge': 0.0, 'commandid': 0.0, 'datalen': 0.0, 'messageidx': 0.0, 'msteer': 0.0, 'ngear': 0.0, 'nwheelspeedfl': 0.0, 'nwheelspeedfr': 0.0, 'nwheelspeedrl': 0.0, 'nwheelspeedrr': 0.0, 'pls_state': 0.0, 'ratepitch': 0.0, 'rateroll': 0.0, 'rateyaw': 0.0, 'rbrake': 0.0, 'rbrakebias': 0.0, 'rclutch': 0.0, 'rthrottle': 0.0, 'rwheelslipfl': 0.0, 'rwheelslipfr': 0.0, 'rwheelsliprl': 0.0, 'rwheelsliprr': 0.0, 'rwingrear': 0.0, 'spare01': 0.0, 'spare02': 0.0, 'spare03': 0.0, 'spare04': 0.0, 'spare05': 0.0, 'spare06': 0.0, 'spare07': 0.0, 'spare08': 0.0, 'spare09': 0.0, 'spare10': 0.0, 'telapsedtime': 0.0, 'timestamp': 0.0, 'vcar': 0.0, 'wengine': 0.0}
    a = my_converter.encode(data)
    #print(a)
    b = my_converter.decode(a)
    print(b)
