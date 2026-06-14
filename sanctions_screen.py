"""
Sanctions / PEP name-screening engine (fuzzy matching).

Screens customer names against a watchlist using normalised fuzzy matching,
returns a match score and a decision band, and is tuned to surface likely hits
WITHOUT drowning analysts in false positives.

Uses only the Python standard library (difflib) — no paid list, no real data.
The watchlist and customers here are entirely SYNTHETIC.

Run:  python screen.py
"""
from __future__ import annotations
import csv
import unicodedata
from difflib import SequenceMatcher

# --- tiny SYNTHETIC "watchlist" (not a real sanctions/PEP list) -------------
WATCHLIST = [
    {"name": "Viktor Petrov",        "type": "SANCTION", "program": "SYNTH-OFAC"},
    {"name": "Aisha Al-Rashid",      "type": "PEP",      "program": "SYNTH-PEP"},
    {"name": "Chen Wei",             "type": "SANCTION", "program": "SYNTH-EU"},
    {"name": "Dmitry Sokolov",       "type": "PEP",      "program": "SYNTH-PEP"},
    {"name": "Maria Gonzalez Ruiz",  "type": "SANCTION", "program": "SYNTH-UN"},
    {"name": "Olusegun Adeyemi",     "type": "PEP",      "program": "SYNTH-PEP"},
]

# --- SYNTHETIC customers, incl. near-misses / transliterations --------------
CUSTOMERS = [
    "John Smith",
    "Viktor Petroff",        # transliteration variant of a sanctioned name
    "Aysha Al Rashid",       # spacing/spelling variant of a PEP
    "Wei Chen",              # name-order swap
    "Maria G. Ruiz",         # abbreviated middle name
    "Sarah Johnson",
    "Dmitriy Sokolov",       # transliteration variant
    "Olusegun Adeyemy",      # one-letter typo
    "Liam O'Connor",
]

REVIEW_THRESHOLD = 0.80   # >= this -> escalate for analyst review
POSSIBLE_THRESHOLD = 0.70 # >= this -> possible match, lower priority


def normalise(name: str) -> str:
    name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    return " ".join(sorted(name.lower().replace(".", " ").replace("'", " ").split()))


def similarity(a: str, b: str) -> float:
    # token-sorted ratio handles name-order swaps and middle-name noise
    return SequenceMatcher(None, normalise(a), normalise(b)).ratio()


def screen(customer: str):
    best = max(WATCHLIST, key=lambda w: similarity(customer, w["name"]))
    sc = similarity(customer, best["name"])
    if sc >= REVIEW_THRESHOLD:
        decision = "ESCALATE"
    elif sc >= POSSIBLE_THRESHOLD:
        decision = "POSSIBLE"
    else:
        decision = "CLEAR"
    return {"customer": customer, "best_match": best["name"], "list_type": best["type"],
            "program": best["program"], "score": round(sc, 3), "decision": decision}


if __name__ == "__main__":
    results = [screen(c) for c in CUSTOMERS]
    with open("screening_results.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        w.writeheader(); w.writerows(results)

    print("SANCTIONS / PEP SCREENING (synthetic)\n" + "-" * 72)
    print(f"{'customer':<22}{'best match':<20}{'type':<10}{'score':<8}decision")
    print("-" * 72)
    for r in sorted(results, key=lambda x: x["score"], reverse=True):
        print(f"{r['customer']:<22}{r['best_match']:<20}{r['list_type']:<10}"
              f"{r['score']:<8}{r['decision']}")
    n_esc = sum(r["decision"] == "ESCALATE" for r in results)
    print("-" * 72)
    print(f"{n_esc} name(s) escalated for review. Wrote screening_results.csv")
