-- Each employee's salary vs their department average (positive = above avg).
SELECT e.name, d.name AS department, e.salary,
       ROUND(AVG(e.salary) OVER (PARTITION BY e.dept_id)) AS dept_avg,
       e.salary - ROUND(AVG(e.salary) OVER (PARTITION BY e.dept_id)) AS diff_vs_avg
FROM employees e
JOIN departments d ON d.id = e.dept_id
ORDER BY diff_vs_avg DESC
LIMIT 15;
