"""Backward-compatible scoring — delegates to role_fit_scorer."""

from src.role_fit_scorer import UNIVERSAL_PROFILE, score_jobs_dataframe, score_role_fit

__all__ = ["UNIVERSAL_PROFILE", "score_jobs_dataframe", "score_role_fit"]
