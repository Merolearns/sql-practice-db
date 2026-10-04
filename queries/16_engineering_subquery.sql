-- Everyone in the Engineering department, found with a subquery (no JOIN).
SELECT name, salary
FROM employees
WHERE dept_id IN (SELECT id FROM departments WHERE name = 'Engineering')
ORDER BY salary DESC;
