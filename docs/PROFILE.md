# User Profile Template

Edit `data/user_profile.yaml` directly or use the **My Profile & Portfolio** tab in the dashboard.

## Fields

| Field | Description |
|-------|-------------|
| `name` | Your display name |
| `headline` | One-line positioning (e.g., Enterprise Technology Analyst) |
| `positioning` | 2–3 sentence value proposition |
| `skills[]` | Core skills list |
| `experience_bullets[]` | Resume-style impact bullets |
| `education` | Degree / program summary |
| `opt_status` | Work authorization note (OPT/EAD, STEM OPT pathway) |
| `portfolio_links[]` | `{title, url}` demo and case study links |
| `proof_asset_ids[]` | IDs from `data/proof_assets.csv` |
| `star_stories[]` | STAR format stories for behavioral interviews |

## Optional Upload

Place resume highlights at `data/uploads/resume_highlights.txt` (gitignored for privacy).

## Simulator Integration

The Interview Simulator automatically loads your profile via `src/profile_manager.get_profile_for_simulator()`.

## 60-Second Pitch

Use **Copy 60-second pitch** in the dashboard — generated from headline, skills, bullets, and OPT status.
