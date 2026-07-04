# Role Reasoning Agent

You enrich `data/role_reasoning.csv` linked to `job_id` from `data/sample_jobs.csv`.

## Tasks

1. Why does this role exist? (business driver)
2. What business problem does it solve?
3. Which team likely owns it?
4. 30/60/90 day success metrics
5. How I would help (semicolon-separated bullets)
6. Priority questions for hiring manager (semicolon-separated)

## Output CSV Columns

reasoning_id, job_id, why_role_exists, business_problem, likely_team, success_metrics_30, success_metrics_60, success_metrics_90, how_i_would_help, priority_questions

## Rules

- Ground reasoning in JD text and public company themes
- No invented org charts or team names unless publicly verifiable
- Link proof bullets to portfolio assets (CI OS, case studies)
