-- BONUS: 2026 sales pivoted -- one row per salesperson, one column per quarter.
SELECT e.name,
       SUM(CASE WHEN CAST(strftime('%m', s.sale_date) AS INTEGER) BETWEEN 1 AND 3
                THEN s.amount ELSE 0 END) AS q1,
       SUM(CASE WHEN CAST(strftime('%m', s.sale_date) AS INTEGER) BETWEEN 4 AND 6
                THEN s.amount ELSE 0 END) AS q2,
       SUM(CASE WHEN CAST(strftime('%m', s.sale_date) AS INTEGER) BETWEEN 7 AND 9
                THEN s.amount ELSE 0 END) AS q3,
       SUM(CASE WHEN CAST(strftime('%m', s.sale_date) AS INTEGER) BETWEEN 10 AND 12
                THEN s.amount ELSE 0 END) AS q4
FROM sales s
JOIN employees e ON e.id = s.emp_id
WHERE s.sale_date LIKE '2026-%'
GROUP BY e.name
ORDER BY q1 + q2 + q3 + q4 DESC
LIMIT 15;
