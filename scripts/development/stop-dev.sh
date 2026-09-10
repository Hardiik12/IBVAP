#!/usr/bin/env bash
# ==============================================================================
# IBVAP — Development Services Shutdown Helper
# ==============================================================================
set -e

echo "=== Stopping IBVAP Development Services ==="
docker compose down

echo "IBVAP development containers stopped."
