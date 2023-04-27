from typing import Dict
import numpy as np
import time
from stress_preprocessor.preprocessors.preprocessor import StressPreprocessor
from stress_preprocessor.config import Config
from copy import deepcopy

subj_params = {
    "4022": (0.08, 100),
    "4396": (0.15, 300),
    "1018": (0.08, 300),
    "4181": (0.20, 300),
    "4235": (1.00, 100),
    "4392": (1.25, 100),
}


class StressModel:
    def __init__(self, subj_id: str, preprocessor_config: Dict) -> None:
        self.preprocessor = StressPreprocessor(**preprocessor_config)
        self.buffer_size = preprocessor_config["buffer_size"]
        self.threshold, self.window_size = subj_params[subj_id]

    def prediction(self, obs: dict) -> int:
        data = self.preprocessor.online_run(obs)
        if data is not None:
            data["pred"] = (
                data.rolling(10).mean().apply(lambda x: 1 if x > self.threshold else 0)
            )
            data["smooth_pred"] = (
                data["pred"].ewm(com=self.window_size, adjust=True).mean()
            )

            return data["smooth_pred"].iloc[-1]

    def to_packet(self, prediction: np.ndarray) -> dict:
        return {
            "timestamp": time.time(),
            "source": "stress",
            "prediction": prediction.item(),
        }


if __name__ == "__main__":
    import random

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
        "1018",
        {
            "config": Config(
                "/Users/vdecaro/Desktop/teaching_avl_exps/stress_preprocessor/config/config.json"
            ),
            "online": True,
            "baseline_path": "/Users/vdecaro/Desktop/teaching_avl_exps/models/DATA_OUT_in.csv",
            "buffer_size": 1000,
        },
    )
    for i in range(800):
        a = predictor.prediction(deepcopy(test_data))
        test_data["timestamp"] += 0.01
        test_data["GSR"] += random.random() * 2 - 1
        test_data["ECG"] += random.random() * 2 - 1

        if a is not None:
            print(a)
