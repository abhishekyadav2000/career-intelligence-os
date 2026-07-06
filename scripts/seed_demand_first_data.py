#!/usr/bin/env python3
"""Seed Demand First v1.3 data files from sample_jobs and public source URLs."""

from __future__ import annotations

import csv
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import pandas as pd

from src.contact_pod_builder import build_pod_template, save_contact_pods
from src.data_loader import load_core
from src.engagement_engine import (
    generate_hook_from_signal,
    generate_message_draft,
    save_outreach_queue,
)
from src.role_demand_scorer import save_role_demand_scores, score_jobs_dataframe

DATA_DIR = ROOT / "data"
REF = datetime(2026, 7, 6)

COMPANIES_TOP10 = [
    ("C001", "JPMorgan Chase", "Plano / Dallas", "https://careers.jpmorgan.com"),
    ("C002", "Goldman Sachs", "Dallas", "https://www.goldmansachs.com/careers"),
    ("C003", "Bank of America", "Dallas", "https://careers.bankofamerica.com"),
    ("C004", "Citi", "Irving", "https://jobs.citi.com"),
    ("C005", "Charles Schwab", "Westlake / DFW", "https://www.schwabjobs.com"),
    ("C006", "Capital One", "Plano", "https://www.capitalonecareers.com"),
    ("C007", "Toyota Motor North America", "Plano", "https://careers.toyota.com"),
    ("C008", "AT&T", "Dallas / Plano / Irving", "https://www.att.jobs"),
    ("C009", "Ericsson", "Plano", "https://jobs.ericsson.com/careers"),
    ("C010", "NTT DATA", "Plano / Dallas", "https://careers.nttdata.com"),
]

POD_COMPANIES = COMPANIES_TOP10[:5]

