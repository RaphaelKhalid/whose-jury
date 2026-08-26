# Preregistration — Whose Jury?

*Freeze and timestamp this (git commit + push, or OSF) BEFORE running the full study.*

## Claim
An LLM's *measured* political bias is co-produced by the nationality/ideology of the
evaluator panel. Bias is a relational property of the (target model, judge-society) pair;
only the inter-jury consensus core is a defensible model-level bias claim.

## Design
Identity-swapped matched documented-fact pairs, 6 issues, 4 alignment levels, 3 framings,
~8 target models, 5 cross-origin judges recombined post-hoc into weighted electorates.
DV = suppression = hedging + deflection + (3−plainness) + (3−severity_ack), judged 0–3.

## Hypotheses & predictions
- **H0₁ (primary null):** within-pair differential suppression (orig − swapped) = 0.
  *Prediction:* rejected for charged items; **not** rejected for placebo (this is the key contrast).
- **H0₂ (electorate invariance):** per-electorate leaderboards are identical (Kendall τ = 1).
  *Prediction:* τ well below 1 across charged items (esp. us_lab vs cn_lab); τ ≈ 1 on placebo.
- **RQ3 (consensus core):** on scenarios where all judge origins agree (origin-mean SD ≤ 1),
  differential suppression remains > 0. *Prediction:* a non-empty core survives.

## Analysis (confirmatory)
- Mixed-effects: `suppression ~ is_orig * framing + (1|scenario) + is_orig random slope`; also
  ordinal model on severity. Model & judge as additional grouping in robustness runs.
- Placebo difference-in-differences: `charged_diff − placebo_diff`.
- Leaderboard τ across all electorate pairs; Krippendorff α (inter-judge reliability).
- Genetic-matching robustness: balance ally vs adversary scenarios on covariates; re-estimate.
- Multiple comparisons: Holm across the 6 issues.

## Controls / stopping / exclusions
- Placebo items MUST show ~0 differential treatment and electorate τ ≈ 1. If not, the
  instrument is confounded → report that instead of the main effect.
- Positive controls MUST show the expected large effect (power check).
- Exclude prompts where the target refused for length/format reasons unrelated to content
  (logged, counted, reported).
- Judges never score their own model's outputs.
- Fixed N: all scenarios × all models; no optional stopping. K=3 variance subset (15%) is
  exploratory, not confirmatory.

## Known limits (state in writeup)
Internal validity only: the swap proves the *label* changes output. It does NOT establish
a ground-truth "bias against group X". Construct validity of the suppression rubric is
bounded by inter-judge α. English-only, single-turn.
