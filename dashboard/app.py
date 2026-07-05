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
from src.data_confidence import (
    compute_confidence,
    confidence_badge_label,
    format_source_freshness_badge,
    get_confidence_warnings,
    is_stale,
    validate_dataset_sources,
)
from src.data_loader import load_all, load_core, load_intelligence, load_mission_control_data
from src.metadata_renderer import (
    display_dataframe_limited,
    inject_metadata_css,
    render_action_metadata,
    render_confidence_bar,
    render_entity_card,
    render_freshness_badge,
    render_metadata_expander,
    render_metadata_ribbon,
    render_section_header,
    render_source_chip,
)
from src.schedule_engine import mark_activity_done
from dashboard.navigation import (
    NAV_GROUP_ORDER,
    NAV_GROUPS,
    feature_key_for_tab,
    get_feature_help,
    load_feature_registry,
)
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
from src.company_workspace import build_company_workspace
from src.interview_simulator import (
    build_simulator_context,
    count_insights_by_company,
    generate_feedback,
    generate_recruiter_question,
    get_round_script,
    load_interview_insights,
    load_interview_journey,
    normalize_round,
    save_simulator_session,
)
from src.profile_manager import (
    build_sixty_second_pitch,
    get_portfolio_summary,
    load_profile,
    save_profile,
)

