# TEACHING AVL EXPS

## Predictors
The *_predictors.py files are both examples of the final evaluation scripts. For now, they are loaded with a dummy model, but later the model will be replaced with the final trained model.

### UDP_predictor 
This script creates a transmitter and a receiver based on UDP communication.

1. Start the ```fake_mc_UDP.py```
2. Start the ```UDP_predictor.py```

### MQTT_predictor 
This script creates a transmitter and a receiver based on MQTT communication.

1. ```docker run -it  -p 1883:1883 -p 9001:9001 -v $(pwd)/mosquitto.conf:/mosquitto/config/mosquitto.conf --rm eclipse-mosquitto```
1. Start the ```fake_mc_MQTT.py```
2. Start the ```MQTT_predictor.py```

You can also create a mix of the two, for example, MQTT_Receiver and UDP_Transmitter, and have a new predictor MQTT_Receiver and UDP_Transmitter.

## Testing

The fake_mc_UDP.py and fake_mc_MQTT.py scripts are both transceivers, but each one uses a different communication protocol (UDP, MQTT). The scripts are created in order to simulate the sensor source component and the MC component.

You can also create a mix of the two, for example, MQTT_Receiver and UDP_Transmitter.