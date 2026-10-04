-- List the 10 highest-paid employees, highest first.
SELECT name, salary
FROM employees
ORDER BY salary DESC
LIMIT 10;
