-- TRICKY: employees assigned to EVERY project their department owns.
SELECT e.name, d.name AS department
FROM employees e
JOIN departments d ON d.id = e.dept_id
WHERE EXISTS (SELECT 1 FROM projects p WHERE p.dept_id = e.dept_id)
  AND NOT EXISTS (
      SELECT 1
      FROM projects p
      WHERE p.dept_id = e.dept_id
        AND NOT EXISTS (
            SELECT 1
            FROM employee_projects ep
            WHERE ep.emp_id = e.id AND ep.project_id = p.id
        )
  );
