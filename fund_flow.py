"""
On-chain fund-flow graph — model transfers as a directed graph and surface
structural red flags (collector / mixer hubs, fan-out, pass-through nodes).

Synthetic transfers only. No real addresses.
Run:  python fund_flow.py   ->  prints findings + writes fund_flow_graph.png
"""
from __future__ import annotations
import numpy as np
import networkx as nx
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RNG = np.random.default_rng(11)
NAVY, RED, BLUE, GREY = "#1F3A5F", "#C0392B", "#2E75B6", "#9AA7B4"


def addr(prefix="0x"):
    return prefix + "".join(RNG.choice(list("0123456789abcdef"), size=6))


def synth_transfers(n_users=22):
    """Most users send to their own destination; a few funnel into one collector
    address (mixer/exchanger pattern) which then fans out."""
    edges = []
    collector = addr()           # the suspicious hub
    sink_a, sink_b = addr(), addr()
    users = [addr() for _ in range(n_users)]
    for u in users:
        if RNG.random() < 0.55:                       # funnel into collector
            edges.append((u, collector, RNG.uniform(5_000, 200_000)))
        else:                                         # normal: own destination
            edges.append((u, addr(), RNG.uniform(100, 20_000)))
    # collector fans out to a couple of sinks (layering)
    edges.append((collector, sink_a, RNG.uniform(300_000, 900_000)))
    edges.append((collector, sink_b, RNG.uniform(200_000, 700_000)))
    return edges, collector


def build(edges):
    G = nx.DiGraph()
    for s, d, amt in edges:
        if G.has_edge(s, d):
            G[s][d]["amount"] += amt
        else:
            G.add_edge(s, d, amount=amt)
    return G


def findings(G):
    out = []
    for node in G.nodes():
        indeg = G.in_degree(node)
        outdeg = G.out_degree(node)
        in_amt = sum(d["amount"] for _, _, d in G.in_edges(node, data=True))
        if indeg >= 5:
            out.append((node, "COLLECTOR/MIXER HUB",
                        f"{indeg} distinct senders, ${in_amt:,.0f} in"))
        if indeg >= 1 and outdeg >= 1 and in_amt > 250_000:
            out.append((node, "PASS-THROUGH",
                        f"funds in (${in_amt:,.0f}) then forwarded — possible layering"))
    return out


def draw(G, collector, path="fund_flow_graph.png"):
    pos = nx.spring_layout(G, seed=3, k=0.9)
    indeg = dict(G.in_degree())
    node_colors = [RED if n == collector else (BLUE if indeg[n] == 0 else GREY)
                   for n in G.nodes()]
    node_sizes = [400 + 220 * indeg[n] for n in G.nodes()]
    fig, ax = plt.subplots(figsize=(10, 7), dpi=130)
    nx.draw_networkx_edges(G, pos, ax=ax, edge_color="#C9D2DC",
                           arrows=True, arrowsize=9, width=1.0)
    nx.draw_networkx_nodes(G, pos, ax=ax, node_color=node_colors,
                           node_size=node_sizes, edgecolors="white", linewidths=0.8)
    ax.set_title("On-chain fund-flow graph (synthetic)\n"
                 "red = collector/mixer hub · blue = source wallets",
                 color=NAVY, fontsize=13, fontweight="bold", loc="left")
    ax.axis("off")
    fig.text(0.01, 0.01,
             "Prepared by Merey Nurkaliyev — AML Team Lead | linkedin.com/in/merey-nurkaliyev",
             fontsize=7.5, color=GREY)
    fig.savefig(path, facecolor="white", bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    edges, collector = synth_transfers()
    G = build(edges)
    print("FUND-FLOW GRAPH (synthetic)\n" + "-" * 60)
    print(f"Nodes: {G.number_of_nodes()}  Edges: {G.number_of_edges()}")
    print("-" * 60)
    for node, kind, detail in findings(G):
        tag = "  <-- collector" if node == collector else ""
        print(f"[{kind}] {node}  {detail}{tag}")
    draw(G, collector)
    print("-" * 60)
    print("Wrote fund_flow_graph.png")
