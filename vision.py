import cv2
import numpy as np
from abc import ABC, abstractmethod
import math


class BaseVision(ABC):
    @abstractmethod
    def process(self, frame):
        pass


class TopCameraVision(BaseVision):

    def __init__(self):
        # --- DEĞİŞTİRİLDİ: Threshold sıkılaştırıldı ---
        self.lower = np.array([0, 0, 0])
        self.upper = np.array([180, 255, 50])

        self.min_area = 1000  # --- DEĞİŞTİRİLDİ: 800 → 1000 ---

    def threshold_strip(self, frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.lower, self.upper)

        kernel = np.ones((5, 5), np.uint8)

        # --- DEĞİŞTİRİLDİ: Close + Open ---
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

        return mask

    def get_largest_contour(self, mask):
        contours, _ = cv2.findContours(
            mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        if not contours:
            return None

        largest = max(contours, key=cv2.contourArea)

        if cv2.contourArea(largest) < self.min_area:
            return None

        return largest

    def compute_centroid(self, contour):
        M = cv2.moments(contour)
        if M["m00"] == 0:
            return None

        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])
        return cx, cy

    def compute_angle(self, contour):
        data_pts = np.float32(contour.reshape(-1, 2))
        mean, eigenvectors = cv2.PCACompute(data_pts, mean=None)

        vx, vy = eigenvectors[0]
        angle = math.degrees(math.atan2(vy, vx))

        # --- DEĞİŞTİRİLDİ: -90 / +90 normalize ---
        if angle > 90:
            angle -= 180
        if angle < -90:
            angle += 180

        return angle

    def detect_turn(self, contour, frame):
        x, y, w, h = cv2.boundingRect(contour)

        # --- DEĞİŞTİRİLDİ: oran arttırıldı (1.2 → 1.5) ---
        if w > h * 1.5:

            centroid = self.compute_centroid(contour)
            if centroid is None:
                return False, None

            cx, _ = centroid
            frame_center = frame.shape[1] // 2

            if cx > frame_center:
                return True, "RIGHT"
            else:
                return True, "LEFT"

        return False, None

    def process(self, frame):

        mask = self.threshold_strip(frame)
        contour = self.get_largest_contour(mask)

        if contour is None:
            return {
                "line_found": False,
                "center_error": 0,
                "angle": 0,
                "turn_detected": False,
                "turn_direction": None
            }

        centroid = self.compute_centroid(contour)
        if centroid is None:
            return {
                "line_found": False,
                "center_error": 0,
                "angle": 0,
                "turn_detected": False,
                "turn_direction": None
            }

        cx, cy = centroid
        frame_center = frame.shape[1] // 2

        center_error = (cx - frame_center) / frame_center
        angle = self.compute_angle(contour)
        turn_flag, direction = self.detect_turn(contour, frame)

        cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)
        cv2.line(frame, (frame_center, 0), (frame_center, frame.shape[0]), (255, 0, 0), 2)

        return {
            "line_found": True,
            "center_error": center_error,
            "angle": angle,
            "turn_detected": turn_flag,
            "turn_direction": direction
        }