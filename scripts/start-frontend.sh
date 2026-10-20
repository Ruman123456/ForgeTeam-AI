#!/usr/bin/env bash
set -e
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR/../frontend"
echo "Starting ForgeTeam AI Frontend on http://127.0.0.1:5173..."
npm run dev
