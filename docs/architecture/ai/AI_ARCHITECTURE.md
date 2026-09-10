# AI Pipeline Architecture (Draft)

Detailed breakdown of the frame processing lifecycle:
1. Camera Ingestion (OpenCV frame reader)
2. Detection Engine (Ultralytics YOLO model)
3. Multi-Object Tracking (ByteTrack identity management)
4. Polygon Spatial Engine (Point-in-polygon containment check)
5. State Transition & Event Engine (OUTSIDE → INSIDE intrusion trigger)
