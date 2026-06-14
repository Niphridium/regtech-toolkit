"""
Rules-as-config transaction engine.

Detection rules live as DATA (not code), so a compliance analyst can add or tune
a rule without touching Python. The engine evaluates each transaction against the
rule set and returns the alerts. This is how you keep monitoring auditable and
change-controlled.

Synthetic rules + transactions. Run:  python rules_engine.py
"""
from __future__ import annotations
import operator

OPS = {">": operator.gt, ">=": operator.ge, "<": operator.lt,
       "<=": operator.le, "==": operator.eq, "in": lambda a, b: a in b}

# --- rules as config (could live in JSON/YAML, version-controlled) ----------
RULES = [
    {"id": "R1", "name": "Large withdrawal", "field": "amount_usd", "op": ">=",
     "value": 100000, "severity": "MEDIUM"},
    {"id": "R2", "name": "High-risk country", "field": "country", "op": "in",
     "value": ["IR", "KP", "SY"], "severity": "HIGH"},
    {"id": "R3", "name": "Structuring band", "field": "amount_usd", "op": "in",
     "value": range(9000, 10000), "severity": "HIGH"},
    {"id": "R4", "name": "New account high value", "field": "account_age_days", "op": "<",
     "value": 7, "severity": "MEDIUM", "and_field": "amount_usd", "and_op": ">=",
     "and_value": 50000},
]

TXNS = [
    {"id": "TX1", "amount_usd": 250000, "country": "AE", "account_age_days": 400},
    {"id": "TX2", "amount_usd": 9500,   "country": "KP", "account_age_days": 30},
    {"id": "TX3", "amount_usd": 60000,  "country": "GB", "account_age_days": 3},
    {"id": "TX4", "amount_usd": 500,    "country": "US", "account_age_days": 900},
]


def evaluate(txn: dict):
    alerts = []
    for r in RULES:
        ok = OPS[r["op"]](txn.get(r["field"]), r["value"])
        if ok and "and_field" in r:  # optional second condition
            ok = OPS[r["and_op"]](txn.get(r["and_field"]), r["and_value"])
        if ok:
            alerts.append((r["id"], r["name"], r["severity"]))
    return alerts


if __name__ == "__main__":
    print("RULES-AS-CONFIG ENGINE (synthetic)\n" + "-" * 60)
    total = 0
    for t in TXNS:
        hits = evaluate(t)
        total += len(hits)
        if hits:
            for rid, name, sev in hits:
                print(f"{t['id']}  [{sev}] {rid} {name}")
        else:
            print(f"{t['id']}  clean")
    print("-" * 60)
    print(f"{total} alert(s) from {len(RULES)} rules over {len(TXNS)} transactions. "
          "Edit RULES (data) to tune — no code change.")
