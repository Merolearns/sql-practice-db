-- Departments with more than 30 employees.
SELECT d.name AS department, COUNT(*) AS headcount
FROM employees e
JOIN departments d ON d.id = e.dept_id
GROUP BY d.name
HAVING COUNT(*) > 30;
