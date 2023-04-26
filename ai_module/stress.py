from typing import Dict
import torch
import numpy as np
import time
import torch_esn
import torch.nn.functional as F
from stress_preprocessor.preprocessors.preprocessor import StressPreprocessor
from stress_preprocessor.config import Config
from copy import deepcopy


class StressModel:
    def __init__(self, model_path: str, preprocessor_config: Dict) -> None:
        self.preprocessor = StressPreprocessor(**preprocessor_config)
        self.model = torch.load(model_path)
        self.reservoir = self.model["reservoir"]
        self.readout = self.model["readout"]

    def prediction(self, obs: dict) -> int:
        data = self.preprocessor.online_run(obs)
        if data is not None:
            data = torch.from_numpy(data)
            prediction = F.linear(self.reservoir(data), self.readout)
            for i in range(len(prediction)):
                self.to_packet(prediction[i])
            return prediction

    def to_packet(self, prediction: np.ndarray) -> dict:
        return {
            "timestamp": time.time(),
            "source": "stress",
            "prediction": prediction.item(),
        }


if __name__ == "__main__":
    test_data = {
        "timestamp": 0.01,
        "GSR": 1.542,
        "ECG": 0.666,
        "Ego_Acceleration_y": 22.343395231146733,
        "Ego_VehicleSpeed": 88.57635631272902,
        "Ego_YawRate": 43.4908623331544,
        "Vehicle.Heading": 10.88244511068094,
        "Ego_Acceleration_x": 45.507506109324396,
        "Ego_SteeringWheelAngle": 172.0640909383301,
        "Vehicle.Engine.Engine Speed": 97.65959727767375,
        "Vehicle.Engine.Engine Torque": 37.03680751673738,
        "Vehicle.Acceleration Vertical": 9.332813872693817,
        "Speed_limit": 41.158294325800554,
        "Lat": 48.06207549472028,
        "Long": 39.83177553805778,
    }

    predictor = StressModel(
        "models/stress_model.pkl",
        {
            "config": Config(
                "/Users/vdecaro/Desktop/teaching_avl_exps/stress_preprocessor/config/config.json"
            ),
            "online": True,
            "baseline_path": "/Users/vdecaro/Desktop/teaching_avl_exps/models/DATA_OUT_in.csv",
            "buffer_size": 1000,
        },
    )
    for i in range(200):
        a = predictor.prediction(deepcopy(test_data))
        test_data["timestamp"] += 0.01
        if a is not None:
            print(a)
