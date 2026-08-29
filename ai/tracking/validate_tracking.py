"""Manual and integration validation script for ByteTrack multi-object tracking.

Validates that moving subjects maintain stable track IDs across successive frames
using either a recorded test video, webcam, or synthetic sequence.
"""

from __future__ import annotations

import argparse
import sys
import time
from collections import defaultdict
from pathlib import Path

# Ensure IBVAP root directory is in sys.path when script is executed directly
ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import cv2

from ai.camera.file import VideoFileSource
from ai.camera.synthetic import SyntheticSource
from ai.camera.webcam import WebcamSource
from ai.tracking.tracker import ByteTracker


def run_tracking_validation(
    source_type: str = "synthetic",
    video_path: str | None = None,
    camera_index: int = 0,
    max_frames: int = 150,
    display: bool = False,
) -> None:
    """
    Execute tracking validation on a video stream and report empirical track metrics.

    :param source_type: 'video', 'webcam', or 'synthetic'
    :param video_path: Path to video file (if source_type == 'video')
    :param camera_index: Webcam device index (if source_type == 'webcam')
    :param max_frames: Maximum number of frames to process
    :param display: Whether to show OpenCV GUI preview window
    """
    print(f"=== IBVAP ByteTrack Validation ===")
    print(f"Source Type : {source_type}")
    print(f"Max Frames  : {max_frames}")

    # 1. Initialize Camera Source
    if source_type == "video":
        if not video_path:
            print("Error: --video path required for 'video' source type.")
            sys.exit(1)
        camera = VideoFileSource(file_path=video_path, loop=False)
    elif source_type == "webcam":
        camera = WebcamSource(camera_index=camera_index)
    else:
        camera = SyntheticSource(width=640, height=480, max_frames=max_frames)

    # 2. Initialize Tracker
    tracker = ByteTracker(confidence_threshold=0.35)
    print("Tracker initialized successfully.")

    # 3. Process Video Sequence
    camera.open()
    frame_count = 0
    track_appearances: dict[int, list[int]] = defaultdict(list)
    start_time = time.perf_counter()

    try:
        while frame_count < max_frames:
            ok, frame = camera.read_frame()
            if not ok or frame is None:
                print(f"Reached end of video stream at frame {frame_count}.")
                break

            frame_count += 1
            tracks = tracker.track(frame)

            for t in tracks:
                if t.track_id >= 0:
                    track_appearances[t.track_id].append(frame_count)

            if display:
                for t in tracks:
                    x1, y1, x2, y2 = [int(v) for v in t.bbox]
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(
                        frame,
                        f"ID: {t.track_id} {t.class_name} ({t.confidence:.2f})",
                        (x1, max(20, y1 - 10)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (0, 255, 0),
                        2,
                    )
                cv2.imshow("IBVAP Tracking Validation", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    print("User interrupted display.")
                    break

    finally:
        camera.release()
        if display:
            cv2.destroyAllWindows()

    total_time = time.perf_counter() - start_time
    avg_fps = frame_count / total_time if total_time > 0 else 0.0

    # 4. Report Empirical Results
    print("\n=== Validation Results ===")
    print(f"Total Frames Processed : {frame_count}")
    print(f"Elapsed Time           : {total_time:.2f}s")
    print(f"Average Pipeline FPS   : {avg_fps:.1f}")
    print(f"Unique Track IDs Found : {len(track_appearances)}")

    if track_appearances:
        print("\n--- Track Continuity Summary ---")
        print(f"{'Track ID':<10} | {'First Frame':<12} | {'Last Frame':<12} | {'Total Frames Active':<20}")
        print("-" * 62)
        for tid, frames in sorted(track_appearances.items()):
            print(f"{tid:<10} | {frames[0]:<12} | {frames[-1]:<12} | {len(frames):<20}")
    else:
        print("Note: No tracked subjects detected in this test sequence.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="IBVAP ByteTrack Validation Script")
    parser.add_argument("--source", choices=["synthetic", "video", "webcam"], default="synthetic")
    parser.add_argument("--video", type=str, help="Path to video file")
    parser.add_argument("--camera-index", type=int, default=0, help="Webcam device index")
    parser.add_argument("--max-frames", type=int, default=100, help="Max frames to process")
    parser.add_argument("--display", action="store_true", help="Display visual GUI window")
    args = parser.parse_args()

    run_tracking_validation(
        source_type=args.source,
        video_path=args.video,
        camera_index=args.camera_index,
        max_frames=args.max_frames,
        display=args.display,
    )
