-- TRICKY: departments where nobody earns over $150k but the average is above $90k.
SELECT d.name AS department,
       ROUND(AVG(e.salary)) AS avg_salary,
       MAX(e.salary) AS top_salary
FROM employees e
JOIN departments d ON d.id = e.dept_id
GROUP BY d.name
HAVING MAX(e.salary) <= 150000 AND AVG(e.salary) > 90000;
