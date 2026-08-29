import base64
import uuid
import hashlib
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.config import settings
from app.models.user import User
from app.models.enums import UserRole, EventType, EventSeverity, EventStatus, AlertStatus
from app.models.event import Event
from app.models.evidence import Evidence
from app.models.alert import Alert
from app.schemas.evidence import (
    EvidenceCreate,
    EvidenceUpdate,
    EvidenceResponse,
    EvidenceHashResponse,
    EvidenceVerificationResponse,
    EvidenceCaptureRequest,
    EvidenceDetailResponse,
)
from app.services.evidence_service import EvidenceService
from app.services.evidence_integrity_service import EvidenceIntegrityService
from app.services.audit_service import AuditService
from app.services.websocket_manager import websocket_manager
from app.api.deps import require_role

logger = logging.getLogger(__name__)

router = APIRouter()

# Role permissions
view_evidence_role = require_role([UserRole.OPERATOR, UserRole.ANALYST, UserRole.ADMINISTRATOR, UserRole.AUDITOR])
manage_evidence_role = require_role([UserRole.OPERATOR, UserRole.ADMINISTRATOR])
hash_evidence_role = require_role([UserRole.OPERATOR, UserRole.ADMINISTRATOR])


def map_evidence_to_response(evidence: Evidence) -> EvidenceResponse:
    """Helper to map Evidence model to EvidenceResponse with dynamic image_url and strict UTC."""
    captured_dt = evidence.captured_at
    if captured_dt.tzinfo is None:
        captured_dt = captured_dt.replace(tzinfo=timezone.utc)
    else:
        captured_dt = captured_dt.astimezone(timezone.utc)

    created_dt = evidence.created_at
    if created_dt.tzinfo is None:
        created_dt = created_dt.replace(tzinfo=timezone.utc)
    else:
        created_dt = created_dt.astimezone(timezone.utc)

    return EvidenceResponse(
        id=evidence.id,
        evidence_identifier=evidence.evidence_identifier,
        event_id=evidence.event_id,
        file_path=evidence.file_path,
        captured_at=captured_dt,
        created_at=created_dt,
        sha256_hash=evidence.sha256_hash,
        image_url=f"/api/v1/evidence/{evidence.id}/image",
        metadata=evidence.evidence_metadata,
    )


