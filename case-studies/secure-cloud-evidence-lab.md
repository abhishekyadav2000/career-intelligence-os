# Case Study: Secure Cloud Evidence Lab

> **Synthetic examples only — not production.** This case study documents a hands-on lab framework for cloud security evidence collection aligned with GRC audit requirements. It connects to Career Intelligence OS gap matrix item **"Cloud / IAM / SIEM / GRC"** and provides interview-ready artifacts for enterprise technology roles.

---

## 1. Executive Summary

Enterprise cloud security teams must produce evidence for IAM reviews, SIEM alert tuning, and GRC control mapping — often under SOC 2 or NIST CSF frameworks. This lab provides **synthetic examples** of IAM policy analysis, SIEM alert samples, NIST control mapping, and an evidence collection checklist — designed as a portfolio artifact for cloud security and business systems analyst interviews.

**Positioning:** Enterprise Technology Analyst — AI Automation, Cloud Security & Data Analytics

---

## 2. Business Problem

Cloud security analysts and GRC professionals face recurring audit cycles that require:

- **IAM evidence** — least-privilege policy review, access reviews, MFA enforcement
- **SIEM evidence** — alert tuning documentation, incident response playbooks, detection coverage
- **GRC mapping** — controls mapped to NIST CSF or SOC 2 Trust Service Criteria
- **Evidence packaging** — organized artifacts for internal audit or external assessor review

Candidates who can speak to this workflow — even with synthetic examples — demonstrate readiness for cloud security, cybersecurity, and technology risk analyst roles.

---

## 3. Lab Modules

| Module | Focus | Synthetic Artifact |
|--------|-------|-------------------|
| **Module 1: IAM** | Least-privilege policy review | Sample AWS IAM policy with over-permissioned role |
| **Module 2: SIEM** | Alert tuning and detection | Sample Splunk/Sentinel alert with false-positive analysis |
| **Module 3: GRC** | Control mapping | NIST CSF → SOC 2 crosswalk spreadsheet |
| **Module 4: Evidence** | Audit packaging | Evidence collection checklist with sample entries |

---

## 4. Module 1 — IAM Policy Analysis (Synthetic)

### Scenario

