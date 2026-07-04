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
from src.company_profile_engine import build_company_360, get_company_research_gaps, load_company_profiles
from src.conversation_brief_generator import (
    export_brief_markdown,
    generate_conversation_brief,
    save_conversation_brief,
)
from src.conversation_feedback_analyzer import get_dashboard_stats
from src.data_loader import load_all
from src.db import DEMO_QUERIES, init_db, run_query
from src.interview_topic_mapper import generate_interview_batch
from src.keyword_extractor import categorize_keywords, extract_keywords
from src.outreach_angle_generator import generate_outreach_batch
from src.people_power_mapper import build_people_map, rank_contacts_for_conversation, load_people_map
from src.profile_gap_analyzer import analyze_jobs_batch
from src.proof_asset_mapper import (
    get_top_proof_assets_for_display,
    identify_missing_proof,
    load_proof_assets,
    match_assets_to_company,
    match_assets_to_role,
)
from src.recommendation_engine import recommend_batch
from src.research_prompt_generator import (
    generate_company_research_prompt,
    generate_interview_packet_prompt,
    generate_people_research_prompt,
    generate_role_research_prompt,
)
from src.role_fit_scorer import UNIVERSAL_PROFILE, score_jobs_dataframe
from src.role_reasoning_engine import build_role_deep_dive, load_role_reasoning

st.set_page_config(
    page_title="Career Intelligence OS",
    page_icon="🎯",
    layout="wide",
)

st.title("Career Intelligence OS")
st.caption("Sponsor-aware career intelligence system for enterprise technology roles.")

ICC_COMPANIES = ["JPMorgan Chase", "Citi", "Capital One", "Toyota Motor North America", "AT&T"]
CONVERSATION_TYPES = ["recruiter", "hiring manager", "peer", "alumni", "informational"]
INTERVIEW_STAGES = [
    "initial outreach", "recruiter screen", "hiring manager screen",
    "technical interview", "final round", "follow-up",
]
VERIFY_COLORS = {"verified": "🟢", "partial": "🟡", "placeholder": "⚪"}


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
profiles_df = data.get("company_profiles", load_company_profiles())
people_df = data.get("people_map", load_people_map())
proof_df = data.get("proof_assets", load_proof_assets())
reasoning_df = data.get("role_reasoning", load_role_reasoning())
projects_df = data.get("company_projects", pd.DataFrame())
sources_df = data.get("research_sources", pd.DataFrame())

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

# Sidebar filters (existing)
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

# Global Interview Command Center selectors (shared across ICC tabs)
st.subheader("Interview Command Center — Global Selection")
icc_col1, icc_col2, icc_col3, icc_col4 = st.columns(4)

with icc_col1:
    icc_company_name = st.selectbox(
        "Target Company",
        options=ICC_COMPANIES,
        index=0,
        key="icc_company",
    )
with icc_col2:
    company_jobs = jobs_df[jobs_df["company_name"] == icc_company_name].sort_values("title")
    icc_job_options = company_jobs["job_id"].tolist()
    icc_job_id = st.selectbox(
        "Target Role",
        options=icc_job_options,
        format_func=lambda jid: f"{jobs_df[jobs_df['job_id']==jid]['title'].values[0]} ({jid})",
        key="icc_job",
    )
with icc_col3:
    icc_conversation_type = st.selectbox(
        "Conversation Type",
        options=CONVERSATION_TYPES,
        index=1,
        key="icc_conv_type",
    )
with icc_col4:
    icc_interview_stage = st.selectbox(
        "Interview Stage",
        options=INTERVIEW_STAGES,
        index=2,
        key="icc_stage",
    )

icc_company_row = companies_df[companies_df["company_name"] == icc_company_name]
icc_company_id = icc_company_row.iloc[0]["company_id"] if not icc_company_row.empty else ""
icc_job_row = jobs_df[jobs_df["job_id"] == icc_job_id].iloc[0] if icc_job_id else None

