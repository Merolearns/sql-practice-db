"""sql-practice-db web UI: the 40 practice queries in the browser.

Thin layer over the files already in this repo — check.py, seed.py and
queries/*.sql are untouched. The home page reads live stats from
company.db, /query/<nn> runs the repo's own query file, and /practice
lets you write your own SELECT against a read-only connection.

If company.db is missing it is built automatically on startup
(schema.sql + seed.py, the same steps build.sh runs).
"""

import re
import sqlite3
from pathlib import Path

from flask import Flask, abort, render_template, request

# check.py holds the sample-answer parsing; reuse it, don't re-implement it
from check import EXPECTED, load_expected, resolve

app = Flask(__name__)


@app.template_filter("fmt")
def _fmt(value):
    """Whole-number floats (like 103180.0 from ROUND(AVG())) print
    without the trailing .0; everything else prints as-is."""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)

HERE = Path(__file__).parent
DB = HERE / "company.db"
QUERIES = HERE / "queries"
SCHEMA = HERE / "schema.sql"
MAX_ROWS = 200

TABLES = ["departments", "employees", "projects",
          "employee_projects", "sales"]

# topic groups for the home-page index (same order as the README)
TOPIC_GROUPS = [
    ("The basics", range(1, 7)),
    ("Aggregates", range(7, 8)),
    ("Joins", range(8, 10)),
    ("GROUP BY and HAVING", range(10, 12)),
    ("Multi-table joins", range(12, 15)),
    ("Subqueries", range(15, 20)),
    ("CTEs", range(20, 22)),
    ("CASE expressions", range(22, 24)),
    ("Dates", range(24, 26)),
    ("Self-joins and UNION", range(26, 29)),
    ("Window functions", range(29, 35)),
    ("The tricky ones", range(35, 38)),
    ("Final boss", range(38, 41)),
]


def ensure_db():
    """Build company.db if it isn't there yet (schema.sql, then seed.py)."""
    if DB.exists():
        return
    con = sqlite3.connect(DB)
    con.executescript(SCHEMA.read_text(encoding="utf-8"))
    con.commit()
    con.close()
    import seed  # seed.py seeds the database its module is next to
    seed.main()


def _connect(read_only=False):
    if read_only:
        return sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    return sqlite3.connect(DB)


def _skip_ws_comments(text, i):
    """Advance past whitespace, -- line comments and /* */ comments."""
    n = len(text)
    while i < n:
        if text[i].isspace():
            i += 1
        elif text.startswith("--", i):
            j = text.find("\n", i)
            i = n if j == -1 else j + 1
        elif text.startswith("/*", i):
            j = text.find("*/", i + 2)
            i = n if j == -1 else j + 2
        else:
            break
    return i


def _read_word(text, i):
    """(word, next index) at i, or ("", i) if no word starts there."""
    m = re.match(r"[A-Za-z_][A-Za-z0-9_]*", text[i:])
    return (m.group(0), i + len(m.group(0))) if m else ("", i)


def _skip_parens(text, i):
    """Skip one balanced (...) group, ignoring parens inside 'strings'."""
    n = len(text)
    depth = 0
    while i < n:
        ch = text[i]
        if ch == "'":
            i += 1
            while i < n:
                if text[i] == "'":
                    if text[i + 1:i + 2] == "'":
                        i += 2
                        continue
                    i += 1
                    break
                i += 1
            continue
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            i += 1
            if depth == 0:
                return i
            continue
        i += 1
    return i


def _statement_keyword(sql):
    """Keyword of the statement that will actually run.

    Skips leading whitespace and -- and /* */ comments. For WITH,
    skips the CTE definitions and returns the keyword of the statement
    after them, so WITH ... DELETE is caught here instead of failing
    on the read-only connection with a raw sqlite error. A statement
    it can't parse returns "" (or the wrong word) and is rejected,
    never allowed.
    """
    i = _skip_ws_comments(sql, 0)
    word, i = _read_word(sql, i)
    if word.upper() != "WITH":
        return word.upper()
    # WITH [RECURSIVE] name [(cols)] AS [NOT] MATERIALIZED (select) [, ...]
    i = _skip_ws_comments(sql, i)
    word, i = _read_word(sql, i)
    if word.upper() == "RECURSIVE":
        i = _skip_ws_comments(sql, i)
    while True:
        _, i = _read_word(sql, i)  # CTE name
        i = _skip_ws_comments(sql, i)
        if i < len(sql) and sql[i] == "(":  # optional column list
            i = _skip_parens(sql, i)
            i = _skip_ws_comments(sql, i)
        _, i = _read_word(sql, i)  # AS
        i = _skip_ws_comments(sql, i)
        word, i = _read_word(sql, i)
        if word.upper() == "NOT":
            i = _skip_ws_comments(sql, i)
            _, i = _read_word(sql, i)  # MATERIALIZED
            i = _skip_ws_comments(sql, i)
        elif word.upper() == "MATERIALIZED":
            i = _skip_ws_comments(sql, i)
        if i < len(sql) and sql[i] == "(":  # the CTE body
            i = _skip_parens(sql, i)
        i = _skip_ws_comments(sql, i)
        if i < len(sql) and sql[i] == ",":
            i = _skip_ws_comments(sql, i + 1)
            continue
        break
    word, _ = _read_word(sql, i)
    return word.upper()


def _run(sql, read_only=False):
    """Run one SELECT and return (columns, rows) — rows capped at 200."""
    con = _connect(read_only=read_only)
    try:
        cur = con.execute(sql)
        cols = [d[0] for d in cur.description] if cur.description else []
        rows = cur.fetchmany(MAX_ROWS)
        return cols, rows
    finally:
        con.close()


