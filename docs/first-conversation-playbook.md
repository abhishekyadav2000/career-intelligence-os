# First Conversation Playbook

**Your first conversation in 24 hours** — a practical, step-by-step guide using Career Intelligence OS Interview Command Center.

---

## Hour 0–1: Pick Your Target

1. Open the dashboard: `streamlit run dashboard/app.py`
2. Go to **Company Ranking** tab — filter for Tier 1 companies with strong sponsorship signals
3. Pick **one company** where you have the strongest proof match (start with JPMorgan Chase, Citi, or Capital One if unsure)
4. In the global selectors at the top, set:
   - **Company:** your target
   - **Role:** highest role-fit score for that company (check **Role Fit** tab first)
   - **Conversation type:** `recruiter` for first outreach, or `hiring manager` if you have a warm intro path
   - **Interview stage:** `initial outreach` or `recruiter screen`

---

## Hour 1–2: Generate Your Brief

1. Switch to **Interview Command Center** tab
2. Click **Generate Brief**
3. Review all sections:
   - **Company 360** — strategic summary and tech themes (your "why this company")
   - **Role Intelligence** — business problem and 30/60/90 plan (your "why this role")
   - **People Map** — ranked contacts with search URLs (who to reach)
   - **Proof Match** — top 3 portfolio assets to reference
   - **Conversation Script** — opening message draft
   - **Interview Prep** — likely questions by category
   - **Action Plan** — follow-up template and next steps
4. Click **Export Brief as Markdown** — save to your notes app
5. Or use a pre-generated sample from `exports/brief-*-sample.md` as a reference

**Shortcut:** If the dashboard isn't running, open `exports/brief-jpmorgan-chase-sample.md` to see the full brief format.

---

## Hour 2–3: Customize What You'll Say

1. Open the matching **company packet** in `company-packets/` (e.g., `jpmorgan-chase.md`)
2. Copy the outreach angle for your conversation type (recruiter / hiring manager / peer)
3. Personalize with:
   - One sentence from **Role Intelligence** (the business problem)
   - One proof asset from **Proof Match** (with GitHub link)
   - No fake names — use "Hi" or leave `[Name]` blank until you verify a contact
4. Keep it under 150 words for LinkedIn; under 200 for email

**Example opening (recruiter):**
> Hi — I'm exploring the [Role Title] opportunity at [Company]. My background aligns with [business problem from brief]. I'd like to share how [proof asset] demonstrates the Python, SQL, and analytics skills this role requires. Could we schedule a brief call?

---

## Hour 3–4: Send and Log

1. Send via the company's careers portal first (see `search_query_url` is backup only)
2. Open `data/conversation_log_template.csv` — add a row:
   - `company`, `contact_type`, `channel` (LinkedIn / email / portal)
   - `message_sent_date`, `status` = `sent`
   - `notes` = one line on what you referenced from the brief
3. Do **not** assume a response — plan a 5-day follow-up

---

## Hour 4–24: Prepare for the Reply

1. Re-read **Interview Prep** section from your brief
2. Open the matching **interview packet** in `interview-packets/` for your role family
3. Practice a 2-minute elevator pitch:
   - Problem the role solves (15 sec)
   - Your proof asset demo hook (45 sec)
   - One question you'd ask them (15 sec)
4. Review **Optional Sponsorship Disclosure** in the brief — decide when to use it (typically recruiter screen, not first message)

---

## After the Conversation: Close the Loop

1. Within 24 hours: send the **Follow-Up Template** from your Action Plan
2. Update `conversation_log_template.csv`:
   - `status` = `replied` / `no_response` / `scheduled`
   - `insight_gained` = one sentence on what you learned
3. If you learned something new about the company or role:
   - Update the relevant CSV manually (see [research-enrichment-workflow.md](research-enrichment-workflow.md))
   - Or note it in the conversation log for later enrichment
4. Generate a **new brief** with updated `interview_stage` if you advance (e.g., `recruiter screen` → `hiring manager screen`)

---

## Quick Reference

| Step | Tab / File | Output |
|------|-----------|--------|
| Pick target | Company Ranking + Role Fit | One company + one role |
| Generate brief | Interview Command Center | 7-section brief |
| Customize message | company-packets/ + brief script | Outreach message |
| Send + log | conversation_log_template.csv | Logged outreach |
| Prepare reply | interview-packets/ + brief prep | 2-min pitch ready |
| Follow up | Action Plan in brief | Thank-you sent |

---

## Rules

- **No fake names** — TBD placeholders until verified
- **No scraping** — use search URLs manually, verify before referencing
- **Signal ≠ certainty** — sponsorship notes are indicative; verify via DOL/USCIS
- **Portfolio first** — lead with proof-of-work, disclose authorization when asked

---

*Part of Career Intelligence OS — Interview Command Center*
