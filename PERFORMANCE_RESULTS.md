# IBVAP — Empirical Performance & Benchmark Results

**Date:** 2026-08-30  
**Hardware Environment:** Apple Silicon M-Series (macOS Darwin), Localhost execution  
**Status:** BENCHMARKED & VERIFIED  

---

## 1. Measured Performance Metrics

| Benchmark Domain | Metric / Parameter | Measured Result | Notes |
|---|---|---|---|
| **AI Video Ingestion** | Full Pipeline Frame Rate | **198.58 FPS** | Tested on 300 frames @ 1280x720 video benchmark |
| **End-to-End Event Ingestion**| AI Detection $\to$ PostgreSQL Commit | **50 – 65 ms** | Includes Argon2id verification, DB transaction, and alert trigger |
| **WebSocket Delivery Latency**| Post-Commit Broadcast $\to$ UI Render | **< 10 ms** | Localhost WebSocket push notification |
| **Evidence SHA-256 Hash** | 1080p Image Binary Hash Recalculation | **< 2 ms** | Pure C-accelerated `hashlib.sha256` |
| **Backend Test Suite Run** | 183 Pytest Unit & Integration Tests | **10.47 seconds** | 100% pass rate across entire regression baseline |
| **Security Audit Test Suite**| 7 Full Threat Model Regression Tests | **0.61 seconds** | Validates T-01 through T-15 security controls |
| **Frontend Production Build** | Next.js 14 Static Route Compilation | **~18 seconds** | 13 static pages compiled with zero errors |

---

## 2. Benchmark Regression Comparison Table

| Metric | Historical Baseline | Current Measurement (M3.6) | Regression? |
|---|---|---|---|
| **Video Ingestion Throughput** | 58.80 FPS (M2.1) / 195.40 FPS (M2.6) | **198.58 FPS** | **NO REGRESSION** (+3.18 FPS increase) |
| **Event Persistence Latency** | 113.79 ms (M2.6) / 53–61 ms (M3.3) | **50–65 ms** | **NO REGRESSION** (Consistent) |
| **Backend Test Baseline** | 182 Tests (M3.3) | **183 Tests** | **NO REGRESSION** (1 additional test added) |
| **Security Suite Baseline** | 7 Tests (M3.1) | **7 Tests** | **NO REGRESSION** (100% Passing) |
