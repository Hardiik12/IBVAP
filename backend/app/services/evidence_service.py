from typing import List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.evidence import Evidence
from app.schemas.evidence import EvidenceCreate, EvidenceUpdate
from app.services.event_service import EventService


class EvidenceService:
    @staticmethod
    def create_evidence(db: Session, event_id: str, evidence_in: EvidenceCreate) -> Evidence:
        """
        Create a new evidence record associated with a valid security event.
        Enforces unique evidence_identifier index checks.
        """
        # 1. Verify event exists
        EventService.get_event(db, event_id)

        # 2. Verify evidence_identifier uniqueness
        existing = db.query(Evidence).filter(Evidence.evidence_identifier == evidence_in.evidence_identifier).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Evidence identifier already exists"
            )

        evidence = Evidence(
            evidence_identifier=evidence_in.evidence_identifier,
            event_id=event_id,
            file_path=evidence_in.file_path,
            sha256_hash=None,
            captured_at=evidence_in.captured_at,
            evidence_metadata=evidence_in.evidence_metadata
        )
        db.add(evidence)
        db.commit()
        db.refresh(evidence)
        return evidence

    @staticmethod
    def list_all_evidence(db: Session, limit: int = 100, offset: int = 0) -> List[Evidence]:
        """
        List all evidence records across all events, sorted by captured_at DESC.
        """
        return db.query(Evidence).order_by(Evidence.captured_at.desc()).offset(offset).limit(limit).all()

    @staticmethod
    def list_evidence(db: Session, event_id: str) -> List[Evidence]:
        """
        List all evidence records associated with an event, sorted by captured_at ASC.
        Raises 404 if event is missing.
        """

        # Verify event exists
        EventService.get_event(db, event_id)

        return db.query(Evidence).filter(Evidence.event_id == event_id).order_by(Evidence.captured_at.asc()).all()

    @staticmethod
    def get_evidence(db: Session, evidence_id: str) -> Evidence:
        """
        Fetch an evidence record by ID. Raises 404 if missing.
        """
        evidence = db.query(Evidence).filter(Evidence.id == evidence_id).first()
        if not evidence:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evidence not found"
            )
        return evidence

    @staticmethod
    def update_evidence(db: Session, evidence_id: str, evidence_in: EvidenceUpdate) -> Evidence:
        """
        Update logically mutable evidence fields (metadata dictionary).
        """
        evidence = EvidenceService.get_evidence(db, evidence_id)
        update_data = evidence_in.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(evidence, key, value)

        db.commit()
        db.refresh(evidence)
        return evidence
