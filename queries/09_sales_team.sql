-- Names and salaries of everyone on the Sales team.
SELECT e.name, e.salary
FROM employees e
JOIN departments d ON d.id = e.dept_id
WHERE d.name = 'Sales'
ORDER BY e.salary DESC;
