import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
import cv2
import math
from point import *

class StickFigureEstimator():
    model_name = "movenet_lightning"
    module = hub.load(
        "https://tfhub.dev/google/movenet/singlepose/lightning/4")
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
        model = StickFigureEstimator.module.signatures['serving_default']

        # SavedModel format expects tensor type of int32.
        input_image = tf.cast(input_image, dtype=tf.int32)
        # Run model inference.
        outputs = model(input_image)
        # Output is a [1, 1, 17, 3] tensor.
        keypoints_with_scores = outputs['output_0'].numpy()
        return keypoints_with_scores


    def generate_points(image):
        cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = tf.expand_dims(image, axis=0)
        resized_image = tf.image.resize(
            image, (StickFigureEstimator.input_size, StickFigureEstimator.input_size))
        keypoints_with_scores = StickFigureEstimator.movenet(resized_image)

        image = np.array(image[0]).astype(np.uint8)
        points = {x: None for x in range(17)}

        for i, (y, x, score) in enumerate(keypoints_with_scores[0][0]):
            # print(x, y)
            if score > 0.5:
                points[i] = (x, y)
            else:
                points[i] = None
        return points


    def get_width(points):
        if points[POINT_LEFT_SHOULDER] and points[POINT_RIGHT_SHOULDER]:
            # return abs(points[POINT_LEFT_SHOULDER][0] - points[POINT_RIGHT_SHOULDER][0])
            # do euclidian distance
            return math.sqrt((points[POINT_LEFT_SHOULDER][0] - points[POINT_RIGHT_SHOULDER][0])**2 + (points[POINT_LEFT_SHOULDER][1] - points[POINT_RIGHT_SHOULDER][1])**2)
        else:
            return None
        '''
        if points[1] and points[2]:
            return abs(points[1][0] - points[2][0])
        else:
            return None
        '''
        

    def get_center(points):
        if points[POINT_LEFT_SHOULDER] and points[POINT_RIGHT_SHOULDER]:
            return (points[POINT_LEFT_SHOULDER][0] + points[POINT_RIGHT_SHOULDER][0]) / 2, (points[POINT_LEFT_SHOULDER][1] + points[POINT_RIGHT_SHOULDER][1]) / 2
        else:
            return None
        '''
        if points[0]:
            return (points[0][0], points[0][1])
        else:
            return None
        '''


    def scale_points(points, new_center, scale_factor=1):
        center = StickFigureEstimator.get_center(points)
        if center:
            for key in points:
                if points[key] and key != POINT_JUMP:
                    points[key] = ((points[key][0] - center[0]) * scale_factor + new_center[0], (points[key][1] - center[1]) * scale_factor + new_center[1])
        return points


    def score(teacher_hand, student_hand):
        buffer_distance = 0.05
        max_distance = 0.8
        distance = math.sqrt((teacher_hand[0] - student_hand[0])**2 + (teacher_hand[1] - student_hand[1])**2)
        if distance <= buffer_distance:
            return 100
        
        # If the distance is greater than the maximum distance, return a score of 0
        if distance > max_distance:
            return 0
        
        # Calculate the score for distances between buffer and max distance
        # Linearly scale the score from 100 at buffer_distance to 0 at max_distance
        score = 100 * ((1 - (distance - buffer_distance) / (max_distance - buffer_distance)) ** 2)
        return score


    def overlay_points(image, points):
        points = dict(points)
        for i in range(17):
            if points[i] is not None:
                points[i] = (int(points[i][0] * image.shape[1]),
                             int(points[i][1] * image.shape[0]))
                
        for i in range(17):
            if points[i]:
                cv2.circle(image, points[i], 20, (255, 0, 0), -1)
                cv2.putText(image, str(
                    i), points[i], cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
                
        if points[5] and points[7]:
            cv2.line(image, points[5], points[7], (0, 0, 255), 5)
        if points[5] and points[6]:
            cv2.line(image, points[5], points[6], (0, 0, 255), 5)
        
        if points[7] and points[9]:
            cv2.line(image, points[7], points[9], (0, 0, 255), 5)

        if points[6] and points[8]:
            cv2.line(image, points[6], points[8], (0, 0, 255), 5)
        if points[8] and points[10]:
            cv2.line(image, points[8], points[10], (0, 0, 255), 5)

        return image


    def rectangle_from_line(point1, point2, thickness):
        # get 4 points of rectangle, lines parallel to point1 and point2
        if point2[0] - point1[0] == 0:  # vertical line, slope is undefined
            p1 = [int(point1[0] - thickness/2), point1[1]]
            p2 = [int(point1[0] + thickness/2), point1[1]]
            p3 = [int(point2[0] + thickness/2), point2[1]]
            p4 = [int(point2[0] - thickness/2), point2[1]]
        elif point2[1] - point1[1] == 0:  # horizontal line, slope is 0
            p1 = [point1[0], int(point1[1] - thickness/2)]
            p2 = [point1[0], int(point1[1] + thickness/2)]
            p3 = [point2[0], int(point2[1] + thickness/2)]
            p4 = [point2[0], int(point2[1] - thickness/2)]
        else:
            slope = (point2[1] - point1[1]) / (point2[0] - point1[0])
            slope_perpendicular = -1 / slope
            # get the 4 points to define the rectangle
            dx = thickness / np.sqrt(1 + slope_perpendicular**2)
            dy = slope_perpendicular * dx

            p1 = [int(point1[0] - dx), int(point1[1] - dy)]
            p2 = [int(point1[0] + dx), int(point1[1] + dy)]
            p3 = [int(point2[0] + dx), int(point2[1] + dy)]
            p4 = [int(point2[0] - dx), int(point2[1] - dy)]
        return np.array([p1, p2, p3, p4])


    def overlay_avatar(image, points):
        points = dict(points)
        for i in range(17):
            if points[i] is not None:
                points[i] = (int(points[i][0] * image.shape[1]),
                             int(points[i][1] * image.shape[0]))

        current_width = StickFigureEstimator.get_width(points)
        if current_width:
            thickness = current_width / 8
        else:
            thickness = 20

        alpha = 0.5
        overlay = np.zeros_like(image, dtype=np.uint8)
        arm_color = (255, 0, 0)
        torso_color = (0, 255, 0)
        head_color = (0, 0, 255)
        outline_color = (255, 255, 255)
        # left arm
        if points[POINT_LEFT_SHOULDER] and points[POINT_LEFT_ELBOW]:
            rect_points = StickFigureEstimator.rectangle_from_line(points[POINT_LEFT_SHOULDER], points[POINT_LEFT_ELBOW], thickness)
            cv2.fillPoly(overlay, [rect_points], arm_color)
            cv2.polylines(overlay, [rect_points], True, outline_color, 2)

        # left forearm
        if points[POINT_LEFT_ELBOW] and points[POINT_LEFT_WRIST]:
            rect_points = StickFigureEstimator.rectangle_from_line(points[POINT_LEFT_ELBOW], points[POINT_LEFT_WRIST], thickness)
            cv2.fillPoly(overlay, [rect_points], arm_color)
            cv2.polylines(overlay, [rect_points], True, outline_color, 2)
            
        # left wrist
        if points[POINT_LEFT_WRIST]:
            cv2.circle(overlay, points[POINT_LEFT_WRIST], thickness * 2, arm_color, -1)
        
        # left elbow
        if points[POINT_LEFT_ELBOW]:
            cv2.circle(overlay, points[POINT_LEFT_ELBOW], thickness * 2, arm_color, -1)
        
        # right arm
        if points[POINT_RIGHT_SHOULDER] and points[POINT_RIGHT_ELBOW]:
            rect_points = StickFigureEstimator.rectangle_from_line(points[POINT_RIGHT_SHOULDER], points[POINT_RIGHT_ELBOW], thickness)
            cv2.fillPoly(overlay, [rect_points], arm_color)
            cv2.polylines(overlay, [rect_points], True, outline_color, 2)

        # right forearm
        if points[POINT_RIGHT_ELBOW] and points[POINT_RIGHT_WRIST]:
            rect_points = StickFigureEstimator.rectangle_from_line(points[POINT_RIGHT_ELBOW], points[POINT_RIGHT_WRIST], thickness)
            cv2.fillPoly(overlay, [rect_points], arm_color)
            cv2.polylines(overlay, [rect_points], True, outline_color, 2)

        # right wrist
        if points[POINT_RIGHT_WRIST]:
            cv2.circle(overlay, points[POINT_RIGHT_WRIST], thickness * 2, arm_color, -1)
        
        # right elbow
        if points[POINT_RIGHT_ELBOW]:
            cv2.circle(overlay, points[POINT_RIGHT_ELBOW], thickness * 2, arm_color, -1)
        
        # torso
        if points[POINT_RIGHT_SHOULDER] and points[POINT_LEFT_SHOULDER] and points[POINT_RIGHT_HIP] and points[POINT_LEFT_HIP]:
            rect_points = np.array([points[POINT_RIGHT_SHOULDER], points[POINT_LEFT_SHOULDER], points[POINT_LEFT_HIP], points[POINT_RIGHT_HIP]])
            cv2.fillPoly(overlay, [rect_points], torso_color)
            cv2.polylines(overlay, [rect_points], True, outline_color, 2)
            
        
        # left thigh
        if points[POINT_LEFT_HIP] and points[POINT_LEFT_KNEE]:
            rect_points = StickFigureEstimator.rectangle_from_line(points[POINT_LEFT_HIP], points[POINT_LEFT_KNEE], thickness)
            cv2.fillPoly(overlay, [rect_points], arm_color)
            cv2.polylines(overlay, [rect_points], True, outline_color, 2)

        # left calf
        if points[POINT_LEFT_KNEE] and points[POINT_LEFT_FOOT]:
            rect_points = StickFigureEstimator.rectangle_from_line(points[POINT_LEFT_KNEE], points[POINT_LEFT_FOOT], thickness)
            cv2.fillPoly(overlay, [rect_points], arm_color)
            cv2.polylines(overlay, [rect_points], True, outline_color, 2)
            
        # left foot
        if points[POINT_LEFT_FOOT]:
            cv2.circle(overlay, points[POINT_LEFT_FOOT], thickness * 2, arm_color, -1)
        
        # left knee
        if points[POINT_LEFT_KNEE]:
            cv2.circle(overlay, points[POINT_LEFT_KNEE], thickness * 2, arm_color, -1)
            
        # right thigh
        if points[POINT_RIGHT_HIP] and points[POINT_RIGHT_KNEE]:
            rect_points = StickFigureEstimator.rectangle_from_line(points[POINT_RIGHT_HIP], points[POINT_RIGHT_KNEE], thickness)
            cv2.fillPoly(overlay, [rect_points], arm_color)
            cv2.polylines(overlay, [rect_points], True, outline_color, 2)
        
        # right calf
        if points[POINT_RIGHT_KNEE] and points[POINT_RIGHT_FOOT]:
            rect_points = StickFigureEstimator.rectangle_from_line(points[POINT_RIGHT_KNEE], points[POINT_RIGHT_FOOT], thickness)
            cv2.fillPoly(overlay, [rect_points], arm_color)
            cv2.polylines(overlay, [rect_points], True, outline_color, 2)
        
        # right foot
        if points[POINT_RIGHT_FOOT]:
            cv2.circle(overlay, points[POINT_RIGHT_FOOT], thickness * 2, arm_color, -1)
        
        # right knee
        if points[POINT_RIGHT_KNEE]:
            cv2.circle(overlay, points[POINT_RIGHT_KNEE], thickness * 2, arm_color, -1)
        
        
        # head
        if points[POINT_NOSE]:
            thickness *= 2
            rect_points = np.array([
                (int(points[POINT_NOSE][0] - thickness), int(points[POINT_NOSE][1] - thickness)),
                (int(points[POINT_NOSE][0] - thickness), int(points[POINT_NOSE][1] + thickness)),
                (int(points[POINT_NOSE][0] + thickness), int(points[POINT_NOSE][1] + thickness)),
                (int(points[POINT_NOSE][0] + thickness), int(points[POINT_NOSE][1] - thickness))]
            )
            cv2.fillPoly(overlay, [rect_points], head_color)
            cv2.polylines(overlay, [rect_points], True, outline_color, 2)

        
        image = cv2.addWeighted(image, 1, overlay, alpha, 0)
        
        return image