DEMAND_SIGNALS = [
    # JPMorgan Chase — full pilot (10+ signals)
    ("DS-C001-01", "C001", "JPMorgan Chase", "job_posting", "Software Engineer Program — Plano TX", "2026-06-28", "Global Technology", "Software Engineering", "Plano, TX", 95, "careers_portal", "https://careers.jpmorgan.com/us/en/students/programs/software-engineer-summer", "high", "2026-07-04", "SEP summer program cites Plano tech hub and Python/Java stack"),
    ("DS-C001-02", "C001", "JPMorgan Chase", "hiring_event", "Design Development Program — Plano tech hub", "2026-06-25", "Global Technology", "UI/UX / Product Design", "Plano, TX", 88, "careers_portal", "https://careers.jpmorgan.com/us/en/students/programs/design-dev-fulltime", "high", "2026-07-04", "Veteran pathway story highlights Plano technology hub"),
    ("DS-C001-03", "C001", "JPMorgan Chase", "press_release", "60,000+ technologists driving innovation", "2026-06-20", "Corporate Technology", "AI / Data / Cloud", "Global / DFW", 90, "careers_portal", "https://careers.jpmorgan.com/about/technology", "high", "2026-07-04", "Official technology careers page — scale and AI themes"),
    ("DS-C001-04", "C001", "JPMorgan Chase", "blog_post", "High-powered tech careers portal", "2026-06-18", "Technology", "Software Engineering / Data Science", "DFW", 85, "careers_portal", "https://careers.jpmorgan.com/professionals", "high", "2026-07-04", "Professionals portal — ML, AI, software engineering hiring"),
    ("DS-C001-05", "C001", "JPMorgan Chase", "transformation_project", "AI productivity platform with governance", "2026-06-15", "Corporate Technology", "AI Automation", "Plano / Dallas", 92, "careers_site", "https://careers.jpmorgan.com/about/technology", "high", "2026-07-04", "AI-driven productivity with governance emphasis"),
    ("DS-C001-06", "C001", "JPMorgan Chase", "product_launch", "Digital banking modernization", "2026-06-10", "Consumer Banking", "Platform Modernization", "DFW", 80, "newsroom", "https://www.jpmorganchase.com/newsroom", "medium", "2026-07-04", "Newsroom themes on digital banking investment"),
    ("DS-C001-07", "C001", "JPMorgan Chase", "leadership_update", "Technology leadership — Global CIO", "2026-05-28", "Executive", "Technology Strategy", "Global", 75, "official_site", "https://www.jpmorganchase.com/about/leadership/lori-beer", "verified_public", "2026-07-04", "Lori Beer — Global CIO on official leadership page"),
    ("DS-C001-08", "C001", "JPMorgan Chase", "webinar", "Explore opportunities — technology lines of business", "2026-06-22", "Campus Recruiting", "Early Career", "Plano, TX", 82, "careers_portal", "https://careers.jpmorgan.com/careers/explore-opportunities", "high", "2026-07-04", "Student and early-career technology pathways"),
    ("DS-C001-09", "C001", "JPMorgan Chase", "job_posting", "Cybersecurity Developer track — SEP", "2026-06-30", "Cybersecurity", "Cloud Security / DevSecOps", "Plano, TX", 94, "careers_portal", "https://careers.jpmorgan.com/us/en/students/programs/software-engineer-summer", "high", "2026-07-04", "Cybersecurity developer opportunity within SEP"),
    ("DS-C001-10", "C001", "JPMorgan Chase", "award", "Plano technology hub recognition", "2026-05-15", "Global Technology", "DFW Tech Hub", "Plano, TX", 78, "careers_site", "https://careers.jpmorgan.com/about/technology", "medium", "2026-07-04", "Plano cited as major US technology hub"),
    ("DS-C001-11", "C001", "JPMorgan Chase", "hiring_event", "CCBSI full-time program — technology scale", "2026-06-12", "Campus", "Data / Technology", "DFW", 80, "careers_portal", "https://careers.jpmorgan.com/global/en/students/programs/ccbsi-fulltime", "high", "2026-07-04", "Campus program page references 60K technologists"),
    ("DS-C001-12", "C001", "JPMorgan Chase", "job_posting", "Site Reliability Engineer — SEP track", "2026-07-01", "Infrastructure", "SRE / Cloud", "Plano, TX", 91, "careers_portal", "https://careers.jpmorgan.com/us/en/students/programs/software-engineer-summer", "high", "2026-07-04", "SRE track within software engineer program"),
    # Goldman Sachs
    ("DS-C002-01", "C002", "Goldman Sachs", "press_release", "Dallas campus expansion — engineering hiring", "2026-06-20", "Engineering", "Software / Data", "Dallas, TX", 88, "careers_portal", "https://www.goldmansachs.com/careers", "high", "2026-07-04", "Major Dallas campus engineering demand"),
    ("DS-C002-02", "C002", "Goldman Sachs", "job_posting", "Technology Analyst — Dallas", "2026-06-25", "Technology", "Analytics / Engineering", "Dallas, TX", 85, "careers_portal", "https://www.goldmansachs.com/careers", "medium", "2026-07-04", "Dallas technology analyst hiring signal"),
    # Bank of America
    ("DS-C003-01", "C003", "Bank of America", "transformation_project", "New Dallas campus technology buildout", "2026-06-18", "Technology", "Platform / Risk", "Dallas, TX", 87, "careers_portal", "https://careers.bankofamerica.com", "high", "2026-07-04", "DFW campus expansion hiring signal"),
    ("DS-C003-02", "C003", "Bank of America", "job_posting", "Platform Engineer — Dallas", "2026-06-28", "Technology", "Cloud / Platform", "Dallas, TX", 84, "careers_portal", "https://careers.bankofamerica.com", "medium", "2026-07-04", "Platform engineering demand in Dallas"),
    # Citi
    ("DS-C004-01", "C004", "Citi", "press_release", "Irving campus — technology and operations", "2026-06-15", "Technology", "Risk / Platform", "Irving, TX", 86, "careers_portal", "https://jobs.citi.com", "high", "2026-07-04", "Irving campus spans technology and global functions"),
    ("DS-C004-02", "C004", "Citi", "job_posting", "AI Automation Analyst — Irving", "2026-06-30", "Technology", "AI / Automation", "Irving, TX", 89, "careers_portal", "https://jobs.citi.com", "high", "2026-07-04", "AI automation analyst demand"),
    # Charles Schwab
    ("DS-C005-01", "C005", "Charles Schwab", "product_launch", "Finance platform modernization — Westlake", "2026-06-22", "Technology", "Cloud / Data", "Westlake, TX", 83, "careers_portal", "https://www.schwabjobs.com", "high", "2026-07-04", "Westlake HQ finance-platform modernization"),
    # Capital One
    ("DS-C006-01", "C006", "Capital One", "blog_post", "Plano technology hub — cloud and data", "2026-06-20", "Technology", "Cloud / Data", "Plano, TX", 88, "careers_portal", "https://www.capitalonecareers.com", "high", "2026-07-04", "Plano cloud/data-heavy employer signal"),
    # Toyota
    ("DS-C007-01", "C007", "Toyota Motor North America", "transformation_project", "Auto platforms — data and cloud demand", "2026-06-18", "Technology", "Cyber / Cloud / Data", "Plano, TX", 82, "careers_portal", "https://careers.toyota.com", "medium", "2026-07-04", "Auto platform modernization hiring"),
    # AT&T
    ("DS-C008-01", "C008", "AT&T", "press_release", "Telecom modernization and AI operations", "2026-06-25", "Technology", "Network / AI / Security", "Dallas, TX", 85, "careers_portal", "https://www.att.jobs", "high", "2026-07-04", "Telecom modernization hiring themes"),
    # Ericsson
    ("DS-C009-01", "C009", "Ericsson", "product_launch", "5G/cloud infrastructure — Plano", "2026-06-20", "Technology", "5G / Cloud", "Plano, TX", 84, "careers_portal", "https://jobs.ericsson.com/careers", "high", "2026-07-04", "5G and cloud infrastructure roles"),
    # NTT DATA
    ("DS-C010-01", "C010", "NTT DATA", "job_posting", "Enterprise modernization consulting — DFW", "2026-06-28", "Consulting", "Cloud / Data", "Plano / Dallas", 80, "careers_portal", "https://careers.nttdata.com", "medium", "2026-07-04", "Consulting delivery and modernization roles"),
]

