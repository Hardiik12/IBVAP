from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User
from app.models.enums import UserRole
from app.schemas.evidence import (
    EvidenceCreate,
    EvidenceUpdate,
    EvidenceResponse,
    EvidenceHashResponse,
    EvidenceVerificationResponse
)
from app.services.evidence_service import EvidenceService
from app.services.evidence_integrity_service import EvidenceIntegrityService
from app.services.audit_service import AuditService
from app.api.deps import require_role

router = APIRouter()

# Role permissions
view_evidence_role = require_role([UserRole.OPERATOR, UserRole.ANALYST, UserRole.ADMINISTRATOR, UserRole.AUDITOR])
manage_evidence_role = require_role([UserRole.OPERATOR, UserRole.ADMINISTRATOR])
hash_evidence_role = require_role([UserRole.OPERATOR, UserRole.ADMINISTRATOR])


def map_evidence_to_response(evidence) -> EvidenceResponse:
    """Helper to bypass SQLAlchemy metadata attribute conflict."""
    return EvidenceResponse(
        id=evidence.id,
        evidence_identifier=evidence.evidence_identifier,
        event_id=evidence.event_id,
        file_path=evidence.file_path,
        captured_at=evidence.captured_at,
        created_at=evidence.created_at,
        sha256_hash=evidence.sha256_hash,
        metadata=evidence.evidence_metadata
    )


@router.post("/events/{event_id}/evidence", response_model=EvidenceResponse, status_code=status.HTTP_201_CREATED)
def create_evidence(
    event_id: str,
    evidence_in: EvidenceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(manage_evidence_role)
):
    """
    Associate a new digital evidence record (e.g. image snapshot) with an event.
    """
    evidence = EvidenceService.create_evidence(db, event_id=event_id, evidence_in=evidence_in)
    return map_evidence_to_response(evidence)


@router.get("/events/{event_id}/evidence", response_model=List[EvidenceResponse])
def list_evidence(
    event_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(view_evidence_role)
):
    """
    List all evidence records associated with a specific event.
    """
    evidence_list = EvidenceService.list_evidence(db, event_id=event_id)
    return [map_evidence_to_response(e) for e in evidence_list]


@router.get("/evidence/{evidence_id}", response_model=EvidenceResponse)
def get_evidence(
    evidence_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(view_evidence_role)
):
    """
    Retrieve metadata details of a specific evidence record.
    """
    evidence = EvidenceService.get_evidence(db, evidence_id)
    return map_evidence_to_response(evidence)


@router.patch("/evidence/{evidence_id}", response_model=EvidenceResponse)
def update_evidence(
    evidence_id: str,
    evidence_in: EvidenceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(manage_evidence_role)
):
    """
    Update allowed fields (metadata) of an evidence record.
    """
    evidence = EvidenceService.update_evidence(db, evidence_id, evidence_in)
    return map_evidence_to_response(evidence)


@router.post("/evidence/{evidence_id}/hash", response_model=EvidenceHashResponse)
def generate_evidence_hash(
    evidence_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(hash_evidence_role)
):
    """
    Generate and persist the cryptographic SHA-256 hash for an evidence record.
    """
    evidence, status_msg = EvidenceIntegrityService.generate_evidence_hash(db, evidence_id)
    return EvidenceHashResponse(
        id=evidence.id,
        evidence_identifier=evidence.evidence_identifier,
        sha256_hash=evidence.sha256_hash,
        status=status_msg
    )


@router.get("/evidence/{evidence_id}/verify", response_model=EvidenceVerificationResponse)
@router.post("/evidence/{evidence_id}/verify", response_model=EvidenceVerificationResponse)
def verify_evidence(
    evidence_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(view_evidence_role)
):
    """
    Verify the content of the physical evidence file against the stored SHA-256 hash.
    Logs audit event EVIDENCE_VERIFIED.
    """
    result = EvidenceIntegrityService.verify_evidence(db, evidence_id)
    
    AuditService.log_action(
        db=db,
        user_id=current_user.id,
        action="EVIDENCE_VERIFIED",
        resource_type="EVIDENCE",
        resource_id=evidence_id,
        metadata={"status": result["status"], "verified": result["verified"]}
    )

    return EvidenceVerificationResponse(
        evidence_id=result["evidence_id"],
        verified=result["verified"],
        status=result["status"],
        stored_hash=result.get("stored_hash"),
        current_hash=result.get("current_hash")
    )

