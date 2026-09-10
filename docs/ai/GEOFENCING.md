# IBVAP Polygon Geofencing Specification

**Module:** `ai/zones/engine.py`  
**Algorithm:** Ray-Casting Point-in-Polygon (PIP) / Even-Odd Crossing Rule  
**Coordinate Formats:** Normalized coordinates $[0.0, 1.0]$ and absolute pixel coordinates $[0, W] \times [0, H]$  

---

## 1. Ray-Casting Algorithm

Given a test point $P(x, y)$ (the subject's feet) and a polygon boundary defined by vertices $V_0, V_1, \dots, V_{n-1}$:

1. A horizontal ray is cast from $(x, y)$ towards positive infinity $(+\infty, y)$.
2. The number of polygon edge intersections is counted:
   - **Odd Intersections:** Point is **INSIDE** the restricted zone.
   - **Even Intersections:** Point is **OUTSIDE** the restricted zone.

```python
def is_point_inside(self, x: float, y: float) -> bool:
    inside = False
    n = len(self.coordinates)
    p1x, p1y = self.coordinates[0]
    for i in range(1, n + 1):
        p2x, p2y = self.coordinates[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside
```

---

## 2. Dynamic Zone Updates

Zones can be created, updated, or deactivated via the REST API (`/api/v1/cameras/{id}/zones`) without requiring an AI pipeline restart.
