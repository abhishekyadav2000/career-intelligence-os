# Interview Packet: AI Automation Analyst

**Role Family:** AI Automation Analyst  
**Universal Profile Fit:** Enterprise Technology Analyst — AI Automation, Cloud Security & Data Analytics  
**Typical Employers:** JPMorgan Chase, Citi, Goldman Sachs, Bank of America, Capital One, Cognizant

---

## Role Summary

AI automation analysts design, evaluate, and implement automated workflows — often involving LLM-powered agents, RPA, data pipeline automation, and governance controls. Enterprise roles require balancing innovation with risk management, audit logging, and human-in-the-loop design.

---

## Key Skills to Demonstrate

| Skill | Portfolio Evidence |
|-------|-------------------|
| Automation pipeline design | CI OS modular Python pipeline |
| AI risk assessment | AI Agent Risk Scoring — 8-category taxonomy |
| Prompt engineering (templates) | `/prompts/` directory — 4 agent templates |
| Rule-based vs LLM tradeoffs | CI OS deliberately rule-based; prompts show LLM integration path |
| Guardrail design | AI risk scoring guardrail checklist |
| Governance awareness | `docs/ai-safety-and-privacy.md` |

---

## Technical Questions (Prepare Answers)

1. **"How would you evaluate an AI agent before production?"**
   → 8-category risk taxonomy: prompt injection, output validation, data leakage, autonomy boundary, audit, rate limiting, human-in-the-loop, model drift. Score 0–100.

2. **"What's the difference between RPA and AI automation?"**
   → RPA = rule-based, structured tasks; AI automation = LLM/ML-powered, handles unstructured input. CI OS uses rule-based scoring today; prompt templates show LLM extension.

3. **"How do you prevent prompt injection?"**
   → Input sanitization, system prompt hardening, output schema validation, adversarial test cases. Reference AI risk scoring Category 1.

4. **"Describe an automation workflow you built."**
   → CI OS pipeline: CSV ingest → validate → score → recommend → outreach/interview generate → dashboard display. Fully automated except human review of recommendations.

5. **"What guardrails matter most for enterprise AI?"**
   → Human-in-the-loop for write actions, audit logging, output validation, rate limiting, PII redaction. Walk through guardrail checklist.

---

## Business Questions

1. "How do you measure ROI on automation projects?"
2. "How do you get stakeholder buy-in for AI automation?"
3. "What's your approach to change management when automating a manual process?"
4. "How do you handle failure modes in automated workflows?"

---

## Behavioral Questions (STAR Format)

| Question | Suggested Story Angle |
|----------|----------------------|
| Automation you built | CI OS end-to-end pipeline |
| Risk you identified in an AI project | AI Agent Risk Scoring — autonomy boundary category |
| Stakeholder resisted automation | Recommendation engine — "network first" vs "apply now" shows human judgment |
| Learning about AI governance | Built risk framework as portfolio artifact |

---

## Questions to Ask Them

1. "What automation tools/platforms does your team use?"
2. "How does your organization govern AI/LLM deployments?"
3. "What's the balance between build vs. buy for automation?"
4. "How do you measure automation success?"

---

## Portfolio Demo Path (3 min)

CI OS pipeline overview → AI Agent Risk Scoring rubric → Prompt templates (show where LLM would plug in)

---

## Key Message

"I built a working automation pipeline today with rule-based modules. I've also designed the risk framework for when LLM agents are added — because enterprise automation requires governance, not just capability."
