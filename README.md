# IoT Sensor Node

The node running this scripts is provides IoT
sensor data like temperature, humidity and energy
consumption. This data is sent via mqtt to a
local broker which integrates mqtt-based applications
into the dtz framework.

## Quickstart

### Installation of the sensor library

In a arbitrary folder:

```bash
git clone https://github.com/adafruit/Adafruit_Python_DHT.git

cd Adafruit_Python_DHT

sudo apt-get install build-essential python-dev3

sudo python3 setup.py install
```

In this git folder:
    
```bash
sudo pip3 install -r requirements.txt
```

### Starting the script
```bash
python3 dht-sensor.py
```


