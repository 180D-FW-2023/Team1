import cv2
import numpy as np
import json
from model_utils import *
from point import *
import random
    

class Movement():
    DRAW_BUFFER = []
    CIRCLE_BASE_RADIUS = 25
    MAX_BUFFER_SIZE = 40

    RED = (255, 0, 0)

    STICK_FIGURE_THICKNESS = 5
    FEEDBACK_RESET = 90

    def __init__(self, mov_json = None):
        self.test_path_ptr = 0
        self.captured_path = []
        self.jump_counter = 0
        self.score = 0
        self.feedback_score = 0
        self.current_score = 0
        self.score_counter = 1
        self.feedback_counter = 1
        self.feedback_rating = ""
        self.feedback_color = (0, 0, 255)
        self.last_seen = {x: None for x in range(17)}
        self.history = [{x: None for x in range(17)}]
        if mov_json != None:
            imported_path = json.JSONDecoder().decode(mov_json)
            # Perform JSON conversion for our expected formatting
            for points in imported_path:
                new_points = {}
                for k, v in points.items():
                    if v is not None:
                        if int(k) == POINT_JUMP:
                            pass
                        else:
                            v = (np.float32(v[0]), np.float32(v[1]))
                    new_points[int(k)] = v
                self.captured_path.append(new_points)
                
                            
            # smoothing captured_path
            count = {x: 0 for x in range(17)}
            for points in self.captured_path:
                for i in range(17):
                    if points[i] is not None:
                        count[i] += 1
            
            
            for points in self.captured_path:
                for i in range(17):
                    if count[i] < 5:
                        points[i] = None
                        
                        
        self.active_points = []

    def get_movement_json(self):
        # Encode into json
        path_to_send = list(self.captured_path)
        for path_points in path_to_send:
            for k in path_points:
                if k == POINT_JUMP:
                    pass
                elif path_points[k] is not None:
                    path_points[k] = (str(path_points[k][0]), str(path_points[k][1]))
        res = json.JSONEncoder().encode(self.captured_path)
        return res

    def add_captured_points(self, points):
        points = dict(points)
        self.captured_path.append(points)

    def __get_stick_figure_lines(points):
        hip_midpoint = None if (points[POINT_RIGHT_HIP] == None or points[POINT_LEFT_HIP] == None) \
                    else (((points[POINT_RIGHT_HIP][0] +  points[POINT_LEFT_HIP][0]) / 2), ((points[POINT_RIGHT_HIP][1] +  points[POINT_LEFT_HIP][1]) / 2))
        res = {
            "RIGHT_UPPER_ARM" : (points[POINT_RIGHT_SHOULDER], points[POINT_RIGHT_ELBOW]),
            "RIGHT_LOWER_ARM" : (points[POINT_RIGHT_ELBOW], points[POINT_RIGHT_WRIST]),
            "LEFT_UPPER_ARM" : (points[POINT_LEFT_SHOULDER], points[POINT_LEFT_ELBOW]),
            "LEFT_LOWER_ARM" : (points[POINT_LEFT_ELBOW], points[POINT_LEFT_WRIST]),
            "RIGHT_UPPER_LEG" : (points[POINT_RIGHT_HIP], points[POINT_RIGHT_KNEE]),
            "RIGHT_LOWER_LEG" : (points[POINT_RIGHT_KNEE], points[POINT_RIGHT_FOOT]),
            "LEFT_UPPER_LEG" : (points[POINT_LEFT_HIP], points[POINT_LEFT_KNEE]),
            "LEFT_LOWER_LEG" : (points[POINT_LEFT_KNEE], points[POINT_LEFT_FOOT]),
            "CHEST" : ((points[POINT_RIGHT_SHOULDER], points[POINT_LEFT_SHOULDER])),
            "HIPS" : ((points[POINT_RIGHT_HIP], points[POINT_LEFT_HIP])),
            "SPINE" : (hip_midpoint, points[POINT_NOSE]),
        }
        return res

    def display_and_advance_frame(self, frame, current_points):
        # ------------------
        # DRAW HAND MOVEMENT
        # ------------------
        # If the buffer is not max size
        if self.test_path_ptr < len(self.captured_path):
            self.active_points.append(self.captured_path[self.test_path_ptr][POINT_RIGHT_WRIST])
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
                smoothed_movement.append((dx, dy))

        # Display smoothed movement
        for coords, i in zip(smoothed_movement, range(len(smoothed_movement), -1, -1)):
            if coords is not None:
                # Convert from relative to absolute
                x, y = int(coords[0] * frame.shape[1]), int(coords[1] * frame.shape[0])
                # Display
                cv2.circle(frame, center=(x,y), radius=max(Movement.CIRCLE_BASE_RADIUS-i//10, 1), color=(min(i*2, 255), min(i*2, 255), 255), thickness=-1)
        # -----------------
        # DRAW STICK FIGURE
        # -----------------
        if self.test_path_ptr < len(self.captured_path):
            captured_points = self.captured_path[self.test_path_ptr]

            # smoothing captured points
            for key, val in captured_points.items():
                if val is None:
                    captured_points[key] = self.last_seen[key]
                else:
                    self.last_seen[key] = val
            
            # smoothing current points 
            alpha = 0.9
            
            for key, val in current_points.items():
                if val is None:
                    current_points[key] = self.history[-1][key]
            
            self.history.append(current_points)


            for k in (POINT_LEFT_SHOULDER, POINT_RIGHT_SHOULDER):
                i = 0
                while self.history[i][k] is None:
                    i += 1
                    if i >= len(self.history):
                        break
                if i >= len(self.history):
                    continue
                smoothed_data = (self.history[i][k])
                i += 1
                while i < len(self.history):
                    st_x = alpha * self.history[i][k][0] + (1 - alpha) * smoothed_data[0]
                    st_y = alpha * self.history[i][k][1] + (1 - alpha) * smoothed_data[1]
                    smoothed_data = (st_x, st_y)
                    i += 1
                current_points[k] = smoothed_data


            captured_width = StickFigureEstimator.get_width(captured_points)

            current_center = StickFigureEstimator.get_center(current_points)
            current_width = StickFigureEstimator.get_width(current_points)
            
            # display avatar and calculate score
            if captured_width and current_center and current_width:
                score_1, score_2 = None, None
                scale_factor = current_width / captured_width
                captured_points = StickFigureEstimator.scale_points(captured_points, current_center, scale_factor)
                
                if captured_points[POINT_RIGHT_WRIST] and current_points[POINT_RIGHT_WRIST]:
                    score_1 = StickFigureEstimator.score(captured_points[POINT_RIGHT_WRIST], current_points[POINT_RIGHT_WRIST])
                if captured_points[POINT_LEFT_WRIST] and current_points[POINT_LEFT_WRIST]:
                    score_2 = StickFigureEstimator.score(captured_points[POINT_LEFT_WRIST], current_points[POINT_LEFT_WRIST])
                
                if score_1 and score_2: 
                    self.current_score = (score_1 + score_2) / 2
                    self.score += (score_1 + score_2) / 2
                    self.feedback_score += (score_1 + score_2) /2
                    self.score_counter += 1
                    self.feedback_counter += 1 
                elif score_1:
                    self.current_score = score_1
                    self.score += score_1
                    self.feedback_score += score_1
                    self.score_counter += 1
                    self.feedback_counter += 1 
                elif score_2:
                    self.current_score = score_2
                    self.score += score_2
                    self.feedback_score += score_2
                    self.score_counter += 1
                    self.feedback_counter += 1 
                
                frame = StickFigureEstimator.overlay_avatar(frame, captured_points)
            feedback_score = self.feedback_score / self.feedback_counter
            
            if self.feedback_counter > self.FEEDBACK_RESET:
                self.feedback_counter = 1
                self.feedback_score = 0
                if feedback_score > 90:
                    self.feedback_rating = "PERFECT!"
                    self.feedback_color = (255, 0, 255) # Purple
                elif feedback_score > 80:
                    self.feedback_rating = "GREAT!"
                    self.feedback_color = (0, 255, 0) # Green
                elif feedback_score > 70:
                    self.feedback_rating = "ALRIGHT!" 
                    self.feedback_color = (255, 255, 0) # Yellow
                elif feedback_score > 60:
                    self.feedback_rating = "OK"
                    self.feedback_color = (255, 165, 0) # Orange
                else:
                    self.feedback_rating = "TRY HARDER"
                    self.feedback_color = (0, 0, 255)
                    
                    
            # Draw score on frame
            cv2.putText(frame, text=str(self.get_score()), org=(75, 100), fontFace=cv2.FONT_HERSHEY_DUPLEX,  
                    fontScale=2, color=(0, 0, 255) , thickness=4, lineType=cv2.LINE_AA) 
            # Draw feedback on frame
            if self.feedback_counter < Movement.FEEDBACK_RESET / 3:
                cv2.putText(frame, text=self.feedback_rating, org=(frame.shape[1]-375, 100), fontFace=cv2.FONT_HERSHEY_SIMPLEX,  
                        fontScale=2, color=self.feedback_color, thickness=4, lineType=cv2.LINE_AA)

        
        # -----------------
        # SEND JUMP MESSAGE
        # -----------------
        if self.test_path_ptr < len(self.captured_path):
            if self.captured_path[self.test_path_ptr][POINT_JUMP] == True or current_points[POINT_JUMP] == True:
                self.jump_counter = 24
            if self.jump_counter > 0:
                text_spot = (int(0.45 * frame.shape[1]), int(0.1 * frame.shape[0]))
                cv2.putText(frame, text='JUMP!', org=text_spot, fontFace=cv2.FONT_HERSHEY_SIMPLEX,  
                fontScale=2, color=(0, 0, 255) , thickness=4, lineType=cv2.LINE_AA) 
                self.jump_counter -= 1
        return frame

    
    def is_done(self):
        return self.test_path_ptr >= len(self.captured_path)

    
    def get_score(self):
        return int(self.score/self.score_counter * 100)/100.0
    
    
    def get_current_score(self):
        return self.current_score

    
    def draw_stick_figure_simple(frame, points):
        for (pointa, pointb) in Movement.__get_stick_figure_lines(points).values():
            if pointa and pointb:
                # Convert from relative to absolute
                pointa = (int(pointa[0] * frame.shape[1]), int(pointa[1] * frame.shape[0]))
                pointb = (int(pointb[0] * frame.shape[1]),  int(pointb[1] * frame.shape[0]))
                # Display
                cv2.line(frame, pointa, pointb, color=Movement.RED, thickness=Movement.STICK_FIGURE_THICKNESS) 
        return frame

    def reset(self):
        self.test_path_ptr = 0
        self.active_points = []
        self.jump_counter = 0
        self.score = 0
        self.score_counter = 1
        self.last_seen = {x: None for x in range(17)}
        self.history = [{x: None for x in range(17)}]