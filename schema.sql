-- company.db schema
-- A tiny fictional company: departments, employees, projects, assignments, sales.
-- All data is randomly generated sample data (see seed.py). Nothing here is real.

PRAGMA foreign_keys = ON;

CREATE TABLE departments (
    id   INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE employees (
    id         INTEGER PRIMARY KEY,
    name       TEXT NOT NULL,
    dept_id    INTEGER NOT NULL REFERENCES departments (id),
    salary     INTEGER NOT NULL,          -- annual salary in USD
    hire_date  TEXT NOT NULL,             -- ISO date: YYYY-MM-DD
    manager_id INTEGER REFERENCES employees (id)  -- NULL for department heads
);

CREATE TABLE projects (
    id         INTEGER PRIMARY KEY,
    name       TEXT NOT NULL,
    dept_id    INTEGER NOT NULL REFERENCES departments (id),
    budget     INTEGER NOT NULL,          -- budget in USD
    start_date TEXT NOT NULL,             -- ISO date: YYYY-MM-DD
    end_date   TEXT                      -- NULL means still ongoing
);

CREATE TABLE employee_projects (
    emp_id     INTEGER NOT NULL REFERENCES employees (id),
    project_id INTEGER NOT NULL REFERENCES projects (id),
    hours      INTEGER NOT NULL DEFAULT 0,  -- hours logged on the project
    PRIMARY KEY (emp_id, project_id)
);

CREATE TABLE sales (
    id        INTEGER PRIMARY KEY,
    emp_id    INTEGER NOT NULL REFERENCES employees (id),
    amount    INTEGER NOT NULL,          -- sale amount in USD
    sale_date TEXT NOT NULL              -- ISO date: YYYY-MM-DD
);
