"""
Career Intelligence OS — Streamlit Dashboard

Run: streamlit run dashboard/app.py
"""

import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from src import __version__
from src.company_priority_scorer import score_companies
from src.company_profile_engine import build_company_360, get_company_research_gaps, load_company_profiles
from src.conversation_brief_generator import (
    export_brief_markdown,
    generate_conversation_brief,
    save_conversation_brief,
    score_brief_completeness,
)
from src.conversation_feedback_analyzer import get_dashboard_stats
from src.data_confidence import compute_confidence, confidence_badge_label, get_confidence_warnings, is_stale
from src.data_loader import load_all
from src.db import DEMO_QUERIES, init_db, run_query
from src.health_check import run_health_check
from src.interview_topic_mapper import generate_interview_batch
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
from src.message_queue_engine import (
    build_message_queue,
    export_message_queue_csv,
    export_message_queue_markdown,
)
from src.mission_control_engine import build_mission_control
from src.pipeline_engine import PIPELINE_STAGES, load_pipeline_cards, save_pipeline_cards
from src.role_reasoning_engine import build_role_deep_dive, load_role_reasoning
from src.schedule_engine import get_daily_plan, get_next_activities, load_launch_plan, mark_activity_done

from dashboard.icc_state import (
    CONVERSATION_TYPES,
    INTERVIEW_STAGES,
    build_company_options,
    format_company_option,
    format_job_option,
    get_jobs_for_company,
    init_icc_state,
    on_company_change,
    on_job_change,
    resolve_icc_context,
    set_target,
)

# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Career Intelligence OS",
    page_icon="CI",
    layout="wide",
    initial_sidebar_state="expanded",
)

PROFESSIONAL_CSS = """
<style>
    .ci-header {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        padding: 1.25rem 2rem;
        border-radius: 8px;
        margin-bottom: 1.25rem;
        border-left: 4px solid #2563eb;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .ci-header h1 {
        color: #f8fafc;
        font-size: 1.65rem;
        font-weight: 600;
        margin: 0 0 0.2rem 0;
        letter-spacing: -0.02em;
    }
    .ci-header p {
        color: #cbd5e1;
        font-size: 0.9rem;
        margin: 0;
    }
    .ci-header-meta {
        text-align: right;
        color: #94a3b8;
        font-size: 0.8rem;
    }
    .ci-breadcrumb {
        color: #64748b;
        font-size: 0.85rem;
        margin-bottom: 0.75rem;
    }
    .ci-breadcrumb strong { color: #2563eb; }
    .status-badge {
        display: inline-block;
        padding: 0.15rem 0.6rem;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }
    .status-verified { background: #064e3b; color: #6ee7b7; }
    .status-partial { background: #78350f; color: #fcd34d; }
    .status-placeholder { background: #334155; color: #94a3b8; }
    .status-needs_verification { background: #7f1d1d; color: #fca5a5; }
    .confidence-verified_public { background: #064e3b; color: #6ee7b7; }
    .confidence-user_verified { background: #1e3a5f; color: #7dd3fc; }
    .confidence-source_backed { background: #365314; color: #bef264; }
    .confidence-hypothesis { background: #78350f; color: #fcd34d; }
    .confidence-placeholder { background: #334155; color: #94a3b8; }
    .confidence-stale { background: #7f1d1d; color: #fca5a5; }
    .mc-panel {
        background: #0f172a;
        padding: 1.25rem 1.5rem;
        border-radius: 8px;
        border: 1px solid #334155;
        margin-bottom: 1rem;
    }
    .sync-indicator {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        font-size: 0.8rem;
        color: #059669;
        font-weight: 500;
    }
    .sync-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #059669;
        display: inline-block;
    }
    .health-green { color: #059669; font-weight: 600; }
    .health-yellow { color: #d97706; font-weight: 600; }
    .health-red { color: #dc2626; font-weight: 600; }
    .ci-footer {
        margin-top: 3rem;
        padding-top: 1rem;
        border-top: 1px solid #334155;
        color: #64748b;
        font-size: 0.8rem;
    }
    div[data-testid="stMetric"] {
        background: #0f172a;
        padding: 0.75rem 1rem;
        border-radius: 6px;
        border: 1px solid #334155;
    }
    .sidebar-stat {
        font-size: 0.85rem;
        color: #94a3b8;
        margin: 0.15rem 0;
    }
</style>
"""
st.markdown(PROFESSIONAL_CSS, unsafe_allow_html=True)

STATUS_LABELS = {
    "verified": ("Verified", "status-verified"),
    "verified_public": ("Verified Public", "status-verified"),
    "source_backed": ("Source Backed", "confidence-source_backed"),
    "partial": ("Partial", "status-partial"),
    "placeholder": ("Placeholder", "status-placeholder"),
    "needs_verification": ("Needs Verification", "status-needs_verification"),
}

CONFIDENCE_CSS = {
    "verified_public": "confidence-verified_public",
    "user_verified": "confidence-user_verified",
    "source_backed": "confidence-source_backed",
    "hypothesis": "confidence-hypothesis",
    "placeholder": "confidence-placeholder",
    "stale": "confidence-stale",
}


def render_confidence_badge(confidence: str) -> str:
    label = confidence_badge_label(confidence)
    css = CONFIDENCE_CSS.get(confidence, "confidence-placeholder")
    return f'<span class="status-badge {css}">{label}</span>'


def render_status_badge(status: str) -> str:
    label, css = STATUS_LABELS.get(status, ("Unknown", "status-placeholder"))
    return f'<span class="status-badge {css}">{label}</span>'


