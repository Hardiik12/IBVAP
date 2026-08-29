from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.camera import Camera
from app.schemas.camera import CameraCreate, CameraUpdate


class CameraService:
    @staticmethod
    def list_cameras(db: Session, is_active: Optional[bool] = None) -> List[Camera]:
        """
        List all cameras, optionally filtered by activity status.
        """
        query = db.query(Camera)
        if is_active is not None:
            query = query.filter(Camera.is_active == is_active)
        return query.all()

    @staticmethod
    def get_camera(db: Session, camera_id: str) -> Camera:
        """
        Fetch a camera by ID. Raises 404 if missing.
        """
        camera = db.query(Camera).filter(Camera.id == camera_id).first()
        if not camera:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Camera not found"
            )
        return camera

    @staticmethod
    def create_camera(db: Session, camera_in: CameraCreate) -> Camera:
        """
        Create a new camera, enforcing camera_identifier uniqueness.
        """
        existing = db.query(Camera).filter(Camera.camera_identifier == camera_in.camera_identifier).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Camera identifier already exists"
            )
        
        camera = Camera(**camera_in.model_dump())
        db.add(camera)
        db.commit()
        db.refresh(camera)
        return camera

    @staticmethod
    def update_camera(db: Session, camera_id: str, camera_in: CameraUpdate) -> Camera:
        """
        Update an existing camera by ID, preserving uniqueness of camera_identifier if updated.
        """
        camera = CameraService.get_camera(db, camera_id)

        update_data = camera_in.model_dump(exclude_unset=True)

        if "camera_identifier" in update_data:
            new_identifier = update_data["camera_identifier"]
            if new_identifier != camera.camera_identifier:
                existing = db.query(Camera).filter(Camera.camera_identifier == new_identifier).first()
                if existing:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Camera identifier already exists"
                    )

        for key, value in update_data.items():
            setattr(camera, key, value)

        db.commit()
        db.refresh(camera)
        return camera

    @staticmethod
    def delete_camera(db: Session, camera_id: str) -> Camera:
        """
        Soft-deactivate camera (is_active = False) to preserve event/evidence audit logs.
        """
        camera = CameraService.get_camera(db, camera_id)
        camera.is_active = False
        db.commit()
        db.refresh(camera)
        return camera
