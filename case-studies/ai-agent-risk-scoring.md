# Case Study: AI Agent Risk Scoring

> **Portfolio framework — not production.** This case study documents a scoring rubric and taxonomy for evaluating LLM-powered agent workflows. It connects to Career Intelligence OS gap matrix item **"AI Risk + Agentic Reliability"** and demonstrates risk-aware AI thinking for enterprise technology interviews.

---

## 1. Executive Summary

As enterprises adopt AI agents for automation, analysts need a structured way to evaluate agent workflows before production deployment. This framework defines an **8-category risk taxonomy**, a **0–100 scoring rubric**, and sample evaluation tables — designed as a portfolio artifact that complements Career Intelligence OS's rule-based decision engine.

**Positioning:** Enterprise Technology Analyst — AI Automation, Cloud Security & Data Analytics

---

## 2. Business Problem

LLM-powered agents are being deployed for customer support, code generation, data analysis, and workflow automation — often without standardized risk assessment. Enterprise teams need answers to:

- What can go wrong when an agent acts autonomously?
- How do we score an agent workflow's production readiness?
- Where do guardrails, human review, and audit logging fit?
- How does this connect to GRC and compliance frameworks?

Without a structured rubric, "AI automation" becomes a buzzword rather than a measurable capability.

---

## 3. Risk Taxonomy (8 Categories)

| # | Category | Definition | Example Failure Mode |
|---|----------|------------|---------------------|
| 1 | **Prompt Injection** | Adversarial input manipulates agent behavior | User embeds "ignore previous instructions" in a support ticket |
| 2 | **Output Validation** | Agent produces incorrect, harmful, or non-compliant output | Agent generates SQL that drops a production table |
| 3 | **Data Leakage** | Agent exposes PII, credentials, or proprietary data | RAG pipeline retrieves another user's documents |
| 4 | **Autonomy Boundary** | Agent takes actions beyond its authorized scope | Agent sends emails or modifies records without approval |
| 5 | **Audit & Observability** | Actions are not logged or traceable | No record of what the agent decided or why |
| 6 | **Rate Limiting & Cost** | Unbounded API calls cause cost or availability issues | Agent loops infinitely on a failed tool call |
| 7 | **Human-in-the-Loop** | Critical decisions lack human review checkpoint | Agent auto-approves financial transactions |
| 8 | **Model Drift & Versioning** | Model updates change behavior without re-validation | New model version produces different scoring results |

---

## 4. Scoring Rubric (0–100)

Each category is scored 0–12.5 points (8 × 12.5 = 100).

| Score Range | Label | Criteria |
|-------------|-------|----------|
| 85–100 | Production Ready | All 8 categories have documented controls; human review on critical paths |
| 70–84 | Conditional | Most controls present; 1–2 gaps with documented remediation plan |
| 50–69 | Prototype | Basic guardrails; not suitable for production without hardening |
| 25–49 | Experimental | Significant gaps; demo/proof-of-concept only |
| 0–24 | High Risk | No meaningful controls; do not deploy |

### Per-Category Scoring Guide

| Points | Control Level |
|--------|--------------|
| 0–3 | No control documented |
| 4–6 | Partial control (informal or untested) |
| 7–9 | Control implemented and tested |
| 10–12.5 | Control implemented, tested, monitored, and documented in runbook |

---

## 5. Sample Evaluation Table

**Agent:** Career Intelligence OS — Company Research Agent (hypothetical LLM extension)

| Category | Score | Evidence | Gap |
|----------|-------|----------|-----|
| Prompt Injection | 8/12.5 | Input sanitization on company names; no free-text user prompts in MVP | No adversarial test suite |
| Output Validation | 9/12.5 | Rule-based scoring validates LLM output against schema | LLM not yet integrated |
| Data Leakage | 10/12.5 | Local CSV only; no external API calls in MVP | N/A for current scope |
| Autonomy Boundary | 11/12.5 | Read-only research; no write actions | — |
| Audit & Observability | 7/12.5 | SQLite audit trail for scoring decisions | No agent action logging |
| Rate Limiting | 6/12.5 | Not applicable in rule-based MVP | Required for LLM integration |
| Human-in-the-Loop | 9/12.5 | Recommendations require user review before action | — |
| Model Drift | 5/12.5 | No LLM in production MVP | Version pinning needed for LLM phase |

**Composite Score: 65/100 — Prototype (rule-based MVP); LLM extension requires hardening to reach Conditional (70+).**

---

## 6. Connection to Career Intelligence OS

| CI OS Component | Agent Risk Relevance |
|----------------|---------------------|
| `prompts/company_research_agent.md` | Future LLM agent — needs prompt injection controls |
| `prompts/job_description_agent.md` | Output validation against schema |
| `prompts/networking_agent.md` | Autonomy boundary — no auto-send |
| `prompts/interview_agent.md` | Data leakage — no PII in prompts |
| `recommendation_engine.py` | Human-in-the-loop — user confirms actions |
| `docs/ai-safety-and-privacy.md` | Governance foundation for agent deployment |

The current MVP deliberately uses **rule-based modules** instead of LLM APIs — this is a risk mitigation decision, not a limitation.

---

## 7. Interview Talking Points

1. **"How would you evaluate an AI agent before production?"**
   → Walk through the 8-category taxonomy and 0–100 rubric. Emphasize human-in-the-loop and audit logging.

2. **"What's the biggest risk with LLM automation in enterprise?"**
   → Autonomy boundary + output validation. Agents that act without review or produce unvalidated output.

3. **"How does this connect to your portfolio?"**
   → Career Intelligence OS uses rule-based scoring today. Prompt templates show where LLM agents would plug in — with this risk framework as the gate.

4. **"Prompt injection — how do you defend?"**
   → Input sanitization, system prompt hardening, output schema validation, adversarial test cases.

5. **"This isn't production — why include it?"**
   → Demonstrates risk-aware AI thinking. Enterprise teams need analysts who can evaluate automation readiness, not just build demos.

---

## 8. Guardrail Checklist (Production Readiness)

- [ ] Input sanitization and length limits
- [ ] Output schema validation (JSON/Pydantic)
- [ ] Rate limiting on API calls
- [ ] Human review checkpoint for write actions
- [ ] Audit log for every agent decision
- [ ] PII redaction in prompts and logs
- [ ] Model version pinning and change notification
- [ ] Adversarial test suite (prompt injection cases)
- [ ] Rollback procedure documented
- [ ] Cost monitoring and alerting

---

## 9. Planned Next Steps

1. Build adversarial prompt injection test cases (10 scenarios)
2. Create demo agent with intentional failure modes
3. Integrate scoring rubric into CI OS dashboard as optional tab
4. Document in portfolio alongside Secure Cloud Evidence Lab

---

## Disclaimer

This is a **portfolio framework** for demonstrating AI risk thinking in interviews. It is not a production security assessment tool. Actual agent deployments require enterprise security review, penetration testing, and compliance sign-off.

## License

MIT — portfolio demonstration project.
