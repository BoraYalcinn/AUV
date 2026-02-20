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

    vision = TopCameraVision()
    decision = DecisionMaker()
    controller = PrintController()

    prev_time = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Frame alınamadı!")
            break

        # ---------------------------
        # VISION
        # ---------------------------
        vision_data = vision.process(frame)

        # ---------------------------
        # DECISION
        # ---------------------------
        action = decision.update(vision_data)

        # ---------------------------
        # CONTROL
        # ---------------------------
        controller.execute(action)

        # ---------------------------
        # FPS HESABI
        # ---------------------------
        current_time = time.time()
        fps = 1 / (current_time - prev_time)
        prev_time = current_time

        cv2.putText(
            frame,
            f"FPS: {int(fps)}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )


        cv2.putText(
            frame,
            f"MODE: {action['mode']}",
            (10, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 255),
            2
        )

        cv2.imshow("Frame", frame)


        key = cv2.waitKey(1) & 0xFF
        if key == 27:
            print("ESC pressed. Exiting...")
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()