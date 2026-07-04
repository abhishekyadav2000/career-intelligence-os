# How I Use This System to Target Companies

This document describes my personal workflow for using Career Intelligence OS as a job search operating system — not a one-time dashboard demo.

---

## My Profile

**Enterprise Technology Analyst — AI Automation, Cloud Security & Data Analytics**

I target DFW enterprise technology roles across six role families: business systems analyst, data analyst, cybersecurity, cloud security, AI automation, and technical project coordinator. My work authorization is OPT with EAD — I disclose transparently when asked.

---

## Step 1: Start with the Ranked List

Every week, I open the dashboard and go to **Company Ranking**. I don't apply everywhere — I work from the top:

1. JPMorgan Chase (Rank 1)
2. Goldman Sachs (Rank 2)
3. Bank of America (Rank 3)
4. Citi (Rank 4)
5. Charles Schwab (Rank 5)
6. Capital One (Rank 6)

These are Tier 1 targets with strong DFW presence, multiple role families, and sponsor-friendly signals. I pick 2–3 per week for active outreach.

---

## Step 2: Open the Company Packet

For each target, I open the corresponding file in `company-packets/`:

- Pre-researched talking points tied to public initiatives
- Target roles from sample data with fit context
- Outreach angles by contact type (recruiter, hiring manager, peer, alumni)
- Sponsorship notes with disclaimer

This saves 30–45 minutes of pre-outreach research per company.

---

## Step 3: Drill into Role Fit

In the **Role Fit** tab, I filter to my target company and sort by fit score. I drill into the top role and review the six-category breakdown:

- **Technical fit** — am I matching on Python, SQL, cloud, security?
- **Sponsorship signal** — what's the indicative signal? (Verify separately via DOL/USCIS)
- **Noise risk** — is this posting likely real or a ghost job?

If fit score is above 70 and noise risk is low, this role goes on my "apply or network" list.

---

## Step 4: Send Targeted Outreach

I use the conversation playbooks in `conversation-playbooks/`:

| Contact Type | Playbook | When |
|-------------|----------|------|
| Recruiter | `recruiter.md` | First contact for a specific role |
| Hiring Manager | `hiring-manager.md` | Referral intro or deep technical conversation |
| Peer | `peer.md` | Informational chat, no referral ask |
| Alumni | `alumni.md` | Shared university connection |

Every message references a **specific role** and a **concrete portfolio artifact** — never generic "I'm looking for opportunities."

---

## Step 5: Log Every Conversation

Immediately after any outreach, response, or conversation, I add a row to `data/conversation_log_template.csv`:

```
date, company, person_type, role_discussed, source, outreach_status,
response, insight_gained, portfolio_gap, next_action, follow_up_date
```

This takes 2 minutes and is the most valuable habit in the system. Without logging, the feedback loop breaks.

---

## Step 6: Check Conversation Feedback

The **Conversation Feedback** tab analyzes my log and shows:

- **Warm companies** — where I got positive responses (prioritize these)
- **Repeated objections** — sponsorship questions, experience level, clearance
- **Skill gaps** — things interviewers asked for that my portfolio doesn't yet prove
- **Next actions** — pending follow-ups with dates

Example from my current log:
- Citi hiring manager wants "IAM policy review evidence — not just keyword match"
- Portfolio gap flagged: "Secure Cloud Evidence Lab module"
- Next action: "Prepare IAM least-privilege walkthrough"

---

## Step 7: Update Portfolio Based on Feedback

When the feedback loop identifies a gap, I update the repo:

| Gap Identified | Action Taken |
|---------------|-------------|
| Cloud / IAM / SIEM lab artifact | Built Secure Cloud Evidence Lab case study |
| AI risk thinking | Built AI Agent Risk Scoring framework |
| SQL analytics depth | Added SQL demo queries to Export tab |
| Conversation feedback loop | Built conversation_feedback_analyzer.py + dashboard tab |

Each portfolio update makes the next outreach stronger — I can reference new artifacts in follow-up messages.

---

## Step 8: Prepare for Interviews

When an interview is scheduled, I open the matching file in `interview-packets/`:

- Technical questions with prepared answers tied to portfolio
- Business and behavioral questions with STAR story angles
- Questions to ask them (shows genuine interest)
- Recommended demo path (3 min, specific tabs)

I also review the company packet and sponsorship disclosure playbook before HR screens.

---

## My Weekly Rhythm

| Day | Activity | Time |
|-----|----------|------|
| Monday | Review feedback tab, pick 2 targets, prepare packets | 30 min |
| Tue–Thu | Send 1–2 outreach messages, log immediately | 30 min/day |
| Friday | Log week's conversations, check feedback patterns | 20 min |
| Weekend | Portfolio update if gap identified | 1–2 hours |

---

## What Makes This Different from Normal Job Search

| Normal Job Search | Career Intelligence OS |
|-------------------|----------------------|
| Apply to 50+ jobs on LinkedIn | Target 2–3 ranked companies per week |
| Generic cover letter | Company packet with specific talking points |
| Hope for callbacks | Track warm/cold signals in conversation log |
| Same portfolio for every interview | Interview packet matched to role family |
| Forget what interviewers asked | Log insights → feedback tab → portfolio gap → fix |
| Start over each cycle | Each loop makes the next outreach stronger |

---

## Current Status

- **5 company packets** ready (JPMorgan, Citi, Capital One, Toyota, AT&T)
- **6 interview packets** for role families
- **6 conversation playbooks** for contact types
- **5 sample conversations** logged with feedback analysis
- **3 case studies** (CI OS, AI risk scoring, cloud evidence lab)
- **8 dashboard screenshots** captured for portfolio README

---

## Repo

https://github.com/abhishekyadav2000/career-intelligence-os

```bash
streamlit run dashboard/app.py
```

See [recursive-job-search-loop.md](recursive-job-search-loop.md) for the full 10-step loop diagram and [demo-guide.md](demo-guide.md) for presentation flows.
