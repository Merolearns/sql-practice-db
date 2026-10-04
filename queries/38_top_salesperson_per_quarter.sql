-- FINAL BOSS: the top salesperson of each quarter in 2026.
WITH qsales AS (
    SELECT e.name,
           strftime('%Y', s.sale_date) || '-Q' ||
           CAST((CAST(strftime('%m', s.sale_date) AS INTEGER) + 2) / 3 AS INTEGER) AS quarter,
           SUM(s.amount) AS total
    FROM sales s
    JOIN employees e ON e.id = s.emp_id
    WHERE s.sale_date >= '2026-01-01'
    GROUP BY e.name, quarter
),
ranked AS (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY quarter ORDER BY total DESC) AS rn
    FROM qsales
)
SELECT name, quarter, total
FROM ranked
WHERE rn = 1
ORDER BY quarter;
