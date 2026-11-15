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


def test_practice_shows_plain_error_for_bad_sql(client):
    resp = client.post("/practice", data={"sql": "SELECT * FROM nope;"})
    assert resp.status_code == 200
    assert b"no such table" in resp.data
    assert b"Traceback" not in resp.data


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
