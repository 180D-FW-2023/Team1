import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
import matplotlib.pyplot as plt
import cv2

model_name = "movenet_lightning"

module = hub.load("https://tfhub.dev/google/movenet/singlepose/lightning/4")
input_size = 192

def movenet(input_image):
    """Runs detection on an input image.

    Args:
      input_image: A [1, height, width, 3] tensor represents the input image
        pixels. Note that the height/width should already be resized and match the
        expected input resolution of the model before passing into this function.

    Returns:
      A [1, 1, 17, 3] float numpy array representing the predicted keypoint
      coordinates and scores.
    """
    model = module.signatures['serving_default']

    # SavedModel format expects tensor type of int32.
    input_image = tf.cast(input_image, dtype=tf.int32)
    # Run model inference.
    outputs = model(input_image)
    # Output is a [1, 1, 17, 3] tensor.
    keypoints_with_scores = outputs['output_0'].numpy()
    return keypoints_with_scores



# font 
font = cv2.FONT_HERSHEY_SIMPLEX 
  
# org 
org = (50, 50) 
  
# fontScale 
fontScale = 1
   
# Blue color in BGR 
color = (255, 0, 0) 
  
# Line thickness of 2 px 
thickness = 2
   

def point_overlay(image):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = tf.expand_dims(image, axis=0)
    resized_image = tf.image.resize(image, (input_size, input_size))
    keypoints_with_scores = movenet(resized_image)

    image = np.array(image[0]).astype(np.uint8)
    points = {x: None for x in range(17)}
    for i, (y, x, score) in enumerate(keypoints_with_scores[0][0]):
        #print(x, y)
        if score > 0.4:
            x = int(x * image.shape[1])
            y = int(y * image.shape[0])
            points[i] = (x, y)
            image = cv2.circle(image, (x, y), 20, (0, 0, 255), -1)
            image = cv2.putText(image, str(i), (x, y), font, fontScale, color, thickness, cv2.LINE_AA)
        else:
            points[i] = None
    if points[5] and points[7]:
      image = cv2.line(image, points[5], points[7], (255,0,0), 5) 
    if points[7] and points[9]:
      image = cv2.line(image, points[7], points[9], (255,0,0), 5) 

    if points[6] and points[8]:
      image = cv2.line(image, points[6], points[8], (255,0,0), 5) 
    if points[8] and points[10]:
      image = cv2.line(image, points[8], points[10], (255,0,0), 5) 
    
    return cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
