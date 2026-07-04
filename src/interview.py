"""Backward-compatible interview prep — delegates to interview_topic_mapper."""

from src.interview_topic_mapper import generate_interview_batch, generate_interview_topics

__all__ = ["generate_interview_batch", "generate_interview_topics"]