if "current_brief" not in st.session_state:
    st.session_state.current_brief = None
if "brief_markdown" not in st.session_state:
    st.session_state.brief_markdown = ""

tabs = st.tabs([
    "Interview Command Center",
    "Company 360",
    "People Map",
    "Role Deep Dive",
    "Proof Assets",
    "Overview",
    "Company Ranking",
    "Role Fit",
    "Sponsorship Signal",
    "Networking Map",
    "Interview Prep",
    "Recommendations",
    "Export",
    "Conversation Feedback",
])

# ── Tab 0: Interview Command Center ──────────────────────────────────────────
with tabs[0]:
    st.subheader("Interview Command Center")
    st.caption(
        f"**{icc_company_name}** · **{icc_job_row['title'] if icc_job_row is not None else 'N/A'}** · "
        f"{icc_conversation_type} · {icc_interview_stage}"
    )

    btn_col1, btn_col2, btn_col3 = st.columns(3)
    with btn_col1:
        if st.button("Generate Brief", type="primary", key="gen_brief"):
            st.session_state.current_brief = generate_conversation_brief(
                icc_company_id, icc_job_id, jobs_df,
                icc_conversation_type, icc_interview_stage,
            )
            st.session_state.brief_markdown = export_brief_markdown(st.session_state.current_brief)
            st.success(f"Brief {st.session_state.current_brief['brief_id']} generated.")
    with btn_col2:
        if st.button("Save Brief", key="save_brief"):
            if st.session_state.current_brief:
                path = save_conversation_brief(
                    st.session_state.current_brief,
                    st.session_state.brief_markdown,
                )
                st.success(f"Saved to {path} and conversation_briefs.csv")
            else:
                st.warning("Generate a brief first.")
    with btn_col3:
        if st.session_state.brief_markdown:
            st.download_button(
                "Export Brief as Markdown",
                st.session_state.brief_markdown,
                file_name=f"brief_{icc_job_id}_{icc_conversation_type.replace(' ', '_')}.md",
                mime="text/markdown",
                key="dl_brief",
            )

    brief = st.session_state.current_brief
    if brief:
        sec = brief["sections"]
        st.markdown("---")

        st.markdown("### 1. Company 360")
        c360 = sec["company_360"]
        c1, c2, c3 = st.columns(3)
        c1.metric("Industry", c360.get("industry", ""))
        c2.metric("DFW Presence", c360.get("dfw_presence", "")[:30])
        c3.metric("Priority", c360.get("priority_tier", ""))
        st.write(c360.get("strategic_summary", ""))
        if c360.get("themes"):
            st.write("**Active Themes:**", ", ".join(t["theme"] for t in c360["themes"][:5]))

        st.markdown("### 2. Role Intelligence")
        role = sec["role_intelligence"]
        st.write(f"**Why role exists:** {role.get('why_role_exists', '')}")
        st.write(f"**Business problem:** {role.get('business_problem', '')}")
        st.write(f"**Likely team:** {role.get('likely_team', '')}")

        st.markdown("### 3. People / Power Map")
        for person in sec["people_power_map"][:4]:
            icon = VERIFY_COLORS.get(person.get("verification_status", "placeholder"), "⚪")
            st.write(
                f"{icon} **{person.get('person_name')}** ({person.get('contact_type')}) — "
                f"priority {person.get('conversation_priority', 0)}"
            )

        st.markdown("### 4. Proof-of-Work Match")
        for asset in sec["proof_of_work_match"].get("top_three_display", []):
            st.write(f"- **{asset['title']}** (match: {asset['match_score']}) — `{asset['url_or_path']}`")

        st.markdown("### 5. Conversation Script")
        st.info(sec["conversation_script"])

        st.markdown("### 6. Interview Prep")
        prep = sec.get("interview_prep", {})
        for label, key in [("Technical", "technical_topics"), ("Business", "business_topics"), ("Behavioral", "behavioral_topics")]:
            topics = prep.get(key, [])
            if topics:
                st.write(f"**{label}:**")
                for t in topics[:2]:
                    st.write(f"- [{t.get('priority', '')}] {t.get('question', '')}")

        st.markdown("### 7. Action Plan")
        st.write("**Follow-up:**")
        st.text(sec["action_plan"]["follow_up"])
        st.write("**Next actions:**")
        for action in sec["action_plan"]["next_actions"]:
            st.write(f"- [ ] {action}")

        with st.expander("Full Markdown Preview"):
            st.markdown(st.session_state.brief_markdown)
    else:
        st.info("Click **Generate Brief** to build a full 7-section conversation package.")

