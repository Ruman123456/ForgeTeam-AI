#!/usr/bin/env bash
set -e
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

cleanup() {
    echo "Stopping ForgeTeam AI services..."
    kill $(jobs -p) 2>/dev/null || true
}
trap cleanup EXIT

echo "Starting Backend..."
cd "$DIR/../backend"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload &

sleep 2

echo "Starting Frontend..."
cd "$DIR/../frontend"
npm run dev &

wait
