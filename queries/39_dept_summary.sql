-- One summary row per department: headcount, salary spend, project count, project budgets.
SELECT d.name AS department,
       (SELECT COUNT(*) FROM employees e WHERE e.dept_id = d.id) AS headcount,
       (SELECT SUM(salary) FROM employees e WHERE e.dept_id = d.id) AS salary_spend,
       (SELECT COUNT(*) FROM projects p WHERE p.dept_id = d.id) AS project_count,
       (SELECT SUM(budget) FROM projects p WHERE p.dept_id = d.id) AS project_budgets
FROM departments d;
