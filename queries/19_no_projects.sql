-- Employees who aren't assigned to any project.
SELECT e.name, d.name AS department
FROM employees e
JOIN departments d ON d.id = e.dept_id
WHERE NOT EXISTS (
    SELECT 1 FROM employee_projects ep WHERE ep.emp_id = e.id
)
ORDER BY e.name;
