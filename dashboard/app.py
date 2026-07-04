"""
Career Intelligence OS — Streamlit Dashboard

Run: streamlit run dashboard/app.py
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import pandas as pd
import streamlit as st

from src.company_priority_scorer import score_companies
from src.conversation_feedback_analyzer import get_dashboard_stats
from src.data_loader import load_all
from src.db import DEMO_QUERIES, init_db, run_query
from src.interview_topic_mapper import generate_interview_batch
from src.keyword_extractor import categorize_keywords, extract_keywords
from src.outreach_angle_generator import generate_outreach_batch
from src.profile_gap_analyzer import analyze_jobs_batch
from src.recommendation_engine import recommend_batch
from src.role_fit_scorer import UNIVERSAL_PROFILE, score_jobs_dataframe

st.set_page_config(
    page_title="Career Intelligence OS",
    page_icon="🎯",
    layout="wide",
)

st.title("Career Intelligence OS")
st.caption("Sponsor-aware career intelligence system for enterprise technology roles.")


@st.cache_data
def load_pipeline():
    data = load_all()
    scores = score_jobs_dataframe(data["jobs"], data["companies"])
    company_scores = score_companies(data["companies"], data["jobs"], data["contacts"])
    recommendations = recommend_batch(scores, company_scores)
    outreach = generate_outreach_batch(data["jobs"], data["contacts"], scores)
    interviews = generate_interview_batch(data["jobs"], scores)
    gaps = analyze_jobs_batch(data["jobs"], scores)
    init_db(data["companies"], data["jobs"], data["contacts"])
    return data, scores, company_scores, recommendations, outreach, interviews, gaps


data, scores, company_scores, recommendations, outreach, interviews, gaps = load_pipeline()
companies_df = data["companies"]
jobs_df = data["jobs"]
contacts_df = data["contacts"]
gap_df = data["gap_matrix"]

scores_df = pd.DataFrame([
    {
        "job_id": s["job_id"],
        "company": s["company_name"],
        "title": s["title"],
        "fit_score": s["fit_score"],
        "fit_label": s["fit_label"],
        "technical_fit": s["category_scores"]["technical_fit"],
        "sponsorship_signal": s["category_scores"]["sponsorship_signal"],
        "dfw_relevance": s["category_scores"]["dfw_relevance"],
        "noise_risk": s["category_scores"]["noise_risk"],
        "matched": ", ".join(s["matched_categories"]),
    }
    for s in scores
])

rec_df = pd.DataFrame(recommendations)
company_rank_df = pd.DataFrame(company_scores)

# Sidebar filters
st.sidebar.header("Filters")
industry_opts = sorted(companies_df["industry"].unique())
industry_filter = st.sidebar.multiselect("Industry", options=industry_opts, default=industry_opts)
company_filter = st.sidebar.selectbox("Company", options=["All"] + sorted(companies_df["company"].unique()))
action_filter = st.sidebar.multiselect(
    "Recommendation",
    options=["apply now", "network first", "research more", "skip/watchlist"],
    default=["apply now", "network first", "research more"],
)

filtered_scores = scores_df.copy()
if company_filter != "All":
    filtered_scores = filtered_scores[filtered_scores["company"] == company_filter]
filtered_scores = filtered_scores[filtered_scores["job_id"].isin(
    rec_df[rec_df["action"].isin(action_filter)]["job_id"]
)]

tabs = st.tabs([
    "Overview", "Company Ranking", "Role Fit", "Sponsorship Signal",
    "Networking Map", "Interview Prep", "Recommendations", "Export",
    "Conversation Feedback",
])

with tabs[0]:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Target Companies", len(companies_df))
    c2.metric("Active Jobs", len(jobs_df))
    c3.metric("Contacts", len(contacts_df))
    c4.metric("Avg Fit Score", f"{scores_df['fit_score'].mean():.1f}")

    st.subheader("Universal Profile")
    st.info(UNIVERSAL_PROFILE)

    if not gap_df.empty:
        st.subheader("Portfolio Gap Matrix (P0)")
        p0 = gap_df[gap_df["priority"] == "P0"] if "priority" in gap_df.columns else gap_df
        st.dataframe(p0, use_container_width=True, hide_index=True)

    st.subheader("Fit Distribution")
    st.bar_chart(scores_df.groupby("fit_label").size())

with tabs[1]:
    st.subheader("Company Priority Ranking")
    st.dataframe(
        company_rank_df[["company", "industry", "location", "priority_score", "priority_label", "job_count", "contact_count"]],
        use_container_width=True, hide_index=True,
    )
    st.bar_chart(company_rank_df.set_index("company")["priority_score"].head(15))

with tabs[2]:
    st.subheader("Role Fit Scores")
    st.dataframe(filtered_scores.sort_values("fit_score", ascending=False), use_container_width=True, hide_index=True)

    selected = st.selectbox(
        "Drill into job",
        options=filtered_scores.sort_values("fit_score", ascending=False)["job_id"].tolist(),
        format_func=lambda jid: f"{scores_df[scores_df['job_id']==jid]['title'].values[0]} @ {scores_df[scores_df['job_id']==jid]['company'].values[0]}",
    )
    if selected:
        detail = next(s for s in scores if s["job_id"] == selected)
        st.write(f"**{detail['fit_label']}** ({detail['fit_score']}/100)")
        cat_df = pd.DataFrame([{"category": k, "score": v} for k, v in detail["category_scores"].items()])
        st.bar_chart(cat_df.set_index("category")["score"])
        job_row = jobs_df[jobs_df["job_id"] == selected].iloc[0]
        with st.expander("Job Description"):
            st.write(job_row["description"])

with tabs[3]:
    st.subheader("Sponsorship Signal Analysis")
    st.warning("Signals are indicative only — not legal certainty. Verify via DOL/USCIS.")
    sponsor_rows = []
    for s in scores:
        sd = s.get("sponsorship_detail", {})
        sponsor_rows.append({
            "company": s["company_name"], "title": s["title"],
            "signal_score": sd.get("score", 0), "label": sd.get("label", ""),
            "disclaimer": sd.get("disclaimer", ""),
        })
    st.dataframe(pd.DataFrame(sponsor_rows).sort_values("signal_score", ascending=False), use_container_width=True, hide_index=True)

with tabs[4]:
    st.subheader("Networking Map")
    contact_type_filter = st.multiselect("Contact Type", options=["recruiter", "hiring_manager", "peer", "alumni"], default=["recruiter", "hiring_manager"])
    filtered_outreach = [o for o in outreach if o["contact_type"] in contact_type_filter]
    if company_filter != "All":
        filtered_outreach = [o for o in filtered_outreach if o["company_name"] == company_filter]
    for item in filtered_outreach[:10]:
        with st.expander(f"{item['company_name']} — {item['contact_type']} (fit: {item['fit_score']})"):
            st.write(f"**Angle:** {item['angle']}")
            st.text_area("Message", item["message"], height=120, key=f"msg_{item['contact_id']}")

with tabs[5]:
    st.subheader("Interview Prep")
    int_job = st.selectbox(
        "Select job",
        options=filtered_scores.sort_values("fit_score", ascending=False)["job_id"].tolist(),
        format_func=lambda jid: f"{scores_df[scores_df['job_id']==jid]['title'].values[0]} @ {scores_df[scores_df['job_id']==jid]['company'].values[0]}",
        key="int_job",
    )
    if int_job:
        prep = next(i for i in interviews if i["job_id"] == int_job)
        for section, key in [("Technical", "technical_topics"), ("Business", "business_topics"), ("Behavioral", "behavioral_topics")]:
            st.write(f"### {section}")
            for topic in prep[key]:
                icon = "🔴" if topic["priority"] == "High" else "🟡"
                st.write(f"{icon} [{topic['category']}] {topic['question']}")

with tabs[6]:
    st.subheader("Action Recommendations")
    st.dataframe(
        rec_df[["company_name", "title", "fit_score", "action", "composite_score", "rationale"]].sort_values("composite_score", ascending=False),
        use_container_width=True, hide_index=True,
    )

with tabs[7]:
    st.subheader("Export & SQL Analytics")
    st.download_button("Download Scores CSV", scores_df.to_csv(index=False), "role_fit_scores.csv", "text/csv")
    st.download_button("Download Recommendations CSV", rec_df.to_csv(index=False), "recommendations.csv", "text/csv")

    st.subheader("SQL Demo")
    query_name = st.selectbox("Demo Query", options=list(DEMO_QUERIES.keys()))
    st.code(DEMO_QUERIES[query_name], language="sql")
    if st.button("Run Query"):
        st.dataframe(pd.DataFrame(run_query(DEMO_QUERIES[query_name])), use_container_width=True, hide_index=True)

with tabs[8]:
    st.subheader("Conversation Feedback Loop")
    st.caption("Rule-based analysis of outreach and interview conversations — no LLM required.")
    feedback = get_dashboard_stats()

    if feedback["total_conversations"] == 0:
        st.info(feedback["summary"])
        st.markdown(
            "Log conversations in `data/conversation_log_template.csv` with fields: "
            "date, company, person_type, role_discussed, source, outreach_status, "
            "response, insight_gained, portfolio_gap, next_action, follow_up_date."
        )
    else:
        c1, c2, c3 = st.columns(3)
        c1.metric("Conversations Logged", feedback["total_conversations"])
        c2.metric("Warm Companies", len(feedback["warm_companies"]))
        c3.metric("Objection Themes", len(feedback["repeated_objections"]))
        st.write(f"**Summary:** {feedback['summary']}")

        col_a, col_b = st.columns(2)
        with col_a:
            st.write("**Warm Companies**")
            if feedback["warm_companies"]:
                st.dataframe(pd.DataFrame({"company": feedback["warm_companies"]}), hide_index=True)
            else:
                st.write("None yet — keep networking.")
        with col_b:
            st.write("**Repeated Objections**")
            if feedback["repeated_objections"]:
                st.dataframe(pd.DataFrame(feedback["repeated_objections"]), hide_index=True)
            else:
                st.write("No objection patterns detected.")

        st.write("**Skill / Portfolio Gaps**")
        if feedback["skill_gaps"]:
            st.dataframe(pd.DataFrame(feedback["skill_gaps"]), hide_index=True)
        else:
            st.write("No gaps logged yet.")

        st.write("**Next Actions**")
        if feedback["next_actions"]:
            st.dataframe(pd.DataFrame(feedback["next_actions"]), hide_index=True)
        else:
            st.write("No pending actions.")

        if feedback["portfolio_improvements"]:
            st.write("**Portfolio Improvements Suggested**")
            st.dataframe(pd.DataFrame(feedback["portfolio_improvements"]), hide_index=True)
