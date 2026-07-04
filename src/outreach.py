"""Backward-compatible outreach — delegates to outreach_angle_generator."""

from src.outreach_angle_generator import generate_outreach, generate_outreach_batch

__all__ = ["generate_outreach", "generate_outreach_batch"]
