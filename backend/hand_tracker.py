import cv2
import mediapipe as mp
import time

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
                x = int(index_tip.x * width)
                y = int(index_tip.y * height)
                return x, y
        return None

    def check_gestures(self):
        """
        Detects:
        - Shooting: Index finger curl (Tip Y > PIP Y)
        - Rocket: V-Sign (Index & Middle fingers up, others down)
        """
        if not self.results or not self.results.multi_hand_landmarks:
            return {"shoot": False, "rocket": False}

        hand_landmarks = self.results.multi_hand_landmarks[0]
        landmarks = hand_landmarks.landmark

        # Index finger landmarks
        index_tip = landmarks[8]
        index_pip = landmarks[6]
        index_mcp = landmarks[5]

        # Middle finger landmarks
        middle_tip = landmarks[12]
        middle_pip = landmarks[10]

        # Ring and Pinky for V-sign check
        ring_tip = landmarks[16]
        pinky_tip = landmarks[20]

        # Shooting logic: Index tip is lower than PIP (curled)
        # Note: In MediaPipe, Y increases downwards
        is_shooting = index_tip.y > index_pip.y

        # Rocket logic (V-Sign): Index and Middle up, others down
        # 'Up' means Tip.y < PIP.y (since Y increases downwards)
        is_v_sign = (index_tip.y < index_pip.y and 
                     middle_tip.y < middle_pip.y and 
                     ring_tip.y > index_mcp.y and 
                     pinky_tip.y > index_mcp.y)

        return {"shoot": is_shooting, "rocket": is_v_sign}
