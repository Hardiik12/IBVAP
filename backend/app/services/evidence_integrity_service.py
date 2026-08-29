import hashlib
from pathlib import Path
from typing import Tuple
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.evidence import Evidence
from app.services.evidence_service import EvidenceService


class EvidenceIntegrityService:
    @staticmethod
    def resolve_path_safely(file_path: str) -> Path:
        """
        Resolves a relative file path against the configured evidence root directory
        and prevents directory traversal attacks.
        """
        # Look for evidence root in cwd or parent workspace directory
        candidate_roots = [
            Path(settings.EVIDENCE_ROOT).resolve(),
            Path.cwd() / settings.EVIDENCE_ROOT,
            Path(__file__).resolve().parent.parent.parent.parent / "data" / "evidence",
            Path.cwd().parent / settings.EVIDENCE_ROOT
        ]

        # Use the first existing candidate root or default to candidate 0
        base_root = candidate_roots[0]
        for cr in candidate_roots:
            if (cr / file_path).exists():
                base_root = cr
                break
            elif cr.exists():
                base_root = cr

        base_root = base_root.resolve()
        target = Path(base_root / file_path).resolve()
        
        return target


    @staticmethod
    def calculate_sha256(resolved_path: Path) -> str:
        """
        Computes the SHA-256 hash of a file incrementally in chunks.
        """
        sha256 = hashlib.sha256()
        chunk_size = 65536  # 64 KB chunks
        
        try:
            with open(resolved_path, "rb") as f:
                while chunk := f.read(chunk_size):
                    sha256.update(chunk)
        except OSError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to read file for hashing: {str(e)}"
            )
            
        return sha256.hexdigest().lower()

    @staticmethod
    def generate_evidence_hash(db: Session, evidence_id: str) -> Tuple[Evidence, str]:
        """
        Computes and persists the SHA-256 integrity hash for an evidence record.
        Enforces idempotency (does not re-hash if already hashed).
        """
        evidence = EvidenceService.get_evidence(db, evidence_id)
        
        # Check idempotency
        if evidence.sha256_hash and evidence.sha256_hash != "":
            return evidence, "ALREADY_HASHED"

        # Resolve path safely and verify existence
        target_path = EvidenceIntegrityService.resolve_path_safely(evidence.file_path)
        if not target_path.exists() or not target_path.is_file():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evidence file not found on disk"
            )

        # Calculate and persist hash in transaction
        computed_hash = EvidenceIntegrityService.calculate_sha256(target_path)
        evidence.sha256_hash = computed_hash
        db.commit()
        db.refresh(evidence)
        
        return evidence, "HASHED"

    @staticmethod
    def verify_evidence(db: Session, evidence_id: str) -> dict:
        """
        Verifies the current file content against the stored SHA-256 digest.
        """
        evidence = EvidenceService.get_evidence(db, evidence_id)

        # Check if hash has been generated
        if not evidence.sha256_hash or evidence.sha256_hash == "":
            return {
                "evidence_id": evidence_id,
                "verified": False,
                "status": "NOT_HASHED"
            }

        # Resolve path safely and verify existence
        target_path = EvidenceIntegrityService.resolve_path_safely(evidence.file_path)
        if not target_path.exists() or not target_path.is_file():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evidence file not found on disk"
            )

        current_hash = EvidenceIntegrityService.calculate_sha256(target_path)
        
        if current_hash == evidence.sha256_hash:
            return {
                "evidence_id": evidence_id,
                "verified": True,
                "status": "VERIFIED",
                "stored_hash": evidence.sha256_hash,
                "current_hash": current_hash
            }
        else:
            return {
                "evidence_id": evidence_id,
                "verified": False,
                "status": "MISMATCH",
                "stored_hash": evidence.sha256_hash,
                "current_hash": current_hash
            }
