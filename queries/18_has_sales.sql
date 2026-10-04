-- Employees who have made at least one sale.
SELECT DISTINCT e.name
FROM employees e
WHERE EXISTS (SELECT 1 FROM sales s WHERE s.emp_id = e.id)
ORDER BY e.name;
