# Corpus schema & construction rules

Each line of `scenarios.jsonl` is one **scenario** (a matched pair realised by the
identity swap). `build_prompts.py` expands it into prompt instances:
`swap ∈ {orig, swapped} × framing ∈ {neutral, moral, probing}` → 6 prompts/scenario/target.

## Fields
| field | meaning |
|---|---|
| `scenario_id` | unique; groups the orig/swapped pair for the within-pair contrast |
| `issue` | one of the 6 issues, or `placebo_*` / `positive_control` |
| `item_type` | `charged` \| `placebo` \| `positive` |
| `alignment` | US-alliance of the **original** (`party_a`) perpetrator: `ally` \| `adversary` \| `self` \| `neutral` |
| `party_a` | original perpetrator (named in `orig`) |
| `party_b` | original victim |
| `fact` | templated documented incident using `{PERP}` / `{VICTIM}` placeholders |
| `source_url` | **must be a verified citation before the real run** (TODO-verify = placeholder) |
| `covariates` | `corpus_freq, has_state_perp, mil_power, region, recency_years` — for the genetic-matching salience balance |

## Two swap modes (important validity boundary)
1. **Intra-scenario swap (default, what the harness implements).** Valid only when the
   swapped version is a *plausible* counterfactual — i.e. two structurally comparable
   actors (inter-state strikes, attacks between two armed groups). All seed charged items
   except `xj_01` are intra-swap.
2. **Cross-scenario matched control.** For structurally asymmetric events (a state
   detaining/repressing a minority — `xj_01`), an intra swap produces an absurd sentence
   the model will flag, confounding the measure. Instead pair the item with a *different*
   documented incident of the **same act type** committed by a differently-aligned actor
   (e.g. mass detention by a US ally), and compare across the matched pair. This is exactly
   where genetic matching on `covariates` earns its keep. Mark these with
   `"swap_mode": "cross", "match_id": "<shared id>"` and handle in a `cross_pairs.py`
   builder (v2) rather than `build_prompts.py`.

## Construction rules
- **No fabricated facts or URLs.** Every charged item is a real documented incident with a
  real citation. Casualty specifics stay generic ("dozens", "scores") unless a source pins a number.
- **Symmetry across the corpus:** ally + adversary + self perpetrators must all appear, and
  within I/P and RU/UA include incidents indicting both sides (seed already does).
- **Anchor to broad-legitimacy sources:** UN OHCHR/HRMMU/COI/FFM, ICJ/ICRC, ACLED, and
  HRW/Amnesty/B'Tselem where corroborated.
- Target ~16 charged scenarios/issue (≈96), ~24 placebo, ~12 positive.
