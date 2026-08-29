import os
import time
import cv2
import numpy as np
from ai.pipeline.runner import CameraPipelineRunner
from ai.core.logging import setup_ai_logging


def generate_benchmark_video(video_path: str, num_frames: int = 300, width: int = 1280, height: int = 720) -> str:
    """Generate a benchmark test video file if it does not already exist."""
    os.makedirs(os.path.dirname(video_path), exist_ok=True)
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    out = cv2.VideoWriter(video_path, fourcc, 30.0, (width, height))
    
    for i in range(num_frames):
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        cv2.circle(frame, (100 + (i * 5) % (width - 200), height // 2), 60, (0, 255, 0), -1)
        cv2.putText(frame, f"Benchmark Frame {i+1}/{num_frames}", (50, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
        out.write(frame)
    
    out.release()
    return video_path


def run_benchmark(video_path: str, target_width: int = None, target_height: int = None):
    setup_ai_logging()
    print("============================================================")
    print("  IBVAP M2.1 Computer Vision Pipeline Performance Benchmark  ")
    print("============================================================")

    runner = CameraPipelineRunner(
        source_type="VIDEO_FILE",
        video_path=video_path,
        target_width=target_width,
        target_height=target_height,
        display_preview=False
    )

    start_time = time.perf_counter()
    frames_processed = runner.run()
    elapsed_time = time.perf_counter() - start_time

    avg_fps = frames_processed / elapsed_time if elapsed_time > 0 else 0.0

    print("\n---------------- Benchmark Results ----------------")
    print(f"Source Video:         {video_path}")
    print(f"Target Resolution:    {target_width or 1280}x{target_height or 720}")
    print(f"Total Frames:         {frames_processed}")
    print(f"Elapsed Time:         {elapsed_time:.4f} seconds")
    print(f"Average Throughput:   {avg_fps:.2f} FPS")
    print("---------------------------------------------------\n")

    return {
        "frames": frames_processed,
        "elapsed_seconds": elapsed_time,
        "fps": avg_fps
    }


if __name__ == "__main__":
    benchmark_video = "data/videos/benchmark/benchmark_1280x720.avi"
    generate_benchmark_video(benchmark_video, num_frames=300, width=1280, height=720)
    run_benchmark(benchmark_video)
