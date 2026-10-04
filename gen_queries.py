#!/usr/bin/env python3
"""Write the 40 numbered practice queries into queries/.

Each file: a plain-English question as a -- comment, then the query.
All queries are verified to run against company.db (see verify step).
"""
from pathlib import Path

OUT = Path(__file__).with_name("queries")
OUT.mkdir(exist_ok=True)

QUERIES = [
    # ---- basics ----------------------------------------------------------
    ("01_select_all.sql",
     "Show every employee's id, name, and salary.",
     """SELECT id, name, salary
FROM employees;"""),

    ("02_high_earners.sql",
     "Find everyone earning more than $120,000 a year.",
     """SELECT name, salary
FROM employees
WHERE salary > 120000;"""),

    ("03_top_10_paid.sql",
     "List the 10 highest-paid employees, highest first.",
     """SELECT name, salary
FROM employees
ORDER BY salary DESC
LIMIT 10;"""),

    ("04_name_filter.sql",
     "Employees hired after 2023 whose first name starts with 'M'.",
     """SELECT name, hire_date
FROM employees
WHERE hire_date > '2023-01-01'
  AND name LIKE 'M%';"""),

    ("05_hired_in_2024.sql",
     "The 10 lowest-paid people hired in 2024.",
     """SELECT name, salary, hire_date
FROM employees
WHERE hire_date BETWEEN '2024-01-01' AND '2024-12-31'
ORDER BY salary ASC
LIMIT 10;"""),

    ("06_distinct_depts.sql",
     "How many different departments actually have employees?",
     """SELECT COUNT(DISTINCT dept_id) AS departments_with_staff
FROM employees;"""),

    ("07_company_stats.sql",
     "Headcount, average salary, lowest salary, highest salary -- whole company.",
     """SELECT COUNT(*) AS headcount,
       ROUND(AVG(salary)) AS avg_salary,
       MIN(salary) AS lowest_salary,
       MAX(salary) AS highest_salary
FROM employees;"""),

    # ---- joins ------------------------------------------------------------
    ("08_employee_departments.sql",
     "Every employee's name next to their department's name.",
     """SELECT e.name AS employee, d.name AS department
FROM employees e
JOIN departments d ON d.id = e.dept_id
ORDER BY employee;"""),

    ("09_sales_team.sql",
     "Names and salaries of everyone on the Sales team.",
     """SELECT e.name, e.salary
FROM employees e
JOIN departments d ON d.id = e.dept_id
WHERE d.name = 'Sales'
ORDER BY e.salary DESC;"""),

    ("10_headcount_by_dept.sql",
     "Headcount and average salary per department.",
     """SELECT d.name AS department,
       COUNT(*) AS headcount,
       ROUND(AVG(e.salary)) AS avg_salary
FROM employees e
JOIN departments d ON d.id = e.dept_id
GROUP BY d.name
ORDER BY headcount DESC;"""),

    ("11_big_departments.sql",
     "Departments with more than 30 employees.",
     """SELECT d.name AS department, COUNT(*) AS headcount
FROM employees e
JOIN departments d ON d.id = e.dept_id
GROUP BY d.name
HAVING COUNT(*) > 30;"""),

    ("12_projects_with_depts.sql",
     "Each project with its owning department and budget.",
     """SELECT p.name AS project, d.name AS department, p.budget
FROM projects p
JOIN departments d ON d.id = p.dept_id
ORDER BY p.budget DESC;"""),

    ("13_hours_per_project.sql",
     "Total hours logged on each project, most hours first.",
     """SELECT p.name AS project, SUM(ep.hours) AS total_hours
FROM projects p
LEFT JOIN employee_projects ep ON ep.project_id = p.id
GROUP BY p.name
ORDER BY total_hours DESC;"""),

    ("14_everyone_and_projects.sql",
     "All employees and the projects they're on -- including people assigned to nothing.",
     """SELECT e.name AS employee, p.name AS project
FROM employees e
LEFT JOIN employee_projects ep ON ep.emp_id = e.id
LEFT JOIN projects p ON p.id = ep.project_id
ORDER BY employee
LIMIT 25;"""),

    # ---- subqueries --------------------------------------------------------
    ("15_above_avg_salary.sql",
     "Employees who earn more than the company-wide average salary.",
     """SELECT name, salary
FROM employees
WHERE salary > (SELECT AVG(salary) FROM employees)
ORDER BY salary DESC;"""),

    ("16_engineering_subquery.sql",
     "Everyone in the Engineering department, found with a subquery (no JOIN).",
     """SELECT name, salary
FROM employees
WHERE dept_id IN (SELECT id FROM departments WHERE name = 'Engineering')
ORDER BY salary DESC;"""),

    ("17_top_earner_per_dept.sql",
     "The single highest-paid employee in each department.",
     """SELECT d.name AS department, e.name AS top_earner, e.salary
FROM employees e
JOIN departments d ON d.id = e.dept_id
WHERE e.salary = (
    SELECT MAX(e2.salary)
    FROM employees e2
    WHERE e2.dept_id = e.dept_id
);"""),

    ("18_has_sales.sql",
     "Employees who have made at least one sale.",
     """SELECT DISTINCT e.name
FROM employees e
WHERE EXISTS (SELECT 1 FROM sales s WHERE s.emp_id = e.id)
ORDER BY e.name;"""),

    ("19_no_projects.sql",
     "Employees who aren't assigned to any project.",
     """SELECT e.name, d.name AS department
FROM employees e
JOIN departments d ON d.id = e.dept_id
WHERE NOT EXISTS (
    SELECT 1 FROM employee_projects ep WHERE ep.emp_id = e.id
)
ORDER BY e.name;"""),

    # ---- CTEs ---------------------------------------------------------------
    ("20_rich_departments.sql",
     "Departments whose average salary beats the company average (use a CTE).",
     """WITH company_avg AS (
    SELECT AVG(salary) AS avg_sal FROM employees
)
SELECT d.name AS department, ROUND(AVG(e.salary)) AS dept_avg
FROM employees e
JOIN departments d ON d.id = e.dept_id
GROUP BY d.name
HAVING AVG(e.salary) > (SELECT avg_sal FROM company_avg);"""),

    ("21_big_spenders.sql",
     "Departments spending over $2M total on salaries.",
     """WITH dept_spend AS (
    SELECT dept_id, SUM(salary) AS total_salaries
    FROM employees
    GROUP BY dept_id
)
SELECT d.name AS department, ds.total_salaries
FROM dept_spend ds
JOIN departments d ON d.id = ds.dept_id
WHERE ds.total_salaries > 2000000
ORDER BY ds.total_salaries DESC;"""),

    # ---- CASE ----------------------------------------------------------------
    ("22_salary_bands.sql",
     "Tag every employee as junior (<70k), mid (70k-120k), or senior (>120k).",
     """SELECT name, salary,
       CASE
           WHEN salary < 70000 THEN 'junior'
           WHEN salary <= 120000 THEN 'mid'
           ELSE 'senior'
       END AS band
FROM employees
ORDER BY salary DESC
LIMIT 20;"""),

    ("23_band_counts.sql",
     "How many employees fall in each salary band?",
     """SELECT
       CASE
           WHEN salary < 70000 THEN 'junior'
           WHEN salary <= 120000 THEN 'mid'
           ELSE 'senior'
       END AS band,
       COUNT(*) AS headcount
FROM employees
GROUP BY band
ORDER BY headcount DESC;"""),

    # ---- dates ----------------------------------------------------------------
    ("24_veterans.sql",
     "Employees hired more than 5 years ago (the veterans).",
     """SELECT name, hire_date
FROM employees
WHERE hire_date < date('now', '-5 years')
ORDER BY hire_date;"""),

    ("25_monthly_sales_2026.sql",
     "Total sales per month in 2026.",
     """SELECT strftime('%Y-%m', sale_date) AS month,
       SUM(amount) AS total_sales,
       COUNT(*) AS num_sales
FROM sales
WHERE sale_date LIKE '2026-%'
GROUP BY month
ORDER BY month;"""),

    # ---- self-joins ------------------------------------------------------------
    ("26_employee_managers.sql",
     "Each employee with their manager's name (department heads have no manager).",
     """SELECT e.name AS employee, m.name AS manager
FROM employees e
LEFT JOIN employees m ON m.id = e.manager_id
ORDER BY employee
LIMIT 25;"""),

    ("27_outearn_manager.sql",
     "Employees who earn MORE than their own manager. Awkward.",
     """SELECT e.name AS employee, e.salary,
       m.name AS manager, m.salary AS manager_salary
FROM employees e
JOIN employees m ON m.id = e.manager_id
WHERE e.salary > m.salary;"""),

    ("28_combined_names.sql",
     "One alphabetized list mixing all employee names and all department names.",
     """SELECT name FROM employees
UNION
SELECT name FROM departments
ORDER BY 1;"""),

    # ---- window functions -------------------------------------------------------
    ("29_top2_per_dept.sql",
     "The 2 highest-paid employees in each department.",
     """SELECT department, name, salary
FROM (
    SELECT d.name AS department, e.name, e.salary,
           ROW_NUMBER() OVER (PARTITION BY e.dept_id ORDER BY e.salary DESC) AS rn
    FROM employees e
    JOIN departments d ON d.id = e.dept_id
)
WHERE rn <= 2
ORDER BY department, salary DESC;"""),

    ("30_salary_rank.sql",
     "Rank every employee by salary. Ties share a rank, and the next rank skips.",
     """SELECT name, salary,
       RANK() OVER (ORDER BY salary DESC) AS salary_rank
FROM employees
ORDER BY salary_rank
LIMIT 15;"""),

    ("31_running_sales.sql",
     "Day-by-day sales with a running total.",
     """WITH daily AS (
    SELECT sale_date, SUM(amount) AS day_total
    FROM sales
    GROUP BY sale_date
)
SELECT sale_date, day_total,
       SUM(day_total) OVER (ORDER BY sale_date) AS running_total
FROM daily
ORDER BY sale_date
LIMIT 20;"""),

    ("32_month_over_month.sql",
     "Monthly sales totals next to the previous month's total.",
     """WITH monthly AS (
    SELECT strftime('%Y-%m', sale_date) AS month, SUM(amount) AS total
    FROM sales
    GROUP BY month
)
SELECT month, total,
       LAG(total) OVER (ORDER BY month) AS prev_month_total,
       total - LAG(total) OVER (ORDER BY month) AS change_vs_prev
FROM monthly
ORDER BY month;"""),

    ("33_vs_dept_avg.sql",
     "Each employee's salary vs their department average (positive = above avg).",
     """SELECT e.name, d.name AS department, e.salary,
       ROUND(AVG(e.salary) OVER (PARTITION BY e.dept_id)) AS dept_avg,
       e.salary - ROUND(AVG(e.salary) OVER (PARTITION BY e.dept_id)) AS diff_vs_avg
FROM employees e
JOIN departments d ON d.id = e.dept_id
ORDER BY diff_vs_avg DESC
LIMIT 15;"""),

    ("34_pay_quartiles.sql",
     "Split all employees into 4 equal pay quartiles.",
     """SELECT name, salary,
       NTILE(4) OVER (ORDER BY salary) AS pay_quartile
FROM employees
ORDER BY salary DESC
LIMIT 20;"""),

    # ---- tricky ones -------------------------------------------------------------
    ("35_second_highest.sql",
     "TRICKY: second-highest salary in each department -- no window functions allowed.",
     """SELECT d.name AS department, MAX(e.salary) AS second_highest_salary
FROM employees e
JOIN departments d ON d.id = e.dept_id
WHERE e.salary < (
    SELECT MAX(e2.salary)
    FROM employees e2
    WHERE e2.dept_id = e.dept_id
)
GROUP BY d.name;"""),

    ("36_all_dept_projects.sql",
     "TRICKY: employees assigned to EVERY project their department owns.",
     """SELECT e.name, d.name AS department
FROM employees e
JOIN departments d ON d.id = e.dept_id
WHERE EXISTS (SELECT 1 FROM projects p WHERE p.dept_id = e.dept_id)
  AND NOT EXISTS (
      SELECT 1
      FROM projects p
      WHERE p.dept_id = e.dept_id
        AND NOT EXISTS (
            SELECT 1
            FROM employee_projects ep
            WHERE ep.emp_id = e.id AND ep.project_id = p.id
        )
  );"""),

    ("37_balanced_depts.sql",
     "TRICKY: departments where nobody earns over $150k but the average is above $90k.",
     """SELECT d.name AS department,
       ROUND(AVG(e.salary)) AS avg_salary,
       MAX(e.salary) AS top_salary
FROM employees e
JOIN departments d ON d.id = e.dept_id
GROUP BY d.name
HAVING MAX(e.salary) <= 150000 AND AVG(e.salary) > 90000;"""),

    # ---- final boss ---------------------------------------------------------------
    ("38_top_salesperson_per_quarter.sql",
     "FINAL BOSS: the top salesperson of each quarter in 2026.",
     """WITH qsales AS (
    SELECT e.name,
           strftime('%Y', s.sale_date) || '-Q' ||
           CAST((CAST(strftime('%m', s.sale_date) AS INTEGER) + 2) / 3 AS INTEGER) AS quarter,
           SUM(s.amount) AS total
    FROM sales s
    JOIN employees e ON e.id = s.emp_id
    WHERE s.sale_date >= '2026-01-01'
    GROUP BY e.name, quarter
),
ranked AS (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY quarter ORDER BY total DESC) AS rn
    FROM qsales
)
SELECT name, quarter, total
FROM ranked
WHERE rn = 1
ORDER BY quarter;"""),

    ("39_dept_summary.sql",
     "One summary row per department: headcount, salary spend, project count, project budgets.",
     """SELECT d.name AS department,
       (SELECT COUNT(*) FROM employees e WHERE e.dept_id = d.id) AS headcount,
       (SELECT SUM(salary) FROM employees e WHERE e.dept_id = d.id) AS salary_spend,
       (SELECT COUNT(*) FROM projects p WHERE p.dept_id = d.id) AS project_count,
       (SELECT SUM(budget) FROM projects p WHERE p.dept_id = d.id) AS project_budgets
FROM departments d;"""),

    ("40_quarterly_pivot.sql",
     "BONUS: 2026 sales pivoted -- one row per salesperson, one column per quarter.",
     """SELECT e.name,
       SUM(CASE WHEN CAST(strftime('%m', s.sale_date) AS INTEGER) BETWEEN 1 AND 3
                THEN s.amount ELSE 0 END) AS q1,
       SUM(CASE WHEN CAST(strftime('%m', s.sale_date) AS INTEGER) BETWEEN 4 AND 6
                THEN s.amount ELSE 0 END) AS q2,
       SUM(CASE WHEN CAST(strftime('%m', s.sale_date) AS INTEGER) BETWEEN 7 AND 9
                THEN s.amount ELSE 0 END) AS q3,
       SUM(CASE WHEN CAST(strftime('%m', s.sale_date) AS INTEGER) BETWEEN 10 AND 12
                THEN s.amount ELSE 0 END) AS q4
FROM sales s
JOIN employees e ON e.id = s.emp_id
WHERE s.sale_date LIKE '2026-%'
GROUP BY e.name
ORDER BY q1 + q2 + q3 + q4 DESC
LIMIT 15;"""),
]

for filename, question, sql in QUERIES:
    (OUT / filename).write_text(f"-- {question}\n{sql}\n")

print(f"Wrote {len(QUERIES)} query files to {OUT}")
