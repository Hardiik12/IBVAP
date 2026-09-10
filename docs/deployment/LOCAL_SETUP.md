# IBVAP Local Development Setup Guide

**Prerequisites:** Python 3.12+, Node.js 20+, PostgreSQL 15+  

---

## 1. Step-by-Step Native Setup

### Step 1: Clone & Configure Environment
```bash
git clone https://github.com/Hardiik12/IBVAP.git
cd IBVAP
cp .env.example .env
```

### Step 2: Set Up Backend Virtual Environment
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd ..
```

### Step 3: Initialize Database & Run Migrations
Ensure PostgreSQL is active on port 5432:
```bash
source backend/.venv/bin/activate
alembic -c backend/alembic.ini upgrade head
python -m backend.app.db.seed || python backend/app/db/seed.py
```

### Step 4: Install Frontend Dependencies
```bash
cd frontend
npm install
cd ..
```

---

## 2. Launching Services (3 Terminals)

### Terminal 1: FastAPI Backend
```bash
cd backend && source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Terminal 2: Next.js Frontend
```bash
cd frontend
npm run dev
```

### Terminal 3: AI Computer Vision Pipeline
```bash
source backend/.venv/bin/activate
python -m ai.pipeline.runner --source webcam --index 0 --display
```
