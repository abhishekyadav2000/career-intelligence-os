"""Interview prep topic generation from job descriptions."""

from src.keyword_extractor import SKILL_TAXONOMY, categorize_keywords

INTERVIEW_TOPIC_BANK: dict[str, list[str]] = {
    "python": [
        "Describe a Python automation script you built. How did you handle errors and logging?",
        "How would you design a data cleaning pipeline using pandas?",
        "Explain how you'd integrate Python with SQL for an ETL workflow.",
    ],
    "sql": [
        "Write a query to find top-performing teams using window functions.",
        "How do you optimize a slow JOIN across large tables?",
        "Explain CTEs vs subqueries — when do you use each?",
    ],
    "cloud": [
        "Walk through a secure cloud architecture: IAM, networking, monitoring, cost.",
        "How do Kubernetes deployments differ from Docker Compose for production?",
        "Explain Infrastructure-as-Code with Terraform — state, modules, drift.",
    ],
    "security": [
        "How would you design IAM with least privilege for a multi-team cloud app?",
        "Describe your approach to SIEM alert tuning and false-positive reduction.",
        "Walk through an incident response lifecycle for a suspected credential breach.",
    ],
    "data_analytics": [
        "How do you define KPIs for an operational dashboard?",
        "Describe a time you used data to influence a business decision.",
        "What's your process for data quality validation before reporting?",
    ],
    "ai_automation": [
        "How do you evaluate whether an AI workflow is production-ready?",
        "Describe guardrails you'd add to an LLM-powered automation pipeline.",
        "What's the difference between RAG and fine-tuning for enterprise use cases?",
    ],
    "risk_grc": [
        "How do you map NIST CSF controls to a cloud application?",
        "What evidence would you collect for a SOC 2 access control audit?",
        "Explain how you'd build and maintain a technology risk register.",
    ],
    "business_analysis": [
        "How do you translate stakeholder needs into user stories with acceptance criteria?",
        "Describe a process you mapped from manual to automated — what changed?",
        "How do you prioritize backlog items when stakeholders disagree?",
    ],
}

BEHAVIORAL_TOPICS = [
    "Tell me about a time you automated a manual workflow and measured the impact.",
    "Describe a situation where you had to explain a technical risk to a non-technical stakeholder.",
    "How do you stay current on cloud security and AI automation trends?",
    "Tell me about a project where data quality issues blocked your analysis — how did you resolve it?",
]


def generate_interview_topics(
    description: str,
    title: str = "",
    business_problem: str = "",
    matched_categories: list[str] | None = None,
    max_per_category: int = 2,
) -> dict:
    categories = categorize_keywords(f"{title} {description}")
    if matched_categories:
        for cat in matched_categories:
            if cat not in categories:
                categories[cat] = SKILL_TAXONOMY.get(cat, [])[:1]

    technical_topics = []
    for category in categories:
        for q in INTERVIEW_TOPIC_BANK.get(category, [])[:max_per_category]:
            technical_topics.append({
                "category": category,
                "question": q,
                "priority": "High" if category in ("security", "python", "sql", "ai_automation") else "Medium",
            })

    problem_topics = []
    if business_problem:
        problem_topics.extend([
            {"category": "business_context", "question": f"How would you approach solving: {business_problem}?", "priority": "High"},
            {"category": "business_context", "question": f"What metrics would you track to show progress on {business_problem}?", "priority": "Medium"},
        ])

    behavioral = [{"category": "behavioral", "question": q, "priority": "High"} for q in BEHAVIORAL_TOPICS[:3]]

    return {
        "technical_topics": technical_topics,
        "business_topics": problem_topics,
        "behavioral_topics": behavioral,
        "total_topics": len(technical_topics) + len(problem_topics) + len(behavioral),
        "categories_covered": list(categories.keys()),
    }


def generate_interview_topics_for_job(job_id: str, jobs_df) -> dict:
    """Generate interview topics for a single job by ID."""
    job_rows = jobs_df[jobs_df["job_id"] == job_id]
    if job_rows.empty:
        return {"technical_topics": [], "business_topics": [], "behavioral_topics": [], "total_topics": 0}
    job = job_rows.iloc[0]
    topics = generate_interview_topics(
        description=job.get("description", ""),
        title=job.get("title", ""),
        business_problem=job.get("business_problem", ""),
    )
    topics["job_id"] = job_id
    topics["company_name"] = job.get("company_name", job.get("company", ""))
    topics["title"] = job.get("title", "")
    return topics


def generate_interview_batch(jobs_df, scores: list[dict]) -> list[dict]:
    score_map = {s["job_id"]: s for s in scores}
    results = []
    for _, job in jobs_df.iterrows():
        score = score_map.get(job["job_id"], {})
        topics = generate_interview_topics(
            description=job.get("description", ""),
            title=job.get("title", ""),
            business_problem=job.get("business_problem", ""),
            matched_categories=score.get("matched_categories", []),
        )
        topics["job_id"] = job["job_id"]
        topics["company_name"] = job["company_name"]
        topics["title"] = job["title"]
        topics["fit_score"] = score.get("fit_score", 0)
        results.append(topics)
    return results