from dashboard.icc_state import (
    CONVERSATION_TYPES,
    INTERVIEW_STAGES,
    QUICK_FILTER_CAPTION,
    build_company_options,
    format_company_option,
    format_job_option,
    get_company_quick_stats,
    get_jobs_for_company,
    init_icc_state,
    on_company_change,
    on_focus_mode_change,
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
    .ci-context-bar {
        position: sticky;
        top: 0;
        z-index: 999;
        background: #0f172a;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 0.65rem 1.25rem;
        margin-bottom: 1rem;
        display: flex;
        flex-wrap: wrap;
        gap: 1.25rem;
        align-items: center;
        font-size: 0.85rem;
        color: #cbd5e1;
    }
    .ci-context-bar strong { color: #f8fafc; }
    .ci-scope-focused {
        background: #1e3a5f;
        border: 1px solid #2563eb;
        color: #bfdbfe;
        padding: 0.6rem 1rem;
        border-radius: 6px;
        margin-bottom: 1rem;
        font-size: 0.9rem;
    }
    .ci-scope-portfolio {
        background: #1e293b;
        border: 1px solid #475569;
        color: #94a3b8;
        padding: 0.6rem 1rem;
        border-radius: 6px;
        margin-bottom: 1rem;
        font-size: 0.9rem;
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


def render_source_freshness_badge(last_verified: str | None, source_url: str | None) -> None:
    """Render verified-source freshness badge or warning."""
    label, severity = format_source_freshness_badge(last_verified, source_url)
    if severity == "ok":
        st.caption(f"✓ {label}")
    elif severity == "warning":
        st.warning(label)
    else:
        st.error(label)


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

# ── Lazy data loading (isolated from tab rendering) ─────────────────────────────

@st.cache_data(show_spinner="Loading core data…")
def load_core_cached():
    return load_core()


@st.cache_data(show_spinner="Loading analytics…")
def load_analytics_cached(_core_key: str):
    core = load_core_cached()
    scores = score_jobs_dataframe(core["jobs"], core["companies"])
    company_scores = score_companies(core["companies"], core["jobs"], core["contacts"])
    recommendations = recommend_batch(scores, company_scores)
    outreach = generate_outreach_batch(core["jobs"], core["contacts"], scores)
    interviews = generate_interview_batch(core["jobs"], scores)
    gaps = analyze_jobs_batch(core["jobs"], scores)
    init_db(core["companies"], core["jobs"], core["contacts"])
    return scores, company_scores, recommendations, outreach, interviews, gaps


@st.cache_data(show_spinner="Loading ICC datasets…")
def load_icc_all_cached():
    from src.data_loader import load_icc_files
    return load_icc_files()


@st.cache_data(show_spinner="Loading company intelligence…")
def load_intelligence_cached(company_id: str):
    core = load_core_cached()
    return load_intelligence(company_id, jobs_df=core["jobs"])


pipeline_error = None
try:
    with st.spinner("Initializing intelligence pipeline…"):
        core_data = load_core_cached()
        scores, company_scores, recommendations, outreach, interviews, gaps = load_analytics_cached("v1")
        data = dict(core_data)
except Exception as exc:
    pipeline_error = exc
    data = scores = company_scores = recommendations = outreach = interviews = gaps = None
    core_data = None

if pipeline_error:
    st.error("Pipeline failed to initialize. Check data files and module imports.")
    st.code(f"{type(pipeline_error).__name__}: {pipeline_error}")
    st.info("Run `python scripts/test_all_tabs.py` to diagnose import and data issues.")
    st.stop()

companies_df = data["companies"]
jobs_df = data["jobs"]
contacts_df = data["contacts"]
gap_df = data["gap_matrix"]

inject_metadata_css()
feature_registry = load_feature_registry()

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

init_icc_state(st.session_state, companies_df, jobs_df)
total_companies = len(companies_df)

# Full ICC for mission control engines; company-scoped for intelligence tabs
icc_all = load_icc_all_cached()
data = load_mission_control_data(data, icc_all)

_intel_company = st.session_state.get("icc_company_id", "")
_intel = load_intelligence_cached(_intel_company) if _intel_company else {}
profiles_tab_df = _intel.get("company_profiles", pd.DataFrame())
people_tab_df = _intel.get("people_map", pd.DataFrame())
projects_tab_df = _intel.get("company_projects", pd.DataFrame())
sources_tab_df = _intel.get("research_sources", pd.DataFrame())
insights_tab_df = _intel.get("interview_insights", pd.DataFrame())
journey_tab_df = _intel.get("interview_journey", pd.DataFrame())
reasoning_tab_df = _intel.get("role_reasoning", pd.DataFrame())
proof_df = _intel.get("proof_assets", icc_all.get("proof_assets", load_proof_assets()))

# Tab-facing dataframes (company-scoped); fall back to full ICC where needed
profiles_df = profiles_tab_df if not profiles_tab_df.empty else icc_all.get("company_profiles", load_company_profiles())
people_df = people_tab_df if not people_tab_df.empty else icc_all.get("people_map", load_people_map())
projects_df = projects_tab_df if not projects_tab_df.empty else icc_all.get("company_projects", pd.DataFrame())
sources_df = sources_tab_df if not sources_tab_df.empty else icc_all.get("research_sources", pd.DataFrame())
insights_df = insights_tab_df if not insights_tab_df.empty else icc_all.get("interview_insights", pd.DataFrame())
journey_df = journey_tab_df if not journey_tab_df.empty else icc_all.get("interview_journey", pd.DataFrame())
reasoning_df = reasoning_tab_df if not reasoning_tab_df.empty else icc_all.get("role_reasoning", load_role_reasoning())

# ── Sidebar (company-first context) ───────────────────────────────────────────

st.sidebar.header("Target Context")

if "ci_sidebar_mode" not in st.session_state:
    st.session_state.ci_sidebar_mode = "Essentials"
if "ci_metadata_level" not in st.session_state:
    st.session_state.ci_metadata_level = "Summary"

st.sidebar.radio(
    "Sidebar mode",
    options=["Essentials", "Advanced"],
    key="ci_sidebar_mode",
    horizontal=True,
    help="Essentials: company, role, focus only. Advanced: filters and system status.",
)

st.sidebar.radio(
    "Metadata detail",
    options=["Summary", "Detailed"],
    key="ci_metadata_level",
    horizontal=True,
    help="Summary: key metrics only. Detailed: all metadata chips and source links.",
)

sidebar_advanced = st.session_state.ci_sidebar_mode == "Advanced"
metadata_detailed = st.session_state.ci_metadata_level == "Detailed"

st.sidebar.text_input(
    "Company Search",
    placeholder="e.g. JPMorgan, Dell, finance…",
    key="icc_company_search",
    help="Filter the company dropdown below.",
)

company_options = build_company_options(
    companies_df, company_rank_df, st.session_state.icc_company_search,
)
shown_count = len(company_options)

if not company_options:
    company_options = build_company_options(companies_df, company_rank_df)
    shown_count = len(company_options)

if st.session_state.icc_company_id not in company_options and company_options:
    st.session_state.icc_company_id = company_options[0]

st.sidebar.caption(f"Showing {shown_count} of {total_companies} companies")


def _handle_company_change():
    on_company_change(
        st.session_state,
        companies_df,
        jobs_df,
        scores=scores,
    )


def _handle_job_change():
    on_job_change(st.session_state, jobs_df)


def _handle_focus_mode_change():
    on_focus_mode_change(st.session_state)


st.sidebar.selectbox(
    "Target Company",
    options=company_options,
    format_func=lambda cid: format_company_option(cid, companies_df),
    key="icc_company_id",
    on_change=_handle_company_change,
    help="Primary control — all views follow this selection.",
)

company_jobs_sidebar = get_jobs_for_company(st.session_state.icc_company_id, jobs_df)
icc_job_options_sidebar = company_jobs_sidebar["job_id"].tolist()
if icc_job_options_sidebar:
    if st.session_state.get("icc_job_id") not in icc_job_options_sidebar:
        st.session_state.icc_job_id = icc_job_options_sidebar[0]
    st.sidebar.selectbox(
        "Target Role",
        options=icc_job_options_sidebar,
        format_func=lambda jid: format_job_option(jid, jobs_df),
        key="icc_job_id",
        on_change=_handle_job_change,
        help="Roles for the selected company.",
    )
else:
    st.sidebar.selectbox("Target Role", options=["—"], disabled=True)

if sidebar_advanced:
    with st.sidebar.expander("Person & Stage", expanded=False):
        st.selectbox(
            "Person Type",
            options=CONVERSATION_TYPES,
            key="icc_person_type",
        )
        st.selectbox(
            "Interview Stage",
            options=INTERVIEW_STAGES,
            key="icc_interview_stage",
        )
else:
    if "icc_person_type" not in st.session_state:
        st.session_state.icc_person_type = "hiring manager"
    if "icc_interview_stage" not in st.session_state:
        st.session_state.icc_interview_stage = "hiring manager screen"

st.sidebar.toggle(
    "Focus Mode",
    key="icc_focus_mode",
    help="ON: filter Mission Control to selected company. OFF: portfolio-wide view.",
    on_change=_handle_focus_mode_change,
)

st.sidebar.divider()

if sidebar_advanced:
    with st.sidebar.expander("Advanced Filters", expanded=False):
        st.caption(QUICK_FILTER_CAPTION)
        pipeline_stage_opts = list(PIPELINE_STAGES)
        tier_opts = sorted(companies_df["priority_tier"].dropna().unique().tolist())
        role_family_opts = sorted(jobs_df["role_family"].dropna().unique().tolist())
        st.multiselect(
            "Pipeline stage",
            options=pipeline_stage_opts,
            key="icc_pipeline_stage_filter",
        )
        st.multiselect(
            "Priority tier",
            options=tier_opts,
            key="icc_priority_tier_filter",
        )
        st.multiselect(
            "Role family",
            options=role_family_opts,
            key="icc_role_family_filter",
        )
else:
    if "icc_pipeline_stage_filter" not in st.session_state:
        st.session_state.icc_pipeline_stage_filter = []
    if "icc_priority_tier_filter" not in st.session_state:
        st.session_state.icc_priority_tier_filter = []
    if "icc_role_family_filter" not in st.session_state:
        st.session_state.icc_role_family_filter = []

icc_ctx = resolve_icc_context(st.session_state, companies_df, jobs_df)
icc_company_id = icc_ctx["company_id"]
icc_company_name = icc_ctx["company_name"]
icc_job_id = icc_ctx["job_id"]
icc_job_row = icc_ctx["job_row"]
icc_person_type = icc_ctx["person_type"]
icc_interview_stage = icc_ctx["interview_stage"]
icc_focus_mode = icc_ctx["focus_mode"]
icc_scope_label = icc_ctx["scope_label"]
selection_complete = icc_ctx["selection_complete"]

# ── Mission Control data (scoped to sidebar context) ────────────────────────────

mission_control = build_mission_control(
    data,
    date=datetime.now(),
    company_id=icc_company_id,
    focus_mode=icc_focus_mode,
    pipeline_stages=st.session_state.icc_pipeline_stage_filter or None,
    priority_tiers=st.session_state.icc_priority_tier_filter or None,
    role_families=st.session_state.icc_role_family_filter or None,
)
mc_cards = mission_control["cards"]
message_queue = mission_control["message_queue"]
card_by_job = {c["job_id"]: c for c in mission_control.get("all_cards", mc_cards)}

company_workspace = None
if icc_focus_mode and icc_company_id and selection_complete:
    company_workspace = build_company_workspace(
        icc_company_id,
        icc_job_id,
        data,
        mission_control,
    )

source_validation = validate_dataset_sources(profiles_df, projects_df, insights_df)

st.sidebar.divider()
st.sidebar.subheader("Quick Stats")
if icc_focus_mode and icc_company_id:
    qstats = get_company_quick_stats(icc_company_id, jobs_df, mission_control.get("all_cards", mc_cards))
    st.sidebar.metric("Jobs", qstats["jobs"])
    st.sidebar.metric("Pipeline cards", qstats["pipeline_cards"])
    st.sidebar.metric("Follow-ups due", qstats["follow_ups_due"])
    st.sidebar.metric("Brief readiness", qstats["briefs_ready"])
else:
    st.sidebar.metric("Companies", total_companies)
    st.sidebar.metric("Active roles", len(jobs_df))
    st.sidebar.metric("Pipeline cards", len(mission_control.get("all_cards", mc_cards)))
    st.sidebar.metric("Follow-ups due", mission_control["metrics"].get("follow_up_due", 0))

with st.sidebar.expander("System Status", expanded=False) if sidebar_advanced else st.sidebar.container():
    if sidebar_advanced:
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

if not profiles_df.empty and "last_updated" in profiles_df.columns:
    last_updated = profiles_df["last_updated"].dropna().max()
    if last_updated:
        st.sidebar.caption(f"Data last updated: {last_updated}")


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


# Portfolio-wide filters for Overview / Role Fit tabs
industry_opts = sorted(companies_df["industry"].unique())
action_filter = ["apply now", "network first", "research more"]

filtered_scores = scores_df.copy()
if icc_focus_mode and icc_company_id:
    filtered_scores = filtered_scores[filtered_scores["company"] == icc_company_name]
filtered_scores = filtered_scores[filtered_scores["job_id"].isin(
    rec_df[rec_df["action"].isin(action_filter)]["job_id"]
)]

selected_card = card_by_job.get(icc_job_id, {})

# ── Sticky context bar ────────────────────────────────────────────────────────

focus_label = icc_scope_label
sync_status = "Synced"
st.markdown(
    f"""
    <div class="ci-context-bar">
        <span><strong>Scope:</strong> {focus_label}</span>
        <span><strong>Company:</strong> {icc_company_name or "—"}</span>
        <span><strong>Role:</strong> {icc_ctx["job_title"] or "—"}</span>
        <span><strong>Stage:</strong> {icc_interview_stage}</span>
        <span><strong>Focus:</strong> {"ON" if icc_focus_mode else "OFF"}</span>
        <span class="sync-indicator"><span class="sync-dot"></span>{sync_status}</span>
    </div>
    """,
    unsafe_allow_html=True,
)

if icc_focus_mode and icc_company_id:
    mc_metrics = mission_control["metrics"]
    st.markdown(
        f'<div class="ci-scope-focused">'
        f'<strong>Focused on {icc_company_name}</strong> — all views filtered · '
        f'{mc_metrics.get("total_cards", 0)} pipeline cards · '
        f'{mc_metrics.get("follow_up_due", 0)} follow-ups due'
        f'</div>',
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        f'<div class="ci-scope-portfolio">'
        f'<strong>Portfolio view</strong> — {total_companies} companies · '
        f'select a company in the sidebar to focus'
        f'</div>',
        unsafe_allow_html=True,
    )

# ── Selected Target (read-only summary — change in sidebar) ───────────────────

with st.container(border=True):
    st.subheader("Selected Target")
    st.caption("Read-only summary · Change company and role in the sidebar →")
    st.markdown(
        f'<p class="ci-breadcrumb">{icc_scope_label} &rsaquo; '
        f'<strong>{icc_company_name or "Select company"}</strong> &rsaquo; '
        f'{icc_ctx["job_title"] or "Select role"}</p>',
        unsafe_allow_html=True,
    )

    if not selection_complete:
        st.info("Select a company and role in the sidebar to unlock Company 360, People Map, Role Deep Dive, and Proof Assets.")

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
        st.write(f"**Next action:** {selected_card.get('next_action', 'Review Mission Control action queue')}")
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


# ── Grouped navigation (v1.2) ─────────────────────────────────────────────────

if "ci_nav_group" not in st.session_state:
    st.session_state.ci_nav_group = "Execute"

nav_group = st.radio(
    "Section",
    options=NAV_GROUP_ORDER,
    horizontal=True,
    key="ci_nav_group",
    label_visibility="collapsed",
)
st.caption(f"**{nav_group}** — {len(NAV_GROUPS[nav_group])} view(s) · metadata: {st.session_state.ci_metadata_level}")

def _feature_caption(tab_name: str) -> None:
    help_text = get_feature_help(feature_key_for_tab(tab_name), feature_registry)
    if help_text:
        st.caption(help_text)


def tab_mission_control():
    mc = mission_control
    readiness = mc["readiness"]
    metrics = mc["metrics"]

    st.subheader("Mission Control")
    _feature_caption("Mission Control")
    if icc_focus_mode and icc_company_id and company_workspace:
        ws = company_workspace
        st.caption(f"Company workspace — **{icc_company_name}** · {ws.get('job_title', '')} · {mc['date']}")
        prof_row = profiles_df[profiles_df["company_id"] == icc_company_id]
        lu = prof_row.iloc[0]["last_updated"] if not prof_row.empty else ws.get("last_updated", "")
        src_url = ""
        if not sources_df.empty:
            co_src = sources_df[sources_df["company_id"] == icc_company_id]
            if not co_src.empty:
                src_url = co_src.iloc[0].get("source_url", "")
        render_source_freshness_badge(lu, src_url or "https://careers.jpmorgan.com")

        st.markdown("#### Company Intel")
        for line in ws.get("intel_summary_lines", []):
            st.write(line)

        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.markdown("#### Top 3 Actions Today")
            actions = ws.get("top_actions", [])
            if actions:
                for i, act in enumerate(actions[:3], 1):
                    st.write(f"{i}. **{act.get('next_action', 'Review pipeline')}**")
                    st.caption(f"{act.get('pipeline_stage', '')} · priority {act.get('priority_score', '')}")
            else:
                st.info("No queued actions — check pipeline board.")
        with col_b:
            st.markdown("#### Message Ready to Copy")
            msg = ws.get("copy_message", "")
            if msg:
                st.text_area("Outreach draft", msg, height=160, key="ws_copy_message")
                copy_to_clipboard_button(msg, "ws_msg")
            else:
                st.info("Move a card to Ready to Contact for message drafts.")
        with col_c:
            st.markdown("#### Proof Assets to Show")
            for asset in ws.get("proof_assets", [])[:3]:
                st.write(f"**{asset.get('title', '')}**")
                st.caption(asset.get("description", "")[:80])
            st.info("Practice interviews in the **Interview Simulator** tab →")

        st.markdown("#### Interview Prep Status")
        journey = ws.get("interview_journey", [])
        if journey:
            for row in journey:
                icon = "✅" if str(row.get("prep_complete", "")).lower() in ("true", "1") else "⬜"
                st.write(
                    f"{icon} **{str(row.get('round', '')).replace('_', ' ').title()}** — "
                    f"{row.get('status', 'pending')} · {row.get('scheduled_date') or 'TBD'}"
                )
        else:
            st.caption("Add rounds to data/interview_journey.csv for this company/role.")

        st.divider()
    elif icc_focus_mode and icc_company_id:
        st.caption(
            f"Focused on: **{icc_company_name}** "
            f"({metrics.get('total_cards', 0)} pipeline cards, "
            f"{metrics.get('follow_up_due', 0)} follow-ups due) · {mc['date']}"
        )
    else:
        st.caption(f"Portfolio view — select a company in sidebar to focus · {mc['date']}")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Monday Readiness", f"{readiness['total']}/100", readiness["label"])
    m2.metric("Pipeline Cards", metrics.get("total_cards", 0))
    m3.metric("Follow-Ups Due", metrics.get("follow_up_due", 0))
    m4.metric("Blocked", metrics.get("blocked", 0))

    if mc.get("warnings"):
        with st.expander("Execution warnings", expanded=False):
            for w in mc["warnings"]:
                st.warning(w)

    if not icc_focus_mode and not icc_company_id:
        st.info("Select a company in the sidebar to begin focused execution.")

    mc_sections = st.tabs([
        "Action Queue",
        "Message Queue",
        "Pipeline",
        "Blockers & Follow-ups",
        "Launch Plan",
    ])

    with mc_sections[0]:
        render_section_header("Today's Action Queue", len(mc["action_queue"]))
        queue_df = pd.DataFrame(mc["action_queue"])
        if queue_df.empty:
            st.caption("No actions queued for current scope.")
        else:
            display_cols = [
                "priority_score", "company_name", "job_title", "pipeline_stage",
                "next_action", "contact_type", "data_confidence",
            ]
            show = [c for c in display_cols if c in queue_df.columns]
            display_dataframe_limited(queue_df[show], key_prefix="action_queue")
            if metadata_detailed:
                for _, row in queue_df.head(5).iterrows():
                    render_action_metadata(row.to_dict(), detailed=metadata_detailed)
            if icc_focus_mode and "company_name" in queue_df.columns:
                other = queue_df[queue_df["company_id"] != icc_company_id] if "company_id" in queue_df.columns else pd.DataFrame()
                if not other.empty:
                    st.warning("Mixed company data detected — refresh or re-select company in sidebar.")
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

    with mc_sections[1]:
        render_section_header("Message Queue", len(mq := mc.get("message_queue", [])))
        if not mq:
            st.caption("No messages ready — move cards to Ready to Contact.")
        else:
            mq_left, mq_right = st.columns([1, 1])
            with mq_left:
                for msg in mq[:5]:
                    with st.expander(f"{msg.get('company_name')} — {msg.get('job_title')} ({msg.get('status')})"):
                        st.text_area("Draft", msg.get("message_draft", ""), height=140, key=f"mq_{msg.get('message_id')}")
                        copy_to_clipboard_button(msg.get("message_draft", ""), msg.get("message_id", "mq"))
            with mq_right:
                if mq:
                    preview = mq[0]
                    st.markdown(f"**Preview:** {preview.get('company_name')} — {preview.get('job_title')}")
                    st.text_area(
                        "Copy-ready draft",
                        preview.get("message_draft", ""),
                        height=220,
                        key="mq_preview_main",
                    )
            mq_path = export_message_queue_csv(mq, ROOT / "exports" / "message_queue.csv")
            st.download_button(
                "Export Message Queue Markdown",
                export_message_queue_markdown(mq),
                "message_queue.md",
                "text/markdown",
                key="dl_mq_md",
            )
            st.caption(f"CSV also saved to {mq_path.relative_to(ROOT)}")

    with mc_sections[2]:
        st.markdown("#### Pipeline Board")
        board = mc["pipeline_board"]
        if icc_focus_mode and icc_company_id:
            cols = st.columns(min(len(PIPELINE_STAGES), 4))
            for col, stage in zip(cols, PIPELINE_STAGES):
                with col:
                    cards_in_stage = board.get(stage, [])
                    st.markdown(f"**{stage}**")
                    st.caption(f"{len(cards_in_stage)} cards")
                    for card in cards_in_stage[:6]:
                        st.write(f"· {card.get('job_title', '')[:24]}")
                        st.caption(f"{card.get('priority_score', '')}")
        else:
            cols = st.columns(len(PIPELINE_STAGES))
            for col, stage in zip(cols, PIPELINE_STAGES):
                with col:
                    cards_in_stage = board.get(stage, [])
                    st.markdown(f"**{stage}**")
                    st.caption(f"{len(cards_in_stage)} cards")
                    for card in cards_in_stage[:3]:
                        st.write(f"· {card.get('company_name', '')[:14]}")
                        st.caption(f"{card.get('priority_score', '')} · {card.get('job_title', '')[:20]}")

        st.markdown("#### Top Targets")
        targets_df = pd.DataFrame(mc["top_targets"])
        if not targets_df.empty:
            label = "Top roles for this company" if icc_focus_mode else "Top 10 targets"
            st.caption(label)
            tcols = ["priority_score", "company_name", "job_title", "pipeline_stage", "recommendation_action", "data_confidence"]
            st.dataframe(targets_df[[c for c in tcols if c in targets_df.columns]], use_container_width=True, hide_index=True)
            for idx, row in targets_df.head(5).iterrows():
                label_btn = f"{row.get('company_name', '')[:20]} — {row.get('job_title', '')[:24]}"
                if st.button(label_btn, key=f"mc_target_{row.get('job_id', idx)}"):
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

    with mc_sections[3]:
        col_r, col_b = st.columns(2)
        with col_r:
            st.markdown("#### Follow-Up Radar")
            fu = mc.get("follow_up_radar", [])
            if fu:
                st.dataframe(pd.DataFrame(fu)[["company_name", "job_title", "follow_up_date", "next_action"]], hide_index=True)
            else:
                st.write("No follow-ups due for current scope.")
        with col_b:
            st.markdown("#### Blockers")
            blockers = mc.get("blockers", [])
            if blockers:
                for b in blockers[:8]:
                    st.warning(f"{b.get('company_name')} — {b.get('blocked_reason') or b.get('pipeline_stage')}")
            else:
                st.success("No blocked cards.")

    with mc_sections[4]:
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
            st.info("Select a company and role in the **sidebar** to enable brief generation.")
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
    _feature_caption("Company 360")
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
    for w in get_confidence_warnings(
        icc_company_id, profiles_df, people_df, sources_df,
        projects_df=projects_df, insights_df=insights_df,
    ):
        st.caption(w)
    src_url = c360.get("sources", [{}])[0].get("source_url") if c360.get("sources") else ""
    footer_chips = [
        render_source_chip(src_url, conf),
        render_freshness_badge(lu),
        f'<span class="ci-chip ci-chip-metric">{src_count} research sources</span>',
    ]
    render_metadata_ribbon(footer_chips)
    render_source_freshness_badge(lu, src_url)

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
        display_dataframe_limited(proj_subset[["theme", "description", "confidence_level", "source_type"]])
        if metadata_detailed:
            for _, prow in proj_subset.iterrows():
                render_metadata_expander(
                    f"Metadata — {prow.get('theme', 'Project')}",
                    {
                        "confidence_level": prow.get("confidence_level"),
                        "source_type": prow.get("source_type"),
                        "last_updated": prow.get("last_updated", lu),
                    },
                )

    c1, c2 = st.columns(2)
    c1.metric("Contacts Mapped", c360["people_count"])
    c2.metric("Verified Contacts", c360["verified_people"])

    st.markdown("#### Research Sources")
    src_subset = sources_df[sources_df["company_id"] == icc_company_id]
    if not src_subset.empty:
        display_dataframe_limited(src_subset[["source_type", "source_title", "source_url", "verified"]])

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
    _feature_caption("People Map")
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
        for p in ranked[:5]:
            hp = p.get("hiring_power_score", 0)
            chips = [
                render_source_chip(p.get("source_url"), p.get("verification_status")),
                render_freshness_badge(p.get("last_updated")),
                f'<span class="ci-chip ci-chip-metric">Hiring power {hp}</span>',
            ]
            render_entity_card(
                "person",
                p,
                title_key="person_name",
                body_key="strategy",
                ribbon_chips=chips,
            )
            if metadata_detailed:
                st.markdown(render_confidence_bar(hp, f"Hiring power {hp}"), unsafe_allow_html=True)
        for p in ranked[:3]:
            with st.expander(f"{p.get('person_name')} — {p.get('contact_type')}"):
                st.write(f"**Strategy:** {p.get('strategy', '')}")
                st.markdown(f"[Search Query URL]({p.get('search_query_url', '')})")

    with st.expander("People Map Research Prompt"):
        st.code(generate_people_research_prompt(icc_company_id), language="markdown")


def tab_role_deep_dive():
    title = icc_job_row["title"] if icc_job_row is not None else ""
    st.subheader(f"Role Deep Dive — {title}")
    _feature_caption("Role Deep Dive")
    if not icc_job_id:
        st.info("Select a target role in the sidebar.")
        return

    dive = build_role_deep_dive(icc_job_id, jobs_df, reasoning_df)
    rr_row = reasoning_df[reasoning_df["job_id"] == icc_job_id] if not reasoning_df.empty else pd.DataFrame()
    conf_level = "source_backed" if not rr_row.empty else "hypothesis"
    tools_signal = icc_job_row.get("role_family", "") if icc_job_row is not None else ""
    render_metadata_ribbon([
        f'<span class="ci-chip ci-chip-metric">Confidence: {conf_level}</span>',
        f'<span class="ci-chip ci-chip-metric">Tools: {tools_signal}</span>',
        render_source_chip(
            sources_df.iloc[0]["source_url"] if not sources_df.empty else None,
            conf_level,
        ),
    ])
    st.write(f"**Why this role exists:** {dive.get('why_role_exists', '')}")
    st.write(f"**Business problem:** {dive.get('business_problem', '')}")
    if metadata_detailed:
        render_metadata_expander("Role reasoning metadata", {
            "confidence_level": conf_level,
            "tools_signal": tools_signal,
            "business_problem": dive.get("business_problem", ""),
            "likely_team": dive.get("likely_team", ""),
        })
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
    _feature_caption("Proof Assets")
    st.caption(f"{icc_company_name} · {icc_job_row['title'] if icc_job_row is not None else 'N/A'}")

    if proof_df.empty:
        st.warning("No proof assets loaded. Add entries to proof_assets.csv.")
        return

    st.markdown("#### Portfolio Assets")
    display_dataframe_limited(proof_df[["asset_type", "title", "tags", "url_or_path", "relevance_score"]])

    st.divider()
    st.markdown("#### Top 3 Assets for This Role")
    top3 = get_top_proof_assets_for_display(icc_job_id, icc_company_id, proof_df, jobs_df, profiles_df, n=3)
    for i, asset in enumerate(top3, 1):
        skills = asset.get("tags", asset.get("skills_proven", ""))
        render_entity_card(
            "proof_asset",
            asset,
            ribbon_chips=[
                f'<span class="ci-chip ci-chip-metric">Match {asset.get("match_score", "")}</span>',
                f'<span class="ci-chip ci-chip-metric">Score {asset.get("relevance_score", "")}</span>',
                render_freshness_badge(asset.get("last_updated")),
            ],
        )
        if metadata_detailed:
            render_metadata_expander(f"Asset metadata — {asset.get('title', i)}", {
                "skills_proven": skills,
                "role_families_supported": asset.get("role_families_supported", icc_job_row.get("role_family") if icc_job_row is not None else ""),
                "status": asset.get("status", "active"),
                "demo_instruction": asset.get("demo_instruction", asset.get("url_or_path", "")),
            })
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
    st.caption(f"Scope: **{icc_scope_label}** · Change target in sidebar")
    display_rank = company_rank_df.copy()
    display_rank["selected"] = display_rank["company"] == icc_company_name
    if icc_focus_mode and icc_company_name:
        selected_row = display_rank[display_rank["selected"]]
        other_rows = display_rank[~display_rank["selected"]].head(10)
        display_rank = pd.concat([selected_row, other_rows]).drop_duplicates(subset=["company"])
    st.dataframe(
        display_rank[["company", "industry", "location", "priority_score", "priority_label", "job_count", "contact_count", "selected"]].head(10),
        use_container_width=True,
        hide_index=True,
        column_config={
            "selected": st.column_config.CheckboxColumn("Target", disabled=True),
            "priority_score": st.column_config.NumberColumn("Priority", format="%.1f"),
        },
    )
    if len(display_rank) > 10:
        with st.expander(f"Show all ({len(display_rank)} companies)"):
            st.dataframe(
                display_rank[["company", "industry", "location", "priority_score", "priority_label", "job_count", "contact_count", "selected"]],
                use_container_width=True,
                hide_index=True,
            )
    st.bar_chart(company_rank_df.set_index("company")["priority_score"].head(15))


def tab_role_fit():
    st.subheader("Role Fit Scores")
    _feature_caption("Role Fit")
    display_dataframe_limited(filtered_scores.sort_values("fit_score", ascending=False))

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
        if icc_focus_mode and icc_company_name and s["company_name"] != icc_company_name:
            continue
        sd = s.get("sponsorship_detail", {})
        sponsor_rows.append({
            "company": s["company_name"], "title": s["title"],
            "signal_score": sd.get("score", 0), "label": sd.get("label", ""),
            "disclaimer": sd.get("disclaimer", ""),
        })
    st.dataframe(pd.DataFrame(sponsor_rows).sort_values("signal_score", ascending=False), use_container_width=True, hide_index=True)


def tab_networking():
    st.subheader("Networking Map")
    if icc_focus_mode and icc_company_name:
        st.caption(f"Showing contacts for **{icc_company_name}**")
    contact_type_filter = st.multiselect(
        "Contact Type", options=["recruiter", "hiring_manager", "peer", "alumni"],
        default=["recruiter", "hiring_manager"], key="net_filter",
    )
    filtered_outreach = [o for o in outreach if o["contact_type"] in contact_type_filter]
    if icc_focus_mode and icc_company_name:
        filtered_outreach = [o for o in filtered_outreach if o["company_name"] == icc_company_name]
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
    _feature_caption("Recommendations")
    rec_display = rec_df.copy()
    if icc_focus_mode and icc_company_name:
        rec_display = rec_display[rec_display["company_name"] == icc_company_name]
        st.caption(f"Scoped to **{icc_company_name}**")
    display_dataframe_limited(
        rec_display[["company_name", "title", "fit_score", "action", "composite_score", "rationale"]].sort_values(
            "composite_score", ascending=False,
        ),
    )


def tab_export():
    st.subheader("Export & SQL Analytics")
    export_scores = scores_df.copy()
    export_recs = rec_df.copy()
    if icc_focus_mode and icc_company_name:
        export_scores = export_scores[export_scores["company"] == icc_company_name]
        export_recs = export_recs[export_recs["company_name"] == icc_company_name]
        st.caption(f"Exports scoped to **{icc_company_name}**")
    st.download_button("Download Scores CSV", export_scores.to_csv(index=False), "role_fit_scores.csv", "text/csv")
    st.download_button("Download Recommendations CSV", export_recs.to_csv(index=False), "recommendations.csv", "text/csv")

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


def tab_profile_portfolio():
    st.subheader("My Profile & Portfolio")
    _feature_caption("My Profile & Portfolio")
    st.caption("In-app profile — used automatically by Interview Simulator")

    profile = load_profile()
    summary = get_portfolio_summary(icc_company_id if icc_focus_mode else None, profile)
    profile_path = ROOT / "data" / "user_profile.yaml"
    last_edited = "—"
    if profile_path.exists():
        last_edited = datetime.fromtimestamp(profile_path.stat().st_mtime).strftime("%Y-%m-%d")
    proof_ids = profile.get("proof_asset_ids", [])
    char_counts = sum(len(str(v)) for v in [
        profile.get("positioning", ""),
        " ".join(profile.get("experience_bullets", [])),
    ])
    render_metadata_ribbon([
        render_freshness_badge(last_edited),
        f'<span class="ci-chip ci-chip-metric">{len(proof_ids)} proof links</span>',
        f'<span class="ci-chip ci-chip-metric">{char_counts} chars</span>',
    ])

    with st.form("profile_edit_form"):
        name = st.text_input("Name", value=profile.get("name", ""))
        headline = st.text_input("Headline", value=profile.get("headline", ""))
        positioning = st.text_area("Positioning", value=profile.get("positioning", ""), height=80)
        skills = st.text_input("Skills (comma-separated)", value=", ".join(profile.get("skills", [])))
        education = st.text_input("Education", value=profile.get("education", ""))
        opt_status = st.text_input("Work authorization", value=profile.get("opt_status", ""))
        bullets_text = st.text_area(
            "Experience bullets (one per line)",
            value="\n".join(profile.get("experience_bullets", [])),
            height=120,
        )
        if st.form_submit_button("Save Profile", type="primary"):
            updated = dict(profile)
            updated.update({
                "name": name,
                "headline": headline,
                "positioning": positioning,
                "skills": [s.strip() for s in skills.split(",") if s.strip()],
                "education": education,
                "opt_status": opt_status,
                "experience_bullets": [b.strip() for b in bullets_text.splitlines() if b.strip()],
            })
            path = save_profile(updated)
            st.success(f"Profile saved to {path.name}")
            st.rerun()

    st.divider()
    st.markdown("#### Linked Proof Assets")
    assets = summary.get("proof_assets", [])
    if assets:
        for asset in assets:
            with st.expander(asset.get("title", "Asset")):
                st.write(asset.get("description", ""))
                link = asset.get("url_or_path", "")
                if link:
                    st.caption(f"Demo: `{link}`")
    else:
        st.info("Add proof_asset_ids to user_profile.yaml")

    st.markdown("#### 60-Second Pitch")
    pitch = summary.get("sixty_second_pitch", build_sixty_second_pitch(profile))
    st.text_area("Pitch preview", pitch, height=120, key="pitch_preview")
    copy_to_clipboard_button(pitch, "pitch_copy")

    highlights = summary.get("resume_highlights", "")
    if highlights:
        st.markdown("#### Resume Highlights (upload)")
        st.text(highlights[:2000])
    else:
        st.caption("Optional: add `data/uploads/resume_highlights.txt` (gitignored)")


def tab_interview_simulator():
    st.subheader("Interview Practice Simulator")
    _feature_caption("Interview Simulator")
    st.markdown('<span id="interview-simulator"></span>', unsafe_allow_html=True)

    if not selection_complete:
        st.warning("Select **Target Company** and **Target Role** in the sidebar to start.")
        return

    round_options = [
        ("recruiter_screen", "Recruiter Screen"),
        ("hm_screen", "Hiring Manager Screen"),
        ("technical", "Technical Interview"),
        ("behavioral", "Behavioral Interview"),
        ("final", "Final Round"),
    ]
    round_labels = [r[1] for r in round_options]
    round_map = {label: key for key, label in round_options}

    sim_round = st.selectbox("Interview Round", options=round_labels, key="sim_round_select")
    round_key = round_map[sim_round]

    role_family = icc_job_row["role_family"] if icc_job_row is not None else "Technology Analyst"
    insights = load_interview_insights(icc_company_id, role_family, round_key)
    company_dict = icc_ctx["company_row"].to_dict() if icc_ctx.get("company_row") is not None else {
        "company_id": icc_company_id, "company_name": icc_company_name,
    }
    job_dict = icc_job_row.to_dict() if icc_job_row is not None else {}
    profile = load_profile()
    proof_list = get_portfolio_summary(icc_company_id, profile).get("proof_assets", [])

    context = build_simulator_context(
        company_dict,
        job_dict,
        profile,
        insights,
        proof_list,
        reasoning_df=reasoning_df,
        jobs_df=jobs_df,
    )
    context["round"] = round_key

    st.caption(f"{icc_company_name} · {icc_ctx['job_title']} · {len(insights)} verified questions for this round/role")

    ctx_col, src_col = st.columns([2, 1])
    with ctx_col:
        st.markdown("#### Context")
        st.write(f"**Company themes:** {context.get('company_themes', '')[:200]}")
        st.write("**Your bullets:**")
        for b in profile.get("experience_bullets", [])[:3]:
            st.write(f"- {b}")
        st.write("**Proof to mention:**")
        for p in proof_list[:3]:
            st.write(f"- {p.get('title', '')}")

    with src_col:
        st.markdown("#### Verified Sources")
        if insights:
            for ins in insights[:8]:
                title = ins.get("source_title", "Source")[:40]
                url = ins.get("source_url", "")
                st.markdown(f"- [{title}]({url})")
                render_source_freshness_badge(ins.get("last_verified"), url)
        else:
            st.warning("No verified insights for this filter — check interview_insights.csv")

    if "sim_history" not in st.session_state:
        st.session_state.sim_history = []
    if "sim_questions" not in st.session_state:
        st.session_state.sim_questions = []

    if st.button("Start New Question", type="primary", key="sim_new_q"):
        q = generate_recruiter_question(context, round_key, st.session_state.sim_history)
        insight_row = _pick_sim_insight(insights, st.session_state.sim_history, round_key)
        st.session_state.sim_current_question = q
        st.session_state.sim_current_insight = insight_row
        st.session_state.sim_questions.append(q)

    if st.button("Reset Session", key="sim_reset"):
        st.session_state.sim_history = []
        st.session_state.sim_questions = []
        st.session_state.pop("sim_current_question", None)
        st.session_state.pop("sim_current_insight", None)
        st.rerun()

    current_q = st.session_state.get("sim_current_question")
    if current_q:
        with st.chat_message("assistant"):
            st.write(current_q)
            ins = st.session_state.get("sim_current_insight")
            if ins:
                meta_parts = []
                if ins.get("source_url"):
                    st.caption(f"Source: [{ins.get('source_title', 'link')}]({ins.get('source_url')})")
                if ins.get("source_type"):
                    meta_parts.append(f"Type: {ins['source_type']}")
                if ins.get("difficulty"):
                    meta_parts.append(f"Difficulty: {ins['difficulty']}")
                if ins.get("last_verified"):
                    meta_parts.append(f"Verified: {ins['last_verified']}")
                if meta_parts:
                    st.caption(" · ".join(meta_parts))
                if metadata_detailed:
                    render_metadata_ribbon([
                        render_source_chip(ins.get("source_url"), ins.get("confidence_level")),
                        render_freshness_badge(ins.get("last_verified")),
                        f'<span class="ci-chip ci-chip-metric">{ins.get("difficulty", "—")}</span>',
                    ])

    answer = st.chat_input("Type your answer…")
    if answer and current_q:
        with st.chat_message("user"):
            st.write(answer)
        feedback = generate_feedback(
            answer,
            current_q,
            context,
            st.session_state.get("sim_current_insight"),
        )
        with st.chat_message("assistant"):
            st.markdown(feedback)
        st.session_state.sim_history.append({
            "question": current_q,
            "answer": answer,
            "insight_id": (st.session_state.get("sim_current_insight") or {}).get("insight_id"),
        })
        st.session_state.pop("sim_current_question", None)

    if st.session_state.sim_questions and st.button("Save Session", key="sim_save"):
        sid = save_simulator_session(
            icc_company_id,
            icc_company_name,
            icc_job_id,
            role_family,
            round_key,
            st.session_state.sim_questions,
            notes=f"{len(st.session_state.sim_history)} Q&A exchanges",
        )
        st.success(f"Session saved: {sid}")


def _pick_sim_insight(insights, history, round_key):
    from src.interview_simulator import _pick_insight_question
    return _pick_insight_question(insights, history, round_key)


# ── Render active navigation group only (lazy tab rendering) ─────────────────

TAB_RENDERERS = {
    "Mission Control": ("mission_control_engine", "Run scripts/seed_pipeline_cards.py and check pipeline CSVs", tab_mission_control),
    "My Profile & Portfolio": ("profile_manager", "Check data/user_profile.yaml and PyYAML", tab_profile_portfolio),
    "Interview Simulator": ("interview_simulator", "Check data/interview_insights.csv", tab_interview_simulator),
    "Command Center": ("conversation_brief_generator", "Check ICC CSV files and brief generator imports", tab_command_center),
    "Company 360": ("company_profile_engine", "Verify company_profiles.csv and company_projects.csv", tab_company_360),
    "People Map": ("people_power_mapper", "Verify people_map.csv schema and contact types", tab_people_map),
    "Role Deep Dive": ("role_reasoning_engine", "Verify role_reasoning.csv covers all job IDs", tab_role_deep_dive),
    "Proof Assets": ("proof_asset_mapper", "Verify proof_assets.csv exists with asset entries", tab_proof_assets),
    "Overview": ("data_loader", "Check core CSV files in data/", tab_overview),
    "Company Ranking": ("company_priority_scorer", "Verify sample_companies.csv and jobs data", tab_company_ranking),
    "Role Fit": ("role_fit_scorer", "Check profile_keywords.csv and scoring module", tab_role_fit),
    "Sponsorship Signal": ("sponsorship_signal", "Verify sponsorship fields in company data", tab_sponsorship),
    "Networking Map": ("outreach_angle_generator", "Check contacts CSV and outreach generator", tab_networking),
    "Interview Prep": ("interview_topic_mapper", "Verify jobs data and interview topic mapper", tab_interview_prep),
    "Recommendations": ("recommendation_engine", "Check scoring pipeline output", tab_recommendations),
    "Export": ("db", "Verify SQLite init and DEMO_QUERIES", tab_export),
    "Conversation Feedback": ("conversation_feedback_analyzer", "Check conversation_log_template.csv", tab_feedback),
}

active_tabs = NAV_GROUPS[nav_group]
if len(active_tabs) == 1:
    name = active_tabs[0]
    module, hint, renderer = TAB_RENDERERS[name]
    safe_tab(module, hint, renderer)
else:
    sub_tabs = st.tabs(active_tabs)
    for tab_obj, name in zip(sub_tabs, active_tabs):
        module, hint, renderer = TAB_RENDERERS[name]
        with tab_obj:
            safe_tab(module, hint, renderer)

if nav_group == "Tools" and "Interview Prep" in active_tabs:
    st.caption("Tip: For interactive practice, use **Prepare → Interview Simulator**.")

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
