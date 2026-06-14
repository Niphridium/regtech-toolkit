"""
Risk-scoring for AML — multivariate anomaly detection with an EXPLAINABILITY layer.

Uses the Mahalanobis distance (a legitimate multivariate outlier measure) so it
runs anywhere with just numpy/pandas — no heavy ML stack required. Every score
ships with the top features that drove it, so an analyst (or a regulator) can see
*why* a customer was flagged. A score you can't explain is a liability, not an
asset. (Drop-in path: swap the scorer for an Isolation Forest at scale.)

Synthetic data only. No real customers.
Run:  python risk_scoring.py
"""
from __future__ import annotations
import numpy as np
import pandas as pd

RNG = np.random.default_rng(7)

FEATURES = [
    "monthly_volume_usd",      # total throughput
    "tx_count",                # number of transactions
    "avg_tx_usd",              # average ticket size
    "pct_to_high_risk_juris",  # share of flows to high-risk jurisdictions
    "rapid_fire_days",         # days with > 5 withdrawals
    "distinct_counterparties", # unique counterparties
    "structuring_hits",        # amounts just below thresholds
]


def synth_customers(n=400):
    rows = []
    for i in range(n):
        profile = RNG.choice(["retail", "active", "high_risk"], p=[0.7, 0.22, 0.08])
        if profile == "retail":
            f = [RNG.uniform(200, 20_000), RNG.integers(1, 15), 0, RNG.uniform(0, .05),
                 0, RNG.integers(1, 6), 0]
        elif profile == "active":
            f = [RNG.uniform(20_000, 400_000), RNG.integers(15, 80), 0, RNG.uniform(0, .15),
                 RNG.integers(0, 2), RNG.integers(5, 30), RNG.integers(0, 2)]
        else:  # high_risk
            f = [RNG.uniform(400_000, 8_000_000), RNG.integers(40, 200), 0, RNG.uniform(.2, .8),
                 RNG.integers(1, 6), RNG.integers(1, 8), RNG.integers(2, 9)]
        f[2] = f[0] / max(int(f[1]), 1)  # avg ticket
        rows.append([f"C{i:04d}", profile] + list(f))
    return pd.DataFrame(rows, columns=["customer_id", "_true_profile"] + FEATURES)


def _standardize(X):
    mu = X.mean(axis=0)
    sd = X.std(axis=0) + 1e-9
    return (X - mu) / sd


def score(df: pd.DataFrame):
    X = df[FEATURES].astype(float).values
    Z = _standardize(X)                                  # z-scored features

    # Mahalanobis distance with a small ridge for numerical stability
    cov = np.cov(Z, rowvar=False) + np.eye(Z.shape[1]) * 1e-3
    inv = np.linalg.pinv(cov)
    d = np.sqrt(np.einsum("ij,jk,ik->i", Z, inv, Z))     # distance per row
    risk = (100 * (d - d.min()) / (np.ptp(d) + 1e-9)).round(1)

    # ---- explainability: which features pushed this row up (in std devs) ----
    reasons = []
    for i in range(len(df)):
        idx = np.argsort(Z[i])[::-1][:3]
        reasons.append(", ".join(
            f"{FEATURES[j]} (+{Z[i][j]:.1f}σ)" for j in idx if Z[i][j] > 0.5))

    out = df[["customer_id", "_true_profile"]].copy()
    out["risk_score"] = risk
    out["band"] = pd.cut(risk, [-1, 40, 70, 101], labels=["LOW", "MEDIUM", "HIGH"])
    out["top_drivers"] = reasons
    return out.sort_values("risk_score", ascending=False).reset_index(drop=True)


if __name__ == "__main__":
    df = synth_customers()
    res = score(df)
    res.to_csv("ml_risk_scores.csv", index=False)
    print("RISK SCORING (synthetic) — explainable multivariate anomaly detection\n" + "-" * 64)
    print(res.head(10).to_string(index=False))
    top = res.head(int(0.08 * len(res)))
    hit = (top["_true_profile"] == "high_risk").mean()
    print("-" * 64)
    print(f"Share of true high-risk profiles in the top 8% by score: {hit:.0%}")
    print("Wrote ml_risk_scores.csv")
