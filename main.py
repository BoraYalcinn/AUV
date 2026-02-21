import cv2
import time

from vision import TopCameraVision
from decision import DecisionMaker
from control import PrintController


def main():

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Kamera açılamadı!")
        return

    # VISION
    vision = TopCameraVision()
    # DECISION
    decision = DecisionMaker()
    # CONTROL
    controller = PrintController()

    prev_time = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        vision_data = vision.process(frame)
        action = decision.update(vision_data)
        controller.execute(action)

        current_time = time.time()
        fps = 1 / (current_time - prev_time)
        prev_time = current_time

        # --- DEBUG OVERLAY ---
        cv2.putText(frame, f"FPS: {int(fps)}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        cv2.putText(frame, f"Mode: {action['mode']}", (10, 55),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

        cv2.putText(frame, f"Angle: {round(vision_data['angle'],2)}", (10, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

        cv2.putText(frame, f"Error: {round(vision_data['center_error'],3)}", (10, 105),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 200, 0), 2)

        cv2.putText(frame, action["debug"], (10, 130),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 200, 255), 2)

        cv2.imshow("Frame", frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()