#!/usr/bin/env python3
"""Check your answer for one of the covered queries against expected/.

Only the 10 queries with a sample answer in expected/ are supported. A
sample answer holds the column names plus the first rows, so the checker
runs your query and compares just those:

    python3 check.py 26
    python3 check.py queries/26_employee_managers.sql

Exits 0 when the column names and the first N rows match (N = rows in
the sample), non-zero otherwise. The seed is fixed, so after ./build.sh
the data is identical every time -- a mismatch means your query.
"""
import re
import sqlite3
import sys
from pathlib import Path

HERE = Path(__file__).parent
DB = HERE / "company.db"
QUERIES = HERE / "queries"
EXPECTED = HERE / "expected"


def load_expected(path):
    """(column names, data rows) parsed from a sample answer file."""
    cols, rows = None, []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.rstrip()
        if not line or line.startswith("--"):
            continue
        parts = [p for p in re.split(r"\s{2,}", line.strip()) if p]
        if not parts:
            continue
        if all(set(p) <= set("-") for p in parts):
            continue  # the --- separator row
        if cols is None:
            cols = parts
        else:
            rows.append(parts)
    return cols, rows


def resolve(arg):
    """queries/<nn>_*.sql from '26' or a path. Returns (query_path, expected_path)."""
    if arg.endswith(".sql") and Path(arg).exists():
        query_path = Path(arg)
    else:
        num = arg.zfill(2)
        matches = sorted(QUERIES.glob(f"{num}_*.sql"))
        if not matches:
            raise SystemExit(f"no query #{num} in queries/")
        query_path = matches[0]
    expected = EXPECTED / f"{query_path.stem}.txt"
    return query_path, expected


def main(argv):
    if len(argv) != 2:
        print(__doc__.splitlines()[2].strip().replace("    ", " "))
        print("\ncovered:", ", ".join(sorted(p.stem for p in EXPECTED.glob("*.txt"))))
        return 2
    query_path, expected_path = resolve(argv[1])
    if not DB.exists():
        return "company.db is missing -- run ./build.sh first"
    if not expected_path.exists():
        return (f"no sample answer for {query_path.name}; "
                "the covered ones are listed with: python3 check.py")

    want_cols, want_rows = load_expected(expected_path)
    try:
        cur = sqlite3.connect(DB).execute(query_path.read_text(encoding="utf-8"))
    except sqlite3.Error as e:
        # A learner's broken query used to die with a raw traceback.
        print(f"your query failed to run: {e}")
        return 1
    if cur.description is None:
        # e.g. DELETE/UPDATE: ran fine, but there's nothing to compare.
        print("your query ran but returned no columns -- "
              "check.py only checks SELECT queries")
        return 1
    got_cols = [d[0] for d in cur.description]
    got_rows = [[str(v) for v in row] for row in cur.fetchmany(len(want_rows))]

    problems = []
    if got_cols != want_cols:
        problems.append(f"columns: expected {want_cols}, got {got_cols}")
    for i, (want, got) in enumerate(zip(want_rows, got_rows)):
        if want != got:
            problems.append(f"row {i + 1}: expected {want}, got {got}")
            break  # one diff is enough to know it's wrong; show the first
    if len(got_rows) < len(want_rows):
        problems.append(
            f"only {len(got_rows)} rows, sample answer has {len(want_rows)}")

    if problems:
        print(f"check FAILED for {query_path.name}:")
        for p in problems:
            print(" ", p)
        return 1
    print(f"OK: {query_path.name} matches expected/{expected_path.name} "
          f"({len(want_rows)} rows)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
