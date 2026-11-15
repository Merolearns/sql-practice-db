# sql-practice-db

A tiny fake company database plus 40 SQL practice queries that go from "what's a SELECT" to window functions and relational division. I built this for myself to drill SQL without signing up for anything — everything runs locally on SQLite, no dependencies.

## What's in here

- `schema.sql` — the database schema: departments, employees, projects, employee_projects, sales
- `seed.py` — generates ~200 fake employees across 6 departments, 15 projects, and 700 sales. Fixed random seed, so the data is identical every time you build it
- `build.sh` — builds `company.db` from scratch
- `queries/` — 40 numbered `.sql` files, easiest first. Each one starts with the question in plain English, then the query
- `expected/` — sample answers (columns + first rows) for 10 of the queries, so you can check your work
- `check.py` — checks your answer for one of those 10 against its sample answer

All data is randomly generated and fictional. No real people, no real company.

## Web UI

The same database and queries, in the browser — no SQL client needed:

```bash
pip install -r requirements.txt
python3 app.py
```

Then open http://127.0.0.1:5000. If `company.db` doesn't exist yet,
the app builds it for you on startup (same steps as `build.sh`).

- **Home** — live stats from the database (200 employees, 6 departments,
  15 projects, 700 sales, average salary $103,180), the 5-table schema,
  and the 40-query index grouped by topic.
- **Query pages** — each query shows its plain-English question and the
  SQL, a "Run it" button that executes the repo's query file and renders
  the result as a table, and — for the 10 queries with a sample answer —
  a "Check my answer" button that runs the same comparison as
  `check.py`. For example, query 07 returns one row: headcount 200,
  average salary 103180, lowest 45000, highest 172000.
- **Try your own SQL** — a free-form runner for your own SELECTs. The
  connection is read-only and only SELECT (and WITH ... SELECT) is
  accepted, so nothing you type can change the data. Results are capped
  at 200 rows; errors are shown in plain English.
- **Browse the tables** — pick one of the 5 tables to see its columns
  and first 20 rows.

The web UI is a thin layer over the files already here: `app.py` reads
`queries/*.sql` and reuses `check.py`'s sample-answer parsing. The
command-line tools below work exactly as before.

## Build it (command line)

You need Python 3 and the `sqlite3` command-line tool. That's it — no pip packages, stdlib only.

```bash
./build.sh
```

This creates `company.db`. Rebuild any time to reset everything.

## How to use the queries

Pick a query file, read the question at the top, and try to write it yourself in a blank file. Then compare with the version in `queries/`. For 10 of them you can also check your work automatically:

```bash
python3 check.py 26          # or: python3 check.py queries/26_employee_managers.sql
```

`check.py` runs your answer against the fixed-seed database and compares
the column names plus the first rows with the sample in `expected/`.
It exits 0 on a match and shows the first differing row otherwise.
A query that fails to run (or isn't a SELECT) prints the error and exits 1
instead of a traceback.

```bash
sqlite3 company.db < queries/01_select_all.sql
```

## Query index

| # | File | Topic |
|---|------|-------|
| 01–06 | `01_select_all` … `06_distinct_depts` | SELECT, WHERE, ORDER BY, LIMIT, LIKE, BETWEEN, DISTINCT |
| 07 | `07_company_stats` | COUNT / AVG / MIN / MAX |
| 08–09 | `08_employee_departments`, `09_sales_team` | INNER JOIN, JOIN + WHERE |
| 10–11 | `10_headcount_by_dept`, `11_big_departments` | GROUP BY, HAVING |
| 12–14 | `12_projects_with_depts` … `14_everyone_and_projects` | Multi-table joins, LEFT JOIN |
| 15–19 | `15_above_avg_salary` … `19_no_projects` | Scalar, IN, correlated subqueries, EXISTS / NOT EXISTS |
| 20–21 | `20_rich_departments`, `21_big_spenders` | CTEs (WITH) |
| 22–23 | `22_salary_bands`, `23_band_counts` | CASE expressions |
| 24–25 | `24_veterans`, `25_monthly_sales_2026` | Date math, strftime |
| 26–28 | `26_employee_managers` … `28_combined_names` | Self-joins, UNION |
| 29–34 | `29_top2_per_dept` … `34_pay_quartiles` | Window functions: ROW_NUMBER, RANK, running totals, LAG, AVG OVER, NTILE |
| 35–37 | `35_second_highest` … `37_balanced_depts` | Tricky ones: no-window top-N, relational division, HAVING combos |
| 38–40 | `38_top_salesperson_per_quarter` … `40_quarterly_pivot` | Final boss: quarterly top-N, dept summary, CASE pivot |

The schema is deliberately small so you can hold the whole thing in your head: 5 tables, obvious foreign keys. The queries are where the difficulty lives.

## Notes

- `gen_queries.py` is the script I used to write out the 40 query files — it's the source of truth if you want to tweak all of them at once. Run `python3 gen_queries.py --verify` after editing to check every query still runs against `company.db`.
- `company.db` is generated and gitignored. Never commit it.
