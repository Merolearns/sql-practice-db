-- Each project with its owning department and budget.
SELECT p.name AS project, d.name AS department, p.budget
FROM projects p
JOIN departments d ON d.id = p.dept_id
ORDER BY p.budget DESC;
