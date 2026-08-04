# Auren Muscle Focus — Synthetic Multimodel Review Harness

Reusable, open-source-tool-based (**Promptfoo, MIT**) harness that runs a **blinded multi-agent
review council** over the Muscle Focus P0 regional plates (chest, shoulders, posterior) and produces
**deterministic aggregate scores, objections, confidence, and vetoes** plus an internal synthetic
verdict per plate.

> **This is internal QA, not a qualified professional anatomical review.** It does **not** claim
> `QUALIFIED_PROFESSIONAL_ANATOMICAL_REVIEW`. It is `SYNTHETIC_MULTIMODEL_INTERNAL_REVIEW`. A future
> professional review may still supersede it. No runtime, no asset intake, no §5bis is authorized here.

## Not in Git
Candidate SVGs, PNG previews/diagnostics, OBJ files, credentials, mutated calibration copies, and all
model outputs/reports live **only** in the external operator workspace. This directory is versioned;
it hardcodes **no** absolute path and reads the external root from:

```
AUREN_MUSCLE_FOCUS_REVIEW_ROOT   # e.g. the auren-operator-...-p0-regional workspace root
```

## Council (5 blinded judges + arbiter)
- **J1** anatomy consistency · **J2** medical illustration & product · **J3** fitness semantics ·
  **J4** adversarial falsifier · **J5** provenance & governance · **arbiter** (post-hoc, may only lower).
Judges return **schema-valid JSON only** (`schemas/agent_review.schema.json`); no free-form answer.

## Providers
Mandatory baseline: **Anthropic Claude vision via Claude Code auth** (`apiKeyRequired: false`; no
credential is written to any file). Optional OpenAI / Gemini vision are used **only** when a valid
credential already exists. Run mode is `MULTI_FAMILY` (≥2 families) or `SINGLE_FAMILY_MULTI_AGENT`.

## Layout
- `promptfooconfig.yaml` — reproducible Promptfoo run definition.
- `prompts/` — one blinded prompt per judge + the arbiter.
- `schemas/` — agent + aggregate JSON schemas.
- `rubrics/` — `common.yaml` (weights/thresholds/veto/status policy) + per-region constraints.
- `scripts/` — `build_cases.py`, `validate_agent_output.py`, `aggregate_reviews.py` (pure/deterministic),
  `build_calibration_mutations.py`, `render_report.py`.
- `fixtures/` — frozen synthetic judge outputs for the deterministic aggregation tests (no real model data).

## Run (once a provider credential + supported Node exist)
```
export AUREN_MUSCLE_FOCUS_REVIEW_ROOT=/path/to/operator/workspace
python scripts/build_cases.py
python scripts/build_calibration_mutations.py
promptfoo eval -c promptfooconfig.yaml      # writes raw judge outputs
python scripts/aggregate_reviews.py --reviews <raw> [--arbiter <arb>]
python scripts/render_report.py
```

## Aggregation (deterministic)
`aggregate_reviews.py` is pure and order-independent: per-criterion normalized median/min/max/stddev,
role/family medians, a weighted regional score (weights total 100), consensus (HIGH/MEDIUM/LOW), veto
confirmation (≥2 roles ≥0.80, or arbiter with cited evidence), and status. **The arbiter can never
raise a score.** Regression tests in `tests/test_auren_muscle_focus_synthetic_review.py`.
