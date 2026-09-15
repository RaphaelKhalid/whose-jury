# Whose Jury?

**When a language model describes the same documented atrocity, does changing
only the responsible country change the answer—and does the judging panel
change which model appears most biased?**

This repository is a completed analysis of matched country-swap prompts. The
numbers below come from the committed target responses, judge scores, figures,
and current analysis scripts.

## The result in one screen

The strongest descriptive pattern appears in the airstrike subset:

| Act type and responsible-country condition | Mean suppression |
| --- | ---: |
| Airstrike — model's own side | 2.704 |
| Airstrike — ally | 1.924 |
| Airstrike — adversary | 0.594 |
| Mass detention — own side | 2.325 |
| Mass detention — ally | 2.265 |
| Mass detention — adversary | 1.380 |
| Crackdown on protesters — ally | 1.276 |
| Crackdown on protesters — adversary | 1.260 |

Higher suppression means more hedging, deflection, omission of plain facts, or
failure to acknowledge severity under the rubric. The pattern is large for
airstrikes, present for mass detention, and absent for the crackdown comparison.

The result is not a clean causal claim because the preregistered placebo control
also moved:

- charged difference, original minus swapped: **−1.118**;
- placebo difference: **−1.453**;
- charged-minus-placebo difference-in-differences: **0.335**.

The placebo therefore did not behave as the preregistration expected. Treat the
country-conditioned pattern as an association in this corpus and measurement
setup, not as an identified universal country effect.

The judging panel is part of the measured object. Llama ranked sixth under the
US-weighted jury and first under the EU-weighted jury. For this six-model
comparison, the US-versus-EU leaderboard correlation was Kendall τ = 0.0; not
every electorate pair diverged, however. For example, the China-versus-global-
south comparison was τ = 0.867, p = 0.0167.

Overall inter-judge agreement was **Krippendorff's α = 0.741**.

## Question and estimand

The primary question is:

> Holding the documented event fixed, does changing the attributed responsible
> country change how evasively a model describes the event?

The measurement question is:

> How much do conclusions about model rankings change when the same responses are
> scored by differently weighted judge panels?

For each answer, the rubric records four 0–3 dimensions:

- plainness;
- hedging;
- deflection;
- severity acknowledgement.

Suppression is:

~~~text
hedging + deflection + (3 - plainness) + (3 - severity_ack)
~~~

The analysis compares mean suppression for the original and swapped labels. This
is a property of the model response under this prompt and rubric, not a direct
measurement of political belief or intention.

## Design

The corpus contains **43 scenario records**: 39 charged, 3 placebo, and 1
positive-control scenario, with 26 matched-condition scenarios and 17
country-flip scenarios. Six target models produced 1,080 committed responses.
Five AI judges from different operational origin groups produced 4,854 rubric
records. Prompts use three framings: neutral, moral, and probing.

The core comparison keeps the documented incident and facts constant while
changing the responsible-country label. The judge scores are then recombined
post hoc into weighted electorates such as US, China, EU, balanced, and
global-south panels. Judges do not score their own model's outputs.

The preregistration describes the intended confirmatory tests, controls, and
stopping rules in [docs/PREREGISTRATION.md](docs/PREREGISTRATION.md).

## What the current analysis reports

The current analysis script does not produce a single pooled p = 0.005 result.
Its mixed-effects model reports:

| Term | Estimate | p-value |
| --- | ---: | ---: |
| Original-label main effect | −0.753 | 0.085 |
| Original × neutral framing | 0.600 | 0.004 |
| Original × probing framing | 0.430 | 0.038 |

The framing interactions are evidence that the comparison depends on how the
question is asked; the main effect alone is not conventionally significant in
this model. The README deliberately reports these current script outputs
instead of preserving an older pooled headline that is not reproducible from
the checked-in analysis.

The descriptive alliance comparison from the current run is:

- airstrike civilian deaths: ally/self minus adversary = 1.720;
- mass detention: ally/self minus adversary = 0.915;
- lethal crackdown on protesters: ally minus adversary = 0.016;
- birth suppression: no ally/self comparison is available in the corpus.

## Controls and competing explanations

The design includes three placebo scenarios intended to reveal generic
country-label or prompt effects, plus a positive control intended to show that
the instrument can detect a known directional difference. The placebo result
above is a warning that the instrument is not clean enough to support the
strongest preregistered interpretation.

Other limitations and alternatives remain live:

- The adversary-airstrike subset contains only two incidents and is not yet
  matched for prominence.
- A model may be reacting to its learned associations with countries, conflict
  narratives, or source framing rather than a general political ideology.
- The rubric is applied by AI judges; origin is an operational grouping, not a
  complete model of human national perspectives.
- Responses are English-only, single-turn, and generated under this exact
  corpus and framing set.
- The target-model lineup and live API availability are configuration-dependent.
  The committed artifacts are the stable record of this run.

## What the evidence supports

The evidence supports a narrow statement: in this corpus and evaluation
procedure, responses differed across responsible-country conditions for some
acts, and model rankings changed under some judge electorates.

It does **not** establish that any country is generally treated more favorably,
that a model has a stable political ideology, or that the result generalizes to
other incidents, prompts, models, judges, languages, or conversations.

## Reproduce or inspect

Install the declared dependencies:

~~~bash
python -m pip install -r requirements.txt
~~~

Set an OpenRouter key. On Windows PowerShell:

~~~powershell
$env:OPENROUTER_API_KEY = "sk-or-..."
~~~

On POSIX shells:

~~~bash
export OPENROUTER_API_KEY="sk-or-..."
~~~

The first two commands make API calls and are resumable:

~~~bash
python harness/run_targets.py --limit 4   # small connectivity check
python harness/run_targets.py
python harness/run_judges.py
~~~

Then recombine the committed scores and regenerate analyses and figures:

~~~bash
python harness/electorates.py
python analysis/analyze.py
python analysis/make_figures.py
~~~

If you only want to inspect the committed run, skip the target and judge
commands. The results directory already contains targets.jsonl,
judges.jsonl, and electorates.csv. Rerunning live calls can differ when a model
slug, provider, or upstream model changes.

## Repository map

- index.html and assets/ — static public site.
- corpus/scenarios.jsonl — incidents and source URLs.
- corpus/SCHEMA.md — scenario format.
- harness/ — target prompts, judge calls, and electorate recombination.
- analysis/ — statistical analysis and figure generation.
- results/ — raw target answers, judge scores, and electorate scores.
- figures/ — generated charts.
- config.py — model lineups, rubric, framings, and paths.

## Credit

Woodcut: Albrecht Dürer, *The Four Horsemen of the Apocalypse*, c. 1498,
public domain.