SIGNAL_COLUMNS = [
    "signal_id", "company_id", "company_name", "signal_type", "signal_title",
    "signal_date", "business_unit", "technology_area", "location", "relevance_score",
    "source_type", "source_url", "confidence_level", "last_verified", "notes",
]

HOOK_COLUMNS = [
    "hook_id", "company_id", "person_id", "hook_type", "hook_title", "hook_content",
    "source_url", "topic", "suggested_opener", "engagement_level", "status", "last_updated",
]

EDGE_COLUMNS = [
    "edge_id", "from_entity", "from_type", "relationship", "to_entity", "to_type",
    "confidence", "source_url",
]


def seed_demand_signals():
    path = DATA_DIR / "company_demand_signals.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(SIGNAL_COLUMNS)
        for row in DEMAND_SIGNALS:
            w.writerow(row)
    print(f"Wrote {len(DEMAND_SIGNALS)} demand signals → {path}")


def seed_role_demand_scores():
    core = load_core(validate=False)
    keywords = core["profile_keywords"]["skill"].tolist()
    scores = score_jobs_dataframe(core["jobs"], core["companies"], keywords, reference=REF)
    save_role_demand_scores(scores)
    tier_a = sum(1 for s in scores if s["fit_tier"] == "A")
    print(f"Wrote {len(scores)} role demand scores ({tier_a} Tier A) → role_demand_scores.csv")


def seed_contact_pods():
    all_pods = []
    for cid, name, loc, _ in POD_COMPANIES:
        all_pods.extend(build_pod_template(cid, name, location=loc))
    save_contact_pods(all_pods)
    print(f"Wrote {len(all_pods)} contact pod slots → contact_pods.csv")


def seed_engagement_hooks():
    hooks = []
    jpm_signals = [s for s in DEMAND_SIGNALS if s[1] == "C001"][:6]
    for sig in jpm_signals:
        signal_dict = dict(zip(SIGNAL_COLUMNS, sig))
        hook = generate_hook_from_signal(signal_dict, None, {"company_name": "JPMorgan Chase"})
        hook["hook_id"] = f"HK-{signal_dict['signal_id']}"
        hooks.append(hook)
    path = DATA_DIR / "engagement_hooks.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=HOOK_COLUMNS, extrasaction="ignore")
        w.writeheader()
        for h in hooks:
            w.writerow({k: h.get(k, "") for k in HOOK_COLUMNS})
    print(f"Wrote {len(hooks)} engagement hooks → {path}")


def seed_outreach_queue():
    from src.contact_pod_builder import get_pod_for_company

    pods = get_pod_for_company("C001")
    hooks_path = DATA_DIR / "engagement_hooks.csv"
    hooks_df = pd.read_csv(hooks_path) if hooks_path.exists() else pd.DataFrame()
    hooks = hooks_df.to_dict("records") if not hooks_df.empty else []

    message_types = ["comment_on_post", "connection_request", "dm_after_connection"]
    queue = []
    qid = 1
    for pod in pods[:5]:
        hook = hooks[(qid - 1) % len(hooks)] if hooks else {}
        for mt in message_types:
            draft = generate_message_draft(pod, hook, mt)
            queue.append({
                "queue_id": f"OQ-{qid:03d}",
                "company_id": "C001",
                "person_id": pod.get("person_id", ""),
                "person_name": pod.get("person_name", ""),
                "person_type": pod.get("person_type", ""),
                "channel": "linkedin",
                "message_type": mt,
                "message_draft": draft,
                "engagement_level": pod.get("engagement_level", 3),
                "hook_id": hook.get("hook_id", ""),
                "status": "draft",
                "next_action": "Review and approve before sending",
                "scheduled_date": "2026-07-07",
                "sent_date": "",
                "notes": f"Demand-first draft for {pod.get('pod_slot', '')}",
            })
            qid += 1
            if qid > 15:
                break
        if qid > 15:
            break

    save_outreach_queue(queue)
    print(f"Wrote {len(queue)} outreach queue drafts → outreach_queue.csv")


