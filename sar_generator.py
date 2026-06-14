"""
SAR / STR draft generator.

Turns a structured set of alert flags into a first-draft Suspicious Activity /
Transaction Report narrative, following a 5-part structure (who / what / when /
why suspicious / action). It DRAFTS — a human MLRO reviews, edits and decides
whether to file. It never files anything.

Synthetic case only.
Run:  python generate_sar.py   ->  prints draft + writes sar_draft.md
"""
from __future__ import annotations
from datetime import datetime

# --- a SYNTHETIC flagged case (would come from your monitoring system) ------
CASE = {
    "case_id": "CASE-2026-0042",
    "subject": "Customer U0093 (synthetic)",
    "account_opened": "2026-01-15",
    "period": "2026-06-01 to 2026-06-08",
    "flags": [
        {"rule": "SHARED_ADDRESS", "severity": "CRITICAL",
         "detail": "withdrew to an address shared by 45 distinct users (possible mixer/P2P exchanger)"},
        {"rule": "HIGH_VELOCITY", "severity": "HIGH",
         "detail": "24h outflow reached $1.4M, against an expected profile of < $50k/month"},
        {"rule": "STRUCTURING", "severity": "HIGH",
         "detail": "4 transactions in the $90k-$100k band, just below the $100k reporting threshold"},
    ],
    "total_out_usd": 4_300_000,
    "expected_monthly_usd": 50_000,
    "kyc_notes": "Source of funds described as 'trading'; no supporting documentation on file.",
}

NARR = {
    "CRITICAL": "a critical indicator of potential money laundering",
    "HIGH": "a significant red flag",
    "MEDIUM": "a notable concern",
}


def build(case: dict) -> str:
    flags_md = "\n".join(
        f"- **{f['rule']}** ({f['severity']}) — {f['detail']}" for f in case["flags"])
    multiplier = case["total_out_usd"] / max(case["expected_monthly_usd"], 1)
    reasons = "; ".join(
        f"{f['detail']} ({NARR.get(f['severity'], 'a concern')})" for f in case["flags"])

    return f"""# SUSPICIOUS ACTIVITY REPORT — DRAFT (for MLRO review)

> Auto-generated draft. Not filed. Requires human review, verification and a
> filing decision by the MLRO. Synthetic data.

**Case ID:** {case['case_id']}
**Subject:** {case['subject']}
**Account opened:** {case['account_opened']}
**Activity period:** {case['period']}
**Generated:** {datetime.utcnow():%Y-%m-%d %H:%M} UTC

## 1. Subject
This report concerns {case['subject']}, an account opened on
{case['account_opened']}.

## 2. Activity observed
During {case['period']}, the account generated total outflows of
**${case['total_out_usd']:,.0f}**, approximately **{multiplier:.0f}x** the
customer's expected monthly activity of ${case['expected_monthly_usd']:,.0f}.

## 3. Indicators triggered
{flags_md}

## 4. Why the activity is suspicious
The combination of the above indicators is consistent with layering and the use
of obfuscation services: {reasons}. KYC notes: {case['kyc_notes']}

## 5. Recommended action
- Escalate to the MLRO for a filing decision (SAR/STR).
- Apply enhanced due diligence; request documentary source of funds.
- Consider a temporary restriction on outbound transfers pending review.

---
*Draft prepared by an automated assistant. The MLRO is responsible for review,
verification and the decision to file.*
"""


if __name__ == "__main__":
    md = build(CASE)
    with open("sar_draft.md", "w") as f:
        f.write(md)
    print(md)
    print("Wrote sar_draft.md")
