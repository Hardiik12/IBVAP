"""Manual validation script demonstrating M3 Camera Ingestion feeding M2 YOLO Detection."""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

# Ensure IBVAP root directory is in sys.path when script is executed directly
ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import cv2

from ai.camera.base import CameraSource
from ai.camera.file import VideoFileSource
from ai.camera.synthetic import SyntheticSource
from ai.camera.webcam import WebcamSource
from ai.detection.detector import YOLODetector


def run_camera_detection_demo(
    source_type: str = "webcam",
    video_path: str | None = None,
    camera_index: int = 0,
    max_frames: int | None = None,
    display: bool = True,
) -> None:
    """
    Acquires frames via M3 CameraSource and passes them directly to existing M2 YOLODetector.

    :param source_type: 'webcam', 'video', or 'synthetic'
    :param video_path: Path to recorded video file (for 'video' source)
    :param camera_index: Webcam hardware device index
    :param max_frames: Optional max frames to process
    :param display: Whether to render GUI window
    """
    print("=== IBVAP M3 Ingestion -> M2 Detection Integration Demo ===")
    print(f"Source Type  : {source_type}")

    # 1. Initialize M3 Camera Source
    camera: CameraSource
    if source_type == "video":
        if not video_path:
            print("Error: --video path required when source_type is 'video'")
            sys.exit(1)
        camera = VideoFileSource(file_path=video_path, loop=False)
    elif source_type == "webcam":
        camera = WebcamSource(camera_index=camera_index)
    else:
        camera = SyntheticSource(width=640, height=480, max_frames=max_frames or 100)

    # 2. Initialize existing M2 YOLO Detector
    detector = YOLODetector(confidence_threshold=0.35)
    print("YOLO Detector initialized.")

    frame_count = 0
    t_start = time.perf_counter()
    fps = 0.0

    camera.open()
    try:
        while True:
            if max_frames is not None and frame_count >= max_frames:
                break

            ok, frame = camera.read_frame()
            if not ok or frame is None:
                print("End of stream or frame acquisition failed.")
                break

            frame_count += 1

            # Direct integration: pass OpenCV BGR frame to existing M2 detector
            detections = detector.detect(frame)

            # Compute running FPS
            elapsed = time.perf_counter() - t_start
            if elapsed >= 1.0:
                fps = frame_count / elapsed

            if display:
                annotated = frame.copy()
                for det in detections:
                    x1, y1, x2, y2 = [int(v) for v in det.bbox]
                    cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(
                        annotated,
                        f"{det.class_name} {det.confidence:.2f}",
                        (x1, max(20, y1 - 8)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (0, 255, 0),
                        2,
                    )

                cv2.putText(
                    annotated,
                    f"M3 Camera Ingestion -> M2 YOLO | FPS: {fps:.1f} | Detections: {len(detections)}",
                    (10, 25),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 255),
                    2,
                )
                cv2.imshow("IBVAP M3 -> M2 Demo (Press 'q' to quit)", annotated)

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    print("User interrupted.")
                    break
            else:
                if frame_count % 30 == 0:
                    print(f"Processed {frame_count} frames | Detections in last frame: {len(detections)}")

    finally:
        camera.release()
        if display:
            cv2.destroyAllWindows()

    print(f"\nTotal Frames Processed: {frame_count}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="M3 Camera Ingestion to M2 Detection Demo")
    parser.add_argument("--source", choices=["webcam", "video", "synthetic"], default="webcam")
    parser.add_argument("--video", type=str, help="Path to video file")
    parser.add_argument("--camera-index", type=int, default=0, help="Camera index")
    parser.add_argument("--max-frames", type=int, help="Max frames")
    parser.add_argument("--no-display", action="store_true", help="Disable GUI window")
    args = parser.parse_args()

    run_camera_detection_demo(
        source_type=args.source,
        video_path=args.video,
        camera_index=args.camera_index,
        max_frames=args.max_frames,
        display=not args.no_display,
    )
