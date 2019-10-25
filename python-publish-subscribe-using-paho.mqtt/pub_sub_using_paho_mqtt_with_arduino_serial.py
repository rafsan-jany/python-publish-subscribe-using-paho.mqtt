import sys
import os
import serial
import paho.mqtt.client as mqtt
import time
import commands
import json, ast

mqtt_data_queue = []
serial_data_queue = []
general_update_interval= 1 #in seconds
now_time = 0
prev_time = 0
broker_address = "127.0.0.1"
port = 1883
result = None
mac_id = commands.getstatusoutput('cat /sys/class/net/eth0/address')[1].replace(':','')
default_sensor_data_req = {"id":str(mac_id),"type":"getSensorData","port":0}
request_topic = "/{0}/local/request".format(str(mac_id))
response_topic = "/{0}/local/response".format(str(mac_id))

### Method_Type functions ###

def setRelayData(msg):
    #print('In set relay data')
    data = 'setData,relay,{0},{1}'.format(str(msg["port"]),str(msg["value"]))
    try:
        ser.write(data)
    except:
        print('Serial Write Relay Data set failed!')
    try:
        c = str(ser.readline())
        c = c.replace('setData,relay,','')
        c = c.strip()
        c = c.split(',')
        msg['port'] = json.loads(c[0])
        msg['value'] = json.loads(c[1])
    except:
        print("Failed to pack Relay Status data!")
    print(msg)
    return msg
    #pass

def setPwmData(msg):
    #print('In set pwm data')
    data = 'setData,pwm,{0},{1}'.format(str(msg["port"]),str(msg["value"]))
    try:
        ser.write(data)
    except:
        print('Serial Write Pwm Data set failed!')
    try:
        c = str(ser.readline())
        c = c.replace('setData,pwm,','')
        c = c.strip()
        c = c.split(',')
        msg['port'] = json.loads(c[0])
        msg['value'] = json.loads(c[1])
    except:
        print("Failed to pack Pwm Set data!")
    #print(msg)
    return msg
    #pass

def getRelayStatus(msg):
    #print('In get relay data')
    data = 'getData,relayStatus,{}'.format(str(msg["port"]))
    try:
        ser.write(data)
    except:
        print('Serial Write Relay Data acq failed!')
    try:
        c = str(ser.readline())
        c = c.replace('getData,relayStatus,','')
        c = c.strip()
        msg['value'] = json.loads(c)
    except:
        print("Failed to pack Relay Status data!")
    print(msg)
    return msg
    #pass
    
def getPwmStatus(msg):
    #print('In get pwm data')
    data = 'getData,pwmStatus,{}'.format(str(msg["port"]))
    try:
        ser.write(data)
    except:
        print('Serial Write PWM Data acq failed!')
    try:
        c = str(ser.readline())
        c = c.replace('getData,pwmStatus,','')
        c = c.strip()
        msg['value'] = json.loads(c)
    except:
        print("Failed to pack PWM Status data!")
    #print(msg)
    return msg
    #pass

def setConfigData(msg):
    #print('In set config data')
    data = 'setData,{0},{1},{2}'.format(str(msg["task"]),str(msg["port"]),str(msg["value"]))
    try:
        ser.write(data)
    except:
        print('Serial Write Config Data set failed!')
    try:
        c = str(ser.readline())
        c = c.replace('setData,','')
        c = c.strip()
        c = c.split(',')
        #print(c)
        msg["task"] = json.loads(c[0])
        msg['port'] = json.loads(c[1])
        msg['value'] = json.loads(c[2])
    except:
        print("Failed to pack Config data!")
    #print(msg)
    return msg
    #pass 

def getModBusData(msg):
    pass
    
