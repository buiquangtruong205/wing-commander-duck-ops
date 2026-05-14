import cv2
import mediapipe as mp
import time
import math

class HandTracker:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.results = None

    def is_detected(self):
        return self.results is not None and self.results.multi_hand_landmarks is not None

    def process_frame(self, frame):
        # Convert the BGR image to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(rgb_frame)
        return self.results

    def get_hand_coords(self, width, height):
        if self.results and self.results.multi_hand_landmarks:
            for hand_landmarks in self.results.multi_hand_landmarks:
                # Landmark 8 is the Index Finger Tip
                index_tip = hand_landmarks.landmark[8]
                # Map normalized [0, 1] to screen width/height
                x = int(index_tip.x * width)
                y = int(index_tip.y * height)
                return x, y
        return None

    def check_gestures(self):
        """
        Detects:
        - Shooting: Index finger curl (Tip Y > PIP Y)
        - Rocket: V-Sign (Index & Middle fingers up, Ring & Pinky curled)
        """
        if not self.results or not self.results.multi_hand_landmarks:
            return {"shoot": False, "rocket": False}

        hand_landmarks = self.results.multi_hand_landmarks[0]
        landmarks = hand_landmarks.landmark

        def is_finger_up(tip_idx, pip_idx):
            # In MediaPipe, Y increases downwards, so Tip Y < PIP Y means Finger is UP
            return landmarks[tip_idx].y < landmarks[pip_idx].y

        # Basic finger states
        index_up = is_finger_up(8, 6)
        middle_up = is_finger_up(12, 10)
        ring_up = is_finger_up(16, 14)
        pinky_up = is_finger_up(20, 18)

        # Shooting logic: Index tip is lower than DIP (more sensitive than PIP)
        is_shooting = landmarks[8].y > landmarks[7].y

        # Rocket logic (V-Sign): Index and Middle up, Ring and Pinky curled
        # We normalize the distance between fingers by the hand size (wrist to middle MCP)
        # to ensure it works consistently at different distances from the camera.
        hand_scale = math.hypot(landmarks[0].x - landmarks[9].x, landmarks[0].y - landmarks[9].y)
        if hand_scale < 0.01: hand_scale = 0.1 # Safety fallback
        
        # Actual Euclidean distance between index and middle tips
        tip_dist = math.hypot(landmarks[8].x - landmarks[12].x, landmarks[8].y - landmarks[12].y)
        norm_dist = tip_dist / hand_scale
        
        is_v_sign = (index_up and 
                     middle_up and 
                     not ring_up and 
                     not pinky_up and
                     norm_dist > 0.45) # Require significant spread (xòe) relative to hand size

        return {"shoot": is_shooting, "rocket": is_v_sign}
