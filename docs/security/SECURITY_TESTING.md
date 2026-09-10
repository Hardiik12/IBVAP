# IBVAP Security Testing & Vulnerability Assessment

## 1. Automated Security Test Battery

Security enforcement is covered by dedicated automated test modules:

1. **`backend/tests/api/test_rbac.py`:** Tests permission enforcement across all 4 roles.
2. **`backend/tests/api/test_auth.py`:** Tests password validation, JWT lifecycle, and expired token rejection.
3. **`backend/tests/api/test_mfa.py`:** Tests TOTP token validation, invalid code rejection, and replay prevention.
4. **`backend/tests/api/test_face_auth.py`:** Tests biometric vector matching and unauthorized bypass rejection.
5. **`backend/tests/api/test_evidence_integrity.py`:** Tests SHA-256 calculation, verified matching, and simulated file tampering.
6. **`backend/tests/api/test_security_audit.py`:** Tests path traversal rejection, rate limiting, and information leakage prevention.
7. **`ai/tests/detection/test_model_integrity.py`:** Tests fail-closed behavior when model weights checksum mismatches.

---

## 2. Running Security Tests

```bash
source backend/.venv/bin/activate
pytest backend/tests/api/test_security_audit.py backend/tests/api/test_evidence_integrity.py backend/tests/api/test_rbac.py -v
```
