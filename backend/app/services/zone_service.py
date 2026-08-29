from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.zone import Zone
from app.schemas.zone import ZoneCreate, ZoneUpdate
from app.services.camera_service import CameraService


class ZoneService:
    @staticmethod
    def list_zones(db: Session, camera_id: str, is_active: Optional[bool] = None) -> List[Zone]:
        """
        List zones for a camera, raising 404 if the camera doesn't exist.
        """
        # Validate camera exists
        CameraService.get_camera(db, camera_id)

        query = db.query(Zone).filter(Zone.camera_id == camera_id)
        if is_active is not None:
            query = query.filter(Zone.is_active == is_active)
        return query.all()

    @staticmethod
    def get_zone(db: Session, zone_id: str) -> Zone:
        """
        Fetch zone details by ID. Raises 404 if missing.
        """
        zone = db.query(Zone).filter(Zone.id == zone_id).first()
        if not zone:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Zone not found"
            )
        return zone

    @staticmethod
    def create_zone(db: Session, camera_id: str, zone_in: ZoneCreate) -> Zone:
        """
        Create a new zone belonging to an existing camera.
        """
        # Validate camera exists
        CameraService.get_camera(db, camera_id)

        zone = Zone(
            camera_id=camera_id,
            name=zone_in.name,
            zone_type=zone_in.zone_type,
            polygon_coordinates=zone_in.polygon_coordinates,
            is_active=zone_in.is_active
        )
        db.add(zone)
        db.commit()
        db.refresh(zone)
        return zone

    @staticmethod
    def update_zone(db: Session, zone_id: str, zone_in: ZoneUpdate) -> Zone:
        """
        Update zone details, validating input coordinates if updated.
        """
        zone = ZoneService.get_zone(db, zone_id)

        update_data = zone_in.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(zone, key, value)

        db.commit()
        db.refresh(zone)
        return zone

    @staticmethod
    def delete_zone(db: Session, zone_id: str) -> Zone:
        """
        Soft-deactivate zone (is_active = False) to preserve historical references.
        """
        zone = ZoneService.get_zone(db, zone_id)
        zone.is_active = False
        db.commit()
        db.refresh(zone)
        return zone
