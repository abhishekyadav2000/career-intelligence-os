# Interview Packet: Cloud Security Analyst

**Role Family:** Cloud Security Analyst  
**Universal Profile Fit:** Enterprise Technology Analyst — AI Automation, Cloud Security & Data Analytics  
**Typical Employers:** JPMorgan Chase, Capital One, Citi, AT&T, Bank of America, Goldman Sachs

---

## Role Summary

Cloud security analysts protect cloud infrastructure — reviewing IAM policies, configuring security groups, monitoring cloud-native SIEM integrations, ensuring compliance with frameworks (NIST, SOC 2), and supporting cloud migration security reviews.

---

## Key Skills to Demonstrate

| Skill | Portfolio Evidence |
|-------|-------------------|
| Cloud IAM (AWS/Azure) | Secure Cloud Evidence Lab — IAM module |
| Cloud security monitoring | SIEM module + keyword taxonomy |
| Infrastructure as Code security | Terraform/Kubernetes in job descriptions |
| Compliance mapping | NIST CSF ↔ SOC 2 crosswalk |
| Risk scoring | AI Agent Risk Scoring rubric |
| Cloud-native architecture | Architecture doc, system design one-pager |

---

## Technical Questions (Prepare Answers)

1. **"How do you secure an S3 bucket?"**
   → Block public access, enable encryption (SSE-S3 or KMS), bucket policy with least privilege, enable logging, MFA delete for sensitive buckets.

2. **"Explain the shared responsibility model."**
   → Cloud provider secures infrastructure (physical, hypervisor); customer secures data, IAM, network config, applications. Reference lab's IAM findings as customer responsibility.

3. **"How would you respond to a cloud misconfiguration alert?"**
   → Triage severity → identify scope → contain (restrict access) → remediate → document → update detection rules.

4. **"Walk me through a cloud security assessment."**
   → Asset inventory → IAM review → network config → encryption status → logging/monitoring → compliance mapping → findings report.

5. **"Terraform and security — what concerns do you have?"**
   → State file sensitivity, overly permissive IAM in modules, secrets in code, drift detection. Reference IaC keywords in scoring taxonomy.

---

## Business Questions

1. "How do you balance cloud agility with security controls?"
2. "Describe your experience with cloud migration security reviews."
3. "How do you work with DevOps on security in CI/CD?"
4. "What's your approach to cloud cost vs. security tradeoffs?"

---

## Behavioral Questions (STAR Format)

| Question | Suggested Story Angle |
|----------|----------------------|
| Cloud security finding you identified | IAM lab — over-permissioned role |
| Working with DevOps/engineering | CI OS architecture — modular pipeline design |
| Learning a new cloud platform | Built evidence lab with AWS-focused examples; adaptable to Azure |
| Communicating cloud risk to leadership | Severity ratings in lab findings table |

---

## Questions to Ask Them

1. "Which cloud platform(s) does your team primarily support?"
2. "How is cloud security organized — centralized or embedded in teams?"
3. "What's your approach to CSPM (Cloud Security Posture Management)?"
4. "How do you handle multi-cloud security?"

---

## Portfolio Demo Path (3 min)

Secure Cloud Evidence Lab (IAM + GRC) → CI OS architecture doc → Role Fit tab showing cloud security keyword matching

---

## Differentiator

Most candidates cite "cloud security" keywords. You can walk through a synthetic IAM policy review with findings, severity ratings, and remediation — that's evidence, not vocabulary.
