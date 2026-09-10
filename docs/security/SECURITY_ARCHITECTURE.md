# IBVAP Security Architecture & Cryptographic Integrity

**Core Standards:** Argon2id, JWT (HS256), RFC 6238 TOTP, SHA-256 binary hashing  

---

## 1. Multi-Layer Defense Architecture

```
Layer 1: Perimeter Access & Anti-Brute-Force
         └── Rate Limiting, Temporary Account Lockouts
Layer 2: Authentication Pipeline (3-Factor Workflow)
         ├── Primary Factor: Argon2id Password Hash
         ├── Secondary Factor: 1-to-1 Facial Biometrics (SFace Cosine Similarity)
         └── Tertiary Factor: RFC 6238 TOTP Multi-Factor Authentication
Layer 3: Authorization & RBAC Enforcement
         └── 4 Strict Roles (ADMINISTRATOR, OPERATOR, ANALYST, AUDITOR)
Layer 4: Evidence Integrity & Chain of Custody
         └── Server-Authoritative SHA-256 File Checksums (On-Demand Tamper Check)
Layer 5: Non-Repudiation & Audit Trail
         └── Append-Only Immutable Audit Log Table
```

---

## 2. Cryptographic Implementation Details

1. **Password Hashing (`backend/app/core/security.py`):**
   - Implemented via `pwdlib[argon2]` with recommended memory cost and time cost parameters.
2. **Access Token Generation:**
   - 256-bit signed HMAC-SHA256 tokens with 30-minute expiration.
3. **Evidence Hashing (`backend/app/services/evidence_integrity_service.py`):**
   - Binary streaming hash `hashlib.sha256()` computed over on-disk snapshot files.
