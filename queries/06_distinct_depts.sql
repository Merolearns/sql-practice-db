-- How many different departments actually have employees?
SELECT COUNT(DISTINCT dept_id) AS departments_with_staff
FROM employees;
