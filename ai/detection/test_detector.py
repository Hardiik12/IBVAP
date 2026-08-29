"""Manual test for the IBVAP YOLO detector."""

import cv2

from ai.detection.detector import YOLODetector


def main() -> None:
    detector = YOLODetector()

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        raise RuntimeError(
            "Could not open camera."
        )

    try:
        while True:

            ok, frame = cap.read()

            if not ok:
                print("Failed to read frame.")
                break

            detections = detector.detect(frame)

            print(
                [
                    detection.to_dict()
                    for detection in detections
                ]
            )

            cv2.imshow(
                "IBVAP Phase 2 Detection Test",
                frame,
            )

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
