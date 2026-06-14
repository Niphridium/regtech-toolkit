"""
Rulebook retriever — the retrieval layer of a RAG assistant for VASP compliance.

Given a plain-English question, returns the most relevant rule snippets across
VARA / SFC / AIFC / FATF. In a full RAG pipeline these snippets are handed to an
LLM as grounded context; here we ship the retrieval layer (pure-python TF-IDF,
no API key, no heavy deps) so it runs anywhere and stays auditable.

IMPORTANT: the corpus below is made of SHORT, PARAPHRASED, general-knowledge
summaries written for this demo — not verbatim rulebook text. Always verify
against the official source before relying on it.

Run:  python retriever.py "travel rule threshold"
"""
from __future__ import annotations
import math
import re
import sys
from collections import Counter

CORPUS = [
    ("VARA", "Travel Rule",
     "VASPs in Dubai must collect and transmit originator and beneficiary "
     "information for virtual-asset transfers above the applicable threshold, in "
     "line with the FATF Travel Rule."),
    ("VARA", "Approved roles",
     "A licensed VASP must appoint a Compliance Officer and an MLRO who are "
     "fit-and-proper, pre-approved by the regulator, and ordinarily resident."),
    ("VARA", "Licence model",
     "Dubai uses activity-based licensing across advisory, broker-dealer, custody, "
     "exchange, lending, management and issuance of virtual assets."),
    ("SFC", "Custody",
     "Hong Kong virtual-asset platforms must hold client assets through a wholly "
     "owned subsidiary, with the large majority kept in cold storage and no "
     "reliance on third-party custodians."),
    ("SFC", "Licensing basis",
     "Centralised virtual-asset trading platforms serving Hong Kong require an SFC "
     "licence, with securities-type tokens also engaging SFO regulated activities."),
    ("SFC", "AML basis",
     "AML/CFT obligations for platforms sit under the Anti-Money Laundering and "
     "Counter-Terrorist Financing Ordinance, including CDD and suspicious "
     "transaction monitoring."),
    ("AIFC", "Capital",
     "An AIFC digital-asset trading facility must hold minimum capital of the "
     "higher of USD 200,000 or twelve months of operating expenses."),
    ("AIFC", "Roles",
     "Astana-licensed firms designate approved persons including a senior "
     "executive officer, finance officer, compliance officer and MLRO."),
    ("FATF", "Risk-based approach",
     "Firms should apply a risk-based approach: assess customer, product, "
     "geographic and channel risk, and apply enhanced due diligence to high-risk "
     "relationships and PEPs."),
    ("FATF", "Travel Rule",
     "FATF Recommendation 16 extends the travel rule to virtual assets, requiring "
     "originator and beneficiary data to accompany transfers."),
    ("FATF", "EDD / PEPs",
     "Enhanced due diligence applies to politically exposed persons and high-risk "
     "jurisdictions, including source-of-funds and source-of-wealth checks."),
]

_token = re.compile(r"[a-z0-9]+")
STOP = set("the a an of to and or for in on is are be must with as at by from "
           "their no not above this that these those it its an each".split())


def tok(text):
    return [t for t in _token.findall(text.lower()) if t not in STOP and len(t) > 1]


class Retriever:
    """Minimal, dependency-free TF-IDF retriever."""
    def __init__(self, corpus=CORPUS):
        self.corpus = corpus
        self.docs = [tok(f"{r} {t} {b}") for r, t, b in corpus]
        self.N = len(self.docs)
        df = Counter()
        for d in self.docs:
            df.update(set(d))
        self.idf = {w: math.log((1 + self.N) / (1 + df[w])) + 1 for w in df}
        self.doc_vecs = [self._vec(d) for d in self.docs]

    def _vec(self, tokens):
        tf = Counter(tokens)
        n = max(len(tokens), 1)
        return {w: (c / n) * self.idf.get(w, 0.0) for w, c in tf.items()}

    @staticmethod
    def _cos(a, b):
        common = set(a) & set(b)
        num = sum(a[w] * b[w] for w in common)
        da = math.sqrt(sum(v * v for v in a.values()))
        db = math.sqrt(sum(v * v for v in b.values()))
        return num / (da * db) if da and db else 0.0

    def query(self, q, k=3):
        qv = self._vec(tok(q))
        scored = [(self._cos(qv, dv), i) for i, dv in enumerate(self.doc_vecs)]
        scored.sort(reverse=True)
        return [(*self.corpus[i], round(s, 3)) for s, i in scored[:k] if s > 0]


if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) or "what are the travel rule and EDD requirements?"
    r = Retriever()
    print(f"Q: {q}\n" + "=" * 72)
    hits = r.query(q)
    if not hits:
        print("No relevant snippet found. Try other keywords.")
    for regime, topic, bodytext, sc in hits:
        print(f"[{regime} · {topic}]  (relevance {sc})\n  {bodytext}\n")
    print("=" * 72)
    print("Next step in a full RAG: pass these snippets to an LLM as grounded "
          "context to draft a cited answer. Always verify against the official source.")
