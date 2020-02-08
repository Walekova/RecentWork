import ibm_boto3
from ibm_botocore.client import Config, ClientError
import time
import cv2
import numpy as np
import io as libio
from PIL import Image

# Constants for IBM COS values
COS_ENDPOINT = "https://s3.eu-gb.cloud-object-storage.appdomain.cloud"
COS_AUTH_ENDPOINT = "https://iam.cloud.ibm.com/identity/token"
COS_API_KEY_ID = "BD98N-vqonh983XVsKzNhIRx62oKMGZDodhNTL4ou9Tp" 
COS_RESOURCE_CRN = "crn:v1:bluemix:public:cloud-object-storage:global:a/5654a1f2157d42d482817601f6b4f60c:1b9a82e2-2215-4c79-ac53-7f021a893306:bucket:cos.deeplearning.walekova" 
COS_BUCKET = 'cos.deeplearning.walekova'

cos = ibm_boto3.client("s3",
    ibm_api_key_id=COS_API_KEY_ID,
    ibm_service_instance_id=COS_RESOURCE_CRN,
    ibm_auth_endpoint=COS_AUTH_ENDPOINT,
    config=Config(signature_version="oauth"),
    endpoint_url=COS_ENDPOINT
)

def cgsWriteImage(client, bucket, file, image):
    # Convert numpy.ndarray into PIL.Image.Image object. This features a 'save' method that will be used below
    # Determine number of dimensions
    n = image.ndim
    # RGB image
    if (n==3):
            img = Image.fromarray(image,'RGB')
    # Binary or graylevel image
    else:
        # Binary
        if (image.max()==1):
            img = Image.fromarray(image,'1').convert('RGB')  
        # Graylevel
        else:
            img = Image.fromarray(image,'L').convert('RGB')            
        
    # Create buffer to hold jpeg representation of image in 'io.BytesIO' object
    bufImage = libio.BytesIO()
    # Store jpeg representation of image in buffer
    img.save(bufImage,"JPEG") 
    # Rewind the buffer to beginning
    bufImage.seek(0)
    # Provide the jpeg object to the Body parameter of put_object to write image to COS
    isr = client.put_object(Bucket=bucket, 
                            Body = bufImage,
                            Key = file, 
                            ContentType = 'image/jpeg')
    #print("cgsWriteImage: \n\tBucket=%s \n\tFile=%s \n\tArraySize=%d %s RawSize=%d\n" % (bucket, file, image.size, image.shape, bufImage.getbuffer().nbytes))

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalcatface_extended.xml')

# read video input
cap = cv2.VideoCapture(0)

while cap.isOpened():
    _, frame = cap.read()
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    for(x,y,w,h) in faces:
        cv2.rectangle(frame, (x,y), (x+w, y+h), (255,0,0), 3)
        face = frame[y:y+h, x:x+w]
        imgFile = "face-" + str(round(time.time())) + ".jpg"
        cgsWriteImage(cos, COS_BUCKET, imgFile, face)
        #cos.Bucket(name=COS_BUCKET).put_object(Key=png_name, Body=face, ContentType = 'image/jpeg')
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
