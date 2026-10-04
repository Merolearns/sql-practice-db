-- All employees and the projects they're on -- including people assigned to nothing.
SELECT e.name AS employee, p.name AS project
FROM employees e
LEFT JOIN employee_projects ep ON ep.emp_id = e.id
LEFT JOIN projects p ON p.id = ep.project_id
ORDER BY employee
LIMIT 25;
