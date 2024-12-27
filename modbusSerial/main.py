
from wifi import WiFiManager
from MqttClient import Mqtt
from modbus_connector import ModbusCon
from utilits import get_local_config,get_modbus_config
from time import time,time_ns,sleep
import json
import  gc   
    
def main():
    while True :
        gc.collect()
        wifiObject = WiFiManager()
        mqttConnection = None
        try:
            localConfig = get_local_config()
            modbusConfig = get_modbus_config()
            print(wifiObject.sta.isconnected())
            if not wifiObject.sta.isconnected() and localConfig.get('ssid',None) and modbusConfig:
                wifiObject.STA(ssid= localConfig.get('ssid',None),password=localConfig.get('wifi-password',None))
            if not wifiObject.sta.isconnected():
                wifiObject.AP()
            if wifiObject.sta.isconnected() and localConfig.get('url',None):
                mqttObject = Mqtt() 
                mqttConnection = mqttObject.connect(localConfig)
                if mqttConnection and modbusConfig : 
                    modbusObject = ModbusCon(mqttObject)
                    modbusConnection = modbusObject.connect(modbusConfig)
                    retry_count = 0
                    max_retries = 5
                    while retry_count < max_retries or wifiObject.sta.isconnected() :
                        modbusRead=modbusObject.read()
                        if not modbusRead:
                            retry_count += 1
                            data= {'name': 'modbus_error',
                                    "value":"connection_error",
                                    "ts": time_ns() // 1_000_000
                                    }
                            mqttObject.Publisher(json.dumps(data))
                        sleep(5)

                    del modbusObject
                del mqttObject
                wifiObject.AP()

        except Exception or KeyboardInterrupt as e:
            print(f'stop ......{e}')


if __name__ == "__main__":
    main()