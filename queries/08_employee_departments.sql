-- Every employee's name next to their department's name.
SELECT e.name AS employee, d.name AS department
FROM employees e
JOIN departments d ON d.id = e.dept_id
ORDER BY employee;
