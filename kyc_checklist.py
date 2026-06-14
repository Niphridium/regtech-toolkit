"""
KYC / EDD document checklist generator.

Produces the right document checklist for a customer based on type and risk band,
so onboarding collects exactly what the risk-based approach requires — no more,
no less. Turns policy into a repeatable, auditable step.

Run:  python kyc_checklist.py [individual|company] [LOW|MEDIUM|HIGH]
"""
from __future__ import annotations
import sys

BASE = {
    "individual": ["Government-issued photo ID", "Proof of address (<3 months)",
                   "Selfie / liveness check"],
    "company": ["Certificate of incorporation", "Register of directors",
                "Register of shareholders / UBOs", "Proof of registered address"],
}
RISK_ADDONS = {
    "MEDIUM": ["Source of funds declaration", "Sanctions & PEP screening"],
    "HIGH": ["Source of funds declaration", "Sanctions & PEP screening",
             "Source of wealth evidence", "Enhanced UBO verification",
             "Senior management approval", "Ongoing enhanced monitoring"],
}


def checklist(ctype: str, risk: str):
    items = list(BASE.get(ctype, BASE["individual"]))
    if risk in ("MEDIUM", "HIGH"):
        for x in RISK_ADDONS[risk]:
            if x not in items:
                items.append(x)
    if ctype == "company" and risk == "HIGH":
        items.append("Ownership-structure chart with UBO % thresholds")
    return items


if __name__ == "__main__":
    ctype = (sys.argv[1] if len(sys.argv) > 1 else "company").lower()
    risk = (sys.argv[2] if len(sys.argv) > 2 else "HIGH").upper()
    print(f"KYC / EDD CHECKLIST — {ctype.title()} customer, {risk} risk\n" + "-" * 56)
    for i, item in enumerate(checklist(ctype, risk), 1):
        print(f"  {i:>2}. [ ] {item}")
    print("-" * 56)
    print("Tier the evidence to risk: HIGH risk => full EDD + senior sign-off.")
