-- The single highest-paid employee in each department.
SELECT d.name AS department, e.name AS top_earner, e.salary
FROM employees e
JOIN departments d ON d.id = e.dept_id
WHERE e.salary = (
    SELECT MAX(e2.salary)
    FROM employees e2
    WHERE e2.dept_id = e.dept_id
);