# ── Tab 1: Company 360 ───────────────────────────────────────────────────────
with tabs[1]:
    st.subheader(f"Company 360 — {icc_company_name}")
    c360 = build_company_360(icc_company_id, profiles_df, projects_df, sources_df, people_df)

    if c360.get("found"):
        st.write(f"**Strategic Summary:** {c360['strategic_summary']}")
        st.write(f"**Growth Signals:** {c360['growth_signals']}")
        st.write(f"**Risk Factors:** {c360['risk_factors']}")
        st.write(f"**Sponsorship Context:** {c360['sponsorship_context']}")

        st.markdown("#### Tech Stack Themes")
        st.write(", ".join(c360["tech_stack_themes"]))

        st.markdown("#### Active Projects")
        proj_subset = projects_df[projects_df["company_id"] == icc_company_id]
        if not proj_subset.empty:
            st.dataframe(proj_subset[["theme", "description", "confidence_level", "source_type"]], hide_index=True)

        st.markdown("#### People Map Summary")
        st.metric("Contacts Mapped", c360["people_count"])
        st.metric("Verified Contacts", c360["verified_people"])

        st.markdown("#### Research Sources")
        src_subset = sources_df[sources_df["company_id"] == icc_company_id]
        if not src_subset.empty:
            st.dataframe(src_subset[["source_type", "source_title", "source_url", "verified"]], hide_index=True)

        st.markdown("#### Research Gaps")
        gaps_list = get_company_research_gaps(icc_company_id, profiles_df, people_df, sources_df)
        for gap in gaps_list:
            st.warning(gap)

        with st.expander("Company Deep Profile Research Prompt"):
            st.code(generate_company_research_prompt(icc_company_id), language="markdown")
    else:
        st.error("Company profile not found in company_profiles.csv")

# ── Tab 2: People Map ────────────────────────────────────────────────────────
with tabs[2]:
    st.subheader(f"People Map — {icc_company_name}")
    pm_filter = st.multiselect(
        "Contact Type Filter",
        options=["recruiter", "hiring_manager", "peer", "alumni"],
        default=["recruiter", "hiring_manager", "peer", "alumni"],
        key="pm_filter",
    )
    people_subset = build_people_map(icc_company_id, people_df)
    if not people_subset.empty:
        people_subset = people_subset[people_subset["contact_type"].isin(pm_filter)]
        ranked = rank_contacts_for_conversation(
            icc_company_id, icc_conversation_type, icc_interview_stage, people_df
        )
        ranked = [p for p in ranked if p["contact_type"] in pm_filter]

        display_rows = []
        for p in ranked:
            icon = VERIFY_COLORS.get(p.get("verification_status", "placeholder"), "⚪")
            display_rows.append({
                "Status": icon,
                "Name": p.get("person_name"),
                "Type": p.get("contact_type"),
                "Role Title": p.get("role_title"),
                "Hiring Power": p.get("hiring_power_score"),
                "Conv. Priority": p.get("conversation_priority"),
                "Verification": p.get("verification_status"),
            })
        st.dataframe(pd.DataFrame(display_rows), hide_index=True)

        for p in ranked[:3]:
            with st.expander(f"{p.get('person_name')} — {p.get('contact_type')}"):
                st.write(f"**Strategy:** {p.get('strategy', '')}")
                st.markdown(f"[Search Query URL]({p.get('search_query_url', '')})")
    else:
        st.info("No people mapped for this company.")

    with st.expander("People Map Research Prompt"):
        st.code(generate_people_research_prompt(icc_company_id), language="markdown")

