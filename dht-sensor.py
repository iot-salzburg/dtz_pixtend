#!/usr/bin/env python3
import sys
import time
import psutil
import Adafruit_DHT
from socket import gethostname
import paho.mqtt.publish as publish


mqtt_broker = "il081"
host = gethostname()

while True:

    humidity, temperature = Adafruit_DHT.read_retry(11, 4, retries=15,
                                                    delay_seconds=2)
    msgs = list()
    if humidity is not None:
        msg = ("{0}/humidity".format(host), humidity, 0, False)
        msgs.append(msg)
    
    if temperature is not None:
        msg = ("{0}/temperature".format(host), temperature, 0, False)
        msgs.append(msg)        
        
    try:
        print('Temp: {} C  Humidity: {} %'.format(temperature, humidity))
    except TypeError:
        print("Couldn't parse a value, {} C / {} %".format(temperature, humidity))
    
    try:
        publish.multiple(msgs, hostname=mqtt_broker)
    except Exception as e:
        print("Cannot publish message, keep trying: ", e)

    
    time.sleep(10)
    