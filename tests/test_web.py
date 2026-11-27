"""Smoke tests for the sql-practice-db web UI.

Uses Flask's test client against the real company.db (fixed seed, so
the numbers below are stable). No network involved.
"""

from pathlib import Path

import pytest

import app as web

HERE = Path(__file__).parent.parent


@pytest.fixture()
def client():
    web.app.config["TESTING"] = True
    with web.app.test_client() as client:
        yield client


def test_home_shows_real_stats(client):
    resp = client.get("/")
    assert resp.status_code == 200
    # live numbers from the fixed-seed database
    assert b"200" in resp.data  # headcount
    assert b"103,180" in resp.data  # average salary, formatted
    assert b"employees" in resp.data
    assert b"departments" in resp.data
    assert b"sales" in resp.data
    # the query index is grouped and linked
    assert b"Window functions" in resp.data
    assert b"/query/29" in resp.data
    assert b"has sample answer" in resp.data


def test_query_page_runs_and_shows_headcount(client):
    resp = client.post("/query/07", data={"action": "run"})
    assert resp.status_code == 200
    assert b"headcount" in resp.data
    assert b"200" in resp.data
    assert b"103180" in resp.data  # average salary, unformatted in the table
    assert b"Headcount, average salary" in resp.data  # the question
    assert b"SELECT COUNT(*)" in resp.data  # the SQL itself


def test_query_page_check_answer_passes(client):
    resp = client.post("/query/07", data={"action": "check"})
    assert resp.status_code == 200
    assert b"matches the sample answer" in resp.data


def test_query_page_get_shows_sql_without_running(client):
    resp = client.get("/query/26")
    assert resp.status_code == 200
    assert b"manager" in resp.data
    assert b"LEFT JOIN" in resp.data
    assert b"Check my answer" in resp.data  # 26 is one of the covered ten


def test_query_page_links_to_prev_and_next(client):
    resp = client.get("/query/07")
    assert resp.status_code == 200
    assert b'href="/query/6"' in resp.data
    assert b'href="/query/8"' in resp.data
    # the ends of the course link one way only, never off the end
    assert b'href="/query/0"' not in client.get("/query/01").data
    assert b'href="/query/41"' not in client.get("/query/40").data


def test_unknown_query_number_404s(client):
    assert client.get("/query/99").status_code == 404
    assert client.get("/query/0").status_code == 404


def test_practice_runs_a_select(client):
    resp = client.post(
        "/practice",
        data={"sql": "SELECT COUNT(*) AS n FROM employees;"},
    )
    assert resp.status_code == 200
    assert b"200" in resp.data


def test_practice_rejects_a_delete(client):
    resp = client.post(
        "/practice",
        data={"sql": "DELETE FROM employees WHERE id = 1;"},
    )
    assert resp.status_code == 200
    assert b"Only SELECT" in resp.data
    # and the table is untouched
    assert client.post(
        "/practice",
        data={"sql": "SELECT COUNT(*) AS n FROM employees;"},
    ).data.count(b"200") >= 1


def test_practice_accepts_block_comment_before_select(client):
    # a /* */ comment before the SELECT used to trip the guard with a
    # misleading "Only SELECT" error even though it is a SELECT
    resp = client.post(
        "/practice",
        data={"sql": "/* headcount */ SELECT COUNT(*) AS n FROM employees;"},
    )
    assert resp.status_code == 200
    assert b"Only SELECT" not in resp.data
    assert b"200" in resp.data


def test_practice_accepts_with_select(client):
    resp = client.post(
        "/practice",
        data={"sql": "WITH one AS (SELECT 200 AS n) SELECT n FROM one;"},
    )
    assert resp.status_code == 200
    assert b"Only SELECT" not in resp.data
    assert b"200" in resp.data


def test_practice_accepts_quoted_cte_name(client):
    # a quoted CTE name ("one") used to trip the guard with a misleading
    # "Only SELECT" error even though it is a plain SELECT
    resp = client.post(
        "/practice",
        data={"sql": 'WITH "one" AS (SELECT 200 AS n) SELECT n FROM "one";'},
    )
    assert resp.status_code == 200
    assert b"Only SELECT" not in resp.data
    assert b"200" in resp.data


def test_practice_rejects_quoted_cte_delete(client):
    # the quoted-name fix must not open a hole: WITH "x" ... DELETE
    # still gets the "Only SELECT" error, not a raw sqlite error
    resp = client.post(
        "/practice",
        data={
            "sql": 'WITH "x" AS (SELECT 1 AS n) '
            "DELETE FROM employees WHERE id = 1;"
        },
    )
    assert resp.status_code == 200
    assert b"Only SELECT" in resp.data
    assert b"readonly" not in resp.data


def test_practice_rejects_with_delete(client):
    # WITH ... DELETE used to pass the guard (first word WITH) and die
    # on the read-only connection with a raw sqlite error
    resp = client.post(
        "/practice",
        data={
            "sql": "WITH x AS (SELECT 1 AS n) "
            "DELETE FROM employees WHERE id = 1;"
        },
    )
    assert resp.status_code == 200
    assert b"Only SELECT" in resp.data
    assert b"readonly" not in resp.data
    # and the table is untouched
    assert client.post(
        "/practice",
        data={"sql": "SELECT COUNT(*) AS n FROM employees;"},
    ).data.count(b"200") >= 1


def test_practice_shows_plain_error_for_bad_sql(client):
    resp = client.post("/practice", data={"sql": "SELECT * FROM nope;"})
    assert resp.status_code == 200
    assert b"no such table" in resp.data
    assert b"Traceback" not in resp.data


def test_practice_rejects_two_statements_with_plain_message(client):
    # pasting two queries used to surface sqlite's raw wording
    resp = client.post(
        "/practice",
        data={"sql": "SELECT COUNT(*) AS n FROM employees; SELECT 1;"},
    )
    assert resp.status_code == 200
    assert b"one statement at a time" in resp.data
    assert b"You can only execute" not in resp.data
    # and the table is untouched
    assert client.post(
        "/practice",
        data={"sql": "SELECT COUNT(*) AS n FROM employees;"},
    ).data.count(b"200") >= 1


def test_practice_empty_input_says_type_a_query_first(client):
    # an empty box used to get the misleading "Only SELECT" error
    resp = client.post("/practice", data={"sql": ""})
    assert resp.status_code == 200
    assert b"Type a query first" in resp.data
    assert b"Only SELECT" not in resp.data


def test_schema_lists_tables_and_rows(client):
    resp = client.get("/schema?table=departments")
    assert resp.status_code == 200
    assert b"Engineering" in resp.data
    assert b"6 rows in total" in resp.data
    resp = client.get("/schema?table=employees")
    assert resp.status_code == 200
    assert b"salary" in resp.data
    assert b"hire_date" in resp.data


def test_schema_unknown_table_404s(client):
    assert client.get("/schema?table=customers").status_code == 404


def test_static_css_served(client):
    resp = client.get("/static/style.css")
    assert resp.status_code == 200
    assert b"--accent" in resp.data