@router.post("/evidence/capture", response_model=EvidenceDetailResponse, status_code=status.HTTP_201_CREATED)
def capture_real_evidence(
    payload: EvidenceCaptureRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(manage_evidence_role),
) -> EvidenceDetailResponse:
    """
    Real-Time Evidence Capture & Ingestion Endpoint.
    1. Saves the raw webcam frame captured at the exact moment of intrusion to disk.
    2. Calculates the cryptographic SHA-256 binary hash digest immediately.
    3. Persists the Event, Alert, and Evidence records atomically in the database with authoritative UTC timestamps.
    4. Broadcasts real-time WebSocket alert.
    """
    try:
        # 1. Decode base64 image bytes
        image_data = payload.image
        if "," in image_data:
            image_data = image_data.split(",", 1)[1]
        image_bytes = base64.b64decode(image_data)
        if len(image_bytes) == 0:
            raise ValueError("Empty image data provided.")

        # 2. Compute cryptographic SHA-256 hash immediately from raw bytes
        calculated_sha256 = hashlib.sha256(image_bytes).hexdigest().lower()

        # 3. Setup file paths & ensure directory exists
        evidence_id = str(uuid.uuid4())
        filename = f"{evidence_id}.jpg"
        
        evidence_dir = Path(settings.EVIDENCE_ROOT).resolve()
        evidence_dir.mkdir(parents=True, exist_ok=True)
        disk_path = evidence_dir / filename

        # 4. Write image bytes to physical file
        with open(disk_path, "wb") as f:
            f.write(image_bytes)

        rel_file_path = f"data/evidence/{filename}"
        
        # Authoritative UTC Server Timestamp
        captured_dt = datetime.now(timezone.utc)

        # 5. Resolve valid camera
        camera_id = payload.camera_id or "cam-01"
        from app.models.camera import Camera
        cam = db.query(Camera).filter((Camera.id == camera_id) | (Camera.camera_identifier == camera_id)).first()
        if cam:
            db_camera_id = cam.id
            cam_name = cam.name
        else:
            first_cam = db.query(Camera).first()
            db_camera_id = first_cam.id if first_cam else camera_id
            cam_name = first_cam.name if first_cam else "Main Webcam 01"

        # 6. Create Database Event
        event_num = int(captured_dt.timestamp() * 1000) % 100000
        event_identifier = f"EVT-INTRUSION-{event_num}"

        event = Event(
            event_identifier=event_identifier,
            event_type=EventType.INTRUSION,
            camera_id=db_camera_id,
            zone_id=payload.zone_id,
            track_id=payload.track_id,
            timestamp=captured_dt,
            severity=EventSeverity.CRITICAL if payload.class_name in {"truck", "car"} else EventSeverity.HIGH,
            status=EventStatus.NEW,
            bounding_box=payload.bbox,
            position={"x": (payload.bbox[0] + payload.bbox[2]) / 2.0, "y": payload.bbox[3]} if payload.bbox else None,
            event_metadata={
                "class_name": payload.class_name,
                "confidence": payload.confidence,
                "zone_name": payload.zone_name or "Restricted Zone",
            },
        )
        db.add(event)
        db.flush()

        # 7. Create Database Alert
        alert = Alert(
            event_id=event.id,
            severity=event.severity,
            status=AlertStatus.ACTIVE,
            message=f"CRITICAL: Unauthorized entry by {payload.class_name or 'person'} (Track #{payload.track_id})",
        )
        db.add(alert)

        # 8. Create Database Evidence
        evidence_identifier = f"EVD-{evidence_id[:8].upper()}"
        evidence = Evidence(
            id=evidence_id,
            evidence_identifier=evidence_identifier,
            event_id=event.id,
            file_path=rel_file_path,
            sha256_hash=calculated_sha256,
            captured_at=captured_dt,
            evidence_metadata={
                "camera_id": db_camera_id,
                "track_id": payload.track_id,
                "class_name": payload.class_name,
                "confidence": payload.confidence,
                "bbox": payload.bbox,
                "zone_name": payload.zone_name,
            },
        )
        db.add(evidence)
        db.commit()
        db.refresh(evidence)
        db.refresh(event)

        # 9. Audit Logging
        AuditService.log_action(
            db=db,
            user_id=current_user.id,
            action="EVIDENCE_CAPTURED",
            resource_type="EVIDENCE",
            resource_id=evidence.id,
            metadata={"event_id": event.id, "sha256_hash": calculated_sha256},
        )

        logger.info(f"Captured real webcam evidence {evidence.id} for Event {event.id}. SHA256: {calculated_sha256}")

        return EvidenceDetailResponse(
            evidence_id=evidence.id,
            evidence_identifier=evidence.evidence_identifier,
            event_id=event.id,
            event_identifier=event.event_identifier,
            file_path=evidence.file_path,
            sha256_hash=evidence.sha256_hash,
            image_url=f"/api/v1/evidence/{evidence.id}/image",
            captured_at=captured_dt,
            camera_id=db_camera_id,
            track_id=event.track_id,
            class_name=payload.class_name,
            confidence=payload.confidence,
            bbox=payload.bbox,
            severity=event.severity.value,
            verified_status="VERIFIED",
        )

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to capture real evidence: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to capture evidence: {str(e)}",
        )


@router.get("/evidence", response_model=List[EvidenceResponse])
def list_all_evidence(
    limit: int = Query(50, description="Pagination limit"),
    db: Session = Depends(get_db),
    current_user: User = Depends(view_evidence_role),
) -> List[EvidenceResponse]:
    """
    List all evidence records from the database with real image URLs.
    """
    records = db.query(Evidence).order_by(Evidence.captured_at.desc()).limit(limit).all()
    return [map_evidence_to_response(e) for e in records]


