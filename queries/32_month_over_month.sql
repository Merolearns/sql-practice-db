-- Monthly sales totals next to the previous month's total.
WITH monthly AS (
    SELECT strftime('%Y-%m', sale_date) AS month, SUM(amount) AS total
    FROM sales
    GROUP BY month
)
SELECT month, total,
       LAG(total) OVER (ORDER BY month) AS prev_month_total,
       total - LAG(total) OVER (ORDER BY month) AS change_vs_prev
FROM monthly
ORDER BY month;
