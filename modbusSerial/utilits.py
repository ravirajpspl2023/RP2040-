
import os 
import json
from machine import Pin
import time



LOCAL_CONFIG = 'local.json'
MODBUS_CONFIG = 'modbus.json'
CHUNK_SIZE = 1024
AP_IF_PIN = Pin(15, Pin.IN)
LED = Pin('LED',Pin.OUT)

def APPin():
    start_time = time.time()
    initial_state = AP_IF_PIN.value()
    LED.on()
    while time.time() - start_time < 5:
        current_state = AP_IF_PIN.value()
        if initial_state != current_state:
            LED.off()
            return True
    LED.off()
    return False
def get_local_config():
    if LOCAL_CONFIG in filelist() :
         with open(LOCAL_CONFIG, 'r') as file:
             return json.load(file)
    return {}
def get_modbus_config():
    if MODBUS_CONFIG in filelist() :
         with open(MODBUS_CONFIG, 'r') as file:
             return json.load(file)
    return {}
def write_local_config(config):
    with open(LOCAL_CONFIG, "w") as local_json:
        json.dump(config, local_json)
def write_modbus_config(config):
    with open(MODBUS_CONFIG, "w") as modbus_json:
        json.dump(config, modbus_json)
        
def text_respons(size=None):
    header=f"""HTTP/1.0 200 OK\r\nContent-Type: text/html; charset=utf-8\r\nContent-Encoding: gzip\r\nContent-Length: {size}\r\n\r\n"""
    return header.encode('utf-8')

def filelist():
    return os.listdir('/')