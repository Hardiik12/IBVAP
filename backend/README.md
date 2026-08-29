# IBVAP Backend Service

FastAPI-based backend server for the Intelligent Border Video Analytics Platform (IBVAP).

## Section Lead
M1 — Backend Lead (supported by M5 — Security)

## Stack
- Python 3.11
- FastAPI
- PostgreSQL + SQLAlchemy
- Alembic (database migrations)
- WebSockets for real-time alert broadcasting
- JWT Authentication

## Structure
```
backend/
├── app/
│   ├── main.py        # FastAPI entrypoint
│   ├── core/          # App config, security, auth
│   ├── db/            # Database session & base class
│   ├── models/        # SQLAlchemy models
│   ├── schemas/       # Pydantic validation schemas
│   ├── api/routes/    # API endpoint controllers
│   ├── services/      # Business logic & event handlers
│   └── utils/         # Helper utilities (hashing, integrity)
├── migrations/        # Database migration scripts
├── tests/             # Unit and API integration tests
├── requirements.txt
└── requirements-dev.txt
```

## Setup (Local Development)
```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
uvicorn app.main:app --reload --port 8000
```
