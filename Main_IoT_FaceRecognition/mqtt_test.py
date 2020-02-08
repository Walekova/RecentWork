import paho.mqtt.client as mqtt
import time

broker = 'mosquitto'
client = mqtt.Client('MSI_msg') # create instance

def on_log(client,userdata, level, buf):
    print('log: ' +buf)

def on_connect(client,userdata, flags, rc):
    if rc==0:
        print('connected OK')
    else:
        print('Bad conncetion Returned code=', rc)


def on_disconnect(client, userdata, flags, rc=0):
    print('Disconnected result code '+ str(rc))

def on_message(client, userdata, msg):
    topic = msg.topic
    m_decode= str(msg.payload.decode('utf-8', 'ignore'))
    print('Message received', m_decode)

client.on_connect = on_connect #bind call back function
client.on_disconnect = on_disconnect
client.con_log = on_log
client.on_message=on_message
print('Connecting to broker ', broker)
client.connect(broker) #connect to broker

client.subscribe('nvidia')
client.publish('nvidia', 'Mikra_from_MSI')

# go into a loop
client.loop_forever()

