# IBVAP — Demo Data Reset Procedure

Use this guide to restore the IBVAP database and test files to a clean baseline prior to a live evaluation demonstration.

---

## 1. Automated Database Re-Seeding

Run the seed script to reset demo accounts, default cameras, and perimeter zones:

```bash
cd /Users/hardik/Downloads/IBVAP
PYTHONPATH=. backend/.venv/bin/python backend/app/db/seed.py
```

This ensures:
- 4 Role Accounts created (`admin`, `operator`, `analyst`, `auditor`).
- Default Camera (`cam-webcam-01`) registered and active.
- Default Polygon Zone (`Perimeter Restricted Zone`) configured.

---

## 2. Test Evidence Cleanup

To clear temporary test evidence files generated during prior demonstration runs:

```bash
# Remove test captures older than current session (preserving directory structure)
mkdir -p data/evidence
rm -f data/evidence/*.test.jpg
```

---

## 3. Fresh Demonstration Readiness Check

1. Verify backend health:
   ```bash
   curl -s http://localhost:8000/health
   ```
2. Verify test baseline:
   ```bash
   backend/.venv/bin/pytest backend/tests/ -q
   ```
3. Open `http://localhost:3000/login` to begin fresh demonstration.
