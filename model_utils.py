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


def point_overlay(image):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = tf.expand_dims(image, axis=0)
    resized_image = tf.image.resize(image, (input_size, input_size))
    keypoints_with_scores = movenet(resized_image)

    image = np.array(image[0]).astype(np.uint8)

    for y, x, score in keypoints_with_scores[0][0]:
        #print(x, y)
        if score > 0.4:
            image = cv2.circle(image, (int(x * image.shape[1]), int(y * image.shape[0])), 20, (0, 0, 255), -1)
    return cv2.cvtColor(image, cv2.COLOR_RGB2BGR)