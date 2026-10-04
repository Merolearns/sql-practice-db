#!/usr/bin/env bash
# Build company.db from scratch: schema first, then seed data.
set -euo pipefail
cd "$(dirname "$0")"

rm -f company.db
sqlite3 company.db < schema.sql
python3 seed.py
echo "Done. Query it with: sqlite3 company.db"
