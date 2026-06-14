"""
Monthly compliance KPI report generator.

Rolls the toolkit's signals into a one-page management report (markdown) — the
kind of MI an MLRO takes to the board: volumes, alerts, cases, SAR/STR filed,
SLA health and screening activity, with simple month-over-month deltas.

Synthetic KPIs. Run:  python compliance_report.py  ->  writes compliance_report.md
"""
from __future__ import annotations
from datetime import datetime

# SYNTHETIC monthly KPIs (this month, last month)
KPIS = {
    "Transactions monitored": (128_400, 121_900),
    "Alerts raised": (412, 388),
    "Alerts -> cases": (96, 88),
    "Cases closed": (90, 79),
    "SARs/STRs filed": (11, 9),
    "Sanctions/PEP screening hits (escalated)": (7, 5),
    "EDD reviews completed": (34, 31),
    "Open cases breaching SLA": (3, 6),
}


def delta(cur, prev):
    if prev == 0:
        return "n/a"
    pct = (cur - prev) / prev * 100
    arrow = "▲" if pct > 0 else ("▼" if pct < 0 else "→")
    return f"{arrow} {pct:+.0f}%"


def build():
    today = datetime.utcnow()
    lines = [
        f"# Compliance MI — Monthly Report (synthetic)",
        f"_Generated {today:%Y-%m-%d} · prepared by Merey Nurkaliyev (AML Team Lead)_",
        "",
        "| KPI | This month | Last month | Δ |",
        "|---|---:|---:|---:|",
    ]
    for k, (cur, prev) in KPIS.items():
        lines.append(f"| {k} | {cur:,} | {prev:,} | {delta(cur, prev)} |")
    sar_rate = KPIS["SARs/STRs filed"][0] / KPIS["Alerts -> cases"][0] * 100
    lines += [
        "",
        "## Highlights",
        f"- SAR conversion rate: **{sar_rate:.0f}%** of cases resulted in a filing.",
        f"- SLA breaches down to **{KPIS['Open cases breaching SLA'][0]}** "
        f"(from {KPIS['Open cases breaching SLA'][1]}).",
        "- Screening escalations trending up — review threshold calibration.",
        "",
        "## Recommended actions",
        "1. Clear remaining SLA-breaching cases this week.",
        "2. Review rule thresholds where false positives are rising.",
        "3. Confirm Travel Rule completeness on all transfers >= USD 1,000.",
        "",
        "_Synthetic data — illustrative MI format only._",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    md = build()
    with open("compliance_report.md", "w") as f:
        f.write(md)
    print(md)
    print("\nWrote compliance_report.md")
