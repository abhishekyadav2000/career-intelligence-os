# Follow-Up Messages Playbook

**Positioning:** Enterprise Technology Analyst — AI Automation, Cloud Security & Data Analytics  
**Tone:** Professional, value-add, concise — one follow-up max unless they re-engage

---

## Follow-Up Rules

1. **One follow-up** after no response (5–7 business days)
2. **Add new value** in every follow-up — never "just checking in"
3. **Keep it under 4 sentences**
4. **Log every follow-up** in conversation log CSV
5. **Move on after two unanswered messages** — redirect energy to warm companies

---

## Template: No Reply After Initial Outreach

> Hi [Name], following up on my message about the [Role Title] at [Company]. Since then, I added a conversation feedback loop to my career intelligence dashboard — it tracks outreach insights and portfolio gaps from real conversations. Happy to share a quick demo if useful. No pressure if timing isn't right.

---

## Template: After Positive Conversation

> Hi [Name], thank you again for our conversation about [specific topic]. As follow-up, I [specific action you promised — e.g., prepared an IAM policy walkthrough / updated my SQL analytics case study]. Here's the link: [portfolio/GitHub]. Let me know if there's a good time to continue the conversation.

---

## Template: After Interview

> Hi [Name], thank you for the opportunity to discuss the [Role Title] role today. I enjoyed learning about [specific team priority they mentioned]. Our conversation reinforced my interest — particularly around [specific technical challenge]. Please let me know if I can provide any additional materials.

---

## Template: After Rejection

> Hi [Name], thank you for letting me know about the decision. I appreciated the opportunity to learn about [Company]'s [team/initiative]. If a future role opens that better matches my background in [specific skill], I'd welcome the chance to reconnect. Wishing you and the team continued success.

**Why thank rejections:** Maintains professional network; hiring managers remember gracious candidates.

---

## Template: Informational Chat Thank-You

> Hi [Name], thank you for taking 15 minutes to share your experience at [Company]. Your insight about [specific thing] was valuable — I'm going to [specific action]. I hope we can stay connected, and please don't hesitate to reach out if I can ever return the favor.

---

## Timing Matrix

| Event | Follow-Up Timing | Max Follow-Ups |
|-------|-----------------|----------------|
| Initial outreach, no reply | 5–7 business days | 1 |
| Positive reply, scheduling | 24 hours to confirm | As needed |
| Interview completed | 24 hours (thank-you) | 1 |
| Rejection received | Same day (thank-you) | 0 |
| Informational chat | 24 hours (thank-you) | 0 |
| Offer received | Same day (accept/negotiate) | As needed |

---

## Conversation Log Integration

After every follow-up, update `data/conversation_log_template.csv`:

```csv
date,company,person_type,role_discussed,source,outreach_status,response,insight_gained,portfolio_gap,next_action,follow_up_date
2026-04-01,JPMorgan Chase,recruiter,Technology Analyst,LinkedIn,follow-up sent,replied,"Interested in demo link","SQL case study depth","Schedule demo call",2026-04-08
```

Check the Conversation Feedback tab for warm company signals and objection patterns.
