"""IBVAP MVP: webcam -> YOLO detection.
Press q to quit.
"""
import os
import time
import cv2
from ultralytics import YOLO

MODEL = os.getenv("YOLO_MODEL", "yolov8n.pt")
CONF = float(os.getenv("YOLO_CONFIDENCE", "0.35"))
CAMERA_INDEX = int(os.getenv("CAMERA_INDEX", "0"))

# COCO classes used by the MVP.
PERSON_CLASS = 0
VEHICLE_CLASSES = {2, 3, 5, 7}  # car, motorcycle, bus, truck


def main() -> None:
    model = YOLO(MODEL)
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        raise RuntimeError(
            f"Could not open camera index {CAMERA_INDEX}. "
            "Check camera permissions and whether another app is using it."
        )

    frames = 0
    started = time.perf_counter()
    fps = 0.0

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                print("Camera frame read failed")
                break

            result = model.predict(frame, conf=CONF, verbose=False)[0]
            annotated = result.plot()

            frames += 1
            elapsed = time.perf_counter() - started
            if elapsed >= 1.0:
                fps = frames / elapsed
                frames = 0
                started = time.perf_counter()

            people = 0
            vehicles = 0
            if result.boxes is not None:
                for cls in result.boxes.cls.tolist():
                    cls = int(cls)
                    if cls == PERSON_CLASS:
                        people += 1
                    elif cls in VEHICLE_CLASSES:
                        vehicles += 1

            cv2.putText(
                annotated,
                f"IBVAP | FPS: {fps:.1f} | People: {people} | Vehicles: {vehicles}",
                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2,
            )
            cv2.imshow("IBVAP - Live Detection", annotated)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
