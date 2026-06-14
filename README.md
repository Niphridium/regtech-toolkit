# RegTech Toolkit — AML × AI

A growing set of small, focused, **explainable** building blocks for crypto/VASP
compliance — the space between "black-box vendor" and "manual spreadsheet".
Each tool runs on **synthetic data**, is documented, and is built to be
defensible to a regulator.

> ⚠️ **Synthetic / public-knowledge only.** No real customer, transaction, or
> employer data anywhere in this repository. These are portfolio demos, not
> production systems.

## Modules

**Detection & monitoring**

| File | What it does |
|------|--------------|
| `risk_scoring.py` | Multivariate anomaly scoring (Mahalanobis) with an explainability layer — every score lists the features that drove it |
| `fund_flow.py` | Directed-graph view of transfers; detects collector/mixer hubs and pass-through layering |
| `rules_engine.py` | Rules-as-config engine — detection rules live as data so analysts tune them without code changes |
| `address_risk.py` | Mock on-chain address risk lookup (score + reasons + BLOCK/REVIEW/ALLOW) |

**Screening**

| File | What it does |
|------|--------------|
| `sanctions_screen.py` | Fuzzy name screening vs a watchlist (transliterations, name-order swaps, typos) |
| `adverse_media.py` | Adverse-media screening — classifies hits into financial-crime categories with severity |
| `travel_rule_validator.py` | FATF Travel Rule (IVMS101-style) payload validation with the de-minimis threshold |

**Investigations & reporting**

| File | What it does |
|------|--------------|
| `sar_generator.py` | Drafts a SAR/STR narrative from alert flags (human-in-the-loop) |
| `case_management.py` | Alert→case lifecycle with SLA aging and breach/unassigned flags |
| `compliance_report.py` | Monthly compliance KPI / MI report (markdown) with month-over-month deltas |
| `rulebook_retriever.py` | Retrieval layer of a RAG assistant over VARA/SFC/AIFC/FATF rule snippets |

**Risk & onboarding**

| File | What it does |
|------|--------------|
| `ewra.py` | Enterprise-Wide Risk Assessment — residual risk from inherent risk × control effectiveness |
| `kyc_checklist.py` | Risk-tiered KYC/EDD document checklist generator |
| `kyc_calculator.html` | Single-file web KYC risk-rating calculator (no data stored) |

![fund-flow example](fund_flow_graph.png)

## Quick start
```bash
pip install -r requirements.txt        # pandas, numpy, networkx, matplotlib

# detection & monitoring
python risk_scoring.py                  # -> ml_risk_scores.csv
python fund_flow.py                     # -> fund_flow_graph.png
python rules_engine.py
python address_risk.py

# screening
python sanctions_screen.py             # -> screening_results.csv
python adverse_media.py "Viktor Petrov"
python travel_rule_validator.py

# investigations & reporting
python sar_generator.py                # -> sar_draft.md
python case_management.py
python compliance_report.py            # -> compliance_report.md
python rulebook_retriever.py "travel rule"

# risk & onboarding
python ewra.py
python kyc_checklist.py company HIGH
# kyc_calculator.html — open in a browser
```

Most modules use only the Python standard library; `risk_scoring.py` and
`fund_flow.py` use numpy/pandas/matplotlib.

## Design principles
1. **Explainable over clever** — every score/flag carries its reason.
2. **Rules first, ML second** — ML augments transparent logic, never replaces it.
3. **Human-in-the-loop** — tools draft and prioritise; people decide and file.
4. **Auditable & reproducible** — seeded synthetic data, no hidden state.

## License
MIT — see [LICENSE](LICENSE).

---
Built by **Merey Nurkaliyev** — AML Team Lead, crypto compliance, on-chain
investigations & RegTech. [linkedin.com/in/merey-nurkaliyev](https://www.linkedin.com/in/merey-nurkaliyev)
