"""H-1B/PERM sponsorship signal scoring — signal only, not legal certainty."""

SPONSOR_POSITIVE = [
    "h1b", "h-1b", "perm", "sponsor", "dol", "uscis", "mega tech center",
    "large dfw", "expansion", "campus",
]
SPONSOR_CAUTION = [
    "must be verified", "validation required", "check in dol", "signal only",
    "not legal certainty", "validate sponsorship",
]


def score_sponsorship(visa_notes: str = "", sponsor_signal: str = "") -> dict:
    """Return sponsorship signal score 0-100 with disclaimer."""
    text = f"{visa_notes} {sponsor_signal}".lower()
    score = 50.0
    signals_found = []

    for phrase in SPONSOR_POSITIVE:
        if phrase in text:
            score += 8
            signals_found.append(phrase)

    for phrase in SPONSOR_CAUTION:
        if phrase in text:
            score -= 3

    score = max(0, min(100, round(score, 1)))

    if score >= 70:
        label = "Strong Signal"
    elif score >= 50:
        label = "Moderate Signal"
    else:
        label = "Weak Signal"

    return {
        "score": score,
        "label": label,
        "signals_found": signals_found,
        "disclaimer": "Signal only — not legal certainty. Verify via DOL/USCIS and employer.",
    }
