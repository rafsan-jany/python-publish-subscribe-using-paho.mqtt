import paho.mqtt.client as mqtt
import time
import sys
from time import sleep
import serial
import json

general_update_interval= 90 #in seconds
now_time = 0
prev_time = 0

serial_data_write_list = []
status_data = {}

ser = serial.Serial('/dev/ttyATH0', 115200)

def serial_write_function(received_commands):
    print ("In Serial Function")
    #ser = serial.Serial('/dev/ttyATH0', 115200)
    ser.write(str(received_commands))
    #print (raf)

def on_connect(client, userdata, flags, rc):
    print("Connected! rc:", rc)

def on_message(client, userdata, message):
    if str(message.topic) != pubtop:
        print ("In Callback Function")
        print(str(message.topic), str(message.payload.decode("utf-8")))
        s_top = str(message.topic).split('/')
        #m_top = ','.join(s_top[1:])
        m_top = '/'.join(s_top[1:])
        msg_payload = str(message.payload.decode("utf-8"))
        #message_buffer = m_top + ',' + msg_payload
        message_buffer = m_top + '/' + msg_payload
        print (message_buffer)
        serial_data_write_list.append(message_buffer)
        #serial_write_function(message_buffer)

broker_address = "127.0.0.1"
port = 1883

# Create the MQTT client and set the callback functions you want to use
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
time.sleep(1) # Sleep for a beat to ensure things occur in order

pubtop = 'pubtop'
subtop = 'subtop/#'

client.connect(broker_address, port)
client.loop_start()
client.subscribe(subtop)

while True:
    sleep(1)
    now_time = int(time.time())
    if((now_time-prev_time)>=general_update_interval):
        prev_time = now_time
        v = ['digital', 'analog', 'relayStatus', 'pwmStatus', 'dht']
        for i in v:
            topic_for_status = 'getData/' + str(i) + '/0'
            print (str(topic_for_status))
            serial_write_function(str(topic_for_status))
            chat1 = ser.readline()
            chat1 = chat1.strip()
            print (chat1)
            #status_data [str(i)] = json.loads(chat1.split('/')[2]
            status_data [str(i)] = chat1.split('/')[2]
        print(status_data)
        #with open('/root/config_sensor.json', 'a') as f:
            #json.dump(status_data, f)
        #client.publish(pubtop, json.dumps(status_data))
        pubtop = 'pubtop'
        pubtop = pubtop + '/getSensorData'
        client.publish(pubtop, str(status_data))
        pubtop = ""

    if(len(serial_data_write_list)>0):
        pubtop = 'pubtop'
        serial_write_function(serial_data_write_list[0])
        chat = ser.readline()
        print ("MQTT request!")
        print (chat)
        val = chat.split('/')
        pubtop = pubtop + '/' + str(val[0]) + '/' + str(val[1])
        print str(val[0])
        print str(val[1])
        print pubtop
        client.publish(pubtop, val[2])
        serial_data_write_list.pop(0)
        pubtop = ""

# Disconnect and stop the loop!
client.disconnect()
client.loop_stop()