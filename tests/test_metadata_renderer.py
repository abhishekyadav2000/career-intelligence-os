"""Tests for metadata_renderer helpers."""

from src.metadata_renderer import (
    format_freshness_label,
    render_confidence_bar,
    render_freshness_badge,
    render_source_chip,
)


def test_render_source_chip_with_url():
    html = render_source_chip("https://example.com/careers", "verified_public")
    assert "https://example.com/careers" in html
    assert "ci-chip-source" in html


def test_render_source_chip_without_url():
    html = render_source_chip(None, "placeholder")
    assert "unverified" in html
    assert "ci-chip-neutral" in html


def test_render_freshness_badge_recent():
    html = render_freshness_badge("2026-07-01")
    assert "Updated" in html
    assert "ci-chip" in html


def test_format_freshness_label_unknown():
    assert "unknown" in format_freshness_label(None).lower()


def test_render_confidence_bar_bounds():
    html = render_confidence_bar(85, "High")
    assert "width:85" in html
    html_low = render_confidence_bar(-5, "Low")
    assert "width:0" in html_low
