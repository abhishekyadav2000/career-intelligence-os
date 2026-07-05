"""Reusable metadata UI helpers for Career Intelligence OS dashboard."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import streamlit as st

from src.data_confidence import (
    confidence_badge_label,
    format_source_freshness_badge,
    is_stale,
    parse_date,
)

METADATA_CSS = """
<style>
    .ci-chip {
        display: inline-block;
        padding: 0.12rem 0.45rem;
        border-radius: 4px;
        font-size: 0.72rem;
        font-weight: 600;
        margin-right: 0.35rem;
        margin-bottom: 0.25rem;
        letter-spacing: 0.02em;
    }
    .ci-chip-source { background: #1e3a5f; color: #7dd3fc; }
    .ci-chip-fresh { background: #064e3b; color: #6ee7b7; }
    .ci-chip-stale { background: #78350f; color: #fcd34d; }
    .ci-chip-danger { background: #7f1d1d; color: #fca5a5; }
    .ci-chip-neutral { background: #334155; color: #cbd5e1; }
    .ci-chip-metric { background: #1e293b; color: #93c5fd; border: 1px solid #475569; }
    .ci-metadata-ribbon {
        display: flex;
        flex-wrap: wrap;
        gap: 0.35rem;
        margin-top: 0.5rem;
        padding-top: 0.45rem;
        border-top: 1px solid #334155;
        font-size: 0.75rem;
    }
    .ci-entity-card {
        background: #0f172a;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 0.85rem 1rem;
        margin-bottom: 0.65rem;
    }
    .ci-entity-card h4 {
        margin: 0 0 0.35rem 0;
        color: #f8fafc;
        font-size: 0.95rem;
    }
    .ci-entity-card p {
        margin: 0;
        color: #94a3b8;
        font-size: 0.85rem;
    }
    .ci-conf-bar {
        height: 6px;
        border-radius: 3px;
        background: #334155;
        overflow: hidden;
        margin: 0.25rem 0 0.5rem 0;
    }
    .ci-conf-bar-fill {
        height: 100%;
        border-radius: 3px;
    }
</style>
"""


def inject_metadata_css() -> None:
    """Inject shared metadata styles once per session."""
    if not st.session_state.get("_ci_metadata_css"):
        st.markdown(METADATA_CSS, unsafe_allow_html=True)
        st.session_state._ci_metadata_css = True


def _freshness_class(last_updated: str | None) -> str:
    if is_stale(last_updated):
        return "ci-chip-stale"
    parsed = parse_date(last_updated)
    if parsed is None:
        return "ci-chip-neutral"
    days = (datetime.now() - parsed).days
    if days <= 14:
        return "ci-chip-fresh"
    if days <= 30:
        return "ci-chip-stale"
    return "ci-chip-danger"


def format_freshness_label(last_updated: str | None) -> str:
    if not last_updated or str(last_updated).strip() in ("", "TBD", "N/A"):
        return "Updated: unknown"
    parsed = parse_date(last_updated)
    if parsed is None:
        return f"Updated: {last_updated}"
    return f"Updated {parsed.strftime('%b %d')}"


def render_source_chip(source_url: str | None, confidence_level: str | None = None) -> str:
    """HTML badge with optional link for a data source."""
    conf = confidence_badge_label(confidence_level or "source_backed")
    if source_url and str(source_url).strip().startswith("http"):
        safe_url = str(source_url).strip()
        return (
            f'<a href="{safe_url}" target="_blank" rel="noopener" '
            f'class="ci-chip ci-chip-source">Source ({conf})</a>'
        )
    return f'<span class="ci-chip ci-chip-neutral">Source: unverified</span>'


def render_freshness_badge(last_updated: str | None) -> str:
    """HTML freshness badge — green/amber/red."""
    css = _freshness_class(last_updated)
    label = format_freshness_label(last_updated)
    return f'<span class="ci-chip {css}">{label}</span>'


def render_confidence_bar(score: int | float, label: str = "") -> str:
    """HTML horizontal confidence bar for scores 0–100."""
    value = max(0, min(100, float(score or 0)))
    if value >= 70:
        color = "#059669"
    elif value >= 40:
        color = "#d97706"
    else:
        color = "#dc2626"
    title = label or f"{value:.0f}%"
    return (
        f'<div title="{title}">'
        f'<div class="ci-conf-bar"><div class="ci-conf-bar-fill" '
        f'style="width:{value}%;background:{color};"></div></div>'
        f'</div>'
    )


def render_metadata_ribbon(chips: list[str]) -> None:
    """Render a row of HTML metadata chips."""
    if not chips:
        return
    inject_metadata_css()
    inner = "".join(chips)
    st.markdown(f'<div class="ci-metadata-ribbon">{inner}</div>', unsafe_allow_html=True)


def render_metadata_expander(title: str, metadata: dict[str, Any], *, expanded: bool = False) -> None:
    """Collapsible key-value metadata panel."""
    if not metadata:
        return
    with st.expander(title, expanded=expanded):
        for key, value in metadata.items():
            if value is None or str(value).strip() in ("", "nan", "None"):
                continue
            st.markdown(f"**{key.replace('_', ' ').title()}:** {value}")


def render_entity_card(
    entity_type: str,
    data: dict[str, Any],
    *,
    title_key: str = "title",
    body_key: str = "description",
    metadata: dict[str, Any] | None = None,
    ribbon_chips: list[str] | None = None,
) -> None:
    """Unified card with optional metadata footer ribbon."""
    inject_metadata_css()
    title = data.get(title_key) or data.get("person_name") or data.get("company_name") or entity_type
    body = data.get(body_key) or data.get("next_action") or ""
    st.markdown(
        f'<div class="ci-entity-card">'
        f'<h4>{title}</h4>'
        f'<p>{body[:240]}{"…" if len(str(body)) > 240 else ""}</p>'
        f'</div>',
        unsafe_allow_html=True,
    )
    chips = list(ribbon_chips or [])
    if metadata:
        for k, v in metadata.items():
            if v is not None and str(v).strip():
                chips.append(f'<span class="ci-chip ci-chip-metric">{k}: {v}</span>')
    render_metadata_ribbon(chips)


def render_action_metadata(row: dict[str, Any], *, detailed: bool = True) -> None:
    """Metadata chips for Mission Control action queue rows."""
    chips: list[str] = []
    if row.get("fit_score") is not None:
        chips.append(f'<span class="ci-chip ci-chip-metric">Fit {row["fit_score"]}</span>')
    if row.get("priority_score") is not None:
        chips.append(f'<span class="ci-chip ci-chip-metric">Priority {row["priority_score"]}</span>')
    if row.get("sponsorship_signal") is not None:
        chips.append(f'<span class="ci-chip ci-chip-metric">Sponsor {row["sponsorship_signal"]}</span>')
    if row.get("proof_asset_count") is not None:
        chips.append(f'<span class="ci-chip ci-chip-metric">Proof {row["proof_asset_count"]}</span>')
    if detailed and row.get("last_updated"):
        chips.append(render_freshness_badge(row.get("last_updated")))
    if detailed and row.get("source_url_count"):
        chips.append(f'<span class="ci-chip ci-chip-source">{row["source_url_count"]} sources</span>')
    render_metadata_ribbon(chips)


def render_section_header(title: str, count: int | None = None, *, help_text: str | None = None) -> None:
    """Section header with optional count badge."""
    suffix = f" ({count})" if count is not None else ""
    st.markdown(f"#### {title}{suffix}")
    if help_text:
        st.caption(help_text)


def display_dataframe_limited(
    df,
    *,
    default_rows: int = 10,
    key_prefix: str = "df",
    **kwargs,
) -> None:
    """Show top N rows with optional Show all expander."""
    if df is None or df.empty:
        return
    st.dataframe(df.head(default_rows), use_container_width=True, hide_index=True, **kwargs)
    if len(df) > default_rows:
        with st.expander(f"Show all ({len(df)} rows)"):
            st.dataframe(df, use_container_width=True, hide_index=True, **kwargs)


def render_empty_line(message: str = "") -> None:
    """Single-line empty state — no big info boxes."""
    if message:
        st.caption(message)
