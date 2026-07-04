"""
Career Intelligence OS — Streamlit Dashboard

Run: streamlit run app/dashboard.py
"""

import sys
from pathlib import Path

# Add project root to path for imports
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import pandas as pd
import streamlit as st

from src.db import DEMO_QUERIES, init_db, run_query
from src.interview import generate_interview_batch
from src.keywords import categorize_keywords, extract_keywords
from src.loader import load_all
from src.outreach import generate_outreach_batch
from src.scoring import UNIVERSAL_PROFILE, score_jobs_dataframe

st.set_page_config(
    page_title="Career Intelligence OS",
    page_icon="🎯",
    layout="wide",
)

st.title("Career Intelligence OS")
st.caption("DFW Enterprise Job Intelligence — AI Automation, Cloud Security & Data Analytics")


@st.cache_data
def load_pipeline():
    """Load data and run full analysis pipeline."""
    data = load_all()
    scores = score_jobs_dataframe(data["jobs"])
    outreach = generate_outreach_batch(data["jobs"], data["contacts"], scores)
    interviews = generate_interview_batch(data["jobs"], scores)
    init_db(data["companies"], data["jobs"], data["contacts"])
    return data, scores, outreach, interviews


data, scores, outreach, interviews = load_pipeline()
companies_df = data["companies"]
jobs_df = data["jobs"]
contacts_df = data["contacts"]
gap_df = data["gap_matrix"]

scores_df = pd.DataFrame([
    {
        "job_id": s["job_id"],
        "company_name": s["company_name"],
        "title": s["title"],
        "fit_score": s["fit_score"],
        "fit_label": s["fit_label"],
        "matched": ", ".join(s["matched_categories"]),
        "gaps": ", ".join(s["gaps"]) if s["gaps"] else "None",
    }
    for s in scores
])

# Sidebar filters
st.sidebar.header("Filters")
tier_filter = st.sidebar.multiselect(
    "Priority Tier",
    options=sorted(jobs_df["priority_tier"].unique()),
    default=sorted(jobs_df["priority_tier"].unique()),
)
company_filter = st.sidebar.selectbox(
    "Company",
    options=["All"] + sorted(companies_df["company_name"].unique()),
)

filtered_jobs = jobs_df[jobs_df["priority_tier"].isin(tier_filter)]
if company_filter != "All":
    filtered_jobs = filtered_jobs[filtered_jobs["company_name"] == company_filter]

filtered_scores = scores_df[scores_df["job_id"].isin(filtered_jobs["job_id"])]

# Tabs
tab_overview, tab_fit, tab_keywords, tab_outreach, tab_interview, tab_sql = st.tabs([
    "Overview", "Job Fit Scores", "Keywords", "Outreach", "Interview Prep", "SQL Analytics",
])

