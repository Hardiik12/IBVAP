# Camera Module

Responsible for video stream ingestion and camera source abstraction.

## Owner
M3 — Video/Edge Lead

## Functionality
- Abstracts webcam (USB / built-in), recorded video files, and future RTSP streams behind a unified interface.
- Delivers standard frame representations (OpenCV format / NumPy array) to the detection module.