def render_health_indicator(status: str) -> str:
    css = {"green": "health-green", "yellow": "health-yellow", "red": "health-red"}.get(status, "")
    label = status.upper()
    return f'<span class="{css}">{label}</span>'


def safe_tab(module_name: str, hint: str, fn):
    """Render a tab inside an error boundary — show error once, no re-raise."""
    try:
        fn()
    except Exception as exc:
        st.error(f"**{module_name}** failed to load.")
        st.caption(f"{type(exc).__name__}: {exc}")
        st.info(f"Fix hint: {hint}")


def copy_to_clipboard_button(text: str, key: str) -> None:
    escaped = text.replace("\\", "\\\\").replace("`", "\\`").replace("$", "\\$").replace("\n", "\\n")
    components.html(
        f"""
        <button id="copy-{key}" style="
            background:#2d3a4f;color:#fff;border:1px solid #4a90d9;
            padding:0.4rem 1rem;border-radius:4px;cursor:pointer;font-size:0.85rem;
        ">Copy Script to Clipboard</button>
        <script>
        document.getElementById('copy-{key}').addEventListener('click', function() {{
            navigator.clipboard.writeText(`{escaped}`);
            this.textContent = 'Copied';
            setTimeout(() => {{ this.textContent = 'Copy Script to Clipboard'; }}, 2000);
        }});
        </script>
        """,
        height=45,
    )


# ── Header ────────────────────────────────────────────────────────────────────

