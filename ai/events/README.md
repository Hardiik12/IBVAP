# Event Engine Module

Responsible for converting object tracks and zone state transitions into operational security events (INTRUSION).

## Owner
M2 — AI/ML Lead

## Functionality
- Evaluates object state transitions (`OUTSIDE` → `INSIDE`).
- Prevents alert spam for objects remaining `INSIDE`.
- Emits structured intrusion event payloads with metadata.
