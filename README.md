# sql-practice-db

A tiny fake company database plus 40 SQL practice queries that go from "what's a SELECT" to window functions and relational division. I built this for myself to drill SQL without signing up for anything — everything runs locally on SQLite, no dependencies.

## What's in here

- `schema.sql` — the database schema: departments, employees, projects, employee_projects, sales
- `seed.py` — generates ~200 fake employees across 6 departments, 15 projects, and 700 sales. Fixed random seed, so the data is identical every time you build it
- `build.sh` — builds `company.db` from scratch
- `queries/` — 40 numbered `.sql` files, easiest first. Each one starts with the question in plain English, then the query
- `expected/` — sample answers (columns + first rows) for 10 of the queries, so you can check your work

All data is randomly generated and fictional. No real people, no real company.

## Build it

You need Python 3 and the `sqlite3` command-line tool. That's it — no pip packages, stdlib only.

```bash
./build.sh
```

This creates `company.db`. Rebuild any time to reset everything.

## How to use the queries

Pick a query file, read the question at the top, and try to write it yourself in a blank file. Then compare with the version in `queries/`. For 10 of them you can also check your output against `expected/`.

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

- `gen_queries.py` is the script I used to write out the 40 query files — it's the source of truth if you want to tweak all of them at once.
- `company.db` is generated and gitignored. Never commit it.
