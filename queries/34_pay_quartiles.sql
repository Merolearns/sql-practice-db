-- Split all employees into 4 equal pay quartiles.
SELECT name, salary,
       NTILE(4) OVER (ORDER BY salary) AS pay_quartile
FROM employees
ORDER BY salary DESC
LIMIT 20;
