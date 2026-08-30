#!/bin/sh
set -e

echo "=== [IBVAP Backend] Starting Container Startup Sequence ==="

# 1. Wait for PostgreSQL database readiness
echo "--> Checking PostgreSQL connection..."
python -c "
import time, os, sys
import psycopg

db_url = os.environ.get('DATABASE_URL', '')
if not db_url:
    print('WARNING: DATABASE_URL is empty, skipping DB ping.')
    sys.exit(0)

# Strip SQLAlchemy driver prefix for psycopg3 native connection
connect_url = db_url.replace('postgresql+psycopg://', 'postgresql://').replace('postgresql+psycopg2://', 'postgresql://')

max_retries = 30
for attempt in range(1, max_retries + 1):
    try:
        conn = psycopg.connect(connect_url)
        conn.close()
        print('--> PostgreSQL is ready and accepting connections.')
        sys.exit(0)
    except Exception as e:
        print(f'--> Waiting for PostgreSQL ({attempt}/{max_retries})... Error: {e}')
        time.sleep(1)


print('ERROR: PostgreSQL connection timed out after 30 seconds.')
sys.exit(1)
"

# 2. Run Alembic Database Migrations
echo "--> Applying Alembic database migrations..."
alembic upgrade head
echo "--> Alembic migrations completed successfully."

# 3. Conditionally run demo seed data
if [ "${RUN_SEED:-false}" = "true" ]; then
    echo "--> RUN_SEED is enabled. Seeding demo records..."
    python -m app.db.seed
    echo "--> Demo seeding completed."
else
    echo "--> RUN_SEED is false. Skipping demo seed data."
fi

# 4. Launch FastAPI Application via Uvicorn
echo "--> Starting FastAPI Application on 0.0.0.0:8000..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1
