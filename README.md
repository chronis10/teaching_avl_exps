# Instructions

! Use the ini file from the MC

### Test communication

``` python3 main.py  --mode 0 ```

### Personalization mode

Tensoflow needed

``` python3 main.py  --mode 1 --profiles drivers.yaml --driver <1...n>```

### Manual mode

The driving mode change base on the right Nitendo Switch controller(SR/SL buttons).

``` python3 main.py  --mode 2 ```

### Scenario mode

``` python3 main.py  --mode 3 --profiles drivers.yaml --driver <1...n>```

### Use an external ini 

Default example.ini

``` --ini avl.ini ```

### Record data and actions in csv 
1 True - 0 Flase

``` --logger 1 ```

### About drivers.yaml
Contains info about drivers preferences and the path for the trainned model.
The preferences used only in mode 3 and the path only in mode 1.

```
driver1:
  speed: 50
  angv: 2.0
  normal: 2
  turns: 1
  model_path: models/driver1.h5 
  ```
