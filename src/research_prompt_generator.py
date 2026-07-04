"""Research prompt generator — Claude/Deep Research ready prompts."""

from src.company_profile_engine import build_company_360
from src.people_power_mapper import generate_people_search_queries, load_people_map
from src.role_reasoning_engine import infer_role_reason, load_role_reasoning


def generate_company_research_prompt(company_id: str) -> str:
    """Generate a deep research prompt for company intelligence enrichment."""
    company = build_company_360(company_id)
    if not company.get("found"):
        return f"Research public information about company_id={company_id}. No seeded profile found."

    name = company["company_name"]
    gaps = company.get("research_gaps", [])
    gap_text = "\n".join(f"- {g}" for g in gaps) if gaps else "- None identified"

    return f"""# Company Deep Profile Research Prompt

Research **{name}** using **public sources only**. Do not scrape LinkedIn or invent contact names.

## Context
- Industry: {company.get('industry', 'N/A')}
- DFW Presence: {company.get('dfw_presence', 'N/A')}
- Current summary: {company.get('strategic_summary', '')}

## Research Tasks
1. Validate strategic summary against recent public news (last 12 months)
2. Identify 3-5 active technology initiatives with confidence levels (high/medium/low)
3. List public tech stack signals from job postings and engineering blogs
4. Note sponsorship context — cite DOL/USCIS or public H-1B data only; include disclaimer
5. Identify research gaps to fill:

{gap_text}

## Output Format
Return structured JSON-compatible sections:
- strategic_summary (updated)
- tech_stack_themes (semicolon-separated)
- growth_signals
- risk_factors
- projects[] with theme, description, confidence_level, source_type
- sources[] with source_type, source_title, source_url, verified

## Rules
- NO fake people names
- NO unverified claims presented as fact
- Mark speculative themes as low confidence
- Include source URLs for every claim
"""


def generate_people_research_prompt(company_id: str, contact_types: list[str] | None = None) -> str:
    """Generate a people mapping research prompt with TBD placeholder guidance."""
    people_df = load_people_map()
    company_people = people_df[people_df["company_id"] == company_id]
    company_name = company_people.iloc[0]["company_name"] if not company_people.empty else company_id
    contact_types = contact_types or ["recruiter", "hiring_manager", "peer", "alumni"]

    search_urls = []
    for ct in contact_types:
        search_urls.append(f"- **{ct}:** {generate_people_search_queries(company_name, ct)}")

    return f"""# People Map Research Prompt

Map key contacts for **{company_name}** using manual verification only.

## Contact Types to Research
{chr(10).join(f'- {ct}' for ct in contact_types)}

## Search Query URLs (manual verification)
{chr(10).join(search_urls)}

## Rules — CRITICAL
- Use **TBD placeholders** until identity is verified (e.g., "TBD Recruiter")
- Set verification_status: placeholder | partial | verified
- NO LinkedIn automation or scraping
- NO fake names or fabricated titles
- Record search_query_url for each placeholder

## Output Format (CSV rows for people_map.csv)
person_id, company_id, company_name, role_title, contact_type, person_name,
verification_status, search_query_url, hiring_power_score, notes

## Scoring Guidance
- hiring_manager: 80-90
- recruiter: 60-70
- alumni: 45-55
- peer: 40-50
Adjust based on relevance to target role family.
"""


def generate_role_research_prompt(job_id: str, jobs_df) -> str:
    """Generate a role reasoning research prompt."""
    reasoning_df = load_role_reasoning()
    reason = infer_role_reason(job_id, jobs_df, reasoning_df)
    job_rows = jobs_df[jobs_df["job_id"] == job_id]
    description = job_rows.iloc[0]["description"] if not job_rows.empty else ""

    return f"""# Role Reasoning Research Prompt

Analyze role **{reason.get('title', job_id)}** at **{reason.get('company', '')}**.

## Job Description
{description[:1500]}

## Research Tasks
1. Why does this role exist? (business driver, not generic HR language)
2. What business problem does it solve?
3. Which team/org unit likely owns it?
4. Define realistic 30/60/90 day success metrics
5. Generate 5 priority questions for a hiring manager conversation
6. Map "How I would help" bullets to portfolio proof assets

## Current Seeded Reasoning (validate/update)
- Why role exists: {reason.get('why_role_exists', '')}
- Business problem: {reason.get('business_problem', '')}
- Likely team: {reason.get('likely_team', '')}

## Output Format (CSV row for role_reasoning.csv)
reasoning_id, job_id, why_role_exists, business_problem, likely_team,
success_metrics_30, success_metrics_60, success_metrics_90,
how_i_would_help (semicolon-separated), priority_questions (semicolon-separated)
"""


def generate_interview_packet_prompt(
    company_id: str,
    job_id: str,
    jobs_df,
    conversation_type: str = "hiring manager",
) -> str:
    """Generate a comprehensive interview packet research prompt."""
    company = build_company_360(company_id)
    reason = infer_role_reason(job_id, jobs_df)
    company_name = company.get("company_name", "")

    return f"""# Interview Packet Research Prompt

Build a complete interview packet for:
- **Company:** {company_name}
- **Role:** {reason.get('title', job_id)}
- **Conversation Type:** {conversation_type}

## Sections Required
1. Company 360 summary (public sources only)
2. Role intelligence (why role exists, business problem, 30/60/90)
3. People map with TBD placeholders and verification_status
4. Top 3 proof assets to show first (from portfolio)
5. Conversation script tailored to {conversation_type}
6. Optional sponsorship disclosure
7. Technical, business, and behavioral interview topics
8. Follow-up template and next actions

## Portfolio Proof Assets Available
- Career Intelligence OS Dashboard (Streamlit)
- CI OS Case Study
- AI Agent Risk Scoring case study
- Secure Cloud Evidence Lab case study
- Interview packets by role family
- Company packets in company-packets/

## Rules
- CSV-first output where possible
- NO scraping, NO fake names
- Include source URLs
- Mark unverified claims with confidence levels
"""
