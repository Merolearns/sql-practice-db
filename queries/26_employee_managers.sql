-- Each employee with their manager's name (department heads have no manager).
SELECT e.name AS employee, m.name AS manager
FROM employees e
LEFT JOIN employees m ON m.id = e.manager_id
ORDER BY employee
LIMIT 25;
