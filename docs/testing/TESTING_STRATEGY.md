# IBVAP Test Strategy (Draft)

Comprehensive testing framework for IBVAP Internal-Round MVP.

## Section Lead
M6 — Integration / QA Lead

## Controlled Test Scenarios (Test Dataset)

### V01 — Normal Movement
- **Condition**: Person moves near restricted zone without crossing inside.
- **Expected Outcome**: No intrusion alert generated.

### V02 — Intrusion
- **Condition**: Person crosses from outside into the restricted zone polygon.
- **Expected Outcome**: Exactly one intrusion event, alert emitted, snapshot captured, SHA-256 recorded.

### V03 — Multiple People
- **Condition**: Multiple people navigate the scene simultaneously.
- **Expected Outcome**: Unique persistent Track IDs assigned and tracked independently.

### V04 — Repeated Crossing
- **Condition**: Person enters, exits, and re-enters the zone.
- **Expected Outcome**: Accurate state transitions (`OUTSIDE` → `INSIDE` → `OUTSIDE` → `INSIDE`) without duplicate alert spam during `INSIDE` stay.

### V05 — Occlusion
- **Condition**: Person is temporarily obscured behind an obstacle.
- **Expected Outcome**: ByteTrack maintains ID continuity without identity switching.

### V06 — Vehicle
- **Condition**: Vehicle enters the camera scene.
- **Expected Outcome**: Vehicle class detection and spatial evaluation.
