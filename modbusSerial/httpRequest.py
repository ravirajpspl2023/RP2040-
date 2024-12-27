import json
from utilits import text_respons, get_local_config ,get_modbus_config,CHUNK_SIZE
from utilits import write_local_config,write_modbus_config
from time import sleep
from pages import page1,page2

class HTTP_Request():
    def __init__(self,wifi_manager=None):
        self.request = None
        self.wifi = wifi_manager
        self.conn = None
        self.config=get_local_config()
        self.modbus_config=get_modbus_config()
    
    def handle_request(self,conn):
        self.conn=conn
        self.request = self.conn.recv(1024).decode('utf-8')
        if self.request.startswith('GET'):
            self.HandleGET()
        elif self.request.startswith('POST'):
            self.HandlePOST()
        elif self.request.startswith('DELETE'):
            self.delete_element()
        
        else:
            print(self.request)

    def delete_element(self):
        if self.request and self.conn and "DELETE /delete" in self.request :
            body = self.request.split('\r\n\r\n')[1]
            jsondata = json.loads(body)
            print(f'request: { jsondata}')
            function_code = str(jsondata['functionCode'])
            if function_code in self.modbus_config['timeseries']:
                self.modbus_config['timeseries'][function_code] = sorted(
                        [item for item in self.modbus_config['timeseries'][function_code]
                        if item['address'] != jsondata['address']],
                        key=lambda x: x['address']
                    )
                if not self.modbus_config['timeseries'][function_code]:
                    del self.modbus_config['timeseries'][function_code]

                write_modbus_config(self.modbus_config)
                self.conn.sendall('HTTP/1.0 200 OK\r\nContent-type: application/json\r\n\r\n')
                self.conn.sendall(json.dumps({"status": "success"}))

    
    def HandleGET(self):
        page= page1()
        print(len(page))
        
        if self.request and self.conn and "GET /favicon.ico" in self.request:
            self.conn.send("HTTP/1.0 204 No Content\r\n\r\n") 

        if self.request and self.conn and "GET / " in self.request :
            self.conn.send(text_respons(len(page)))
            for i in range(0, len(page), CHUNK_SIZE):
                chunk = page[i:i+CHUNK_SIZE]
                self.conn.send(chunk)
        if self.request and self.conn and "GET /modbus-config" in self.request :
            self.config=get_local_config()
            if self.config.get('ssid',None) and self.config.get('url',None) and self.config.get('tenant-id',None):
                modbus_page= page2()
                self.conn.send(text_respons(len(modbus_page)))
                for i in range(0, len(modbus_page), CHUNK_SIZE):
                    chunk = modbus_page[i:i+ CHUNK_SIZE]
                    self.conn.send(chunk)
            else:
                respons = """ <h3> missing page 1 inputs or failed...</h3> 
                               <h2> Try again...... </h2>"""
                
                self.conn.sendall(text_respons(len(respons)))
                self.conn.sendall(respons)
        if self.request and self.conn and "GET /table" in self.request :
            respons=json.dumps({"status": "success","table":self.modbus_config.get('timeseries',[])})
            self.conn.sendall(f'HTTP/1.0 200 OK\r\nContent-type: application/json\r\n Content-Length: {len(respons)}\r\n\r\n')
            self.conn.sendall(respons)

        if self.request and self.conn and "GET /wifi_scan" in self.request :
            if self.wifi:
                networks = self.wifi.scan_networks() # type: ignore
                print(networks)

    def HandlePOST(self):
        if self.request and self.conn and ('POST /mqttconfig' in self.request or 'POST /teantconfig' in self.request or 'POST /wificonfig'
                                           in self.request or 'POST /modbusconfig' in self.request ,'POST /ModbusResisterConfig' in self.request) :
            body = self.request.split('\r\n\r\n')[1]
            jsondata = json.loads(body)
            if 'ssid' in jsondata:
                self.config['ssid'] = jsondata.get('ssid',None) # type: ignore
                self.config['wifi-password'] = jsondata.get('wifi-password',None) # type: ignore
                respons=json.dumps({"status": "success"})
                write_local_config(self.config)
            elif 'machine-id' in jsondata:
                self.config['machine-id'] = jsondata.get('machine-id',None) # type: ignore
                self.config['edge-id'] = jsondata.get('edge-id',None) # type: ignore
                self.config['tenant-id'] = jsondata.get('tenant-id',None) # type: ignore
                respons=json.dumps({"status": "success"})
                write_local_config(self.config)
            elif 'url' in jsondata :
                self.config['url'] = jsondata.get('url',None) # type: ignore
                self.config['port'] = int(jsondata.get('port',1883)) # type: ignore
                self.config['topic'] = jsondata.get('topic',None) # type: ignore
                self.config['username'] = jsondata.get('username',None) # type: ignore
                self.config['password'] = jsondata.get('password',None) # type: ignore
                respons=json.dumps({"status": "success"})
                write_local_config(self.config)
            elif 'POST /ModbusResisterConfig' in self.request or 'slave_addr' in jsondata :
                if jsondata.get('tag',None):
                    self.modbus_config=get_modbus_config()
                    funCode = jsondata['functionCode']
                    disc = {
                        'type':jsondata['type'],
                        'objectsCount':int(jsondata['objectsCount']),
                        'tag': jsondata['tag'],
                        'address':int(jsondata['address'])
                    }
                    try:
                        self.modbus_config['timeseries'][funCode].append(disc)
                    except KeyError:
                        print(f"funaction not precent {funCode}")
                        if 'timeseries' not in self.modbus_config:
                            self.modbus_config['timeseries'] ={}
                        if funCode not in self.modbus_config['timeseries']:
                             self.modbus_config['timeseries'][funCode] = []
                        self.modbus_config['timeseries'][funCode].append(disc)
                    for funCode in self.modbus_config['timeseries']:
                        self.modbus_config['timeseries'][funCode].sort(key=lambda x: x['address'])
                    respons=json.dumps({"status": "success","table":jsondata})
                    write_modbus_config(self.modbus_config)
                    sleep(0.7)
                elif jsondata.get('slave_addr',None):
                    self.modbus_config['uart_id'] = int(jsondata.get('uart_id',0))
                    self.modbus_config['slave_addr'] = int(jsondata.get('slave_addr',1))
                    self.modbus_config['pins'] = [int(x) for x in jsondata.get('pins','0,1').split(',')]
                    self.modbus_config['baudrate'] = int(jsondata.get('baudrate',9600))
                    self.modbus_config['parity'] = jsondata.get('parity','N')
                    self.modbus_config['data_bits'] = int(jsondata.get('data_bits',8))
                    self.modbus_config['stop_bits'] = int(jsondata.get('stop_bits',1))
                    self.modbus_config['ctrl_pin'] = int(jsondata.get('ctrl_pin',12))
                    respons=json.dumps({"status": "success"})
                    write_modbus_config(self.modbus_config)
                else:
                    print("jsondata not precent")
            self.conn.sendall('HTTP/1.0 200 OK\r\nContent-type: application/json\r\n\r\n')
            self.conn.sendall(respons)
        else:
            self.conn.sendall('HTTP/1.0 400 Bad Request\r\nContent-type: application/json\r\n\r\n') # type: ignore
            self.conn.sendall(json.dumps({"status": "failed"})) # type: ignore



        
    
    