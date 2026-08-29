from sqlalchemy.orm import Session
from app.core.logging import logger
from app.db.database import SessionLocal
from app.models.camera import Camera
from app.models.zone import Zone
from app.models.user import User
from app.models.enums import CameraSourceType, ZoneType, UserRole


def seed_demo_data(db: Session) -> None:
    """
    Seeds development-only demo records into database.
    Creates 1 demo camera, 1 demo polygon zone, and 1 development admin user.
    """
    logger.info("Checking for demo seed data...")

    # Seed Demo User
    user = db.query(User).filter(User.username == "admin").first()
    if not user:
        user = User(
            username="admin",
            email="admin@ibvap.local",
            # Placeholder hash for development seed user (e.g. bcrypt hash of 'admin123')
            password_hash="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeg6Lruj3vjPGga31lW",
            role=UserRole.ADMINISTRATOR,
            is_active=True
        )
        db.add(user)
        logger.info("Seeded development admin user ('admin').")

    # Seed Demo Camera
    camera = db.query(Camera).filter(Camera.camera_identifier == "cam-webcam-01").first()
    if not camera:
        camera = Camera(
            name="Main Perimeter Webcam 01",
            camera_identifier="cam-webcam-01",
            source_type=CameraSourceType.WEBCAM,
            source_url="0",
            location="Gate Alpha Perimeter",
            is_active=True
        )
        db.add(camera)
        db.flush()
        logger.info("Seeded development camera ('cam-webcam-01').")

    # Seed Demo Zone
    zone = db.query(Zone).filter(Zone.name == "Perimeter Restricted Zone A").first()
    if not zone:
        zone = Zone(
            camera_id=camera.id,
            name="Perimeter Restricted Zone A",
            zone_type=ZoneType.RESTRICTED,
            # Ordered 2D normalized coordinates [[x1, y1], [x2, y2], ...]
            polygon_coordinates=[
                [0.20, 0.30],
                [0.80, 0.30],
                [0.85, 0.85],
                [0.15, 0.85]
            ],
            is_active=True
        )
        db.add(zone)
        logger.info("Seeded development restricted zone ('Perimeter Restricted Zone A').")

    db.commit()
    logger.info("Demo seed data process complete.")


if __name__ == "__main__":
    db_session = SessionLocal()
    try:
        seed_demo_data(db_session)
    finally:
        db_session.close()