# --- Overview Tab ---
with tab_overview:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Target Companies", len(companies_df))
    col2.metric("Active Jobs", len(jobs_df))
    col3.metric("Contacts", len(contacts_df))
    col4.metric("Avg Fit Score", f"{scores_df['fit_score'].mean():.1f}")

    st.subheader("Universal Profile")
    st.info(UNIVERSAL_PROFILE)

    st.subheader("Portfolio Gap Matrix (P0 Capabilities)")
    p0_gap = gap_df[gap_df["priority"] == "P0"]
    st.dataframe(
        p0_gap[["capability_bucket", "gap_risk", "career_intelligence_os_coverage"]],
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Top Companies by Priority")
    tier1 = companies_df[companies_df["priority_tier"].str.contains("Tier 1")]
    st.dataframe(
        tier1[["rank", "company_name", "location", "industry", "h1b_confidence"]].head(15),
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Role Fit Distribution")
    st.bar_chart(scores_df.groupby("fit_label")["fit_score"].count())

# --- Job Fit Scores Tab ---
with tab_fit:
    st.subheader("Role Fit Scores")
    st.dataframe(
        filtered_scores.sort_values("fit_score", ascending=False),
        use_container_width=True,
        hide_index=True,
    )

    selected_job = st.selectbox(
        "Drill into job",
        options=filtered_scores.sort_values("fit_score", ascending=False)["job_id"].tolist(),
        format_func=lambda jid: f"{jid} — {scores_df[scores_df['job_id']==jid]['title'].values[0]} @ {scores_df[scores_df['job_id']==jid]['company_name'].values[0]}",
    )

    if selected_job:
        score_detail = next(s for s in scores if s["job_id"] == selected_job)
        st.write(f"**Fit Label:** {score_detail['fit_label']} ({score_detail['fit_score']}/100)")

        dim_df = pd.DataFrame([
            {"dimension": k, "score": v}
            for k, v in score_detail["dimension_scores"].items()
        ])
        st.bar_chart(dim_df.set_index("dimension")["score"])

        job_row = jobs_df[jobs_df["job_id"] == selected_job].iloc[0]
        with st.expander("Job Description"):
            st.write(job_row["description"])
        st.write(f"**Business Problem:** {job_row['business_problem']}")

# --- Keywords Tab ---
with tab_keywords:
    st.subheader("Keyword Extraction")
    kw_job = st.selectbox(
        "Select job for keyword analysis",
        options=jobs_df["job_id"].tolist(),
        format_func=lambda jid: f"{jobs_df[jobs_df['job_id']==jid]['title'].values[0]} @ {jobs_df[jobs_df['job_id']==jid]['company_name'].values[0]}",
        key="kw_job",
    )

    if kw_job:
        job_row = jobs_df[jobs_df["job_id"] == kw_job].iloc[0]
        keywords = extract_keywords(job_row["description"], top_n=20)
        categories = categorize_keywords(job_row["description"])

        col_a, col_b = st.columns(2)
        with col_a:
            st.write("**Top Keywords**")
            for kw, count in keywords:
                st.write(f"- {kw} ({count})")
        with col_b:
            st.write("**Categories**")
            for cat, phrases in categories.items():
                st.write(f"**{cat}:** {', '.join(phrases)}")

# --- Outreach Tab ---
with tab_outreach:
    st.subheader("Outreach Angles")
    contact_type_filter = st.multiselect(
        "Contact Type",
        options=["recruiter", "hiring_manager", "peer", "alumni"],
        default=["recruiter", "hiring_manager"],
    )

    filtered_outreach = [o for o in outreach if o["contact_type"] in contact_type_filter]
    if company_filter != "All":
        filtered_outreach = [o for o in filtered_outreach if o["company_name"] == company_filter]

    for item in filtered_outreach[:10]:
        with st.expander(f"{item['company_name']} — {item['contact_type']} (fit: {item['fit_score']})"):
            st.write(f"**Angle:** {item['angle']}")
            st.text_area("Message", item["message"], height=120, key=f"msg_{item['contact_id']}")
            st.caption(f"Follow-up: {item['follow_up']}")

# --- Interview Prep Tab ---
with tab_interview:
    st.subheader("Interview Prep Topics")
    int_job = st.selectbox(
        "Select job",
        options=filtered_scores.sort_values("fit_score", ascending=False)["job_id"].tolist(),
        format_func=lambda jid: f"{scores_df[scores_df['job_id']==jid]['title'].values[0]} @ {scores_df[scores_df['job_id']==jid]['company_name'].values[0]}",
        key="int_job",
    )

    if int_job:
        prep = next(i for i in interviews if i["job_id"] == int_job)
        st.write(f"**{prep['title']}** at {prep['company_name']} — {prep['total_topics']} topics")

        for section, key in [("Technical", "technical_topics"), ("Business Context", "business_topics"), ("Behavioral", "behavioral_topics")]:
            st.write(f"### {section}")
            for topic in prep[key]:
                priority_color = "🔴" if topic["priority"] == "High" else "🟡"
                st.write(f"{priority_color} [{topic['category']}] {topic['question']}")

# --- SQL Analytics Tab ---
with tab_sql:
    st.subheader("SQL Analytics (SQLite Demo)")
    query_name = st.selectbox("Demo Query", options=list(DEMO_QUERIES.keys()))
    st.code(DEMO_QUERIES[query_name], language="sql")

    if st.button("Run Query"):
        results = run_query(DEMO_QUERIES[query_name])
        st.dataframe(pd.DataFrame(results), use_container_width=True, hide_index=True)

    st.caption("Database: data/career_intel.db — auto-initialized from CSV on first load.")
