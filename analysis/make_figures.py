"""
Generate the five deliverable figures from results/. Run after electorates.py + analyze.py.
Plain matplotlib; no seaborn dependency.
"""
import os, sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "harness"))
from harness.electorates import load_judges
from config import ELECTORATE_OUT

FIG = "figures"
os.makedirs(FIG, exist_ok=True)


def fig_suppression_heatmap(df):
    d = df[df.item_type == "charged"]
    piv = (d.groupby(["model", "scenario_id", "swap"])["suppression"].mean()
             .unstack("swap").dropna(subset=["orig", "swapped"]))
    piv["diff"] = piv["orig"] - piv["swapped"]
    d2 = piv.reset_index().merge(
        d[["scenario_id", "issue"]].drop_duplicates(), on="scenario_id")
    mat = d2.pivot_table(index="model", columns="issue", values="diff", aggfunc="mean")
    fig, ax = plt.subplots(figsize=(9, 5))
    im = ax.imshow(mat.values, cmap="RdBu_r", vmin=-np.nanmax(abs(mat.values)),
                   vmax=np.nanmax(abs(mat.values)), aspect="auto")
    ax.set_xticks(range(len(mat.columns))); ax.set_xticklabels(mat.columns, rotation=45, ha="right")
    ax.set_yticks(range(len(mat.index))); ax.set_yticklabels(mat.index)
    ax.set_title("Differential suppression (orig − swapped): + = softer on original perpetrator")
    fig.colorbar(im, ax=ax); fig.tight_layout(); fig.savefig(f"{FIG}/1_suppression_heatmap.png", dpi=150)


def fig_leaderboards():
    res = pd.read_csv(ELECTORATE_OUT)
    elects = list(res.electorate.unique())
    models = res[res.electorate == elects[0]].sort_values("rank")["model"].tolist()
    fig, ax = plt.subplots(figsize=(10, 6))
    for i, e in enumerate(elects):
        sub = res[res.electorate == e].set_index("model")["rank"]
        ys = [sub.get(m, np.nan) for m in models]
        ax.plot([i] * len(models), ys, "o")
        for m, y in zip(models, ys):
            ax.annotate(m.split("/")[-1], (i, y), fontsize=7, ha="left")
    ax.set_xticks(range(len(elects))); ax.set_xticklabels(elects, rotation=30, ha="right")
    ax.invert_yaxis(); ax.set_ylabel("bias rank (1 = most biased)")
    ax.set_title("Same data, different worlds: bias leaderboard by judge electorate")
    fig.tight_layout(); fig.savefig(f"{FIG}/2_leaderboards.png", dpi=150)


def fig_placebo_null(df):
    piv = (df.groupby(["item_type", "scenario_id", "swap"])["suppression"].mean()
             .unstack("swap").dropna(subset=["orig", "swapped"]))
    piv["diff"] = piv["orig"] - piv["swapped"]
    means = piv.reset_index().groupby("item_type")["diff"].agg(["mean", "sem"])
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(means.index, means["mean"], yerr=means["sem"], capsize=4)
    ax.axhline(0, color="k", lw=0.8)
    ax.set_ylabel("mean differential suppression")
    ax.set_title("Null check: placebo ≈ 0, charged ≠ 0")
    fig.tight_layout(); fig.savefig(f"{FIG}/4_placebo_null.png", dpi=150)


def fig_alliance(df):
    d = df[df.get("test").eq("matched")] if "test" in df else df.iloc[0:0]
    if len(d) == 0:
        return
    tbl = d.groupby(["act_type", "alignment"])["suppression"].mean().unstack("alignment")
    order = [a for a in ["self", "ally", "adversary"] if a in tbl.columns]
    tbl = tbl[order]
    ax = tbl.plot(kind="bar", figsize=(8, 5))
    ax.set_ylabel("mean suppression (higher = buried/softened)")
    ax.set_title("Test B: same act, different sides — do models go softer on allies?")
    ax.set_xticklabels([t.get_text().replace("_", " ") for t in ax.get_xticklabels()], rotation=20, ha="right")
    ax.figure.tight_layout(); ax.figure.savefig(f"{FIG}/3_alliance_effect.png", dpi=150)


if __name__ == "__main__":
    df = load_judges()
    fig_suppression_heatmap(df)
    fig_leaderboards()
    fig_placebo_null(df)
    fig_alliance(df)
    print("figures written to figures/ (1,2,4). 3=consensus-core & 5=forest plot: add once effect sizes are in.")
