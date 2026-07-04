"""Ghost job and noise detection heuristics."""

GHOST_SIGNS = [
    "we are seeking a",
    "responsibilities include building data pipelines",
    "must have python, sql, cloud platforms",
    "preferred: experience with data analytics",
]

VAGUE_TITLES = ["analyst", "specialist", "associate"]


def detect_noise(description: str, title: str = "") -> dict:
    """Detect signs of templated or low-quality job postings."""
    desc_lower = (description or "").lower()
    title_lower = (title or "").lower()
    flags = []

    for sign in GHOST_SIGNS:
        if sign in desc_lower:
            flags.append(f"template_phrase:{sign[:30]}")

    if len(desc_lower) < 200:
        flags.append("short_description")

    if desc_lower.count("python") > 3:
        flags.append("keyword_stuffing")

    word_count = len(desc_lower.split())
    unique_ratio = len(set(desc_lower.split())) / max(word_count, 1)
    if unique_ratio < 0.4 and word_count > 50:
        flags.append("low_uniqueness")

    risk_score = min(len(flags) * 20, 100)

    return {
        "risk_score": risk_score,
        "risk_label": "High Noise" if risk_score >= 60 else "Moderate" if risk_score >= 30 else "Low Noise",
        "flags": flags,
        "is_likely_ghost": risk_score >= 60,
    }
