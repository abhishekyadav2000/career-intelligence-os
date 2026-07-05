# Interview Practice Simulator Guide

## Quick Start (No LLM Required)

1. Open the dashboard: `streamlit run dashboard/app.py`
2. Select **Target Company** and **Target Role** in the sidebar (e.g., JPMorgan Chase)
3. Go to **Interview Simulator** tab
4. Choose interview round (Recruiter, HM, Technical, Behavioral, Final)
5. Answer each question in the chat — feedback is rule-based from verified `interview_insights.csv`

The simulator **never invents questions** without a source URL. All rule-based questions come from `data/interview_insights.csv`.

## Context Panel

Before practicing, review:

- Company themes from Company 360
- Role fit from role reasoning
- Your profile bullets and STAR stories
- Proof assets to mention

## Verified Sources Sidebar

Each question links to its public source (Glassdoor, careers site, etc.). Refresh insights via the research workflow — see `docs/research-enrichment-workflow.md`.

## Session History

Sessions append to `data/simulator_sessions.csv` with date, company, role, round, and questions asked.

## Optional LLM Enhancement

Copy `.env.example` to `.env` and configure **one** of:

### Ollama (local-first)

```bash
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

Start Ollama: `ollama serve` then `ollama pull llama3.2`

### OpenAI-compatible API

```bash
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://api.openai.com/v1   # optional
OPENAI_MODEL=gpt-4o-mini                     # optional
```

When configured, the simulator enhances question phrasing and feedback. **Rule-based mode always works offline** if LLM calls fail.

## Multi-Round Journey

Mission Control shows **Interview Prep Status** when focused on a company. Track rounds in `data/interview_journey.csv` and link to the Simulator for each round.

## Company Packets

For JPMorgan Chase, the simulator also loads `company-packets/jpmorgan-chase.md` plus company-specific insights.
