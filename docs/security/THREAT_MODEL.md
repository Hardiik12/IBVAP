# IBVAP Threat Model & Risk Mitigation (T-01 to T-15)

## Threat Model Matrix

| Threat ID | Threat Category | Attack Vector | IBVAP Countermeasure & Mitigation |
| :--- | :--- | :--- | :--- |
| **T-01** | Credential Stuffing | Brute-force password guessing | Argon2id password hashing + failed attempt rate limiting |
| **T-02** | Token Forgery | Modifying JWT payload | 256-bit secret signature verification with HS256 algorithm |
| **T-03** | Replay Attack | Replaying captured requests | Short token TTL (30 min) + stateful user session checks |
| **T-04** | Privilege Escalation | Operator attempting admin tasks | Backend `require_role` dependency on every protected endpoint |
| **T-05** | Evidence Tampering | Altering on-disk JPEG snapshot | SHA-256 integrity verification detects 1-bit file alteration |
| **T-06** | Model Poisoning | Replacing YOLO weights file | SHA-256 weight checksum check on detector initialization |
| **T-07** | Path Traversal | Requesting `../../etc/passwd` | `Path.resolve()` boundary checking against `EVIDENCE_ROOT` |
| **T-08** | Symlink Exploitation | Symlinking sensitive system files | Real path resolution rejects symlinks pointing outside media root |
| **T-09** | WebSocket Hijacking | Unauthorized event eavesdropping | Token validation during WebSocket HTTP upgrade handshake |
| **T-10** | Repudiation | Denying an administrative action | Append-only immutable `audit_logs` table recording all events |
| **T-11** | Stolen Password | Single-factor credential theft | RFC 6238 TOTP MFA + 1-to-1 SFace biometric verification |
| **T-12** | Zone Tampering | Unauthorized boundary deletion | Soft-deactivation only; deletion disabled on event logs |
| **T-13** | SQL Injection | Malformed SQL in query params | Parameterized queries enforced via SQLAlchemy 2.0 ORM |
| **T-14** | XSS / Client Injection | Malicious script in event text | React / Next.js automatic DOM sanitization & escaping |
| **T-15** | Information Leakage | Password hash exposure in API | Pydantic response schemas exclude all hash and secret fields |
