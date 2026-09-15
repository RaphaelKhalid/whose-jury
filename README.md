# Whose Jury?

**Do language models describe the same documented atrocity differently when only the responsible country changes—and does the jury used to score them change the result?**

This repository studies political bias in language-model descriptions using a matched country-swap design. The incidents and facts stay fixed; the responsible country changes.

## Headline findings

- For an airstrike that killed civilians, model responses were most evasive when the responsible country was the United States or an ally, and most direct when it was an adversary.
- Mean evasiveness scores were **2.70** for the model's own side, **1.92** for an ally, and **0.59** for an adversary.
- The pattern held for mass detention but disappeared for crackdowns on protesters.
- The pooled comparison had **p = 0.005**.
- The apparent ranking of models depends strongly on the nationality of the judges: Llama ranked last under an American jury and first under a European one, and the two rankings were uncorrelated.
- Agreement among judges was **Krippendorff's α = 0.74**.

These are results for this corpus, model set, prompt, and judging procedure—not a claim about any country or about political bias in language models in general.

## Question

When the underlying event is held constant, does changing only the country responsible change how evasively language models describe the event?

A second question is measurement-related:

**How much does the nationality of the judging panel affect conclusions about model bias?**

## Identification logic

The country-swap comparison holds the documented event constant while changing the attributed responsible country. If model descriptions change systematically under that swap, the difference is consistent with a country-conditioned response rather than a change in the underlying facts.

The study also compares judge panels. If model rankings change with the nationality of the jury, then the measured ranking is partly a property of the evaluation panel, not only of the model responses.

The repository includes a swap control. That control did not pass, so the results are interpreted through the matched comparison rather than as a clean success of the full swap design.

## Method

- **Corpus:** real atrocities documented by the UN, Human Rights Watch, and Amnesty International.
- **Model comparison:** six AI models received the same documented incident, with the responsible country changed for the comparison condition.
- **Outcome:** judges scored how evasive each answer was.
- **Judging panels:** five AI judges from different national backgrounds.
- **Analysis:** model responses, judge scores, and figures are retained in the repository for recomputation.

The adversary-airstrike subset contains two incidents, and the incidents are not yet matched for prominence.

## Results

### Country-conditioned response differences

For the same kind of documented event, responses were most evasive about the United States and its allies and most direct about an adversary:

| Responsible-country condition | Mean evasiveness |
| --- | ---: |
| Own side | 2.70 |
| Ally | 1.92 |
| Adversary | 0.59 |

The pattern held for mass detention but disappeared for crackdowns on protesters. The pooled comparison was **p = 0.005**.

### Judge nationality changes model rankings

The model ranking was not stable across judging panels:

- Llama ranked last under an American jury.
- Llama ranked first under a European jury.
- The two rankings were uncorrelated.
- Overall judge agreement was **Krippendorff's α = 0.74**.

This makes the evaluation panel part of the measured object: conclusions about “which model is most biased” depend on who—or what—does the scoring.

## What the evidence supports

The results support a narrow claim: in this corpus and evaluation setup, changing the responsible country was associated with different levels of evasiveness in model descriptions, and the ranking of models depended on the judging panel.

The study does not establish that any country is generally treated more favorably, that the models possess a stable political ideology, or that the observed pattern generalizes to other incidents, prompts, models, or judges.

## Limitations

- The swap test did not pass its own control.
- The adversary-airstrike sample contains only two incidents.
- Incidents are not yet matched for prominence.
- The study measures model outputs under this prompt and corpus, not political beliefs or intentions.
- AI judge nationality is an operational grouping for this evaluation; it should not be treated as a complete account of human national perspectives.
- The pooled result should not be read as proof of a universal effect.

## Repository map

- `index.html`, `assets/` — static public site.
- `corpus/scenarios.jsonl` — incidents with source URLs.
- `corpus/CORPUS-incidents-plain-english.md` — plain-English corpus list.
- `harness/` — model and judge queries.
- `analysis/` — statistical analysis and figure generation.
- `results/` — raw model answers and judge scores.
- `figures/` — charts.

## Reproduce

```bash
pip install -r requirements.txt
set OPENROUTER_API_KEY=sk-or-...
python harness/run_targets.py
python harness/run_judges.py
python harness/electorates.py
python analysis/analyze.py
python analysis/make_figures.py
```

Every number on the site can be recomputed from the raw files in this repository.

## Credit

Woodcut: Albrecht Dürer, *The Four Horsemen of the Apocalypse*, c. 1498, public domain.
