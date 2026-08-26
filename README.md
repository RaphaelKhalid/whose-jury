# Whose Jury?

A study of political bias in language models.

Six AI models read the same documented atrocities. We changed which country was responsible, and measured how each model responded. The live site is `index.html`.

## The setup

We collected real atrocities documented by the UN, Human Rights Watch and Amnesty International. Nothing was invented. For each one, six models were asked to describe what happened. Then the country responsible was changed and the models were asked again. The facts stayed identical. Five AI judges of different nationality scored how evasive each answer was.

## Findings

On the same act, an airstrike that killed civilians, the models were most evasive about the United States and its allies and most direct about an adversary. Own side 2.70, ally 1.92, adversary 0.59. The pattern held for mass detention. It vanished for crackdowns on protesters. Pooled p = 0.005.

The bias ranking of the models depends on the nationality of the judges used to score them. Llama ranks last under an American jury and first under a European one. The two rankings are uncorrelated.

Judge agreement was high, at 0.74 Krippendorff alpha.

## Honest limits

The swap test did not pass its own control, so the results rely on the matched comparison instead. The adversary airstrike sample is small, at two incidents. The incidents are not yet matched for prominence. This is not a judgment about any country. It measures the models, on facts held constant.

## What is here

- `index.html` plus `assets/` is the site. It is static and deploys to Vercel as is.
- `corpus/scenarios.jsonl` is every incident, each with a source URL.
- `corpus/CORPUS-incidents-plain-english.md` is the same list in plain English.
- `harness/` queried the models and the judges.
- `analysis/` ran the statistics and drew the figures.
- `results/` holds the raw model answers and the raw judge scores.
- `figures/` holds the charts.

## Reproduce

```
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

Woodcut: Albrecht Dürer, The Four Horsemen of the Apocalypse, c. 1498, public domain.
