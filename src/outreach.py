"""Outreach angle generation by contact type."""

OUTREACH_TEMPLATES: dict[str, str] = {
    "recruiter": (
        "Hi {name}, I'm a recent MIS graduate authorized on OPT/EAD, targeting DFW "
        "{role_cluster} roles. I noticed {company} is hiring for {title} — my background "
        "aligns with {top_skills}. Before applying, could I ask what skills matter most "
        "for this team and whether OPT candidates are considered for this role family?"
    ),
    "hiring_manager": (
        "Hi {name}, I'm mapping DFW teams building cloud/security/data systems and "
        "{company} stood out for {business_problem}. My portfolio includes a job "
        "intelligence system I built using Python, SQL, and Streamlit — directly relevant "
        "to {top_skills}. Could I ask what problem this {title} role is being opened to "
        "solve and what a strong early-career candidate should demonstrate?"
    ),
    "peer": (
        "Hi {name}, I saw you're working on {role_cluster} at {company}. I'm an MIS "
        "graduate building proof around {top_skills} and would value 10 minutes on what "
        "the day-to-day looks like on your team — especially around {business_problem}. "
        "Happy to share what I'm learning from my Career Intelligence OS project."
    ),
    "alumni": (
        "Hi {name}, fellow UNT alum here — I'm targeting enterprise technology roles in "
        "DFW focused on {top_skills}. I noticed {company} has openings around "
        "{business_problem}. Would you be open to a brief chat about how you navigated "
        "the team culture and what skills proved most valuable early on?"
    ),
}

FOLLOW_UP = (
    "Thanks for the context. Based on what you shared, {title} aligns with my work in "
    "{top_skills}. I've built a portfolio project demonstrating SQL/Python analytics and "
    "role-fit scoring — happy to share. Would you be comfortable pointing me to the right "
    "recruiter or confirming if this requisition is actively reviewed?"
)


def _format_skills(matched_categories: list[str], max_skills: int = 3) -> str:
    """Format matched skill categories for outreach copy."""
    labels = {
        "python": "Python automation",
        "sql": "SQL analytics",
        "cloud": "cloud platforms",
        "security": "cloud security & IAM",
        "data_analytics": "data analytics",
        "ai_automation": "AI automation",
        "risk_grc": "risk controls & GRC",
        "business_analysis": "business systems analysis",
    }
    skills = [labels.get(c, c) for c in matched_categories[:max_skills]]
    if not skills:
        return "Python, SQL, and data analytics"
    if len(skills) == 1:
        return skills[0]
    return ", ".join(skills[:-1]) + f", and {skills[-1]}"


def generate_outreach(
    contact_type: str,
    contact_name: str,
    company_name: str,
    job_title: str,
    business_problem: str,
    matched_categories: list[str] | None = None,
    role_cluster: str = "cloud, security, data, and AI automation",
) -> dict[str, str]:
    """Generate outreach message for a contact type."""
    contact_type = contact_type.lower().strip()
    template = OUTREACH_TEMPLATES.get(contact_type, OUTREACH_TEMPLATES["recruiter"])

    top_skills = _format_skills(matched_categories or [])
    first_name = contact_name.split()[-1] if contact_name else "there"
    if first_name.startswith("Sample"):
        first_name = "there"

    message = template.format(
        name=first_name,
        company=company_name,
        title=job_title,
        business_problem=business_problem or "platform modernization and secure automation",
        top_skills=top_skills,
        role_cluster=role_cluster,
    )

    follow_up = FOLLOW_UP.format(
        title=job_title,
        top_skills=top_skills,
    )

    return {
        "contact_type": contact_type,
        "message": message,
        "follow_up": follow_up,
        "angle": f"Lead with {top_skills} proof; reference {business_problem}",
    }


def generate_outreach_batch(jobs_df, contacts_df, scores: list[dict]) -> list[dict]:
    """Generate outreach angles for all contact-job pairings."""
    score_map = {s["job_id"]: s for s in scores}
    results = []

    for _, contact in contacts_df.iterrows():
        company_jobs = jobs_df[jobs_df["company_id"] == contact["company_id"]]
        if company_jobs.empty:
            continue

        best_job = company_jobs.iloc[0]
        for _, job in company_jobs.iterrows():
            job_score = score_map.get(job["job_id"], {})
            if job_score.get("fit_score", 0) >= score_map.get(best_job["job_id"], {}).get("fit_score", 0):
                best_job = job

        score = score_map.get(best_job["job_id"], {})
        outreach = generate_outreach(
            contact_type=contact["contact_type"],
            contact_name=contact.get("name", ""),
            company_name=contact["company_name"],
            job_title=best_job.get("title", ""),
            business_problem=best_job.get("business_problem", ""),
            matched_categories=score.get("matched_categories", []),
        )
        outreach["contact_id"] = contact["contact_id"]
        outreach["company_name"] = contact["company_name"]
        outreach["job_id"] = best_job["job_id"]
        outreach["job_title"] = best_job.get("title", "")
        outreach["fit_score"] = score.get("fit_score", 0)
        results.append(outreach)

    return results
