-- One alphabetized list mixing all employee names and all department names.
SELECT name FROM employees
UNION
SELECT name FROM departments
ORDER BY 1;
