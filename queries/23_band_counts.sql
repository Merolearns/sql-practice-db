-- How many employees fall in each salary band?
SELECT
       CASE
           WHEN salary < 70000 THEN 'junior'
           WHEN salary <= 120000 THEN 'mid'
           ELSE 'senior'
       END AS band,
       COUNT(*) AS headcount
FROM employees
GROUP BY band
ORDER BY headcount DESC;
