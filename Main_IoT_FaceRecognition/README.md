## IoT exercise - capture face and send to cloud via mqtt

## Cloud
https://s3.direct.eu-gb.cloud-object-storage.appdomain.cloud/

bucket: cos.deeplearning.walekova

## Content

### Docker files 

used to build the Opencv to Cloud Object store Architecture

### Python files

capture_and_send_face_v0.2.py (should be used to capture face however see error above)

img_process.py (used to store to COS)

mqtt_fwd.py (used to forward the message)

## Add-on - Save faces to directly to cloud using API

please have a look at Save_pix.py
