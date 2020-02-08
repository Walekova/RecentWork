import numpy as np
import cv2
import time
import numpy as np
import cv2
import time
import io as libio
import tensorflow as tf
import tensorflow.contrib.tensorrt as trt
import os
#from PIL import Image

# Load the frozen graph
output_dir=''
frozen_graph = tf.GraphDef()
with open(os.path.join(output_dir, '/frozen_inference_graph_face.pb'), 'rb') as f:
  frozen_graph.ParseFromString(f.read())

# constants
# https://github.com/NVIDIA-AI-IOT/tf_trt_models/blob/master/tf_trt_models/detection.py
INPUT_NAME='image_tensor'
BOXES_NAME='detection_boxes'
CLASSES_NAME='detection_classes'
SCORES_NAME='detection_scores'
MASKS_NAME='detection_masks'
NUM_DETECTIONS_NAME='num_detections'

input_names = [INPUT_NAME]
output_names = [BOXES_NAME, CLASSES_NAME, SCORES_NAME, NUM_DETECTIONS_NAME]

# Optimize the frozen graph using TensorRT
trt_graph = trt.create_inference_graph(
    input_graph_def=frozen_graph,
    outputs=output_names,
    max_batch_size=1,
    max_workspace_size_bytes=1 << 25,
    precision_mode='FP16',
    minimum_segment_size=50
)


# Create session and load graph
tf_config = tf.ConfigProto()
tf_config.gpu_options.allow_growth = True

tf_sess = tf.Session(config=tf_config)

# use this if you want to try on the optimized TensorRT graph
# Note that this will take a while
# tf.import_graph_def(trt_graph, name='')

# use this if you want to try directly on the frozen TF graph
# this is much faster
tf.import_graph_def(frozen_graph, name='')

tf_input = tf_sess.graph.get_tensor_by_name(input_names[0] + ':0')
tf_scores = tf_sess.graph.get_tensor_by_name('detection_scores:0')
tf_boxes = tf_sess.graph.get_tensor_by_name('detection_boxes:0')
tf_classes = tf_sess.graph.get_tensor_by_name('detection_classes:0')
tf_num_detections = tf_sess.graph.get_tensor_by_name('num_detections:0')

cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if ret == 0:
        break

    image = cv2.flip(frame, 1)
    image_np = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image_resized = np.expand_dims(image_np, axis=0)

    # Run network on Image
    scores, boxes, classes, num_detections = tf_sess.run(
        [tf_scores, tf_boxes, tf_classes, tf_num_detections],
        feed_dict={
            tf_input: image_resized
            })
    boxes = boxes[0] # index by 0 to remove batch dimension
    scores = scores[0]
    classes = classes[0]
    num_detections = num_detections[0]
    faces = []

    # suppress boxes that are below the threshold.. 
    DETECTION_THRESHOLD = 0.5

    for i in range(int(num_detections)):
        if scores[i] < DETECTION_THRESHOLD:
            continue
        # scale box to image coordinates
        box = boxes[i] * np.array([image.shape[0], image.shape[1], image.shape[0], image.shape[1]])

        faces.append(box)

    for(x,y,w,h) in faces:
        cv2.rectangle(frame, (int(x),int(y)), (int(x+w), int(y+h)), (255,0,0), 3)
        face = frame[int(y):int(y+h), int(x):int(x+w)]
        imgFile = "tensor-face-" + str(round(time.time())) + ".jpg"
        cv2.imwrite('/mnt/mybucket/'+ imgFile,face)

    # Display output
    cv2.imshow('frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


# When everything done, release the video capture object
cap.release()

# Closes all the frames
cv2.destroyAllWindows()