def _load_queries():
    """One dict per query file: number, name, question, sql, covered?"""
    items = []
    for path in sorted(QUERIES.glob("*.sql")):
        num = int(path.stem.split("_", 1)[0])
        text = path.read_text(encoding="utf-8")
        first = text.splitlines()[0] if text else ""
        question = first.lstrip("- ").strip()
        items.append({
            "num": num,
            "num_str": f"{num:02d}",
            "name": path.stem[3:],
            "question": question,
            "sql": text.strip(),
            "covered": (EXPECTED / f"{path.stem}.txt").exists(),
        })
    return items


QUERIES_INDEX = _load_queries()
BY_NUM = {q["num"]: q for q in QUERIES_INDEX}


def _stats():
    con = _connect()
    try:
        row = con.execute(
            "SELECT COUNT(*), ROUND(AVG(salary)), MIN(salary), MAX(salary)"
            " FROM employees").fetchone()
        return {
            "headcount": row[0],
            "avg_salary": int(row[1]),  # ROUND(AVG()) comes back a float
            "lowest_salary": row[2],
            "highest_salary": row[3],
            "departments": con.execute(
                "SELECT COUNT(*) FROM departments").fetchone()[0],
            "projects": con.execute(
                "SELECT COUNT(*) FROM projects").fetchone()[0],
            "sales": con.execute(
                "SELECT COUNT(*) FROM sales").fetchone()[0],
            "total_sales": con.execute(
                "SELECT COALESCE(SUM(amount), 0) FROM sales").fetchone()[0],
        }
    finally:
        con.close()


def _schema_summary():
    con = _connect()
    try:
        out = []
        for table in TABLES:
            cols = [r[1] for r in con.execute(
                f"PRAGMA table_info({table})").fetchall()]
            count = con.execute(
                f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            out.append({"name": table, "columns": cols, "rows": count})
        return out
    finally:
        con.close()


def _check_answer(num):
    """Run the repo query and compare with expected/ — same inputs as
    check.py, reported as (ok, problems, want_cols, want_rows)."""
    query_path, expected_path = resolve(f"{num:02d}")
    want_cols, want_rows = load_expected(expected_path)
    cols, rows = _run(query_path.read_text(encoding="utf-8"))
    got_rows = [[str(v) for v in row] for row in rows[:len(want_rows)]]
    problems = []
    if cols != want_cols:
        problems.append(f"columns: expected {want_cols}, got {cols}")
    for i, (want, got) in enumerate(zip(want_rows, got_rows)):
        if want != got:
            problems.append(f"row {i + 1}: expected {want}, got {got}")
            break
    if len(got_rows) < len(want_rows):
        problems.append(
            f"only {len(got_rows)} rows, sample answer has {len(want_rows)}")
    return not problems, problems, want_cols, want_rows


@app.route("/", methods=["GET"])
def index():
    groups = []
    for label, nums in TOPIC_GROUPS:
        members = [q for q in QUERIES_INDEX if q["num"] in nums]
        if members:
            groups.append({"label": label, "queries": members})
    return render_template(
        "index.html",
        stats=_stats(),
        schema=_schema_summary(),
        groups=groups,
    )


@app.route("/query/<int:num>", methods=["GET", "POST"])
def query_page(num):
    q = BY_NUM.get(num)
    if q is None:
        abort(404)
    cols = rows = None
    check = None  # (ok, problems) once "Check my answer" is pressed
    error = None
    if request.method == "POST":
        if request.form.get("action") == "check" and q["covered"]:
            try:
                ok, problems, _, _ = _check_answer(num)
                check = (ok, problems)
            except sqlite3.Error as exc:
                error = f"The query failed to run: {exc}"
        else:
            try:
                cols, rows = _run(q["sql"])
            except sqlite3.Error as exc:
                error = f"The query failed to run: {exc}"
    return render_template(
        "query.html", q=q, cols=cols, rows=rows,
        check=check, error=error, max_rows=MAX_ROWS,
    )


@app.route("/practice", methods=["GET", "POST"])
def practice():
    sql = request.form.get("sql", "").strip() if request.method == "POST" else ""
    if request.method == "GET" and not sql:
        sql = "SELECT name, salary FROM employees\nORDER BY salary DESC\nLIMIT 10;"
    cols = rows = None
    error = None
    if request.method == "POST":
        # only SELECT statements, against a read-only connection.
        # _statement_keyword looks past leading comments and any
        # WITH ... CTE definitions, so the word it returns is the
        # statement that will actually run.
        if _statement_keyword(sql) != "SELECT":
            error = ("Only SELECT (and WITH ... SELECT) statements are "
                     "allowed here — no INSERT, UPDATE, DELETE, DROP, "
                     "or anything that changes the database.")
        else:
            try:
                cols, rows = _run(sql, read_only=True)
            except sqlite3.Error as exc:
                error = f"That didn't run: {exc}"
    return render_template(
        "practice.html", sql=sql, cols=cols, rows=rows,
        error=error, max_rows=MAX_ROWS,
    )


@app.route("/schema", methods=["GET"])
def schema_page():
    table = request.args.get("table", "employees")
    if table not in TABLES:
        abort(404)
    con = _connect()
    try:
        cols = [r[1] for r in con.execute(
            f"PRAGMA table_info({table})").fetchall()]
        rows = con.execute(
            f"SELECT * FROM {table} LIMIT 20").fetchall()
        count = con.execute(
            f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    finally:
        con.close()
    return render_template(
        "schema.html", tables=TABLES, table=table,
        cols=cols, rows=rows, count=count,
    )


@app.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404


ensure_db()

if __name__ == "__main__":
    app.run(debug=True)