A developer role `DevOps-Engineer-Prod` has the following attached policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "s3:*",
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": "iam:*",
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": "ec2:*",
      "Resource": "*"
    }
  ]
}
```

### Findings

| Finding | Severity | Recommendation |
|---------|----------|----------------|
| `s3:*` on `*` | Critical | Scope to specific buckets; remove `DeleteBucket`, `PutBucketPolicy` |
| `iam:*` on `*` | Critical | Remove IAM write permissions; use separate break-glass role with MFA |
| `ec2:*` on `*` | High | Scope to specific VPC/subnet; remove `TerminateInstances` for non-admin |
| No MFA condition | High | Add `aws:MultiFactorAuthPresent` condition on sensitive actions |
| No resource tagging | Medium | Require `aws:RequestedRegion` and tag-based conditions |

### Evidence Artifact

- Policy document (above)
- Findings table with severity ratings
- Remediation recommendation with least-privilege replacement policy
- Access review sign-off template

---

## 5. Module 2 — SIEM Alert Tuning (Synthetic)

### Scenario

Alert: **"Multiple Failed Login Attempts — User Account"**

```
index=security sourcetype=WinEventLog:Security EventCode=4625
| stats count by Account_Name, src_ip
| where count > 5
| eval severity="high"
```

### Tuning Analysis

| Issue | Impact | Fix |
|-------|--------|-----|
| Threshold too low (5 attempts) | False positives from service accounts | Increase to 10; exclude service account OU |
| No time window | Counts accumulate indefinitely | Add `earliest=-15m` time bound |
| No geo/IP enrichment | Cannot distinguish internal vs external | Add `lookup geo_ip src_ip` |
| No escalation path | Alert fires but no runbook | Link to incident response playbook ID-IR-042 |

### Evidence Artifact

- Original and tuned SPL/query
- False-positive rate before/after (synthetic: 47 → 8 per week)
- Incident response playbook reference
- Detection coverage matrix entry

---

## 6. Module 3 — Control Mapping (NIST CSF ↔ SOC 2)

| NIST CSF Function | NIST Category | SOC 2 TSC | Control Example | Evidence Type |
|-------------------|--------------|-----------|-----------------|---------------|
| Identify | ID.AM (Asset Management) | CC6.1 | Cloud asset inventory maintained | Asset register export |
| Protect | PR.AC (Access Control) | CC6.1, CC6.2 | IAM least-privilege enforced | Policy review + access review log |
| Protect | PR.DS (Data Security) | C1.1 | Encryption at rest for S3/RDS | Configuration screenshot + KMS key policy |
| Detect | DE.CM (Continuous Monitoring) | CC7.1 | SIEM alerts for unauthorized access | Alert tuning doc + sample incidents |
| Respond | RS.RP (Response Planning) | CC7.3 | Incident response playbook tested | Tabletop exercise record |
| Recover | RC.RP (Recovery Planning) | A1.2 | Backup and restore tested quarterly | Restore test log |

---

## 7. Evidence Collection Checklist

| # | Control Area | Evidence Required | Status (Synthetic) | Owner |
|---|-------------|-------------------|---------------------|-------|
| 1 | IAM — Access Review | Quarterly user access review sign-off | ✅ Complete (Q1 2026) | Cloud Security |
| 2 | IAM — MFA Enforcement | MFA policy + compliance report | ✅ Complete | Identity Team |
| 3 | IAM — Least Privilege | Policy review findings + remediation | 🔄 In Progress | Cloud Security |
| 4 | SIEM — Detection Coverage | MITRE ATT&CK coverage matrix | ✅ Complete | SOC Team |
| 5 | SIEM — Alert Tuning | Before/after false-positive metrics | 🔄 In Progress | SOC Team |
| 6 | GRC — Control Mapping | NIST CSF ↔ SOC 2 crosswalk | ✅ Complete | GRC Team |
| 7 | GRC — Risk Register | Updated risk register with cloud entries | ✅ Complete | GRC Team |
| 8 | Incident Response | Tabletop exercise record | ⬜ Scheduled Q2 2026 | SOC Team |

---

## 8. Connection to Career Intelligence OS

| CI OS Component | Lab Connection |
|----------------|---------------|
| Keyword taxonomy (IAM, SIEM, GRC, NIST, SOC 2) | Shared vocabulary across scoring and lab |
| Interview Prep tab | Technical topics reference lab artifacts |
| Gap matrix P0 | "Cloud / IAM / SIEM / GRC" — this lab addresses it |
| Company packets | Cloud security roles at Citi, Capital One, Toyota cite these skills |
| Conversation Feedback | Interview insights like "wants IAM evidence" map to lab modules |

---

## 9. Interview Talking Points

1. **"Walk me through an IAM review."**
   → Policy analysis scenario above: identify over-permissions, recommend least-privilege, document findings.

2. **"How do you tune SIEM alerts?"**
   → Threshold adjustment, time windows, exclusion lists, false-positive tracking, escalation paths.

3. **"NIST vs SOC 2 — how do they relate?"**
   → NIST CSF is a framework; SOC 2 TSC are audit criteria. Crosswalk maps functions to controls.

4. **"What evidence does an auditor need?"**
   → Policy docs, access review logs, configuration screenshots, alert tuning metrics, incident records.

5. **"Is this real production data?"**
   → No. Synthetic examples designed for portfolio demonstration. Production work requires enterprise access and NDA compliance.

---

## 10. Skills Demonstrated

| Skill | Evidence |
|-------|----------|
| IAM policy analysis | Least-privilege review with findings table |
| SIEM alert tuning | SPL query before/after with false-positive metrics |
| GRC control mapping | NIST CSF ↔ SOC 2 crosswalk |
| Evidence packaging | Audit checklist with status tracking |
| Risk communication | Severity ratings and remediation recommendations |
| Domain vocabulary | IAM, SIEM, Splunk, NIST, SOC 2, GRC, MFA, KMS |

---

## Disclaimer

All examples in this lab are **synthetic** and created for portfolio demonstration. No real AWS accounts, SIEM environments, or audit data are included. Production cloud security work requires enterprise credentials, change management, and compliance review.

## License

MIT — portfolio demonstration project.
