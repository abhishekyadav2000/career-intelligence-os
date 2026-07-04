# AI Safety and Privacy

## Principles

1. **No legal claims** — Sponsorship signals are heuristic indicators, not immigration advice.
2. **No PII exposure** — Sample contacts use placeholder names; no real LinkedIn profiles stored.
3. **No external API calls in MVP** — All intelligence is rule-based and local.
4. **Transparent scoring** — Every score includes category breakdown and rationale.
5. **User control** — CSV export lets users own their data.

## Sponsorship Signal Disclaimer

All sponsorship-related outputs include:

> Signal only — not legal certainty. Verify via DOL/USCIS and employer.

This disclaimer appears in:
- Dashboard sponsorship tab
- `src/sponsorship_signal.py` output
- Job `visa_notes` field

## Data Handling

| Data Type | Storage | Retention |
|-----------|---------|-----------|
| Company/job CSVs | Local `data/` | Static sample data |
| Contact placeholders | Local CSV | Sample only |
| SQLite analytics DB | Local `data/career_intel.db` | Regenerated on load |
| User filters/exports | Browser session | Not persisted |

## Future LLM Integration Guardrails

When LLM agents are added (see `prompts/`):

- No automated LinkedIn messaging
- No scraping of personal profiles
- Human review required before any outreach send
- Rate limiting on API calls
- Prompt injection protection on job description inputs
- Audit log of all LLM-generated content

## Privacy Compliance Notes

- MVP does not collect user data
- No cookies, analytics, or tracking
- `.env` for local config only — never commit secrets
- `data/career_intel.db` is gitignored
