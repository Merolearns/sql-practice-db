-- Headcount and average salary per department.
SELECT d.name AS department,
       COUNT(*) AS headcount,
       ROUND(AVG(e.salary)) AS avg_salary
FROM employees e
JOIN departments d ON d.id = e.dept_id
GROUP BY d.name
ORDER BY headcount DESC;
