"""
Confirmatory analysis.

  RQ1  primary null: differential suppression = 0 (mixed-effects, scenario+model+judge REs)
  RQ2  leaderboard robustness: Kendall's tau between per-electorate leaderboards
  RQ3  consensus core: items where all judge origins agree, effect persists
  Null placebo: difference-in-differences (charged vs placebo) must isolate the effect
  Reliability: Krippendorff's alpha across judges

Genetic matching (entity-salience balance) is a robustness check — see NOTE at bottom;
run in R (Matching::GenMatch) or Python (see stub) on the per-scenario diffs with covariates.
"""
import json, os, sys, itertools
import numpy as np
import pandas as pd
from scipy.stats import kendalltau
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import JUDGES_OUT, ELECTORATE_OUT, RUBRIC_DIMS

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "harness"))
from harness.electorates import load_judges


def rq1_mixed_effects(df):
    import statsmodels.formula.api as smf
    d = df[df["item_type"] == "charged"].copy()
    # collapse judges to a per-(model,scenario,swap,framing) mean suppression, keep judge as RE via long form
    d["is_orig"] = (d["swap"] == "orig").astype(int)
    # continuous suppression ~ is_orig * framing, random intercepts for scenario & model
    d["grp"] = d["scenario_id"]
    md = smf.mixedlm("suppression ~ is_orig * C(framing)", d, groups=d["grp"],
                     re_formula="~is_orig")
    res = md.fit(method="lbfgs", maxiter=200)
    return res.summary()


def rq2_leaderboard_tau(electorate_csv=ELECTORATE_OUT):
    res = pd.read_csv(electorate_csv)
    elects = res.electorate.unique()
    taus = {}
    for a, b in itertools.combinations(elects, 2):
        ra = res[res.electorate == a].set_index("model")["rank"]
        rb = res[res.electorate == b].set_index("model")["rank"]
        common = ra.index.intersection(rb.index)
        tau, p = kendalltau(ra[common], rb[common])
        taus[(a, b)] = (round(tau, 3), round(p, 4))
    return taus


def rq3_consensus_core(df, agree_sd=1.0):
    """Items where judge-origin means agree (low spread) AND target still shows
    asymmetric suppression. Returns the surviving scenario set + its mean effect."""
    d = df[df["item_type"] == "charged"]
    # spread across judge origins on suppression, per scenario
    origin_means = (d.groupby(["scenario_id", "judge_origin"])["suppression"].mean()
                      .groupby("scenario_id").std())
    consensus = origin_means[origin_means <= agree_sd].index
    core = d[d["scenario_id"].isin(consensus)]
    piv = (core.groupby(["model", "scenario_id", "swap"])["suppression"].mean()
               .unstack("swap").dropna(subset=["orig", "swapped"]))
    eff = (piv["orig"] - piv["swapped"]).mean()
    return {"n_consensus_scenarios": len(consensus), "mean_diff_suppression": round(float(eff), 3)}


def placebo_did(df):
    d = df.copy()
    piv = (d.groupby(["item_type", "scenario_id", "swap"])["suppression"].mean()
             .unstack("swap").dropna(subset=["orig", "swapped"]))
    piv["diff"] = piv["orig"] - piv["swapped"]
    by_type = piv.reset_index().groupby("item_type")["diff"].mean()
    did = by_type.get("charged", np.nan) - by_type.get("placebo", np.nan)
    return {"charged_diff": round(float(by_type.get("charged", np.nan)), 3),
            "placebo_diff": round(float(by_type.get("placebo", np.nan)), 3),
            "DiD": round(float(did), 3)}


def alliance_effect(df):
    """TEST B: for matched-act items, compare mean suppression by alignment WITHIN each
    act_type (no swap). The alliance hypothesis: models suppress LESS (soften more) for
    ally/self perpetrators than for adversary ones, holding act_type fixed.
    Returns per-act means + an ally/self-minus-adversary contrast (negative = softer on allies)."""
    d = df[df.get("test").eq("matched")] if "test" in df else df[df["item_type"] == "charged"]
    if len(d) == 0:
        return "no matched items"
    # mean suppression per (act_type, alignment), averaged over judges & scenarios
    tbl = (d.groupby(["act_type", "alignment"])["suppression"].mean().round(3).unstack("alignment"))
    contrasts = {}
    for act, row in tbl.iterrows():
        allyself = np.nanmean([row.get("ally", np.nan), row.get("self", np.nan)])
        adv = row.get("adversary", np.nan)
        contrasts[act] = round(float(allyself - adv), 3)  # <0 => allies softened more
    return {"suppression_by_act_alignment": tbl, "allyself_minus_adversary": contrasts}


def krippendorff_alpha(df):
    try:
        import krippendorff
    except ImportError:
        return "krippendorff not installed"
    d = df[df["item_type"] == "charged"]
    wide = d.pivot_table(index="judge", columns="prompt_id", values="suppression")
    return round(float(krippendorff.alpha(reliability_data=wide.values,
                                          level_of_measurement="ordinal")), 3)


if __name__ == "__main__":
    df = load_judges()
    print("=== RQ2 leaderboard Kendall tau (low = different worlds) ===")
    for k, v in rq2_leaderboard_tau().items():
        print(f"  {k[0]:>12} vs {k[1]:<12}: tau={v[0]}  p={v[1]}")
    print("\n=== RQ3 consensus core ===", rq3_consensus_core(df))
    print("\n=== Placebo difference-in-differences ===", placebo_did(df))
    print("\n=== TEST B: alliance effect (matched acts; <0 = allies softened more) ===")
    ae = alliance_effect(df)
    if isinstance(ae, dict):
        print(ae["suppression_by_act_alignment"].to_string())
        print("ally/self minus adversary:", ae["allyself_minus_adversary"])
    else:
        print(ae)
    print("\n=== Inter-judge Krippendorff alpha ===", krippendorff_alpha(df))
    print("\n=== RQ1 mixed-effects ===")
    print(rq1_mixed_effects(df))

# NOTE genetic matching: the swap already identifies the label effect. Genetic
# matching is only for the entity-salience robustness check — balance ally- vs
# adversary-perpetrator SCENARIOS on covariates (corpus_freq, has_state_perp,
# mil_power, region, recency). Canonical: R Matching::GenMatch on scenario-level
# diffs. Python alt: build a balanced subsample via coarsened exact matching on the
# covariate bins, then re-run placebo_did / rq3 on it and confirm the effect holds.