def seed_knowledge_graph():
    edges = [
        ("KG-001", "JPMorgan Chase", "company", "HAS_ROLE", "AI Automation Analyst", "role", 0.95, "https://careers.jpmorgan.com"),
        ("KG-002", "JPMorgan Chase", "company", "HAS_ROLE", "Technology Analyst", "role", 0.95, "https://careers.jpmorgan.com"),
        ("KG-003", "JPMorgan Chase", "company", "HAS_ROLE", "Cloud Security Analyst", "role", 0.92, "https://careers.jpmorgan.com"),
        ("KG-004", "AI Automation Analyst", "role", "REQUIRES", "Python", "skill", 0.9, ""),
        ("KG-005", "AI Automation Analyst", "role", "REQUIRES", "SQL", "skill", 0.9, ""),
        ("KG-006", "AI Automation Analyst", "role", "REQUIRES", "AI Automation", "skill", 0.88, ""),
        ("KG-007", "Technology Analyst", "role", "REQUIRES", "Data Analytics", "skill", 0.9, ""),
        ("KG-008", "Technology Analyst", "role", "REQUIRES", "Cloud Security", "skill", 0.85, ""),
        ("KG-009", "Cloud Security Analyst", "role", "REQUIRES", "IAM", "skill", 0.92, ""),
        ("KG-010", "Cloud Security Analyst", "role", "REQUIRES", "SIEM", "skill", 0.88, ""),
        ("KG-011", "Python", "skill", "DEMONSTRATES", "PA001 Career Intelligence OS Dashboard", "proof", 0.9, "dashboard/app.py"),
        ("KG-012", "SQL", "skill", "DEMONSTRATES", "PA001 Career Intelligence OS Dashboard", "proof", 0.88, "dashboard/app.py"),
        ("KG-013", "AI Automation", "skill", "DEMONSTRATES", "PA003 AI Agent Risk Scoring", "proof", 0.92, "case-studies/ai-agent-risk-scoring.md"),
        ("KG-014", "Cloud Security", "skill", "DEMONSTRATES", "PA004 Secure Cloud Evidence Lab", "proof", 0.95, "case-studies/secure-cloud-evidence-lab.md"),
        ("KG-015", "IAM", "skill", "DEMONSTRATES", "PA004 Secure Cloud Evidence Lab", "proof", 0.93, "case-studies/secure-cloud-evidence-lab.md"),
        ("KG-016", "SIEM", "skill", "DEMONSTRATES", "PA004 Secure Cloud Evidence Lab", "proof", 0.9, "case-studies/secure-cloud-evidence-lab.md"),
        ("KG-017", "Data Analytics", "skill", "DEMONSTRATES", "PA001 Career Intelligence OS Dashboard", "proof", 0.87, "dashboard/app.py"),
        ("KG-018", "JPMorgan Chase", "company", "HAS_SIGNAL", "DS-C001-03", "signal", 0.9, "https://careers.jpmorgan.com/about/technology"),
        ("KG-019", "JPMorgan Chase", "company", "HAS_SIGNAL", "DS-C001-09", "signal", 0.92, "https://careers.jpmorgan.com/us/en/students/programs/software-engineer-summer"),
        ("KG-020", "JPMorgan Chase", "company", "TARGETS", "Plano Technology Hub", "location", 0.95, "https://careers.jpmorgan.com/about/technology"),
        ("KG-021", "Goldman Sachs", "company", "HAS_ROLE", "Security Engineer", "role", 0.85, "https://www.goldmansachs.com/careers"),
        ("KG-022", "Bank of America", "company", "HAS_SIGNAL", "DS-C003-01", "signal", 0.85, "https://careers.bankofamerica.com"),
    ]
    path = DATA_DIR / "knowledge_graph_edges.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(EDGE_COLUMNS)
        for row in edges:
            w.writerow(row)
    print(f"Wrote {len(edges)} knowledge graph edges → {path}")


def main():
    seed_demand_signals()
    seed_role_demand_scores()
    seed_contact_pods()
    seed_engagement_hooks()
    seed_outreach_queue()
    seed_knowledge_graph()
    print("Demand First v1.3 seed complete.")


if __name__ == "__main__":
    main()
