import paho.mqtt.client as mqtt

# keeping track of the IP of the MQTT brokers
local_broker = "172.18.0.2"
cloud_broker = "158.177.159.243"
topic = "nvidia"

# subscribe to the topic on local mqtt connect
def on_connect_local(client,userdata, flags, rc):
    if rc==0:
        print('connected OK - local')
    else:
        print('Bad conncetion Returned code=', rc)
    client.subscribe(topic)

# just showing it connected to the cloud mqtt       
def on_connect_cloud(client,userdata, flags, rc):
    if rc==0:
        print('connected OK - cloud')
    else:
        print('Bad conncetion Returned code=', rc)

def on_message(client, userdata, msg):
    cloud_client.publish(topic, payload=msg.payload, qos=1, retain=False)

# when the local mqtt client receives new messages on the topic, publish to the cloud mqtt
def on_message(client, userdata, msg):
	cloud_client.publish(topic, payload=msg.payload, qos=1, retain=False)

# local mqtt client
local_client = mqtt.Client("forward")
local_client.on_connect = on_connect_local
local_client.connect(local_broker)
local_client.on_message = on_message

# connection to the mqtt on the cloud
cloud_client = mqtt.Client("forward")  
cloud_client.on_connect = on_connect_cloud
cloud_client.connect(cloud_broker)

local_client.loop_forever()