# Data Dictionary

## sample_companies.csv

| Column | Type | Description |
|--------|------|-------------|
| company | string | Company name (primary key) |
| industry | string | Industry sector |
| location | string | Primary DFW location |
| sponsor_signal | string | H-1B/PERM sponsorship indicators (signal only) |
| target_roles | string | Semicolon-separated target role families |
| career_url | string | Company careers page URL |
| notes | string | Priority tier, rank, confidence notes |

## sample_jobs.csv

| Column | Type | Description |
|--------|------|-------------|
| company | string | FK to companies |
| title | string | Job title |
| location | string | Job location |
| job_url | string | Posting URL (sample) |
| description | string | Full job description text |
| posted_date | string | ISO date (YYYY-MM-DD) |
| role_family | string | Role cluster (e.g., Enterprise Technology) |
| visa_notes | string | Sponsorship notes with disclaimer |

## sample_contacts.csv

| Column | Type | Description |
|--------|------|-------------|
| company | string | FK to companies |
| contact_type | string | recruiter, hiring_manager, peer, alumni |
| search_query | string | LinkedIn search persona/query |
| LinkedIn_search_url | string | Quoted LinkedIn search string |
| message_angle | string | Recommended outreach angle |
| notes | string | Status and priority tier |

## profile_keywords.csv

| Column | Type | Description |
|--------|------|-------------|
| skill | string | Core skill label |
| category | string | Taxonomy bucket (python, sql, cloud, etc.) |
| weight | float | Scoring weight (0-1) |

## Enriched Columns (Runtime)

The data loader adds these columns for downstream modules:

- `company_id`, `job_id`, `contact_id` — stable identifiers
- `company_name` — alias for `company`
- `role_cluster`, `business_problem`, `priority_tier`, `status` — legacy compatibility

## gap_matrix.csv (Reference)

Portfolio capability gap matrix from DFW Universal Portfolio Sprint workbook. Used in dashboard overview tab.
