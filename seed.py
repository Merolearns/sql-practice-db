#!/usr/bin/env python3
"""Seed company.db with fictional sample data.

Everything in here is made up. Names are randomly combined from public
first/last name lists, salaries and dates are random within sane ranges.
random.seed() is fixed so the database is identical on every build --
that way the sample answers in expected/ always match.

Run via build.sh (schema.sql must be loaded first).
"""

import random
import sqlite3
from datetime import date, timedelta
from pathlib import Path

random.seed(42)

DB = Path(__file__).with_name("company.db")

FIRST_NAMES = [
    "James", "Maria", "Robert", "Linda", "Michael", "Sarah", "David", "Emma",
    "Daniel", "Olivia", "Matthew", "Sophia", "Andrew", "Ava", "Joshua",
    "Mia", "Kevin", "Chloe", "Brian", "Ella", "Jason", "Grace", "Ryan",
    "Lily", "Eric", "Aria", "Nathan", "Zoe", "Tyler", "Nora", "Aaron",
    "Hannah", "Kyle", "Ella", "Marcus", "Priya", "Omar", "Yuki", "Fatima",
    "Carlos", "Nina", "Victor", "Aisha", "Tom", "Lena", "Sam", "Dana",
]

LAST_NAMES = [
    "Smith", "Garcia", "Johnson", "Lee", "Brown", "Kim", "Patel", "Nguyen",
    "Davis", "Miller", "Wilson", "Moore", "Taylor", "Anderson", "Thomas",
    "Hernandez", "Moore", "Martin", "Jackson", "Thompson", "White", "Lopez",
    "Gonzalez", "Clark", "Lewis", "Robinson", "Walker", "Hall", "Young",
    "King", "Wright", "Scott", "Green", "Baker", "Adams", "Nelson", "Carter",
    "Mitchell", "Perez", "Roberts", "Turner", "Phillips", "Campbell",
    "Parker", "Evans", "Edwards", "Collins", "Stewart", "Morris", "Rogers",
]

DEPARTMENTS = [
    "Engineering",
    "Sales",
    "Marketing",
    "Customer Support",
    "Finance",
    "Operations",
]

# plausible salary bands per department (USD, annual)
SALARY_BANDS = {
    "Engineering": (95_000, 175_000),
    "Sales": (60_000, 140_000),
    "Marketing": (65_000, 130_000),
    "Customer Support": (45_000, 85_000),
    "Finance": (75_000, 150_000),
    "Operations": (60_000, 120_000),
}

PROJECT_NAMES = [
    "Website Redesign",
    "Mobile App v2",
    "Data Warehouse Migration",
    "CRM Rollout",
    "Customer Portal",
    "Billing System Upgrade",
    "Analytics Dashboard",
    "Onboarding Flow Revamp",
    "API Gateway",
    "Support Ticket Automation",
    "Marketing Site Launch",
    "Inventory Tracker",
    "Payroll Integration",
    "Security Audit",
    "Cloud Cost Optimization",
]

HIRE_START = date(2019, 1, 1)
HIRE_END = date(2026, 9, 30)


def random_date(start: date, end: date) -> str:
    delta = (end - start).days
    return (start + timedelta(days=random.randint(0, delta))).isoformat()


