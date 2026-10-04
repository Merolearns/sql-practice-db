-- Day-by-day sales with a running total.
WITH daily AS (
    SELECT sale_date, SUM(amount) AS day_total
    FROM sales
    GROUP BY sale_date
)
SELECT sale_date, day_total,
       SUM(day_total) OVER (ORDER BY sale_date) AS running_total
FROM daily
ORDER BY sale_date
LIMIT 20;
