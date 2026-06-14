"""
On-chain address risk lookup (mock API).

Given a crypto address, returns a risk score (0-100), a band, and the reasons —
the kind of enrichment a monitoring system calls before approving a withdrawal.
Known addresses come from a small SYNTHETIC risk DB; unknown ones get a
deterministic pseudo-score so the demo is reproducible.

No real addresses or intelligence. Run:  python address_risk.py [ADDRESS]
"""
from __future__ import annotations
import hashlib
import sys

# SYNTHETIC risk intelligence (not real)
KNOWN = {
    "Tmixer000000000000000000000000000": (95, ["mixer/tumbler exposure", "high-risk cluster"]),
    "Tsanction0000000000000000000000000": (99, ["sanctioned entity (synthetic list)"]),
    "Tdarknet00000000000000000000000000": (90, ["darknet market exposure"]),
    "Texchange00000000000000000000000000": (20, ["licensed exchange deposit address"]),
    "Tclean0000000000000000000000000000": (5,  ["no adverse signals"]),
}
CATS = ["no adverse signals", "P2P exchanger exposure", "gambling exposure",
        "high-velocity counterpart", "new/low-history address"]


def lookup(address: str):
    if address in KNOWN:
        score, reasons = KNOWN[address]
    else:
        h = int(hashlib.sha256(address.encode()).hexdigest(), 16)
        score = h % 101
        reasons = [CATS[h % len(CATS)]]
        if score >= 70:
            reasons.append("elevated cluster risk")
    band = ("CRITICAL" if score >= 85 else "HIGH" if score >= 60
            else "MEDIUM" if score >= 30 else "LOW")
    decision = "BLOCK" if score >= 85 else "REVIEW" if score >= 60 else "ALLOW"
    return {"address": address, "risk_score": score, "band": band,
            "decision": decision, "reasons": reasons}


if __name__ == "__main__":
    targets = sys.argv[1:] or list(KNOWN.keys()) + ["TnewUserWithdrawAddr0001"]
    print("ON-CHAIN ADDRESS RISK (mock, synthetic)\n" + "-" * 70)
    for a in targets:
        r = lookup(a)
        print(f"{a[:22]:<24} score={r['risk_score']:>3} {r['band']:<9} "
              f"{r['decision']:<7} {'; '.join(r['reasons'])}")
    print("-" * 70)
    print("Wire this into withdrawal approval: BLOCK >=85, REVIEW >=60.")