def main() -> None:
    con = sqlite3.connect(DB)
    cur = con.cursor()

    # Seeding twice used to silently double every row, and then the sample
    # answers in expected/ stopped matching with no clue why. Refuse a
    # second run on the same database -- ./build.sh rebuilds from scratch.
    seeded = cur.execute(
        "SELECT COUNT(*) FROM sqlite_master"
        " WHERE type = 'table' AND name = 'employees'"
    ).fetchone()[0]
    if seeded and cur.execute("SELECT COUNT(*) FROM employees").fetchone()[0]:
        print(f"{DB.name} is already seeded -- run ./build.sh to rebuild it")
        raise SystemExit(1)

    # --- departments -----------------------------------------------------
    dept_ids = {}
    for name in DEPARTMENTS:
        cur.execute("INSERT INTO departments (name) VALUES (?)", (name,))
        dept_ids[name] = cur.lastrowid

    # --- employees -------------------------------------------------------
    # ~200 people, weighted toward bigger departments
    dept_weights = {
        "Engineering": 55,
        "Sales": 35,
        "Marketing": 25,
        "Customer Support": 40,
        "Finance": 20,
        "Operations": 25,
    }

    used_names = set()
    employees = []  # (id, name, dept_id)

    for dept, count in dept_weights.items():
        dept_id = dept_ids[dept]
        lo, hi = SALARY_BANDS[dept]
        for _ in range(count):
            name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
            while name in used_names:  # keep names unique
                name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
            used_names.add(name)
            salary = random.randint(lo, hi)
            salary = round(salary / 1000) * 1000  # round to nearest 1k
            hire = random_date(HIRE_START, HIRE_END)
            cur.execute(
                "INSERT INTO employees (name, dept_id, salary, hire_date, manager_id)"
                " VALUES (?, ?, ?, ?, NULL)",
                (name, dept_id, salary, hire),
            )
            employees.append((cur.lastrowid, name, dept_id))

    # --- manager hierarchy ------------------------------------------------
    # First person hired in each department becomes the head (manager_id NULL);
    # everyone else reports to a random earlier hire in the same department.
    by_dept = {}
    for emp_id, name, dept_id in employees:
        by_dept.setdefault(dept_id, []).append(emp_id)

    for dept_id, ids in by_dept.items():
        head, rest = ids[0], ids[1:]
        for emp_id in rest:
            manager = random.choice([head] + [i for i in rest if i < emp_id] or [head])
            cur.execute(
                "UPDATE employees SET manager_id = ? WHERE id = ?",
                (manager, emp_id),
            )

    # --- projects ---------------------------------------------------------
    project_ids = []
    for pname in PROJECT_NAMES:
        dept = random.choice(DEPARTMENTS)
        dept_id = dept_ids[dept]
        budget = round(random.randint(50_000, 800_000) / 10_000) * 10_000
        start = random_date(date(2024, 1, 1), date(2026, 6, 1))
        start_d = date.fromisoformat(start)
        if random.random() < 0.35:
            end = None  # still ongoing
        else:
            end = (start_d + timedelta(days=random.randint(60, 400))).isoformat()
        cur.execute(
            "INSERT INTO projects (name, dept_id, budget, start_date, end_date)"
            " VALUES (?, ?, ?, ?, ?)",
            (pname, dept_id, budget, start, end),
        )
        project_ids.append((cur.lastrowid, dept_id))

    # --- project assignments -------------------------------------------------
    # employees work on projects owned by their own department
    dept_employees = {}
    for emp_id, name, dept_id in employees:
        dept_employees.setdefault(dept_id, []).append(emp_id)

    for project_id, dept_id in project_ids:
        crew = random.sample(
            dept_employees[dept_id],
            k=random.randint(4, min(12, len(dept_employees[dept_id]))),
        )
        for emp_id in crew:
            hours = random.randint(5, 200)
            cur.execute(
                "INSERT INTO employee_projects (emp_id, project_id, hours)"
                " VALUES (?, ?, ?)",
                (emp_id, project_id, hours),
            )

    # --- sales ----------------------------------------------------------------
    # only the Sales department sells; ~700 sales across 2025-2026
    sales_team = dept_employees[dept_ids["Sales"]]
    for _ in range(700):
        emp_id = random.choice(sales_team)
        amount = round(random.randint(500, 50_000) / 100) * 100
        sale_date = random_date(date(2025, 1, 1), date(2026, 9, 30))
        cur.execute(
            "INSERT INTO sales (emp_id, amount, sale_date) VALUES (?, ?, ?)",
            (emp_id, amount, sale_date),
        )

    con.commit()

    # sanity printout
    counts = {
        t: cur.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        for t in ("departments", "employees", "projects", "employee_projects", "sales")
    }
    con.close()
    print(f"Seeded {DB.name}: " + ", ".join(f"{t}={n}" for t, n in counts.items()))


if __name__ == "__main__":
    main()
