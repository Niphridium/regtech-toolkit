"""
EWRA — Enterprise-Wide Risk Assessment scorer.

Computes residual risk per category from inherent risk and control
effectiveness, then rolls up to an overall firm rating. This is the backbone
document every AML programme is examined against.

Synthetic inputs. Scores 1 (low) .. 5 (high). Run:  python ewra.py
"""
from __future__ import annotations

# (category, inherent_risk 1-5, control_effectiveness 1-5)
ASSESSMENT = [
    ("Customer base (PEPs, high-risk)", 4, 3),
    ("Products & services (OTC, custody)", 4, 4),
    ("Geographies (high-risk jurisdictions)", 5, 3),
    ("Delivery channels (non-face-to-face)", 4, 3),
    ("Transactions (volume, velocity)", 5, 4),
]

BANDS = [(0, 1.8, "LOW"), (1.8, 2.8, "MEDIUM"), (2.8, 3.6, "HIGH"), (3.6, 9, "CRITICAL")]


def residual(inherent: int, control: int) -> float:
    # stronger controls reduce inherent risk; control 5 => up to ~70% reduction
    reduction = (control - 1) / 4 * 0.7
    return round(inherent * (1 - reduction), 2)


def band(score: float) -> str:
    for lo, hi, label in BANDS:
        if lo <= score < hi:
            return label
    return "CRITICAL"


if __name__ == "__main__":
    print("ENTERPRISE-WIDE RISK ASSESSMENT (synthetic)\n" + "-" * 72)
    print(f"{'Category':<42}{'Inh':>4}{'Ctrl':>5}{'Resid':>7}  Band")
    print("-" * 72)
    total = 0.0
    for cat, inh, ctrl in ASSESSMENT:
        r = residual(inh, ctrl)
        total += r
        print(f"{cat:<42}{inh:>4}{ctrl:>5}{r:>7}  {band(r)}")
    overall = round(total / len(ASSESSMENT), 2)
    print("-" * 72)
    print(f"{'OVERALL residual risk':<42}{'':>4}{'':>5}{overall:>7}  {band(overall)}")
    print("\nAction: prioritise control uplift where residual risk is HIGH/CRITICAL.")
