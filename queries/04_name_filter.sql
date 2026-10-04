-- Employees hired after 2023 whose first name starts with 'M'.
SELECT name, hire_date
FROM employees
WHERE hire_date > '2023-01-01'
  AND name LIKE 'M%';
