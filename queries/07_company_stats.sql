-- Headcount, average salary, lowest salary, highest salary -- whole company.
SELECT COUNT(*) AS headcount,
       ROUND(AVG(salary)) AS avg_salary,
       MIN(salary) AS lowest_salary,
       MAX(salary) AS highest_salary
FROM employees;
