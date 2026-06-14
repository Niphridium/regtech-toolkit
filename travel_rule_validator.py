"""
Travel Rule validator (IVMS101-style).

Checks virtual-asset transfer payloads for the originator/beneficiary data the
FATF Travel Rule (Recommendation 16) requires, applies the de-minimis threshold,
and returns a clear PASS / FAIL with the exact missing fields.

Synthetic payloads only. Field set is a simplified IVMS101 subset for the demo.
Run:  python travel_rule_validator.py
"""
from __future__ import annotations

THRESHOLD_USD = 1000  # FATF de-minimis; below this, reduced data may apply

REQUIRED = {
    "originator": ["name", "account", "address_or_id"],
    "beneficiary": ["name", "account"],
}
# below threshold: name + account still expected, full address/id relaxed
REQUIRED_BELOW = {
    "originator": ["name", "account"],
    "beneficiary": ["name", "account"],
}

TRANSFERS = [
    {"id": "T1", "amount_usd": 25000,
     "originator": {"name": "Alex Rivera", "account": "wlt_abc", "address_or_id": "ID-99"},
     "beneficiary": {"name": "Sam Chen", "account": "wlt_xyz"}},
    {"id": "T2", "amount_usd": 8000,
     "originator": {"name": "Jordan Kim", "account": "wlt_111"},  # missing address_or_id
     "beneficiary": {"name": "Taylor Novak", "account": "wlt_222"}},
    {"id": "T3", "amount_usd": 300,                                # below threshold
     "originator": {"name": "Casey Berg", "account": "wlt_333"},
     "beneficiary": {"name": "Noor Haddad", "account": "wlt_444"}},
    {"id": "T4", "amount_usd": 150000,
     "originator": {"name": "Marat Abenov", "account": ""},        # empty account
     "beneficiary": {"name": "", "account": "wlt_555"}},           # empty name
]


def validate(t: dict):
    spec = REQUIRED if t["amount_usd"] >= THRESHOLD_USD else REQUIRED_BELOW
    missing = []
    for party, fields in spec.items():
        for f in fields:
            if not t.get(party, {}).get(f):
                missing.append(f"{party}.{f}")
    return {"id": t["id"], "amount_usd": t["amount_usd"],
            "threshold_applies": t["amount_usd"] >= THRESHOLD_USD,
            "result": "PASS" if not missing else "FAIL",
            "missing": missing}


if __name__ == "__main__":
    print("TRAVEL RULE VALIDATOR (IVMS101-style, synthetic)\n" + "-" * 60)
    fails = 0
    for t in TRANSFERS:
        r = validate(t)
        fails += r["result"] == "FAIL"
        miss = f"  missing: {', '.join(r['missing'])}" if r["missing"] else ""
        print(f"{r['id']}  ${r['amount_usd']:>8,}  {r['result']}{miss}")
    print("-" * 60)
    print(f"{fails} transfer(s) failed Travel Rule validation and must be blocked/remediated.")
