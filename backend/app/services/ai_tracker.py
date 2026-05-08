import cv2
import mediapipe as mp
import numpy as np
from app.core.config import settings

class AITracker:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=settings.MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=settings.MIN_TRACKING_CONFIDENCE
        )
        self.mp_draw = mp.solutions.drawing_utils

    def process_frame(self, frame):
        """
        Process a frame and return the coordinates of the index finger tip.
        Returns: (x, y) normalized coordinates or None if no hand detected.
        """
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Get Index Finger Tip (Landmark 8)
                index_finger_tip = hand_landmarks.landmark[8]
                return {
                    "x": index_finger_tip.x,
                    "y": index_finger_tip.y,
                    "z": index_finger_tip.z,
                    "detected": True
                }
        
        return {"detected": False}

tracker = AITracker()
