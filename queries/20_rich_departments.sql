-- Departments whose average salary beats the company average (use a CTE).
WITH company_avg AS (
    SELECT AVG(salary) AS avg_sal FROM employees
)
SELECT d.name AS department, ROUND(AVG(e.salary)) AS dept_avg
FROM employees e
JOIN departments d ON d.id = e.dept_id
GROUP BY d.name
HAVING AVG(e.salary) > (SELECT avg_sal FROM company_avg);
