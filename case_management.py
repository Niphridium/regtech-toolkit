"""
Case management — alert -> case lifecycle with SLA aging.

Tracks compliance cases through their lifecycle (OPEN -> INVESTIGATING ->
ESCALATED -> CLOSED), computes age against a per-priority SLA, and flags
breaches that need attention. The backbone of a defensible investigations
function: nothing falls through the cracks.

Synthetic cases only. Run:  python case_management.py
"""
from __future__ import annotations
from datetime import datetime, timedelta

NOW = datetime(2026, 6, 14)
SLA_DAYS = {"P1": 1, "P2": 3, "P3": 7, "P4": 30}

CASES = [
    {"id": "C-1001", "priority": "P1", "status": "INVESTIGATING", "owner": "analyst_a", "opened": "2026-06-12"},
    {"id": "C-1002", "priority": "P2", "status": "OPEN",          "owner": None,        "opened": "2026-06-09"},
    {"id": "C-1003", "priority": "P3", "status": "ESCALATED",     "owner": "analyst_b", "opened": "2026-06-03"},
    {"id": "C-1004", "priority": "P1", "status": "OPEN",          "owner": None,        "opened": "2026-06-14"},
    {"id": "C-1005", "priority": "P4", "status": "CLOSED",        "owner": "analyst_a", "opened": "2026-05-01"},
    {"id": "C-1006", "priority": "P2", "status": "INVESTIGATING", "owner": "analyst_c", "opened": "2026-06-05"},
]


def enrich(c: dict):
    opened = datetime.strptime(c["opened"], "%Y-%m-%d")
    age = (NOW - opened).days
    sla = SLA_DAYS[c["priority"]]
    breached = c["status"] != "CLOSED" and age > sla
    unassigned = c["owner"] is None and c["status"] != "CLOSED"
    return {**c, "age_days": age, "sla_days": sla,
            "sla_breach": breached, "unassigned": unassigned}


if __name__ == "__main__":
    rows = [enrich(c) for c in CASES]
    print("CASE MANAGEMENT — SLA aging (synthetic)\n" + "-" * 78)
    print(f"{'Case':<8}{'Pri':<5}{'Status':<15}{'Owner':<12}{'Age':>4}{'SLA':>5}  Flags")
    print("-" * 78)
    for r in sorted(rows, key=lambda x: (not x["sla_breach"], x["priority"])):
        flags = []
        if r["sla_breach"]:
            flags.append("SLA BREACH")
        if r["unassigned"]:
            flags.append("UNASSIGNED")
        print(f"{r['id']:<8}{r['priority']:<5}{r['status']:<15}"
              f"{str(r['owner']):<12}{r['age_days']:>4}{r['sla_days']:>5}  {', '.join(flags) or 'ok'}")
    breaches = sum(r["sla_breach"] for r in rows)
    unassigned = sum(r["unassigned"] for r in rows)
    print("-" * 78)
    print(f"{breaches} SLA breach(es), {unassigned} unassigned open case(s) need action.")