def getSensorData(msg):
    # digital data acq
    data = 'getData,digital,{}'.format(str(msg["port"]))
    try:
        ser.write(data)
    except:
        print('Serial Write Digital Data acq failed!')
    try:
        c = str(ser.readline())
        c = c.replace('getData,digital,','')
        c = c.strip()
        msg['digital'] = json.loads(c)
    except:
        print("Failed to pack digital data!")
    
    # Analog data acq
    data = 'getData,analog,{}'.format(str(msg["port"]))
    try:
        ser.write(data)
    except:
        print('Serial Write Analog Data acq failed!')
    try:
        c = str(ser.readline())
        c = c.replace('getData,analog,','')
        c = c.strip()
        msg['analog'] = json.loads(c)
    except:
        print("Failed to pack analog data!")
        
    # Relay data acq
    data = 'getData,relayStatus,{}'.format(str(msg["port"]))
    try:
        ser.write(data)
    except:
        print('Serial Write Relay Data acq failed!')
    try:
        c = str(ser.readline())
        c = c.replace('getData,relayStatus,','')
        c = c.strip()
        msg['relay'] = json.loads(c)
    except:
        print("Failed to pack relay data!")
        
    # Pwm data acq
    data = 'getData,pwmStatus,{}'.format(str(msg["port"]))
    try:
        ser.write(data)
    except:
        print('Serial Write PWM Data acq failed!')
    try:
        c = str(ser.readline())
        c = c.replace('getData,pwmStatus,','')
        c = c.strip()
        msg['pwm'] = json.loads(c)
    except:
        print("Failed to pack pwm data!")
    
    return msg
    #pass

def getDhtData(msg):
    #print('In get dht data')
    data = 'getData,dht,{}'.format(str(msg["port"]))
    try:
        ser.write(data)
    except:
        print('Serial Write DHT Data acq failed!')
    try:
        c = str(ser.readline())
        c = c.replace('getData,dht,','')
        c = c.strip()
        msg['value'] = json.loads(c)
    except:
        print("Failed to pack DHT data!")
    #print(msg)
    return msg
    #pass 

def removeData(msg):
    pass
    
def readConfigData(msg):
    with open('/usr/lib/lua/luci/config/config.json') as f:
        data = json.load(f)
    return str(data)
    
def writeConfigData(msg):
    with open('/usr/lib/lua/luci/config/config.json', 'w') as f:
        json.dump(msg, f)
    return str(msg)
    
    
def getCanData(msg):
    pass

### Method_Type functions ###

method_type = {
    'setRelayData': setRelayData,
    'setPwmData': setPwmData,
    'getRelayStatus': getRelayStatus,
    'getPwmStatus': getPwmStatus,
    'setConfigData': setConfigData,
    'getModBusData': getModBusData,
    'getSensorData': getSensorData,
    'getDhtData': getDhtData,
    'removeData': removeData,
    'getCanData': getCanData,
    'readConfigData': readConfigData,
    'writeConfigData': writeConfigData
}

### MQTT Callbacks ###

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to Server!")
    else:
        print("Check Again Not Connected!")

def on_message(client, userdata, message):
    tmp_data = ast.literal_eval(message.payload)
    #print('Debug', tmp_data)
    #tmp_data = [s.encode('utf-8') for s in tmp_data]
    serial_data_queue.append(tmp_data)
    #serial_data_queue = [(str(message.topic),str(message.payload.decode("utf-8")))]
    #print(serial_data_queue)
    pass

def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed:", str(mid), str(granted_qos))
    pass

def on_unsubscribe(client, userdata, mid):
    print("Unsubscribed:", str(mid))

def on_publish(client, userdata, mid):
    print("Published: ", client)

def on_log(client, userdata, level, buf):
    print("log:", buf)

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnection.")

### MQTT Callbacks ###

def serial_activate(port='/dev/ttyATH0',baudrate=115200):
    global ser
    ser = serial.Serial(port, baudrate,timeout = 10) # Establish the connection on a specific port
    #print(port, baudrate)
    
serial_activate()

### Broker Init ###
b_client = mqtt.Client()
b_client.on_subscribe = on_subscribe
b_client.on_unsubscribe = on_unsubscribe
b_client.on_connect = on_connect
b_client.on_message = on_message
time.sleep(1)
b_client.connect(broker_address, port)
b_client.loop_start()
b_client.subscribe(request_topic,0)
### Broker Init ###

now_time = int(time.time())
number = 0

while True:
    now_time = int(time.time())
    if((now_time-prev_time)>=general_update_interval):
        prev_time = now_time
        #serial_data_queue.append(default_sensor_data_req)
        try:
            result = method_type[default_sensor_data_req['type']](default_sensor_data_req)
        except:
            print("Method calling Failed!")
        if result:
            number = number + 1
            b_client.publish(response_topic,json.dumps(result))
            b_client.publish(response_topic,json.dumps(number))
        else:
            print("Error !")
    if(len(serial_data_queue)>0):
        try:
            result = method_type[serial_data_queue[0]['type']](serial_data_queue[0])
        except:
            print("Method calling Failed!")
            print(serial_data_queue[0]['type'])
            
        if result:
            b_client.publish(response_topic,json.dumps(result))
            serial_data_queue.pop(0)
        else:
            print("Error !")