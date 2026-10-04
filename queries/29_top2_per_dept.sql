-- The 2 highest-paid employees in each department.
SELECT department, name, salary
FROM (
    SELECT d.name AS department, e.name, e.salary,
           ROW_NUMBER() OVER (PARTITION BY e.dept_id ORDER BY e.salary DESC) AS rn
    FROM employees e
    JOIN departments d ON d.id = e.dept_id
)
WHERE rn <= 2
ORDER BY department, salary DESC;