# ── Tab 3: Role Deep Dive ────────────────────────────────────────────────────
with tabs[3]:
    st.subheader(f"Role Deep Dive — {icc_job_row['title'] if icc_job_row is not None else ''}")
    if icc_job_id:
        dive = build_role_deep_dive(icc_job_id, jobs_df, reasoning_df)
        st.write(f"**Why this role exists:** {dive.get('why_role_exists', '')}")
        st.write(f"**Business problem:** {dive.get('business_problem', '')}")
        st.write(f"**Likely team:** {dive.get('likely_team', '')}")

        st.markdown("#### JD Keywords Detected")
        st.write(", ".join(dive.get("jd_keywords", [])))

        st.markdown("#### 30 / 60 / 90 Day Plan")
        plan = dive.get("plan_30_60_90", {})
        st.write(f"- **30 days:** {plan.get('30_days', '')}")
        st.write(f"- **60 days:** {plan.get('60_days', '')}")
        st.write(f"- **90 days:** {plan.get('90_days', '')}")

        st.markdown("#### How I Would Help")
        for bullet in dive.get("how_i_would_help", []):
            st.write(f"- {bullet}")

        st.markdown("#### Priority Questions")
        for q in dive.get("priority_questions", []):
            st.write(f"- {q}")

        with st.expander("Full Job Description"):
            st.write(icc_job_row["description"])

        with st.expander("Role Reasoning Research Prompt"):
            st.code(generate_role_research_prompt(icc_job_id, jobs_df), language="markdown")

# ── Tab 4: Proof Assets ──────────────────────────────────────────────────────
with tabs[4]:
    st.subheader("Proof Assets")
    st.write(f"Context: **{icc_company_name}** · **{icc_job_row['title'] if icc_job_row is not None else ''}**")

    if not proof_df.empty:
        st.markdown("#### All Portfolio Assets")
        st.dataframe(
            proof_df[["asset_type", "title", "tags", "url_or_path", "relevance_score"]],
            hide_index=True,
        )

        st.markdown("#### 3 Proof Assets to Show First")
        top3 = get_top_proof_assets_for_display(
            icc_job_id, icc_company_id, proof_df, jobs_df, profiles_df, n=3,
        )
        for i, asset in enumerate(top3, 1):
            st.write(f"**{i}. {asset['title']}** (combined score: {asset['match_score']})")
            st.caption(asset["description"])
            st.code(asset["url_or_path"])

        missing = identify_missing_proof(icc_job_id, icc_company_id, proof_df, jobs_df, profiles_df)
        if missing:
            st.markdown("#### Missing Proof Gaps")
            for gap in missing:
                st.warning(gap)

        with st.expander("Reverse Mapping — Company Assets"):
            company_assets = match_assets_to_company(icc_company_id, proof_df, profiles_df)
            for a in company_assets[:5]:
                st.write(f"- {a['title']} (score: {a['match_score']})")

        with st.expander("Reverse Mapping — Role Assets"):
            role_assets = match_assets_to_role(icc_job_id, proof_df, jobs_df)
            for a in role_assets[:5]:
                st.write(f"- {a['title']} (score: {a['match_score']})")

    with st.expander("Interview Packet Research Prompt"):
        st.code(
            generate_interview_packet_prompt(
                icc_company_id, icc_job_id, jobs_df, icc_conversation_type,
            ),
            language="markdown",
        )

# ── Existing tabs (unchanged logic) ──────────────────────────────────────────
with tabs[5]:
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

