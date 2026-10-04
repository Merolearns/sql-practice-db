-- Employees hired more than 5 years ago (the veterans).
SELECT name, hire_date
FROM employees
WHERE hire_date < date('now', '-5 years')
ORDER BY hire_date;
