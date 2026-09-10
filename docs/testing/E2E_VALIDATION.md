# IBVAP End-to-End Pipeline Validation

**Module:** `backend/tests/integration/test_e2e_pipeline.py` & `test_ai_live_dispatch.py`  
**Execution:** Automated integration test asserting full flow from simulated OpenCV frame -> YOLO detection -> ByteTrack tracking -> Polygon zone intersection -> Event dispatch -> Database persistence -> WebSocket broadcast -> Evidence verification.  

---

## 1. Verified E2E Scenarios

1. **Normal Movement (No Intrusion):** Person walks along perimeter path outside restricted polygon. `0 events emitted`.
2. **Perimeter Breach:** Person crosses boundary line into restricted zone. `1 INTRUSION event emitted`, `1 active alert created`, `1 evidence record stored with SHA-256 hash`, `1 WebSocket broadcast received`.
3. **Continuous Intrusion:** Person remains inside zone across 50 frames. Alert suppression prevents multiple duplicate alert floods.
4. **Forensic Integrity Verification:** Evidence snapshot on-disk is verified against database checksum; tampering is simulated and proven detected.
