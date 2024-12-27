from lib.umqtt.simple import MQTTClient
from utilits import LED
from time import sleep

class Mqtt():
    
    def __init__(self) :
        self.LED = LED

    def connect(self,config): 
        try:
            self.config=config
            self.client = MQTTClient(client_id='humac',server=self.config['url'],port=self.config['port'],
                                        user=self.config['username'],password=self.config['password'],keepalive=60)
            if self.config.get('edge-id',None):
                self.topic=f"{self.config.get('topic',None)}/{self.config.get('edge-id',None)}"
            else:
                self.topic=f"{self.config.get('topic',None)}"
            self.client.connect()
            print('mqtt client is coneeted ..')
            return True
        except Exception as e:
            print(f'mqtt client error {e}')
            return False

    def Publisher(self,message=None):
            self.LED.toggle()
            self.client.publish(self.topic,message) # type: ignore
            self.LED.toggle()
          
    def disconnect(self):
        self.client.disconnect() # type: ignore
        