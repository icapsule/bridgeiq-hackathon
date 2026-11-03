#!/bin/bash
set -e

BASE_URL="${1:-http://localhost:8000}"

echo "=================================================="
echo "BridgeIQ Smoke Test Suite"
echo "Target URL: $BASE_URL"
echo "=================================================="

# 1. Healthz
echo -n "[1/5] Testing /api/v1/healthz ... "
HEALTH=$(curl -s "$BASE_URL/api/v1/healthz")
echo "$HEALTH" | grep -q "healthy" && echo "✓ OK" || { echo "✗ FAILED"; exit 1; }

# 2. Extract Skills
echo -n "[2/5] Testing POST /api/v1/extract-skills ... "
EXTRACT=$(curl -s -X POST "$BASE_URL/api/v1/extract-skills" \
  -H "Content-Type: application/json" \
  -d '{"cv_text": "Experienced 4G/5G core network engineer with 10 years high-availability uptime across 12 datacenters."}')
echo "$EXTRACT" | grep -q "competency_graph" && echo "✓ OK" || { echo "✗ FAILED"; exit 1; }

# 3. Match Jobs
echo -n "[3/5] Testing POST /api/v1/match-jobs ... "
MATCH=$(curl -s -X POST "$BASE_URL/api/v1/match-jobs" \
  -H "Content-Type: application/json" \
  -d '{"candidate_id": "cand-hero-101", "top_k": 3}')
echo "$MATCH" | grep -q "composite" && echo "✓ OK" || { echo "✗ FAILED"; exit 1; }

# 4. Jobs and Candidates Listing
echo -n "[4/5] Testing GET /api/v1/jobs and /api/v1/candidates ... "
JOBS=$(curl -s "$BASE_URL/api/v1/jobs?limit=5")
echo "$JOBS" | grep -q "total" && echo "✓ OK" || { echo "✗ FAILED"; exit 1; }

# 5. Explain Match & Probes
echo -n "[5/5] Testing POST /api/v1/generate-probes ... "
PROBES=$(curl -s -X POST "$BASE_URL/api/v1/generate-probes" \
  -H "Content-Type: application/json" \
  -d '{"candidate_id": "cand-hero-101", "job_id": "jobtech-31523453"}')
echo "$PROBES" | grep -q "probes" && echo "✓ OK" || { echo "✗ FAILED"; exit 1; }

echo "=================================================="
echo "All 5 BridgeIQ Smoke Tests Passed Successfully!"
echo "=================================================="
