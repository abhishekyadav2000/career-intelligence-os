"""Interview Practice Simulator — rule-based + optional LLM recruiter practice."""

from __future__ import annotations

import csv
import os
import random
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
PACKETS_DIR = ROOT / "company-packets"
PROMPTS_DIR = ROOT / "prompts"

INSIGHTS_PATH = DATA_DIR / "interview_insights.csv"
SESSIONS_PATH = DATA_DIR / "simulator_sessions.csv"
JOURNEY_PATH = DATA_DIR / "interview_journey.csv"

ROUND_SCRIPT = [
    {"round": "recruiter_screen", "label": "Recruiter Screen", "order": 1},
    {"round": "hm_screen", "label": "Hiring Manager Screen", "order": 2},
    {"round": "technical", "label": "Technical Interview", "order": 3},
    {"round": "behavioral", "label": "Behavioral Interview", "order": 4},
    {"round": "final", "label": "Final Round", "order": 5},
]

ROUND_ALIASES = {
    "recruiter": "recruiter_screen",
    "recruiter screen": "recruiter_screen",
    "recruiter_screen": "recruiter_screen",
    "hm": "hm_screen",
    "hiring manager": "hm_screen",
    "hiring manager screen": "hm_screen",
    "hm_screen": "hm_screen",
    "technical": "technical",
    "technical interview": "technical",
    "behavioral": "behavioral",
    "behavioral interview": "behavioral",
    "final": "final",
    "final round": "final",
}

SESSION_COLUMNS = [
    "session_id",
    "date",
    "company_id",
    "company_name",
    "job_id",
    "role_family",
    "round",
    "questions_asked",
    "notes",
]


def _slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug or "company"


def load_interview_insights(
    company_id: str | None = None,
    role_family: str | None = None,
    round_name: str | None = None,
) -> list[dict]:
    """Load verified interview insights from CSV with optional filters."""
    if not INSIGHTS_PATH.exists():
        return []

    df = pd.read_csv(INSIGHTS_PATH)
    if company_id:
        df = df[df["company_id"] == company_id]
    if role_family:
        rf = role_family.lower()
        df = df[
            df["role_family"].str.lower().str.contains(rf.split("/")[0].strip(), na=False)
            | df["role_family"].str.lower().eq("all")
        ]
    if round_name:
        normalized = normalize_round(round_name)
        df = df[df["interview_round"].apply(normalize_round) == normalized]

    return df.to_dict("records")


def normalize_round(round_name: str) -> str:
    key = (round_name or "").lower().strip().replace("-", " ")
    return ROUND_ALIASES.get(key, key.replace(" ", "_"))


def get_round_script(company: str, role_family: str) -> list[dict]:
    """Return ordered interview rounds for a company/role journey."""
    return [{**r, "company": company, "role_family": role_family} for r in ROUND_SCRIPT]


def load_company_packet(company_name: str) -> str:
    """Load markdown company packet if available."""
    path = PACKETS_DIR / f"{_slugify(company_name)}.md"
    if path.exists():
        return path.read_text(encoding="utf-8")
    for candidate in PACKETS_DIR.glob("*.md"):
        if company_name.lower().replace(" ", "") in candidate.stem.replace("-", ""):
            return candidate.read_text(encoding="utf-8")
    return ""


def load_role_reasoning_snippet(job_id: str, jobs_df: pd.DataFrame, reasoning_df: pd.DataFrame) -> str:
    if reasoning_df.empty or not job_id:
        return ""
    row = reasoning_df[reasoning_df["job_id"] == job_id]
    if row.empty:
        return ""
    rec = row.iloc[0]
    parts = []
    for field in ("day_30_focus", "day_60_focus", "day_90_focus", "key_skills"):
        val = rec.get(field, "")
        if val and str(val).strip():
            parts.append(f"{field}: {val}")
    return " | ".join(parts[:4])


def build_simulator_context(
    company: dict,
    job: dict | None,
    profile: dict,
    insights: list[dict],
    proof_assets: list[dict],
    *,
    reasoning_df: pd.DataFrame | None = None,
    jobs_df: pd.DataFrame | None = None,
) -> dict[str, Any]:
    """Assemble full context for simulator UI and question generation."""
    from src.profile_manager import get_profile_for_simulator

    sim_profile = get_profile_for_simulator(profile)
    company_name = company.get("company_name", company.get("company", ""))
    company_id = company.get("company_id", "")
    job_id = job.get("job_id", "") if job else ""
    role_family = job.get("role_family", "Technology Analyst") if job else "Technology Analyst"

    packet = load_company_packet(company_name)
    reasoning = ""
    if reasoning_df is not None and jobs_df is not None and job_id:
        reasoning = load_role_reasoning_snippet(job_id, jobs_df, reasoning_df)

    themes = company.get("strategic_summary", company.get("current_strategic_themes", ""))
    if isinstance(themes, str) and len(themes) > 300:
        themes = themes[:300] + "…"

    return {
        "company_id": company_id,
        "company_name": company_name,
        "job_id": job_id,
        "job_title": job.get("title", "") if job else "",
        "role_family": role_family,
        "company_themes": themes,
        "company_packet_excerpt": packet[:2000] if packet else "",
        "role_reasoning": reasoning,
        "profile": sim_profile,
        "experience_bullets": sim_profile.get("experience_bullets", []),
        "insights": insights,
        "proof_assets": proof_assets[:5],
        "verified_question_count": len(insights),
    }


