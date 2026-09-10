# IBVAP Multi-Object Tracking Specification

**Module:** `ai/tracking/tracker.py`  
**Algorithm:** ByteTrack (ByteTrack association with Kalman filtering)  
**Track Schema:** `ai/tracking/schemas.py` (`Track` dataclass)  

---

## 1. ByteTrack Spatial Association

ByteTrack associates detection boxes with existing trajectories by preserving both high-confidence and low-confidence detections:

1. **High-Score Association:** Detections with confidence $\ge 0.35$ are matched first using Intersection-over-Union (IoU) cost matrix.
2. **Low-Score Association:** Remaining unmatched tracks are matched against lower-score detections ($0.1 \le \text{conf} < 0.35$), maintaining track continuity through temporary occlusions or motion blur.
3. **Kalman Filter Propagation:** Predicts position and velocity across frames when subjects are momentarily hidden behind terrain or structures.

---

## 2. Feet Coordinate Calculation

For surveillance geofencing, evaluating ground contact points (feet) avoids false alarms from upper-body shadows or leaning postures:

$$\text{feet\_x} = \frac{x_1 + x_2}{2}, \quad \text{feet\_y} = y_2$$

This bottom-center coordinate is passed directly to the polygon geofence engine.