with tabs[6]:
    st.subheader("Company Priority Ranking")
    st.dataframe(
        company_rank_df[["company", "industry", "location", "priority_score", "priority_label", "job_count", "contact_count"]],
        use_container_width=True, hide_index=True,
    )
    st.bar_chart(company_rank_df.set_index("company")["priority_score"].head(15))

with tabs[7]:
    st.subheader("Role Fit Scores")
    st.dataframe(filtered_scores.sort_values("fit_score", ascending=False), use_container_width=True, hide_index=True)

    role_fit_jobs = filtered_scores.sort_values("fit_score", ascending=False)["job_id"].tolist()
    default_job = icc_job_id if icc_job_id in role_fit_jobs else (role_fit_jobs[0] if role_fit_jobs else None)
    selected = st.selectbox(
        "Drill into job",
        options=role_fit_jobs,
        index=role_fit_jobs.index(default_job) if default_job and default_job in role_fit_jobs else 0,
        format_func=lambda jid: f"{scores_df[scores_df['job_id']==jid]['title'].values[0]} @ {scores_df[scores_df['job_id']==jid]['company'].values[0]}",
        key="role_fit_job",
    )
    if selected:
        detail = next(s for s in scores if s["job_id"] == selected)
        st.write(f"**{detail['fit_label']}** ({detail['fit_score']}/100)")
        cat_df = pd.DataFrame([{"category": k, "score": v} for k, v in detail["category_scores"].items()])
        st.bar_chart(cat_df.set_index("category")["score"])
        job_row = jobs_df[jobs_df["job_id"] == selected].iloc[0]
        with st.expander("Job Description"):
            st.write(job_row["description"])

with tabs[8]:
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

with tabs[9]:
    st.subheader("Networking Map")
    contact_type_filter = st.multiselect("Contact Type", options=["recruiter", "hiring_manager", "peer", "alumni"], default=["recruiter", "hiring_manager"])
    filtered_outreach = [o for o in outreach if o["contact_type"] in contact_type_filter]
    if company_filter != "All":
        filtered_outreach = [o for o in filtered_outreach if o["company_name"] == company_filter]
    for item in filtered_outreach[:10]:
        with st.expander(f"{item['company_name']} — {item['contact_type']} (fit: {item['fit_score']})"):
            st.write(f"**Angle:** {item['angle']}")
            st.text_area("Message", item["message"], height=120, key=f"msg_{item['contact_id']}")

with tabs[10]:
    st.subheader("Interview Prep")
    int_jobs = filtered_scores.sort_values("fit_score", ascending=False)["job_id"].tolist()
    int_default = icc_job_id if icc_job_id in int_jobs else (int_jobs[0] if int_jobs else None)
    int_job = st.selectbox(
        "Select job",
        options=int_jobs,
        index=int_jobs.index(int_default) if int_default and int_default in int_jobs else 0,
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

with tabs[11]:
    st.subheader("Action Recommendations")
    st.dataframe(
        rec_df[["company_name", "title", "fit_score", "action", "composite_score", "rationale"]].sort_values("composite_score", ascending=False),
        use_container_width=True, hide_index=True,
    )

with tabs[12]:
    st.subheader("Export & SQL Analytics")
    st.download_button("Download Scores CSV", scores_df.to_csv(index=False), "role_fit_scores.csv", "text/csv")
    st.download_button("Download Recommendations CSV", rec_df.to_csv(index=False), "recommendations.csv", "text/csv")

    st.subheader("SQL Demo")
    query_name = st.selectbox("Demo Query", options=list(DEMO_QUERIES.keys()))
    st.code(DEMO_QUERIES[query_name], language="sql")
    if st.button("Run Query"):
        st.dataframe(pd.DataFrame(run_query(DEMO_QUERIES[query_name])), use_container_width=True, hide_index=True)

with tabs[13]:
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
