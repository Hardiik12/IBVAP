# IBVAP Forensic Evidence Integrity & SHA-256 Tamper Detection

**Module:** `backend/app/services/evidence_integrity_service.py`  
**Endpoint:** `GET /api/v1/evidence/{evidence_id}/verify`  
**Hashing Standard:** NIST FIPS 180-4 SHA-256 (256-bit cryptographic digest)  

---

## 1. Evidence Lifecycle & Chain of Custody

```mermaid
sequenceDiagram
    participant AI as AI Ingestion Pipeline
    participant API as FastAPI Backend
    participant FS as Local Evidence Storage
    participant DB as PostgreSQL DB
    participant Judge as Operator / Auditor (UI)

    AI->>FS: 1. Write Snapshot JPEG
    AI->>API: 2. POST /events with Snapshot Metadata
    API->>FS: 3. Compute SHA-256 Hash of JPEG on Disk
    API->>DB: 4. Store Evidence Record with Immutable Hash
    Note over FS,DB: Evidence Stored with Fixed Cryptographic Hash

    Judge->>API: 5. GET /evidence/{id}/verify
    API->>FS: 6. Recompute Hash of Current File on Disk
    API->>DB: 7. Retrieve Stored Hash
    alt Hashes Match
        API-->>Judge: Status: VERIFIED (Green Badge)
    else Hashes Mismatch (File Altered)
        API-->>Judge: Status: TAMPERED (Red Alarm Badge)
    end
```

---

## 2. Live Tamper Test Verification

To demonstrate tamper detection during the hackathon:

1. Locate a captured evidence file in `data/evidence/`.
2. Verify its hash in the UI: Status shows `VERIFIED`.
3. Modify a single byte of the JPEG image using a hex editor or shell:
   ```bash
   echo "tamper" >> data/evidence/sample_snapshot.jpg
   ```
4. Click **Verify SHA-256 Hash** in the UI: Status immediately switches to `TAMPERED`.
