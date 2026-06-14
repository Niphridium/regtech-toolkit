"""
Adverse-media screening.

Scans a (synthetic) news corpus for a subject name and classifies any hits into
financial-crime categories (fraud, corruption, sanctions, laundering, terrorism)
with a severity. Adverse media is a core EDD input the FATF risk-based approach
expects for higher-risk customers.

Synthetic articles only. Run:  python adverse_media.py "Subject Name"
"""
from __future__ import annotations
import re
import sys

# SYNTHETIC headlines (not real)
CORPUS = [
    "Viktor Petrov charged in multimillion fraud and embezzlement scheme",
    "Local entrepreneur Sarah Johnson opens new bakery downtown",
    "Authorities link Chen Wei to sanctions-evasion network",
    "Dmitry Sokolov named in corruption and bribery probe",
    "Aisha Al-Rashid honoured for charity work in the community",
    "Funds traced to laundering ring; Maria Gonzalez Ruiz under investigation",
]

CATEGORIES = {
    "fraud": ["fraud", "embezzlement", "ponzi", "scam"],
    "corruption": ["corruption", "bribery", "kickback"],
    "sanctions": ["sanctions", "sanction", "evasion", "embargo"],
    "money_laundering": ["laundering", "launder", "smurfing"],
    "terrorism_financing": ["terror", "financing of terrorism"],
}
SEVERITY = {"sanctions": "CRITICAL", "terrorism_financing": "CRITICAL",
            "money_laundering": "HIGH", "corruption": "HIGH", "fraud": "MEDIUM"}


def screen(name: str):
    name_l = name.lower()
    hits = []
    for article in CORPUS:
        if name_l in article.lower():
            cats = [c for c, kws in CATEGORIES.items()
                    if any(re.search(rf"\b{kw}", article.lower()) for kw in kws)]
            if cats:
                hits.append((article, cats))
    return hits


if __name__ == "__main__":
    name = " ".join(sys.argv[1:]) or "Viktor Petrov"
    hits = screen(name)
    print(f"ADVERSE-MEDIA SCREENING — {name} (synthetic)\n" + "-" * 64)
    if not hits:
        print("No adverse media found. (Clear — record the negative result.)")
    worst = "LOW"
    order = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    for article, cats in hits:
        sev = max((SEVERITY[c] for c in cats), key=order.index)
        worst = max(worst, sev, key=order.index)
        print(f"[{sev}] {', '.join(cats)}\n   \"{article}\"")
    if hits:
        print("-" * 64)
        print(f"Overall adverse-media risk: {worst}. Escalate to EDD if HIGH/CRITICAL.")
