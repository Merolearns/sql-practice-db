-- Tag every employee as junior (<70k), mid (70k-120k), or senior (>120k).
SELECT name, salary,
       CASE
           WHEN salary < 70000 THEN 'junior'
           WHEN salary <= 120000 THEN 'mid'
           ELSE 'senior'
       END AS band
FROM employees
ORDER BY salary DESC
LIMIT 20;
