import paho.mqtt.client as mqtt
import ibm_boto3
from ibm_botocore.client import Config, ClientError
import time

# Constants for IBM COS values
COS_ENDPOINT = "https://s3.eu-gb.cloud-object-storage.appdomain.cloud"
COS_AUTH_ENDPOINT = "https://iam.cloud.ibm.com/identity/token"
COS_API_KEY_ID = "BD98N-vqonh983XVsKzNhIRx62oKMGZDodhNTL4ou9Tp"
COS_RESOURCE_CRN = "crn:v1:bluemix:public:cloud-object-storage:global:a/5654a1f2157d42d482817601f6b4f60c:1b9a82e2-2215-4c79-ac53-7f021a893306:bucket:cos.deeplearning.walekova"
COS_BUCKET = 'cos.deeplearning.walekova'

broker = '158.177.159.243'
topic = 'nvidia'
client = mqtt.Client('MSI_message') # create instance   

cos = ibm_boto3.resource("s3",
    ibm_api_key_id=COS_API_KEY_ID,
    ibm_service_instance_id=COS_RESOURCE_CRN,
    ibm_auth_endpoint=COS_AUTH_ENDPOINT,
    config=Config(signature_version="oauth"),
    endpoint_url=COS_ENDPOINT
)

### MQTT
def on_log(client,userdata, level, buf):
    print('log: ' +buf)

def on_connect(client,userdata, flags, rc):
    if rc==0:
        print('connected OK')
    else:
        print('Bad conncetion Returned code=', rc)
    client.subscribe(topic)
    print('Subsribed to: '+ topic)

def on_disconnect(client, userdata, flags, rc=0):
    print('Disconnected result code '+str(rc))

def on_message(client, userdata, msg):
    print("message received")
    png_name = "face-" + str(round(time.time())) + ".png"
    cos.Bucket(name=COS_BUCKET).put_object(Key=png_name, Body=msg.payload)
    print("wrote to bucket")


client.on_connect = on_connect #bind call back function
client.on_disconnect = on_disconnect
client.con_log = on_log
client.on_message=on_message
print('Connecting to broker ', broker)
client.connect(broker) #connect to broker


# go into a loop
client.loop_forever()

