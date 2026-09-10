# IBVAP Security Policy & Forensic Integrity Protocols

## 1. Security Architecture Overview

IBVAP (Intelligent Border Video Analytics Platform) implements multi-layered defense-in-depth security designed for operational border surveillance environments:

1. **Password Hashing:** Argon2id via `pwdlib`/`passlib` with salt and memory-hardness parameters.
2. **Authentication & Session Tokens:** JWT (JSON Web Token) with HS256 algorithm and strict expiration policies.
3. **Multi-Factor Authentication (MFA):** RFC 6238 Time-based One-Time Password (TOTP) and biometric facial verification pipeline (OpenCV YuNet + SFace cosine similarity matching).
4. **Role-Based Access Control (RBAC):** 4 strictly segregated roles (`ADMINISTRATOR`, `OPERATOR`, `ANALYST`, `AUDITOR`) enforced on all backend endpoints and reflected in frontend navigation.
5. **Evidence Integrity:** Server-authoritative SHA-256 binary checksums recorded upon snapshot capture; tamper-detection verification API (`GET /api/v1/evidence/{id}/verify`) recomputes on-disk hashes to identify unauthorized byte modification (`VERIFIED` vs `TAMPERED`).
6. **Model Checksum Integrity:** Optional SHA-256 verification of YOLO and face recognition neural network weights on initialization (`AI_MODEL_SHA256`) with fail-closed security.
7. **Audit Trail:** Immutable append-only audit log recording administrative actions, authentications, zone modifications, and evidence verification checks.
8. **Path Traversal & Symlink Protection:** Canonical path resolution prevents directory traversal attacks on media storage endpoints.

---

## 2. Reporting Security Vulnerabilities

If you discover a security vulnerability within the IBVAP platform, please report it responsibly:

- **Contact:** Open a confidential vulnerability advisory or reach out to the repository maintainers.
- **Response Timeline:** Acknowledgment within 24 hours; patch and mitigation deployment within 72 hours.
- **Do Not Disclose Publicly:** Please avoid posting vulnerability details in public issues until a security fix has been released.

---

## 3. Environment & Credential Security Guidelines

- **Never Commit Secrets:** Do not commit `.env`, private keys, JWT secrets, or production passwords to version control.
- **Use `.env.example`:** Maintain sanitized configuration templates with clear placeholders.
- **Rotate Secrets Regularly:** In production, regenerate `JWT_SECRET_KEY` and database passwords using cryptographically secure random generators (`openssl rand -hex 32`).
