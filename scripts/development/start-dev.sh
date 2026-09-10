#!/usr/bin/env bash
# ==============================================================================
# IBVAP — Development Services Startup Helper
# ==============================================================================
set -e

echo "=== Starting IBVAP Development Environment ==="

# 1. Start PostgreSQL Container
echo "[1/3] Ensuring PostgreSQL container is running..."
docker compose up -d postgres

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL database to be healthy..."
until docker compose exec postgres pg_isready -U postgres -d ibvap > /dev/null 2>&1; do
    sleep 1
done
echo "PostgreSQL is healthy and accepting connections."

# 2. Run Database Migrations & Seeds
echo "[2/3] Checking database schema & migrations..."
if [ -d "backend/.venv" ]; then
    source backend/.venv/bin/activate
    alembic -c backend/alembic.ini upgrade head
    python -m backend.app.db.seed || python backend/app/db/seed.py
fi

echo "[3/3] IBVAP Development Services Initialized."
echo ""
echo "To start the FastAPI backend:"
echo "  cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000"
echo ""
echo "To start the Next.js frontend:"
echo "  cd frontend && npm run dev"
echo ""
echo "To run the AI pipeline:"
echo "  source backend/.venv/bin/activate && python -m ai.pipeline.runner --source webcam --index 0"