def _pick_insight_question(
    insights: list[dict],
    history: list[dict],
    round_name: str,
) -> dict | None:
    asked_ids = {h.get("insight_id") for h in history if h.get("insight_id")}
    pool = [i for i in insights if i.get("insight_id") not in asked_ids and i.get("source_url")]
    if not pool:
        pool = [i for i in insights if i.get("source_url")]
    if not pool:
        return None
    normalized = normalize_round(round_name)
    round_pool = [i for i in pool if normalize_round(i.get("interview_round", "")) == normalized]
    if round_pool:
        return random.choice(round_pool)
    return random.choice(pool)


def generate_recruiter_question(
    context: dict,
    round_name: str,
    history: list[dict] | None = None,
) -> str:
    """Generate next recruiter question — LLM if configured, else rule-based from insights."""
    history = history or []
    insights = context.get("insights", [])
    question_row = _pick_insight_question(insights, history, round_name)

    llm = _try_llm_question(context, round_name, history, question_row)
    if llm:
        return llm

    if question_row:
        return question_row.get("question_or_topic", "Tell me about yourself and your interest in this role.")

    return _fallback_question(round_name, context)


def _fallback_question(round_name: str, context: dict) -> str:
    company = context.get("company_name", "the company")
    title = context.get("job_title", "this role")
    normalized = normalize_round(round_name)
    profile = context.get("profile", {})
    bullets = context.get("experience_bullets") or profile.get("experience_bullets", [])
    bullet_hint = bullets[0][:80] if bullets else "a recent project from your portfolio"
    headline = profile.get("headline", "your background")

    fallbacks = {
        "recruiter_screen": (
            f"Tell me about yourself and why you're interested in {title} at {company}. "
            f"(Hint: lead with your headline — {headline})"
        ),
        "hm_screen": (
            f"Walk me through a project that best demonstrates your fit for {title}. "
            f"(Consider: {bullet_hint})"
        ),
        "technical": (
            "Describe how you would approach a data pipeline or automation task using your core technical skills. "
            f"Reference a real example if possible — e.g. {bullet_hint}."
        ),
        "behavioral": (
            "Tell me about a time you had to learn a new technology quickly to deliver on a deadline. "
            "Use STAR format with a specific situation from your experience."
        ),
        "final": (
            f"Why {company}, and where do you see yourself contributing in the first 90 days?"
        ),
    }
    return fallbacks.get(normalized, fallbacks["recruiter_screen"])


def generate_feedback(
    user_answer: str,
    question: str,
    context: dict,
    insight_row: dict | None = None,
) -> str:
    """Generate brief feedback — LLM if configured, else rule-based."""
    llm = _try_llm_feedback(user_answer, question, context, insight_row)
    if llm:
        return llm
    return _rule_based_feedback(user_answer, question, context, insight_row)


def _rule_based_feedback(
    user_answer: str,
    question: str,
    context: dict,
    insight_row: dict | None = None,
) -> str:
    answer = (user_answer or "").strip()
    word_count = len(answer.split())
    star_stories = context.get("profile", {}).get("star_stories", [])
    suggested_star = _suggest_star_story(question, star_stories)

    parts = []
    if word_count < 30:
        parts.append(
            "**Feedback:** Your answer is too brief — expand with a concrete example and measurable outcome."
        )
    elif word_count > 250:
        parts.append(
            "**Feedback:** Good detail, but tighten to 90–120 seconds — lead with the headline, then STAR."
        )
    else:
        parts.append("**Feedback:** Solid structure — add one quantified result to strengthen impact.")

    if "tell me about yourself" in question.lower():
        parts.append(
            "**Improve:** Open with your headline, 2 proof points, and why this company/role now."
        )
    elif any(k in question.lower() for k in ("technical", "sql", "python", "cloud", "security")):
        parts.append(
            "**Improve:** State your approach first, then tools, then trade-offs and validation steps."
        )
    else:
        parts.append("**Improve:** Use STAR — Situation, Task, Action, Result — in that order.")

    if suggested_star:
        parts.append(f"**STAR story to use:** {suggested_star.get('title', '')} ({suggested_star.get('id', '')})")

    proof = context.get("proof_assets", [])
    if proof and word_count >= 30:
        parts.append(f"**Proof to mention:** {proof[0].get('title', '')}")

    if insight_row and insight_row.get("source_url"):
        parts.append(f"*Question sourced from verified insight: {insight_row.get('source_title', 'public source')}*")

    return "\n\n".join(parts)