st.markdown(
    f"""
    <div class="ci-header">
        <div>
            <h1>Career Intelligence OS</h1>
            <p>Sponsor-aware career intelligence for enterprise technology roles</p>
        </div>
        <div class="ci-header-meta">
            v{__version__}<br>
            Enterprise Dashboard
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Data loading (isolated from tab rendering) ──────────────────────────────────

@st.cache_data(show_spinner="Loading pipeline data…")
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


pipeline_error = None
try:
    with st.spinner("Initializing intelligence pipeline…"):
        data, scores, company_scores, recommendations, outreach, interviews, gaps = load_pipeline()
except Exception as exc:
    pipeline_error = exc
    data = scores = company_scores = recommendations = outreach = interviews = gaps = None

if pipeline_error:
    st.error("Pipeline failed to initialize. Check data files and module imports.")
    st.code(f"{type(pipeline_error).__name__}: {pipeline_error}")
    st.info("Run `python scripts/test_all_tabs.py` to diagnose import and data issues.")
    st.stop()

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

# ── Mission Control data ───────────────────────────────────────────────────────

mission_control = build_mission_control(data, date=datetime.now())
mc_cards = mission_control["cards"]
message_queue = mission_control["message_queue"]
card_by_job = {c["job_id"]: c for c in mc_cards}

# ── Sidebar ───────────────────────────────────────────────────────────────────

st.sidebar.header("System")
with st.sidebar.container(border=True):
    st.markdown("**Quick Stats**")
    st.markdown(f'<p class="sidebar-stat">{len(companies_df)} companies loaded</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="sidebar-stat">{len(jobs_df)} active roles</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="sidebar-stat">{len(mc_cards)} pipeline cards</p>', unsafe_allow_html=True)
    if not profiles_df.empty and "last_updated" in profiles_df.columns:
        last_updated = profiles_df["last_updated"].dropna().max()
        if last_updated:
            st.caption(f"Data last updated: {last_updated}")

st.sidebar.divider()
st.sidebar.header("Filters")
industry_opts = sorted(companies_df["industry"].unique())
industry_filter = st.sidebar.multiselect("Industry", options=industry_opts, default=industry_opts)
company_filter = st.sidebar.selectbox("Overview Filter", options=["All"] + sorted(companies_df["company"].unique()))
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

st.sidebar.divider()
with st.sidebar.expander("System Status", expanded=False):
    health = run_health_check()
    overall_html = render_health_indicator(health["overall"])
    st.markdown(f"**Overall:** {overall_html}", unsafe_allow_html=True)

    st.markdown("**Imports**")
    for check in health["imports"]["checks"]:
        icon = render_health_indicator(check["status"])
        mod_short = check["module"].replace("src.", "")
        st.markdown(f"{icon} `{mod_short}`", unsafe_allow_html=True)

    st.markdown("**Data Files**")
    for check in health["csvs"]["checks"]:
        if check["status"] == "red":
            st.markdown(f'<span class="health-red">FAIL</span> {check["file"]}: {check["detail"]}', unsafe_allow_html=True)
        elif check["rows"] == 0 and check["file"] in health["csvs"]["checks"]:
            st.markdown(f'<span class="health-yellow">WARN</span> {check["file"]}', unsafe_allow_html=True)

    st.markdown("**Pipeline**")
    for check in health["pipeline"]["checks"]:
        icon = render_health_indicator(check["status"])
        st.markdown(f"{icon} {check['step']}: {check['detail']}", unsafe_allow_html=True)

def _export_brief_from_panel():
    if st.session_state.icc_company_id and st.session_state.icc_job_id:
        brief = generate_conversation_brief(
            st.session_state.icc_company_id,
            st.session_state.icc_job_id,
            jobs_df,
            st.session_state.icc_person_type,
            st.session_state.icc_interview_stage,
        )
        st.session_state.current_brief = brief
        st.session_state.brief_markdown = export_brief_markdown(brief)


# ── ICC global selectors (session state) ─────────────────────────────────────

init_icc_state(st.session_state, companies_df, jobs_df)

st.sidebar.divider()
st.sidebar.header("Company Search")
st.sidebar.caption("Filter the global target selector below.")
st.sidebar.text_input(
    "Search companies",
    placeholder="e.g. JPMorgan, Dell, finance…",
    key="icc_company_search",
)

company_options = build_company_options(
    companies_df, company_rank_df, st.session_state.icc_company_search,
)
total_companies = len(companies_df)
shown_count = len(company_options)

if not company_options:
    company_options = build_company_options(companies_df, company_rank_df)
    shown_count = len(company_options)

if st.session_state.icc_company_id not in company_options and company_options:
    st.session_state.icc_company_id = company_options[0]
    on_company_change(st.session_state, companies_df, jobs_df)

def _handle_company_change():
    on_company_change(st.session_state, companies_df, jobs_df)

def _handle_job_change():
    on_job_change(st.session_state, jobs_df)

icc_ctx = resolve_icc_context(st.session_state, companies_df, jobs_df)
icc_company_id = icc_ctx["company_id"]
icc_company_name = icc_ctx["company_name"]
icc_job_id = icc_ctx["job_id"]
icc_job_row = icc_ctx["job_row"]
icc_person_type = icc_ctx["person_type"]
icc_interview_stage = icc_ctx["interview_stage"]
selection_complete = icc_ctx["selection_complete"]
selected_card = card_by_job.get(icc_job_id, {})

with st.container(border=True):
    st.subheader("Selected Target")
    count_label = f"{shown_count} of {total_companies} companies"
    if st.session_state.icc_company_search.strip():
        count_label += f" matching \"{st.session_state.icc_company_search.strip()}\""
    st.caption(f"Persistent context synced across all tabs · {count_label}")
    st.markdown(
        f'<p class="ci-breadcrumb">Mission Control &rsaquo; '
        f'<strong>{icc_company_name or "Select company"}</strong> &rsaquo; '
        f'{icc_ctx["job_title"] or "Select role"}</p>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<span class="sync-indicator"><span class="sync-dot"></span>Synced across all views</span>',
        unsafe_allow_html=True,
    )

    icc_col1, icc_col2, icc_col3, icc_col4 = st.columns(4)

    with icc_col1:
        st.selectbox(
            f"Target Company ({total_companies} total)",
            options=company_options,
            format_func=lambda cid: format_company_option(cid, companies_df),
            key="icc_company_id",
            on_change=_handle_company_change,
            help="All DFW Top-50 companies sorted by priority score.",
        )
    with icc_col2:
        company_jobs = get_jobs_for_company(icc_company_id, jobs_df)
        icc_job_options = company_jobs["job_id"].tolist()
        if not icc_job_options:
            st.selectbox("Target Role", options=["—"], disabled=True, help="No roles for this company.")
            icc_job_id = ""
        else:
            if icc_job_id not in icc_job_options:
                st.session_state.icc_job_id = icc_job_options[0]
                on_job_change(st.session_state, jobs_df)
                icc_job_id = st.session_state.icc_job_id
            st.selectbox(
                f"Target Role ({len(icc_job_options)} roles)",
                options=icc_job_options,
                format_func=lambda jid: format_job_option(jid, jobs_df),
                key="icc_job_id",
                on_change=_handle_job_change,
                help="All open roles for the selected company.",
            )
            icc_job_id = st.session_state.icc_job_id
            icc_job_row = jobs_df[jobs_df["job_id"] == icc_job_id].iloc[0]
    with icc_col3:
        st.selectbox(
            "Conversation Type",
            options=CONVERSATION_TYPES,
            key="icc_person_type",
            help="Contact persona for brief and people map ranking.",
        )
        icc_person_type = st.session_state.icc_person_type
    with icc_col4:
        st.selectbox(
            "Interview Stage",
            options=INTERVIEW_STAGES,
            key="icc_interview_stage",
            help="Stage-specific talking points and next actions.",
        )
        icc_interview_stage = st.session_state.icc_interview_stage

    if not selection_complete:
        st.info("Select a company and role to unlock Company 360, People Map, Role Deep Dive, and Proof Assets.")

    st.markdown('<div class="mc-panel">', unsafe_allow_html=True)
    st_col1, st_col2, st_col3, st_col4, st_col5 = st.columns(5)
    job_title = icc_job_row["title"] if icc_job_row is not None else "—"
    st_col1.metric("Company", icc_company_name or "—")
    st_col2.metric("Role", job_title[:28] + ("…" if len(str(job_title)) > 28 else ""))
    st_col3.metric("Contact Type", selected_card.get("contact_type", icc_person_type))
    st_col4.metric("Pipeline Stage", selected_card.get("pipeline_stage", "—"))
    st_col5.metric("Priority", selected_card.get("priority_score", "—"))

    panel_a, panel_b = st.columns([2, 1])
    with panel_a:
        st.write(f"**Next action:** {selected_card.get('next_action', 'Select a role and review Mission Control queue')}")
        proof_title = selected_card.get("proof_asset_title", "")
        if proof_title:
            conf = selected_card.get("data_confidence", "placeholder")
            st.markdown(
                f"**Proof asset:** {proof_title} {render_confidence_badge(conf)}",
                unsafe_allow_html=True,
            )
    with panel_b:
        st.button(
            "Export Brief",
            key="panel_export_brief",
            type="primary",
            disabled=not selection_complete,
            help="Generate a conversation brief for the selected company and role.",
            on_click=_export_brief_from_panel,
        )

    with st.expander("Quick links to related views"):
        ql1, ql2, ql3 = st.columns(3)
        ql1.caption("Company 360 · People Map · Proof Assets tabs")
        ql2.caption(f"Stage: {icc_interview_stage} · Type: {icc_person_type}")
        ql3.caption(f"Recommendation: {selected_card.get('recommendation_action', '—')}")

    st.markdown("</div>", unsafe_allow_html=True)

st.divider()

def _sync_role_fit_job():
    selected = st.session_state.role_fit_job
    job_row_sel = jobs_df[jobs_df["job_id"] == selected]
    if not job_row_sel.empty:
        set_target(st.session_state, job_row_sel.iloc[0]["company_id"], selected, companies_df, jobs_df)


def _sync_interview_job():
    selected = st.session_state.int_job
    job_row_sel = jobs_df[jobs_df["job_id"] == selected]
    if not job_row_sel.empty:
        set_target(st.session_state, job_row_sel.iloc[0]["company_id"], selected, companies_df, jobs_df)


# ── Tabs ──────────────────────────────────────────────────────────────────────

tabs = st.tabs([
    "Mission Control",
    "Command Center",
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
    "Feedback",
])


def tab_mission_control():
    mc = mission_control
    readiness = mc["readiness"]
    metrics = mc["metrics"]
    top_target = mc.get("top_target", {})

    st.subheader("Mission Control")
    st.caption(f"Monday-ready execution · {mc['date']}")

    m1, m2, m3, m4, m5, m6 = st.columns(6)
    m1.metric("Monday Readiness", f"{readiness['total']}/100", readiness["label"])
    m2.metric("Date", mc["date"])
    m3.metric("Top Target", (top_target.get("company_name", "—")[:18] if top_target else "—"))
    m4.metric("Briefs Ready", mc.get("briefs_ready", 0))
    m5.metric("Follow-Ups Due", metrics.get("follow_up_due", 0))
    m6.metric("Blocked", metrics.get("blocked", 0))

    if mc.get("warnings"):
        with st.expander("Execution warnings", expanded=False):
            for w in mc["warnings"]:
                st.warning(w)

    st.divider()
    st.markdown("#### Today's Action Queue")
    queue_df = pd.DataFrame(mc["action_queue"])
    if queue_df.empty:
        st.info("No actions queued — refresh pipeline cards or adjust filters.")
    else:
        display_cols = [
            "priority_score", "company_name", "job_title", "pipeline_stage",
            "next_action", "contact_type", "data_confidence",
        ]
        show = [c for c in display_cols if c in queue_df.columns]
        st.dataframe(queue_df[show], use_container_width=True, hide_index=True)
        eq1, eq2 = st.columns(2)
        with eq1:
            st.download_button(
                "Export Queue CSV",
                queue_df.to_csv(index=False),
                "action_queue.csv",
                "text/csv",
                key="dl_action_queue",
            )
        with eq2:
            md_lines = ["# Today's Action Queue", ""]
            for _, row in queue_df.iterrows():
                md_lines.append(f"- **{row.get('company_name')}** — {row.get('job_title')}: {row.get('next_action')}")
            st.download_button(
                "Export Queue Markdown",
                "\n".join(md_lines),
                "action_queue.md",
                "text/markdown",
                key="dl_action_md",
            )

    st.divider()
    st.markdown("#### Pipeline Board")
    board = mc["pipeline_board"]
    cols = st.columns(len(PIPELINE_STAGES))
    for col, stage in zip(cols, PIPELINE_STAGES):
        with col:
            st.markdown(f"**{stage}**")
            cards_in_stage = board.get(stage, [])
            st.caption(f"{len(cards_in_stage)} cards")
            for card in cards_in_stage[:4]:
                st.write(f"· {card.get('company_name', '')[:14]}")
                st.caption(f"{card.get('priority_score', '')} · {card.get('job_title', '')[:20]}")

    st.divider()
    st.markdown("#### Top 10 Targets")
    targets_df = pd.DataFrame(mc["top_targets"])
    if not targets_df.empty:
        tcols = ["priority_score", "company_name", "job_title", "pipeline_stage", "recommendation_action", "data_confidence"]
        st.dataframe(targets_df[[c for c in tcols if c in targets_df.columns]], use_container_width=True, hide_index=True)
        st.caption("Set global target from a pipeline card:")
        for idx, row in targets_df.head(5).iterrows():
            label = f"{row.get('company_name', '')[:20]} — {row.get('job_title', '')[:24]}"
            if st.button(label, key=f"mc_target_{row.get('job_id', idx)}"):
                job_row = jobs_df[jobs_df["job_id"] == row.get("job_id")]
                if not job_row.empty:
                    set_target(
                        st.session_state,
                        job_row.iloc[0]["company_id"],
                        row.get("job_id"),
                        companies_df,
                        jobs_df,
                    )
                    st.rerun()

    st.divider()
    col_r, col_b = st.columns(2)
    with col_r:
        st.markdown("#### Follow-Up Radar")
        fu = mc.get("follow_up_radar", [])
        if fu:
            st.dataframe(pd.DataFrame(fu)[["company_name", "job_title", "follow_up_date", "next_action"]], hide_index=True)
        else:
            st.write("No follow-ups due.")
    with col_b:
        st.markdown("#### Blockers")
        blockers = mc.get("blockers", [])
        if blockers:
            for b in blockers[:8]:
                st.warning(f"{b.get('company_name')} — {b.get('blocked_reason') or b.get('pipeline_stage')}")
        else:
            st.success("No blocked cards.")

    st.divider()
    st.markdown("#### Monday Launch Plan")
    daily = mc.get("daily_plan")
    if daily:
        st.write(f"**Focus:** {daily.get('focus', '')}")
        st.write(f"**Outputs:** {daily.get('key_outputs', '')}")
        st.write(f"**Metrics:** {daily.get('success_metrics', '')}")
    else:
        st.info("No launch plan entry for today — see monday_launch_plan.csv")

    week = mc.get("week_plan", {})
    if week.get("entries"):
        with st.expander("Full week plan"):
            st.dataframe(pd.DataFrame(week["entries"]), hide_index=True)

    st.markdown("#### Today's Schedule")
    for act in mc.get("next_activities", []):
        st.write(f"**{act.get('start_time')}** — {act.get('activity_name')}")
    for act in mc.get("overdue_activities", []):
        c1, c2 = st.columns([4, 1])
        c1.warning(f"Overdue: {act.get('start_time')} — {act.get('activity_name')}")
        if c2.button("Done", key=f"done_{act.get('activity_id')}"):
            if mark_activity_done(act.get("activity_id", "")):
                st.rerun()

    st.divider()
    st.markdown("#### Message Queue Preview")
    mq = mc.get("message_queue", [])
    if not mq:
        st.info("No messages ready — verify contacts and move cards to Ready to Contact.")
    else:
        for msg in mq[:5]:
            with st.expander(f"{msg.get('company_name')} — {msg.get('job_title')} ({msg.get('status')})"):
                st.text_area("Draft", msg.get("message_draft", ""), height=140, key=f"mq_{msg.get('message_id')}")
                copy_to_clipboard_button(msg.get("message_draft", ""), msg.get("message_id", "mq"))
        mq_path = export_message_queue_csv(mq, ROOT / "exports" / "message_queue.csv")
        st.download_button(
            "Export Message Queue CSV",
            export_message_queue_markdown(mq),
            "message_queue.md",
            "text/markdown",
            key="dl_mq_md",
        )
        st.caption(f"CSV also saved to {mq_path.relative_to(ROOT)}")


def tab_command_center():
    st.subheader("Interview Command Center")
    job_title = icc_job_row["title"] if icc_job_row is not None else "—"
    st.caption(f"{icc_company_name} · {job_title} · {icc_person_type} · {icc_interview_stage}")

    btn_col1, btn_col2, btn_col3 = st.columns(3)
    with btn_col1:
        if st.button("Generate Brief", type="primary", key="gen_brief", disabled=not selection_complete):
            st.session_state.current_brief = generate_conversation_brief(
                icc_company_id, icc_job_id, jobs_df,
                icc_person_type, icc_interview_stage,
            )
            st.session_state.brief_markdown = export_brief_markdown(st.session_state.current_brief)
    with btn_col2:
        if st.button("Save Brief", key="save_brief", disabled=not st.session_state.current_brief):
            if st.session_state.current_brief:
                path = save_conversation_brief(st.session_state.current_brief, st.session_state.brief_markdown)
                st.success(f"Saved to {path}")
            else:
                st.warning("Generate a brief before saving.")
    with btn_col3:
        if st.session_state.brief_markdown:
            st.download_button(
                "Download Markdown",
                st.session_state.brief_markdown,
                file_name=f"brief_{icc_job_id}_{icc_person_type.replace(' ', '_')}.md",
                mime="text/markdown",
                key="dl_brief",
            )

    brief = st.session_state.current_brief
    if not brief:
        if not selection_complete:
            st.info("Select a company and role in **Selected Target** above to enable brief generation.")
        else:
            st.info("Click **Generate Brief** to build a seven-section conversation package.")
        return

    readiness = score_brief_completeness(brief)
    r1, r2 = st.columns([1, 3])
    r1.metric("Brief Readiness", f"{readiness['score']}%")
    with r2:
        if readiness["gaps"]:
            st.caption("Gaps: " + "; ".join(readiness["gaps"]))

    sec = brief["sections"]
    st.divider()

    st.markdown("#### 1. Company 360")
    c360 = sec["company_360"]
    c1, c2, c3 = st.columns(3)
    c1.metric("Industry", c360.get("industry", "—"))
    c2.metric("DFW Presence", (c360.get("dfw_presence", "") or "—")[:40])
    c3.metric("Priority Tier", c360.get("priority_tier", "—"))
    st.write(c360.get("strategic_summary", ""))
    if c360.get("themes"):
        st.write("**Active Themes:**", ", ".join(t["theme"] for t in c360["themes"][:5]))

    st.divider()
    st.markdown("#### 2. Role Intelligence")
    role = sec["role_intelligence"]
    st.write(f"**Why role exists:** {role.get('why_role_exists', '')}")
    st.write(f"**Business problem:** {role.get('business_problem', '')}")
    st.write(f"**Likely team:** {role.get('likely_team', '')}")

    st.divider()
    st.markdown("#### 3. People / Power Map")
    if sec["people_power_map"]:
        for person in sec["people_power_map"][:4]:
            badge = render_status_badge(person.get("verification_status", "placeholder"))
            st.markdown(
                f'{badge} **{person.get("person_name")}** ({person.get("contact_type")}) — '
                f'priority {person.get("conversation_priority", 0)}',
                unsafe_allow_html=True,
            )
    else:
        st.warning("No contacts mapped. Add entries to people_map.csv.")

    st.divider()
    st.markdown("#### 4. Proof-of-Work Match")
    for asset in sec["proof_of_work_match"].get("top_three_display", []):
        st.write(f"- **{asset['title']}** (match: {asset['match_score']}) — `{asset['url_or_path']}`")

    st.divider()
    st.markdown("#### 5. Conversation Script")
    script_text = sec["conversation_script"]
    st.code(script_text, language=None)
    copy_to_clipboard_button(script_text, "conv_script")

    st.divider()
    st.markdown("#### 6. Interview Prep")
    prep = sec.get("interview_prep", {})
    for label, key in [("Technical", "technical_topics"), ("Business", "business_topics"), ("Behavioral", "behavioral_topics")]:
        topics = prep.get(key, [])
        if topics:
            st.write(f"**{label}:**")
            for t in topics[:2]:
                st.write(f"- [{t.get('priority', '')}] {t.get('question', '')}")

    st.divider()
    st.markdown("#### 7. Action Plan")
    st.write("**Follow-up:**")
    st.text(sec["action_plan"]["follow_up"])
    st.write("**Next actions:**")
    for action in sec["action_plan"]["next_actions"]:
        st.write(f"- [ ] {action}")

    with st.expander("Full Markdown Preview"):
        st.markdown(st.session_state.brief_markdown)


def tab_company_360():
    st.subheader(f"Company 360 — {icc_company_name}")
    c360 = build_company_360(icc_company_id, profiles_df, projects_df, sources_df, people_df)
    if not c360.get("found"):
        st.warning("Company profile not found. Add an entry to company_profiles.csv for this company.")
        return

    prof_row = profiles_df[profiles_df["company_id"] == icc_company_id]
    lu = prof_row.iloc[0]["last_updated"] if not prof_row.empty else ""
    src_count = len(sources_df[sources_df["company_id"] == icc_company_id]) if not sources_df.empty else 0
    conf = compute_confidence("partial", lu, src_count > 0)
    st.markdown(render_confidence_badge(conf), unsafe_allow_html=True)
    if is_stale(lu):
        st.warning(f"Profile last updated {lu} — data may be stale (>30 days).")
    for w in get_confidence_warnings(icc_company_id, profiles_df, people_df, sources_df):
        st.caption(w)

    st.write(f"**Strategic Summary:** {c360['strategic_summary']}")
    st.write(f"**Growth Signals:** {c360['growth_signals']}")
    st.write(f"**Risk Factors:** {c360['risk_factors']}")
    st.write(f"**Sponsorship Context:** {c360['sponsorship_context']}")

    st.divider()
    st.markdown("#### Tech Stack Themes")
    st.write(", ".join(c360["tech_stack_themes"]))

    st.markdown("#### Active Projects")
    proj_subset = projects_df[projects_df["company_id"] == icc_company_id]
    if not proj_subset.empty:
        st.dataframe(proj_subset[["theme", "description", "confidence_level", "source_type"]], hide_index=True)
    else:
        st.info("No project themes recorded. Add rows to company_projects.csv.")

    c1, c2 = st.columns(2)
    c1.metric("Contacts Mapped", c360["people_count"])
    c2.metric("Verified Contacts", c360["verified_people"])

    st.markdown("#### Research Sources")
    src_subset = sources_df[sources_df["company_id"] == icc_company_id]
    if not src_subset.empty:
        st.dataframe(src_subset[["source_type", "source_title", "source_url", "verified"]], hide_index=True)

    st.markdown("#### Research Gaps")
    gaps_list = get_company_research_gaps(icc_company_id, profiles_df, people_df, sources_df)
    if gaps_list:
        for gap in gaps_list:
            st.warning(gap)
    else:
        st.success("No critical research gaps identified.")

    with st.expander("Company Deep Profile Research Prompt"):
        st.code(generate_company_research_prompt(icc_company_id), language="markdown")


def tab_people_map():
    st.subheader(f"People Map — {icc_company_name}")
    pm_filter = st.multiselect(
        "Contact Type Filter",
        options=["recruiter", "hiring_manager", "peer", "alumni"],
        default=["recruiter", "hiring_manager", "peer", "alumni"],
        key="pm_filter",
    )
    people_subset = build_people_map(icc_company_id, people_df)
    src_subset = sources_df[sources_df["company_id"] == icc_company_id] if not sources_df.empty else pd.DataFrame()
    career_rows = src_subset[src_subset["source_type"] == "careers_portal"] if not src_subset.empty else pd.DataFrame()
    career_url = career_rows.iloc[0]["source_url"] if not career_rows.empty else ""

    if people_subset.empty:
        if career_url:
            st.info(
                f"No verified individual contact — use careers link: [{career_url}]({career_url})"
            )
        else:
            st.info(
                "No verified contact — add research_sources careers_portal row or people_map entry."
            )
    else:
        ranked = rank_contacts_for_conversation(icc_company_id, icc_person_type, icc_interview_stage, people_df)
        ranked = [p for p in ranked if p["contact_type"] in pm_filter]
        display_rows = []
        for p in ranked:
            label, _ = STATUS_LABELS.get(p.get("verification_status", "placeholder"), ("Unknown", ""))
            conf = compute_confidence(p.get("verification_status", "placeholder"))
            display_rows.append({
                "Confidence": confidence_badge_label(conf),
                "Status": label,
                "Name": p.get("person_name"),
                "Type": p.get("contact_type"),
                "Role Title": p.get("role_title"),
                "Hiring Power": p.get("hiring_power_score"),
                "Conv. Priority": p.get("conversation_priority"),
            })
        st.dataframe(pd.DataFrame(display_rows), hide_index=True)
        for p in ranked[:3]:
            with st.expander(f"{p.get('person_name')} — {p.get('contact_type')}"):
                st.write(f"**Strategy:** {p.get('strategy', '')}")
                st.markdown(f"[Search Query URL]({p.get('search_query_url', '')})")

    with st.expander("People Map Research Prompt"):
        st.code(generate_people_research_prompt(icc_company_id), language="markdown")


def tab_role_deep_dive():
    title = icc_job_row["title"] if icc_job_row is not None else ""
    st.subheader(f"Role Deep Dive — {title}")
    if not icc_job_id:
        st.info("Select a target role in the global selectors above.")
        return

    dive = build_role_deep_dive(icc_job_id, jobs_df, reasoning_df)
    st.write(f"**Why this role exists:** {dive.get('why_role_exists', '')}")
    st.write(f"**Business problem:** {dive.get('business_problem', '')}")
    st.write(f"**Likely team:** {dive.get('likely_team', '')}")

    st.divider()
    st.markdown("#### JD Keywords Detected")
    st.write(", ".join(dive.get("jd_keywords", [])) or "None detected")

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


def tab_proof_assets():
    st.subheader("Proof Assets")
    st.caption(f"{icc_company_name} · {icc_job_row['title'] if icc_job_row is not None else 'N/A'}")

    if proof_df.empty:
        st.warning("No proof assets loaded. Add entries to proof_assets.csv.")
        return

    st.markdown("#### Portfolio Assets")
    st.dataframe(proof_df[["asset_type", "title", "tags", "url_or_path", "relevance_score"]], hide_index=True)

    st.divider()
    st.markdown("#### Top 3 Assets for This Role")
    top3 = get_top_proof_assets_for_display(icc_job_id, icc_company_id, proof_df, jobs_df, profiles_df, n=3)
    for i, asset in enumerate(top3, 1):
        st.write(f"**{i}. {asset['title']}** (score: {asset['match_score']})")
        st.caption(asset["description"])
        st.code(asset["url_or_path"])

    missing = identify_missing_proof(icc_job_id, icc_company_id, proof_df, jobs_df, profiles_df)
    if missing:
        st.markdown("#### Proof Gaps")
        for gap in missing:
            st.warning(gap)

    with st.expander("Reverse Mapping — Company Assets"):
        for a in match_assets_to_company(icc_company_id, proof_df, profiles_df)[:5]:
            st.write(f"- {a['title']} (score: {a['match_score']})")
    with st.expander("Reverse Mapping — Role Assets"):
        for a in match_assets_to_role(icc_job_id, proof_df, jobs_df)[:5]:
            st.write(f"- {a['title']} (score: {a['match_score']})")
    with st.expander("Interview Packet Research Prompt"):
        st.code(generate_interview_packet_prompt(icc_company_id, icc_job_id, jobs_df, icc_person_type), language="markdown")


def tab_overview():
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Target Companies", len(companies_df))
    c2.metric("Active Jobs", len(jobs_df))
    c3.metric("Contacts", len(contacts_df))
    c4.metric("Avg Fit Score", f"{scores_df['fit_score'].mean():.1f}")

    st.divider()
    st.subheader("Universal Profile")
    st.info(UNIVERSAL_PROFILE)

    if not gap_df.empty:
        st.subheader("Portfolio Gap Matrix (P0)")
        p0 = gap_df[gap_df["priority"] == "P0"] if "priority" in gap_df.columns else gap_df
        st.dataframe(p0, use_container_width=True, hide_index=True)

    st.subheader("Fit Distribution")
    st.bar_chart(scores_df.groupby("fit_label").size())


def tab_company_ranking():
    st.subheader("Company Priority Ranking")
    st.caption(f"Global target: **{icc_company_name}** · Click a row context in Mission Control to sync selection.")
    display_rank = company_rank_df.copy()
    display_rank["selected"] = display_rank["company"] == icc_company_name
    st.dataframe(
        display_rank[["company", "industry", "location", "priority_score", "priority_label", "job_count", "contact_count", "selected"]],
        use_container_width=True,
        hide_index=True,
        column_config={
            "selected": st.column_config.CheckboxColumn("Target", disabled=True),
            "priority_score": st.column_config.NumberColumn("Priority", format="%.1f"),
        },
    )
    st.bar_chart(company_rank_df.set_index("company")["priority_score"].head(15))


def tab_role_fit():
    st.subheader("Role Fit Scores")
    st.dataframe(filtered_scores.sort_values("fit_score", ascending=False), use_container_width=True, hide_index=True)

    role_fit_jobs = filtered_scores.sort_values("fit_score", ascending=False)["job_id"].tolist()
    if not role_fit_jobs:
        st.info("No jobs match current filters.")
        return

    default_job = icc_job_id if icc_job_id in role_fit_jobs else role_fit_jobs[0]
    selected = st.selectbox(
        "Drill into job",
        options=role_fit_jobs,
        index=role_fit_jobs.index(default_job) if default_job in role_fit_jobs else 0,
        format_func=lambda jid: f"{scores_df[scores_df['job_id']==jid]['title'].values[0]} @ {scores_df[scores_df['job_id']==jid]['company'].values[0]}",
        key="role_fit_job",
        on_change=_sync_role_fit_job,
    )
    detail = next(s for s in scores if s["job_id"] == selected)
    st.write(f"**{detail['fit_label']}** ({detail['fit_score']}/100)")
    cat_df = pd.DataFrame([{"category": k, "score": v} for k, v in detail["category_scores"].items()])
    st.bar_chart(cat_df.set_index("category")["score"])
    job_row = jobs_df[jobs_df["job_id"] == selected].iloc[0]
    with st.expander("Job Description"):
        st.write(job_row["description"])


def tab_sponsorship():
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


def tab_networking():
    st.subheader("Networking Map")
    contact_type_filter = st.multiselect(
        "Contact Type", options=["recruiter", "hiring_manager", "peer", "alumni"],
        default=["recruiter", "hiring_manager"], key="net_filter",
    )
    filtered_outreach = [o for o in outreach if o["contact_type"] in contact_type_filter]
    if company_filter != "All":
        filtered_outreach = [o for o in filtered_outreach if o["company_name"] == company_filter]
    if not filtered_outreach:
        st.info("No outreach angles match current filters.")
        return
    for item in filtered_outreach[:10]:
        with st.expander(f"{item['company_name']} — {item['contact_type']} (fit: {item['fit_score']})"):
            st.write(f"**Angle:** {item['angle']}")
            st.text_area("Message", item["message"], height=120, key=f"msg_{item['contact_id']}")


def tab_interview_prep():
    st.subheader("Interview Prep")
    int_jobs = filtered_scores.sort_values("fit_score", ascending=False)["job_id"].tolist()
    if not int_jobs:
        st.info("No jobs match current filters.")
        return
    int_default = icc_job_id if icc_job_id in int_jobs else int_jobs[0]
    int_job = st.selectbox(
        "Select job",
        options=int_jobs,
        index=int_jobs.index(int_default) if int_default in int_jobs else 0,
        format_func=lambda jid: f"{scores_df[scores_df['job_id']==jid]['title'].values[0]} @ {scores_df[scores_df['job_id']==jid]['company'].values[0]}",
        key="int_job",
        on_change=_sync_interview_job,
    )
    prep = next(i for i in interviews if i["job_id"] == int_job)
    for section, key in [("Technical", "technical_topics"), ("Business", "business_topics"), ("Behavioral", "behavioral_topics")]:
        st.markdown(f"#### {section}")
        for topic in prep[key]:
            priority_label = f"[{topic['priority']}]" if topic.get("priority") else ""
            st.write(f"{priority_label} [{topic['category']}] {topic['question']}")


def tab_recommendations():
    st.subheader("Action Recommendations")
    st.dataframe(
        rec_df[["company_name", "title", "fit_score", "action", "composite_score", "rationale"]].sort_values("composite_score", ascending=False),
        use_container_width=True, hide_index=True,
    )


def tab_export():
    st.subheader("Export & SQL Analytics")
    st.download_button("Download Scores CSV", scores_df.to_csv(index=False), "role_fit_scores.csv", "text/csv")
    st.download_button("Download Recommendations CSV", rec_df.to_csv(index=False), "recommendations.csv", "text/csv")

    st.divider()
    st.subheader("SQL Demo")
    query_name = st.selectbox("Demo Query", options=list(DEMO_QUERIES.keys()))
    st.code(DEMO_QUERIES[query_name], language="sql")
    if st.button("Run Query"):
        st.dataframe(pd.DataFrame(run_query(DEMO_QUERIES[query_name])), use_container_width=True, hide_index=True)


def tab_feedback():
    st.subheader("Conversation Feedback")
    st.caption("Rule-based analysis of outreach and interview conversations.")
    feedback = get_dashboard_stats()

    if feedback["total_conversations"] == 0:
        st.info(feedback["summary"])
        st.markdown(
            "Log conversations in `data/conversation_log_template.csv` with fields: "
            "date, company, person_type, role_discussed, source, outreach_status, "
            "response, insight_gained, portfolio_gap, next_action, follow_up_date."
        )
        return

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
            st.write("None recorded.")
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
        st.write("No gaps logged.")

    st.write("**Next Actions**")
    if feedback["next_actions"]:
        st.dataframe(pd.DataFrame(feedback["next_actions"]), hide_index=True)

    if feedback["portfolio_improvements"]:
        st.write("**Portfolio Improvements Suggested**")
        st.dataframe(pd.DataFrame(feedback["portfolio_improvements"]), hide_index=True)


# ── Render tabs with error boundaries ─────────────────────────────────────────

TAB_RENDERERS = [
    ("Mission Control", "mission_control_engine", "Run scripts/seed_pipeline_cards.py and check pipeline CSVs", tab_mission_control),
    ("Command Center", "conversation_brief_generator", "Check ICC CSV files and brief generator imports", tab_command_center),
    ("Company 360", "company_profile_engine", "Verify company_profiles.csv and company_projects.csv", tab_company_360),
    ("People Map", "people_power_mapper", "Verify people_map.csv schema and contact types", tab_people_map),
    ("Role Deep Dive", "role_reasoning_engine", "Verify role_reasoning.csv covers all job IDs", tab_role_deep_dive),
    ("Proof Assets", "proof_asset_mapper", "Verify proof_assets.csv exists with asset entries", tab_proof_assets),
    ("Overview", "data_loader", "Check core CSV files in data/", tab_overview),
    ("Company Ranking", "company_priority_scorer", "Verify sample_companies.csv and jobs data", tab_company_ranking),
    ("Role Fit", "role_fit_scorer", "Check profile_keywords.csv and scoring module", tab_role_fit),
    ("Sponsorship Signal", "sponsorship_signal", "Verify sponsorship fields in company data", tab_sponsorship),
    ("Networking Map", "outreach_angle_generator", "Check contacts CSV and outreach generator", tab_networking),
    ("Interview Prep", "interview_topic_mapper", "Verify jobs data and interview topic mapper", tab_interview_prep),
    ("Recommendations", "recommendation_engine", "Check scoring pipeline output", tab_recommendations),
    ("Export", "db", "Verify SQLite init and DEMO_QUERIES", tab_export),
    ("Feedback", "conversation_feedback_analyzer", "Check conversation_log_template.csv", tab_feedback),
]

for tab_obj, (name, module, hint, renderer) in zip(tabs, TAB_RENDERERS):
    with tab_obj:
        safe_tab(module, hint, renderer)

# ── Footer ────────────────────────────────────────────────────────────────────

st.markdown(
    f"""
    <div class="ci-footer">
        Career Intelligence OS v{__version__} · Internal research tool ·
        {total_companies} companies · {len(jobs_df)} roles ·
        Data derived from structured CSV sources · Verify all contact and company information independently ·
        Not affiliated with any employer listed
    </div>
    """,
    unsafe_allow_html=True,
)