@router.get("/evidence/{evidence_id}", response_model=EvidenceResponse)
def get_evidence(
    evidence_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(view_evidence_role),
) -> EvidenceResponse:
    """
    Retrieve metadata and hash details of a specific evidence record.
    """
    evidence = EvidenceService.get_evidence(db, evidence_id)
    return map_evidence_to_response(evidence)


@router.get("/evidence/{evidence_id}/image")
@router.get("/evidence/{evidence_id}/file")
@router.get("/evidence/{evidence_id}/download")
def get_evidence_image_file(
    evidence_id: str,
    db: Session = Depends(get_db),
) -> FileResponse:
    """
    Streams the physical high-resolution evidence snapshot image directly from disk.
    """
    evidence = EvidenceService.get_evidence(db, evidence_id)
    target_path = EvidenceIntegrityService.resolve_path_safely(evidence.file_path)

    if not target_path.exists() or not target_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evidence snapshot file not found on disk at '{evidence.file_path}'",
        )

    return FileResponse(
        path=str(target_path),
        media_type="image/jpeg",
        filename=f"{evidence.evidence_identifier}.jpg",
    )


@router.post("/events/{event_id}/evidence", response_model=EvidenceResponse, status_code=status.HTTP_201_CREATED)
def create_evidence(
    event_id: str,
    evidence_in: EvidenceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(manage_evidence_role),
):
    """Associate a new digital evidence record with an existing event."""
    evidence = EvidenceService.create_evidence(db, event_id=event_id, evidence_in=evidence_in)
    return map_evidence_to_response(evidence)


@router.get("/events/{event_id}/evidence", response_model=List[EvidenceResponse])
def list_evidence(
    event_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(view_evidence_role),
):
    """List all evidence records associated with a specific event."""
    evidence_list = EvidenceService.list_evidence(db, event_id=event_id)
    return [map_evidence_to_response(e) for e in evidence_list]


@router.patch("/evidence/{evidence_id}", response_model=EvidenceResponse)

def update_evidence(
    evidence_id: str,
    evidence_in: EvidenceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(manage_evidence_role),
):
    """Update metadata of an evidence record."""
    evidence = EvidenceService.update_evidence(db, evidence_id, evidence_in)
    return map_evidence_to_response(evidence)


@router.post("/evidence/{evidence_id}/hash", response_model=EvidenceHashResponse)
def generate_evidence_hash(
    evidence_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(hash_evidence_role),
):
    """Generate and persist cryptographic SHA-256 hash."""
    evidence, status_msg = EvidenceIntegrityService.generate_evidence_hash(db, evidence_id)
    return EvidenceHashResponse(
        id=evidence.id,
        evidence_identifier=evidence.evidence_identifier,
        sha256_hash=evidence.sha256_hash,
        status=status_msg,
    )


@router.get("/evidence/{evidence_id}/verify", response_model=EvidenceVerificationResponse)
@router.post("/evidence/{evidence_id}/verify", response_model=EvidenceVerificationResponse)
def verify_evidence(
    evidence_id: str,
    simulate_tamper: bool = Query(False, description="Simulate controlled file tamper for verification testing"),
    db: Session = Depends(get_db),
    current_user: User = Depends(view_evidence_role),
):
    """
    Verify physical evidence file against stored cryptographic SHA-256 hash.
    """
    result = EvidenceIntegrityService.verify_evidence(db, evidence_id, simulate_tamper=simulate_tamper)

    AuditService.log_action(
        db=db,
        user_id=current_user.id,
        action="EVIDENCE_VERIFIED",
        resource_type="EVIDENCE",
        resource_id=evidence_id,
        metadata={"status": result["status"], "verified": result["verified"], "simulate_tamper": simulate_tamper},
    )

    return EvidenceVerificationResponse(
        evidence_id=result["evidence_id"],
        verified=result["verified"],
        status=result["status"],
        stored_hash=result.get("stored_hash"),
        current_hash=result.get("current_hash"),
    )
