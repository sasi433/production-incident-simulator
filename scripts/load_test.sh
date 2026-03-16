#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:8080}"
REQUESTS="${REQUESTS:-20}"

echo "Running load test against ${BASE_URL}"
echo "Total checkout requests: ${REQUESTS}"

success=0
failure=0

for i in $(seq 1 "$REQUESTS"); do
  status_code=$(curl -s -o /dev/null -w "%{http_code}" -X POST "${BASE_URL}/checkout")

  if [ "${status_code}" = "200" ]; then
    success=$((success + 1))
  else
    failure=$((failure + 1))
  fi

  echo "Request ${i}: HTTP ${status_code}"
done

echo
echo "Load test summary"
echo "Success: ${success}"
echo "Failure: ${failure}"