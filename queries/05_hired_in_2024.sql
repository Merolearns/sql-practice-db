-- The 10 lowest-paid people hired in 2024.
SELECT name, salary, hire_date
FROM employees
WHERE hire_date BETWEEN '2024-01-01' AND '2024-12-31'
ORDER BY salary ASC
LIMIT 10;
