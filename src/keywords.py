"""Backward-compatible keywords — delegates to keyword_extractor."""

from src.keyword_extractor import SKILL_TAXONOMY, categorize_keywords, extract_keywords, keyword_summary

__all__ = ["SKILL_TAXONOMY", "categorize_keywords", "extract_keywords", "keyword_summary"]
