import cv2
import numpy as np
import json

class Movement():
    DRAW_BUFFER = []
    CIRCLE_BASE_RADIUS = 25
    MAX_BUFFER_SIZE = 40

    POINT_NOSE = 0
    POINT_RIGHT_EYE = 1
    POINT_LEFT_EYE = 2
    POINT_RIGHT_EAR = 3
    POINT_LEFT_EAR = 4
    POINT_RIGHT_SHOULDER = 5
    POINT_LEFT_SHOULDER = 6
    POINT_RIGHT_ELBOW = 7
    POINT_LEFT_ELBOW = 8
    POINT_RIGHT_WRIST = 9
    POINT_LEFT_WRIST = 10
    POINT_RIGHT_HIP = 11
    POINT_LEFT_HIP = 12
    POINT_RIGHT_KNEE = 13
    POINT_LEFT_KNEE = 14
    POINT_RIGHT_FOOT = 15
    POINT_LEFT_FOOT = 16

    RED = (0, 0, 255)
    STICK_FIGURE_THICKNESS = 5


    def __init__(self, mov_json = None):
        self.test_path_ptr = 0
        self.captured_path = []
        if mov_json != None:
            imported_path = json.JSONDecoder().decode(mov_json)
            # Perform JSON conversion for our expected formatting
            for points in imported_path:
                new_points = {int(x) : (tuple(y) if y else None) for x,y in points.items()}
                self.captured_path.append(new_points)
        self.active_points = []

    def get_movement_json(self):
        # Encode into json
        res = json.JSONEncoder().encode(self.captured_path)
        return res

    def add_captured_points(self, points):
        self.captured_path.append(points)

    def __get_stick_figure_lines(self, points):
        hip_midpoint = None if (points[Movement.POINT_RIGHT_HIP] == None or points[Movement.POINT_LEFT_HIP] == None) \
                    else ((int(points[Movement.POINT_RIGHT_HIP][0] +  points[Movement.POINT_LEFT_HIP][0]) // 2), (int(points[Movement.POINT_RIGHT_HIP][1] +  points[Movement.POINT_LEFT_HIP][1]) // 2))
        res = {
            "RIGHT_UPPER_ARM" : (points[Movement.POINT_RIGHT_SHOULDER], points[Movement.POINT_RIGHT_ELBOW]),
            "RIGHT_LOWER_ARM" : (points[Movement.POINT_RIGHT_ELBOW], points[Movement.POINT_RIGHT_WRIST]),
            "LEFT_UPPER_ARM" : (points[Movement.POINT_LEFT_SHOULDER], points[Movement.POINT_LEFT_ELBOW]),
            "LEFT_LOWER_ARM" : (points[Movement.POINT_LEFT_ELBOW], points[Movement.POINT_LEFT_WRIST]),
            "RIGHT_UPPER_LEG" : (points[Movement.POINT_RIGHT_HIP], points[Movement.POINT_RIGHT_KNEE]),
            "RIGHT_LOWER_LEG" : (points[Movement.POINT_RIGHT_KNEE], points[Movement.POINT_RIGHT_FOOT]),
            "LEFT_UPPER_LEG" : (points[Movement.POINT_LEFT_HIP], points[Movement.POINT_LEFT_KNEE]),
            "LEFT_LOWER_LEG" : (points[Movement.POINT_LEFT_KNEE], points[Movement.POINT_LEFT_FOOT]),
            "CHEST" : ((points[Movement.POINT_RIGHT_SHOULDER], points[Movement.POINT_LEFT_SHOULDER])),
            "HIPS" : ((points[Movement.POINT_RIGHT_HIP], points[Movement.POINT_LEFT_HIP])),
            "SPINE" : (hip_midpoint, points[Movement.POINT_NOSE]),
        }
        return res

    def display_and_advance_frame(self, frame):
        # TODO: change from absolute x y to scaling
        # ------------------
        # DRAW HAND MOVEMENT
        # ------------------

        # If the buffer is not max size
        if self.test_path_ptr < len(self.captured_path):
            self.active_points.append(self.captured_path[self.test_path_ptr][Movement.POINT_RIGHT_WRIST])
            self.test_path_ptr += 1
        # If buffer is over max size, pop oldest coordinate
        if len(self.active_points) > Movement.MAX_BUFFER_SIZE:
            self.active_points.pop(0)

        # Smooth movement with 5 points in between each, and replace None with an average of the two nearest
        smooth_factor = 5
        smoothed_movement = []
        if len(self.active_points) > 0:
            smoothed_movement.append(self.active_points[0])
        for i, coords in enumerate(self.active_points):
            # Do nothing if curr point is None
            if coords is None:
                continue
            # Add next points
            if i == len(self.active_points) - 1:
                smoothed_movement.append(self.active_points[i])
                break
            thisx, thisy = coords
            j = i + 1
            while j < len(self.active_points):
                if self.active_points[j] is not None:
                    nextx, nexty = self.active_points[j]
                    break
                else:
                    j += 1
            else:
                break
            for dx, dy in zip(np.linspace(thisx, nextx, smooth_factor), np.linspace(thisy, nexty, smooth_factor)):
                smoothed_movement.append((int(dx), int(dy)))

        # Display smoothed movement
        for coords, i in zip(smoothed_movement, range(len(smoothed_movement), -1, -1)):
            if coords is not None:
                x, y = coords
                cv2.circle(frame, center=(x,y), radius=max(Movement.CIRCLE_BASE_RADIUS-i//10, 1), color=(255, min(i*2, 255), min(i*2, 255)), thickness=-1)
        # -----------------
        # DRAW STICK FIGURE
        # -----------------
        if self.test_path_ptr < len(self.captured_path):
            for (pointa, pointb) in self.__get_stick_figure_lines(self.captured_path[self.test_path_ptr]).values():
                if pointa and pointb:
                    frame = cv2.line(frame, pointa, pointb, color=Movement.RED, thickness=Movement.STICK_FIGURE_THICKNESS) 
        return frame

    def is_done(self):
        return self.test_path_ptr >= len(self.captured_path)

    def reset(self):
        self.test_path_ptr = 0
        self.active_points = []