#!/usr/bin/env bash
# smoke_local.sh – build image, start container, health-check, then tear down.
# Works on Linux and macOS.  See README for Windows alternatives.
set -euo pipefail

IMAGE="stock-analyzer:dev"
CONTAINER="sa-smoke-test"
PORT=8080
MAX_WAIT=30  # seconds to wait for Streamlit to become ready

cleanup() {
  echo "--- Stopping container ---"
  docker rm -f "$CONTAINER" >/dev/null 2>&1 || true
}
trap cleanup EXIT

echo "=== 1/4  Building image ==="
docker build -t "$IMAGE" .

echo "=== 2/4  Starting container ==="
docker run -d --name "$CONTAINER" -p "${PORT}:${PORT}" "$IMAGE"

echo "=== 3/4  Waiting for Streamlit (up to ${MAX_WAIT}s) ==="
elapsed=0
until curl -sf "http://localhost:${PORT}/_stcore/health" >/dev/null 2>&1; do
  sleep 2
  elapsed=$((elapsed + 2))
  if [ "$elapsed" -ge "$MAX_WAIT" ]; then
    echo "FAIL: Streamlit did not become ready within ${MAX_WAIT}s"
    echo "--- Container logs ---"
    docker logs "$CONTAINER"
    exit 1
  fi
done

echo "=== 4/4  Smoke check ==="
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:${PORT}/")
if [ "$STATUS" -ge 200 ] && [ "$STATUS" -lt 400 ]; then
  echo "PASS – HTTP $STATUS from http://localhost:${PORT}/"
else
  echo "FAIL – HTTP $STATUS from http://localhost:${PORT}/"
  docker logs "$CONTAINER"
  exit 1
fi

echo "=== Smoke test passed ==="
