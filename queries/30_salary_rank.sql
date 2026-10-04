-- Rank every employee by salary. Ties share a rank, and the next rank skips.
SELECT name, salary,
       RANK() OVER (ORDER BY salary DESC) AS salary_rank
FROM employees
ORDER BY salary_rank
LIMIT 15;
