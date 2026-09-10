# IBVAP Automated Test Results & Verification Log

**Date:** 2026-09-10  
**Status:** 🟢 100% Passing  
**Total Automated Tests:** 187 / 187 Passed (0 Failures, 0 Skips)  
**Execution Time:** 10.51 seconds  

---

## 1. Test Execution Breakdown

```
============================= test session starts ==============================
Platform: darwin -- Python 3.13.5, pytest-9.1.1, pluggy-1.6.0
Rootdir: /Users/hardik/Downloads/IBVAP
Configfile: pytest.ini
Testpaths: ai/tests, backend/tests

ai/tests/camera/test_camera.py .........                                 [  4%]
ai/tests/detection/test_detection_schemas.py ..                          [  5%]
ai/tests/detection/test_detector_unit.py ....                            [  8%]
ai/tests/detection/test_model_integrity.py ....                          [ 10%]
ai/tests/events/test_dispatcher.py ........                              [ 14%]
ai/tests/events/test_events.py .......                                   [ 18%]
ai/tests/pipeline/test_pipeline.py ..                                    [ 19%]
ai/tests/test_pipeline.py .......                                        [ 22%]
ai/tests/test_processor.py ........                                      [ 27%]
ai/tests/test_source.py ..........                                       [ 32%]
ai/tests/tracking/test_tracker.py ....                                   [ 34%]
ai/tests/tracking/test_tracking_schemas.py ..                            [ 35%]
ai/tests/zones/test_zones.py .......                                     [ 39%]
backend/tests/api/test_alerts.py .....                                   [ 42%]
backend/tests/api/test_audit.py ...                                      [ 43%]
backend/tests/api/test_auth.py .........                                 [ 48%]
backend/tests/api/test_cameras.py ........                               [ 52%]
backend/tests/api/test_events.py ............                            [ 59%]
backend/tests/api/test_evidence.py ...........                           [ 65%]
backend/tests/api/test_evidence_integrity.py .......                     [ 68%]
backend/tests/api/test_face_auth.py ..                                   [ 70%]
backend/tests/api/test_health.py ...                                     [ 71%]
backend/tests/api/test_mfa.py .                                          [ 72%]
backend/tests/api/test_rbac.py ....                                      [ 74%]
backend/tests/api/test_security_audit.py .......                         [ 78%]
backend/tests/api/test_users.py .....                                    [ 80%]
backend/tests/api/test_websocket.py ........                             [ 85%]
backend/tests/api/test_zones.py .........                                [ 89%]
backend/tests/integration/test_ai_live_dispatch.py ...                   [ 91%]
backend/tests/integration/test_e2e_pipeline.py .......                   [ 95%]
backend/tests/unit/test_config.py ..                                     [ 96%]
backend/tests/unit/test_models.py .......                                [100%]

======================= 187 passed, 1 warning in 10.51s ========================
```

---

## 2. Frontend Quality Gate Results

- **ESLint (`npm run lint`):** 0 Errors (PASS)
- **TypeScript Compiler (`npx tsc --noEmit`):** 0 Type Errors (PASS)
- **Next.js Production Build (`npm run build`):** 16 / 16 Static Routes Compiled (PASS)
