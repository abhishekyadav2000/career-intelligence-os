"""Keyword extraction from job descriptions."""

import re
from collections import Counter

# Skill taxonomy mapped to DFW top-50 workbook keywords
SKILL_TAXONOMY: dict[str, list[str]] = {
    "python": ["python", "pandas", "etl", "scripting", "automation"],
    "sql": ["sql", "database", "queries", "joins", "cte", "window function"],
    "cloud": ["aws", "azure", "gcp", "cloud", "kubernetes", "docker", "terraform", "vpc", "vnet"],
    "security": ["iam", "siem", "splunk", "sentinel", "zero trust", "mfa", "rbac", "least privilege", "incident response", "cybersecurity", "security"],
    "data_analytics": ["data pipeline", "data pipelines", "analytics", "dashboard", "kpi", "metrics", "visualization", "tableau", "power bi"],
    "ai_automation": ["ai", "automation", "machine learning", "ml", "llm", "rag", "prompt", "workflow"],
    "risk_grc": ["risk", "controls", "grc", "compliance", "audit", "sox", "nist", "soc 2", "iso 27001", "evidence"],
    "business_analysis": ["requirements", "stakeholder", "business analysis", "user stories", "process", "agile", "jira"],
}

STOP_WORDS = {
    "the", "and", "for", "with", "you", "will", "our", "are", "this", "that",
    "have", "from", "your", "into", "including", "across", "support", "role",
    "team", "work", "using", "must", "required", "preferred", "experience",
}


def _tokenize(text: str) -> list[str]:
    """Lowercase tokenization with basic cleanup."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s/\-]", " ", text)
    return [t for t in text.split() if len(t) > 2 and t not in STOP_WORDS]


def extract_keywords(text: str, top_n: int = 15) -> list[tuple[str, int]]:
    """Extract top keywords from job description text."""
    if not text or not isinstance(text, str):
        return []

    text_lower = text.lower()
    counts: Counter[str] = Counter()

    # Phrase matches from taxonomy (multi-word)
    for category, phrases in SKILL_TAXONOMY.items():
        for phrase in phrases:
            if phrase in text_lower:
                counts[phrase] += text_lower.count(phrase)

    # Single-token frequency
    for token in _tokenize(text):
        counts[token] += 1

    return counts.most_common(top_n)


def categorize_keywords(text: str) -> dict[str, list[str]]:
    """Group matched keywords into capability buckets."""
    text_lower = text.lower() if text else ""
    result: dict[str, list[str]] = {}

    for category, phrases in SKILL_TAXONOMY.items():
        matched = [p for p in phrases if p in text_lower]
        if matched:
            result[category] = matched

    return result


def keyword_summary(text: str) -> dict:
    """Full keyword analysis for a job description."""
    keywords = extract_keywords(text)
    categories = categorize_keywords(text)
    return {
        "top_keywords": keywords,
        "categories": categories,
        "category_count": len(categories),
        "keyword_density": sum(c for _, c in keywords),
    }
