#!/bin/bash
set -euo pipefail

DEPENDENCY_RETRIES="${DEPENDENCY_RETRIES:-15}"
TIMEOUT=1

if [[ -n "${DEPENDENCY_ADDRESS:-}" ]]; then
  HOST="${DEPENDENCY_ADDRESS%%:*}"
  PORT="${DEPENDENCY_ADDRESS##*:}"
  RETRIES="${DEPENDENCY_RETRIES}"

  echo "[INFO] Waiting for ${HOST}:${PORT}..."
  while ! timeout "${TIMEOUT}" nc -v -z -w "${TIMEOUT}" "${HOST}" "${PORT}"; do
    ((--RETRIES)) || (echo "[ERROR] Max ${DEPENDENCY_RETRIES} retries exceeded"; exit 1)
    sleep 1
  done
  echo "[INFO] Connection to ${HOST}:${PORT} ok"
fi

exec "$@"
