from lib.umodbus.serial import Serial as ModbusRTUMaster
from time import time_ns
import ustruct
import json
class ModbusCon():
    def __init__(self,mqtt) :
        self.connected =True
        self.client = mqtt

    def connect(self,config):
        try:
            self.config=config
            self.host = ModbusRTUMaster(uart_id = self.config['uart_id'],pins=(self.config['pins'][0],self.config['pins'][1]),
                                        baudrate=self.config['baudrate'],data_bits=self.config['data_bits'],stop_bits=self.config['stop_bits'],
                                        parity=None,ctrl_pin=self.config['ctrl_pin'])
            print("connected modbus ")
            return True
        except Exception as e:
             print(e)
             return False
    
    def read(self,):
        try:
            while self.connected:
                try:
                    for funactions in self.config['timeseries']:
                        func_start = time_ns()// 1_000_000
                        first_address = self.config['timeseries'][funactions][0]['address']
                        last_address = self.config['timeseries'][funactions][-1]['address']
                        if self.config['timeseries'][funactions][-1].get('objectsCount',1):
                            objectCount=self.config['timeseries'][funactions][-1]['objectsCount']
                            objectCount = last_address+(objectCount)
                        if funactions == '1':
                            #  print(first_address,last_address)
                                reading=(self.host.read_coils(slave_addr=self.config['slave_addr'],starting_addr=int(first_address),coil_qty=int(objectCount)))
                                reading = reading[::-1]
                        elif funactions == '2':
                                reading=self.host.read_discrete_inputs(slave_addr=self.config['slave_addr'],starting_addr=int(first_address),input_qty=int(objectCount))
                                reading = reading[::-1]
                        elif funactions == '3':
                                reading=self.host.read_holding_registers(slave_addr=self.config['slave_addr'],starting_addr=int(first_address),register_qty=int(objectCount),signed=True)

                        elif funactions == '4':
                                reading=self.host.read_input_registers(slave_addr=self.config['slave_addr'],starting_addr=int(first_address),register_qty=int(objectCount),signed=True)

                                                        
                        for index ,registers in enumerate(self.config['timeseries'][funactions]):
                            data= {'name': registers['tag'],
                                    "value":reading[index],
                                    "ts": time_ns() // 1_000_000
                                    }
                            if registers["type"] == 'float':
                                data['value'] = ustruct.unpack('>f', ustruct.pack('>HH', reading[int(registers['address'])], reading[int(registers['address'])+1]))[0]
                            print(data)
                            try:
                                self.client.Publisher(message=json.dumps(data))
                                pub_end=time_ns() // 1_000_000
                                print(f"pub requird : {pub_end-data['ts']}")
                            except Exception as e :
                                print(f'publish error {e}')
                                # self.client.connect()
                                return False 
                        func_end = time_ns()// 1_000_000
                        print(f'requird time {func_end-func_start}')                
                except Exception as e :
                    print(f"modbus error : {e}")
                    return False
                        
        except KeyboardInterrupt as e:
            print(e)
            return False
    def ModbusStop(self):
         self.connected=False

            
        


