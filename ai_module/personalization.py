import tensorflow as tf
from tensorflow import keras
from keras import layers
from keras.models import Model, load_model
import tensorflow_addons as tfa
import numpy as np
import time


class Personalization_Model:

    def __init__(self,model_path:str) -> None:
        self.model = keras.models.load_model(model_path,custom_objects={'AdamW': tfa.optimizers.AdamW})

    def prediction(self,obs: dict ) -> int:
        obs_converted = self.convert(obs)
        prediction = self.model.predict(obs_converted)
        return self.to_packet(prediction)
    
    def convert(self, obs: dict) -> np.ndarray:
        obs.pop('timestamp',None)
        obs_list = list(obs.values())
        return np.expand_dims(np.array(obs_list),axis=0)
    
    def to_packet(self, prediction: np.ndarray) -> dict:
        return {'timestamp': time.time(), 'source': 'ai', 'prediction': int(np.argmax(prediction))}
    

def create_dummy():
    #just a dummy model
    optimizer = tfa.optimizers.AdamW(learning_rate=0.001, weight_decay=0.001)
    input = layers.Input(shape=(12,), name='policy_input')
    policy = layers.BatchNormalization()(input)
    policy = layers.Dense(128, activation="relu")(policy)
    policy = layers.BatchNormalization()(policy)
    policy = layers.Dense(64, activation="relu")(policy)
    policy = layers.BatchNormalization()(policy)
    policy = layers.Dense(32, activation="relu")(policy)
    policy = layers.BatchNormalization()(policy)
    policy = layers.Dense(16, activation="relu")(policy)
    logits = layers.Dense(3, activation = 'linear')(policy)
    model = Model(inputs=input, outputs=logits)
    model.compile(loss = 'mae', optimizer = optimizer, metrics = ['accuracy'])
    print(model.summary())
    model.save('pers_hua.h5')

if __name__ == "__main__":
    #create_dummy()
    test_data = {'timestamp': 1679608828.9645798, 'Ego_Acceleration_y': 22.343395231146733,
                 'Ego_VehicleSpeed': 88.57635631272902, 'Ego_YawRate': 43.4908623331544,
                 'Vehicle.Heading': 10.88244511068094, 'Ego_Acceleration_x': 45.507506109324396,
                 'Ego_SteeringWheelAngle': 172.0640909383301, 'Vehicle.Engine.Engine Speed': 97.65959727767375,
                 'Vehicle.Engine.Engine Torque': 37.03680751673738, 'Vehicle.Acceleration Vertical': 9.332813872693817,
                 'Speed_limit': 41.158294325800554, 'Lat': 48.06207549472028, 'Long': 39.83177553805778}
    
    predictor = Personalization_Model('pers_hua.h5')
    a = predictor.prediction(test_data)
    print(a)