def _suggest_star_story(question: str, stories: list[dict]) -> dict | None:
    if not stories:
        return None
    q = question.lower()
    for story in stories:
        tags = " ".join(story.get("tags", [])).lower()
        if any(t in q for t in tags.split()):
            return story
    if any(k in q for k in ("security", "cloud", "iam", "siem")):
        for story in stories:
            if "security" in " ".join(story.get("tags", [])).lower():
                return story
    if any(k in q for k in ("ai", "automation", "agent")):
        for story in stories:
            if "ai" in " ".join(story.get("tags", [])).lower():
                return story
    return stories[0]


def _llm_configured() -> bool:
    return bool(os.getenv("OLLAMA_BASE_URL") or os.getenv("OPENAI_API_KEY"))


def _try_llm_question(
    context: dict,
    round_name: str,
    history: list[dict],
    insight_row: dict | None,
) -> str | None:
    if not _llm_configured() or not insight_row:
        return None
    prompt = (
        f"Ask ONE interview question for round '{round_name}' based on this verified topic: "
        f"{insight_row.get('question_or_topic', '')}. "
        f"Company: {context.get('company_name')}. Role: {context.get('job_title')}."
    )
    return _call_llm(prompt, system=_load_round_prompt(round_name))


def _try_llm_feedback(
    user_answer: str,
    question: str,
    context: dict,
    insight_row: dict | None,
) -> str | None:
    if not _llm_configured():
        return None
    prompt = (
        f"Question: {question}\nCandidate answer: {user_answer}\n"
        f"Give brief feedback (2-3 sentences), one improvement, and STAR story suggestion."
    )
    return _call_llm(prompt, system=_load_round_prompt(context.get("round", "recruiter_screen")))


def _load_round_prompt(round_name: str) -> str:
    path = PROMPTS_DIR / "interview-simulator-agent.md"
    if not path.exists():
        return "You are a professional enterprise recruiter."
    text = path.read_text(encoding="utf-8")
    normalized = normalize_round(round_name)
    section_map = {
        "recruiter_screen": "Recruiter Screen",
        "hm_screen": "Hiring Manager Screen",
        "technical": "Technical Interview",
        "behavioral": "Behavioral Interview",
        "final": "Final Round",
    }
    section = section_map.get(normalized, "Recruiter Screen")
    if f"## {section}" in text:
        start = text.index(f"## {section}")
        end = text.find("\n## ", start + 1)
        return text[start:end] if end > 0 else text[start:]
    return text[:1500]


def _call_llm(prompt: str, system: str = "") -> str | None:
    try:
        if os.getenv("OPENAI_API_KEY"):
            return _call_openai(prompt, system)
        if os.getenv("OLLAMA_BASE_URL"):
            return _call_ollama(prompt, system)
    except Exception:
        return None
    return None


def _call_openai(prompt: str, system: str) -> str | None:
    import urllib.request
    import json

    base = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    url = f"{base.rstrip('/')}/chat/completions"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system or "You are a professional recruiter."},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": 400,
        "temperature": 0.7,
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode())
    return data["choices"][0]["message"]["content"].strip()


def _call_ollama(prompt: str, system: str) -> str | None:
    import urllib.request
    import json

    base = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    model = os.getenv("OLLAMA_MODEL", "llama3.2")
    url = f"{base.rstrip('/')}/api/chat"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system or "You are a professional recruiter."},
            {"role": "user", "content": prompt},
        ],
        "stream": False,
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode())
    return data.get("message", {}).get("content", "").strip()


def load_interview_journey(company_id: str | None = None, job_id: str | None = None) -> list[dict]:
    if not JOURNEY_PATH.exists():
        return []
    df = pd.read_csv(JOURNEY_PATH)
    if company_id:
        df = df[df["company_id"] == company_id]
    if job_id:
        df = df[df["job_id"] == job_id]
    return df.to_dict("records")


def save_simulator_session(
    company_id: str,
    company_name: str,
    job_id: str,
    role_family: str,
    round_name: str,
    questions_asked: list[str],
    notes: str = "",
) -> str:
    """Append session to simulator_sessions.csv."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    session_id = f"SIM-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    row = {
        "session_id": session_id,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "company_id": company_id,
        "company_name": company_name,
        "job_id": job_id,
        "role_family": role_family,
        "round": normalize_round(round_name),
        "questions_asked": " | ".join(questions_asked),
        "notes": notes,
    }
    write_header = not SESSIONS_PATH.exists()
    with open(SESSIONS_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=SESSION_COLUMNS)
        if write_header:
            writer.writeheader()
        writer.writerow(row)
    return session_id


def count_insights_by_company() -> dict[str, int]:
    if not INSIGHTS_PATH.exists():
        return {}
    df = pd.read_csv(INSIGHTS_PATH)
    return df.groupby("company_name").size().to_dict()
