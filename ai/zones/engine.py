"""Virtual polygon zone engine for spatial containment analysis."""

from __future__ import annotations

import cv2
import numpy as np

from ai.tracking.schemas import Track
from ai.zones.schemas import ZoneConfig, ZoneState


def calculate_reference_point(bbox: list[float]) -> tuple[float, float]:
    """
    Calculate the bottom-center reference point of a bounding box.

    Complies with ADR-004: In ground-plane surveillance, the bottom-center
    ( (x1 + x2) / 2, y2 ) represents where the subject's feet touch the ground.
    """
    if len(bbox) != 4:
        raise ValueError(f"Expected 4 bounding box coordinates [x1, y1, x2, y2], got {len(bbox)}")

    x1, _y1, x2, y2 = bbox
    x_center = (float(x1) + float(x2)) / 2.0
    y_bottom = float(y2)
    return (x_center, y_bottom)


class PolygonZone:
    """Represents a single restricted polygon zone and evaluates point containment."""

    def __init__(
        self,
        config: ZoneConfig,
        frame_resolution: tuple[int, int] | None = None,
    ) -> None:
        """
        Initialize PolygonZone.

        :param config: ZoneConfig dataclass containing coordinates and metadata.
        :param frame_resolution: Optional (width, height) used to denormalize coordinates.
        """
        self.config = config
        self.frame_resolution = frame_resolution
        self._polygon_np = self._prepare_polygon_array()

    def _prepare_polygon_array(self) -> np.ndarray:
        """Convert polygon coordinates into a contiguous float32 / int32 NumPy contour."""
        coords = np.array(self.config.polygon_coordinates, dtype=np.float32)

        if coords.ndim != 2 or coords.shape[0] < 3 or coords.shape[1] != 2:
            raise ValueError(
                f"Polygon must have at least 3 vertices with [x, y] coordinates. Got shape: {coords.shape}"
            )

        if self.config.is_normalized:
            if self.frame_resolution is None:
                raise ValueError(
                    "frame_resolution (width, height) is required when zone coordinates are normalized."
                )
            width, height = self.frame_resolution
            coords[:, 0] *= width
            coords[:, 1] *= height

        return coords.astype(np.float32)

    def set_frame_resolution(self, width: int, height: int) -> None:
        """Update frame resolution and recompute polygon array if coordinates are normalized."""
        self.frame_resolution = (width, height)
        self._polygon_np = self._prepare_polygon_array()

    def contains_point(self, point: tuple[float, float]) -> bool:
        """
        Test if a coordinate (x, y) falls inside or on the boundary of the polygon zone.

        Uses OpenCV pointPolygonTest (measureDist=False).
        Returns True if point is inside (>= 0), False otherwise (< 0).
        """
        pt_x, pt_y = point
        # cv2.pointPolygonTest expects float coordinates and contour array
        result = cv2.pointPolygonTest(self._polygon_np, (float(pt_x), float(pt_y)), measureDist=False)
        return result >= 0

    def evaluate_track(self, track: Track) -> ZoneState:
        """
        Evaluate whether a tracked object's reference point is inside this polygon zone.

        Returns ZoneState.INSIDE or ZoneState.OUTSIDE.
        """
        ref_pt = track.reference_point
        is_inside = self.contains_point(ref_pt)
        return ZoneState.INSIDE if is_inside else ZoneState.OUTSIDE


class ZoneEngine:
    """Manages multiple virtual polygon zones and evaluates collections of tracks."""

    def __init__(self, zones: list[PolygonZone] | None = None) -> None:
        self._zones: dict[str, PolygonZone] = {}
        if zones:
            for zone in zones:
                self.add_zone(zone)

    def add_zone(self, zone: PolygonZone) -> None:
        """Register a new polygon zone."""
        self._zones[zone.config.zone_id] = zone

    def remove_zone(self, zone_id: str) -> None:
        """Remove a polygon zone by ID."""
        self._zones.pop(zone_id, None)

    def get_zone(self, zone_id: str) -> PolygonZone | None:
        """Retrieve a polygon zone by ID."""
        return self._zones.get(zone_id)

    @property
    def zones(self) -> list[PolygonZone]:
        """Return list of all registered zones."""
        return list(self._zones.values())

    def evaluate_tracks(
        self,
        tracks: list[Track],
    ) -> dict[str, list[Track]]:
        """
        Evaluate all tracks against all registered zones.

        Returns a dictionary mapping zone_id to the list of tracks currently INSIDE that zone.
        """
        zone_occupancy: dict[str, list[Track]] = {
            zone_id: [] for zone_id in self._zones
        }

        for track in tracks:
            for zone_id, zone in self._zones.items():
                if zone.evaluate_track(track) == ZoneState.INSIDE:
                    zone_occupancy[zone_id].append(track)

        return zone_occupancy
