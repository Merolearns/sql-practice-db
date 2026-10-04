-- Total hours logged on each project, most hours first.
SELECT p.name AS project, SUM(ep.hours) AS total_hours
FROM projects p
LEFT JOIN employee_projects ep ON ep.project_id = p.id
GROUP BY p.name
ORDER BY total_hours DESC;
