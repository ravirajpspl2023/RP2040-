import network ,machine
import ntptime
from utilits import get_local_config,LED
import socket
from time import sleep,time
from httpRequest import HTTP_Request
class WiFiManager:
    def __init__(self, ):
        # Initialize AP settings
        self.ap_ssid = 'humac'
        self.ap_password = 'humac@2023'
        self.ssid = '402DEV'
        self.password = 'TechDev402'
        self.ap = network.WLAN(network.AP_IF)
        self.sta = network.WLAN(network.STA_IF)
        self.ap.config(essid=self.ap_ssid, password=self.ap_password)
        self.sock_respons = HTTP_Request(self)
        self.s= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sta.active(False)
        self.ap.active(False)
    def sock(self):
        try:
            self.s.bind(('0.0.0.0',80))
        except Exception :
            self.s.close()
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.bind(('0.0.0.0',80))
        self.s.settimeout(30)
        self.s.listen(1)
    def setTime(self,):
        retry_count = 0
        max_retries = 5
        while retry_count < max_retries:
            try:
                ntptime.settime()
                print(f'time is set {time()}')
                return
            except Exception as e:
                retry_count += 1
                print(f'exception in set time {e}')
                sleep(1)
        if retry_count == max_retries:
            if self.sta.isconnected():
                print(f'disconnecte current wifi { self.sta.config('ssid')}')
                self.sta.disconnect()
                while self.sta.isconnected():
                    pass
            machine.reset()

    def AP(self):
        if self.sta.isconnected():
            print('disconnect current wifi ')
            self.sta.disconnect()
        self.sta.active(False)
        self.sock()
        self.ap.active(True)
        print('AP ACTIVETE ...')
        ApStart =time()
        while time()-ApStart < 20 or not get_local_config():
            clients=self.ap.status('stations')
            LED.on()
            if clients:
                try:
                    LED.on()
                    print('socket start .....')
                    cl, addr = self.s.accept()
                    if cl and addr :
                        self.sock_respons.handle_request(cl)
                        cl.close()
                    ApStart=time()
                except Exception as e:
                    ApStart=time()
            sleep(0.5)
            LED.off()
        
        self.s.close()
        self.ap.active(False)
        sleep(1)

    def scan_networks(self):
        self.sta.active(True)
        networks = self.sta.scan()
        print("Networks found:", networks)
        self.AP()
        return networks

    def STA(self, ssid="", password=""):
        if ssid and password :
            self.ssid=ssid
            self.password = password
        print('STA ACTIVATE...')
        if self.sta.isconnected() and self.ssid==self.sta.config('ssid'):
            print(f'wifi allredy connected :{self.ssid}')
            self.sta.disconnect()
            sleep(5)  
        self.sta.active(True)
        print(self.sta.ifconfig()) 
        sleep(1)
        self.sta.connect(ssid=self.ssid, key=self.password) 
        StaStart = time()
        while time()-StaStart < 20 :
            LED.on()
            print(self.sta.status())
            if 0 < self.sta.status() <= 3:
                print('wifi is availabale ...')
            if self.sta.status() <=0:
                print('wifi is not available ...')
            if self.sta.isconnected():
                print("Connected to:", self.ssid)
                sleep(5)
                LED.off()
                self.setTime()
                break
            sleep(1)
            LED.off()
    
 