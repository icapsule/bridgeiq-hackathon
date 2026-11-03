#!/bin/bash
set -e

export PYTHONPATH="/app:${PYTHONPATH}"

echo "Starting BridgeIQ Backend API (Uvicorn on port 8000)..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 &

echo "Starting BridgeIQ Dashboard (Streamlit on port 8501)..."
exec streamlit run ui/streamlit_app.py \
    --server.port 8501 \
    --server.address 0.0.0.0 \
    --server.enableCORS false \
    --server.enableXsrfProtection false \
    --browser.gatherUsageStats false

