#!/usr/bin/env bash
# ==============================================================================
# IBVAP — Database Seeder Helper
# ==============================================================================
set -e

echo "=== Seeding IBVAP Database Demo Data ==="

if [ -d "backend/.venv" ]; then
    source backend/.venv/bin/activate
fi

export PYTHONPATH=.
python -m backend.app.db.seed || python backend/app/db/seed.py

echo "=== Database Seeding Complete ==="
