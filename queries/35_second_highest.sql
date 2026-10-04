-- TRICKY: second-highest salary in each department -- no window functions allowed.
SELECT d.name AS department, MAX(e.salary) AS second_highest_salary
FROM employees e
JOIN departments d ON d.id = e.dept_id
WHERE e.salary < (
    SELECT MAX(e2.salary)
    FROM employees e2
    WHERE e2.dept_id = e.dept_id
)
GROUP BY d.name;
