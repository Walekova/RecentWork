import cv2
import paho.mqtt.client as mqtt
import time

# MQTT set up 
broker = 'mosquitto'
client = mqtt.Client('MSI_message') # create instance
topic = 'nvidia'

# MQTT functions
def on_log(client,userdata, level, buf):
    print('log: ' +buf)

def on_connect(client,userdata, flags, rc):
    if rc==0:
        print('connected OK')
    else:
        print('Bad conncetion Returned code=', rc)

def on_disconnect(client, userdata, flags, rc=0):
    print('Disconnected result code '+str(rc))

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

# read video input
cap = cv2.VideoCapture(0)

while cap.isOpened():
    _, frame = cap.read()

    face_cascade = cv2.CascadeClassifier('/usr/share/opencv/haarcascades/haarcascade_frontalface_default.xml')
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    for(x,y,w,h) in faces:
        cv2.rectangle(frame, (x,y), (x+w, y+h), (255,0,0), 3)
        face = frame[y:y+h, x:x+w]
        client.publish(topic, cv2.imencode('.png',face)[1].tobytes())
        print("message sent")

    # Display output
    cv2.imshow('frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the video capture object
cap.release()

# Closes all the frames
cv2.destroyAllWindows()

# go into a loop
client.loop_forever()

