-- Departments spending over $2M total on salaries.
WITH dept_spend AS (
    SELECT dept_id, SUM(salary) AS total_salaries
    FROM employees
    GROUP BY dept_id
)
SELECT d.name AS department, ds.total_salaries
FROM dept_spend ds
JOIN departments d ON d.id = ds.dept_id
WHERE ds.total_salaries > 2000000
ORDER BY ds.total_salaries DESC;
