-- Total sales per month in 2026.
SELECT strftime('%Y-%m', sale_date) AS month,
       SUM(amount) AS total_sales,
       COUNT(*) AS num_sales
FROM sales
WHERE sale_date LIKE '2026-%'
GROUP BY month
ORDER BY month;
