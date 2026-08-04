# Sb_ASSET_03B.2R-C2 — Synthetic Multimodel Review Spec

## Purpose
A reusable, open-source-tool-based (**Promptfoo, MIT**) harness that runs a **blinded multi-agent
review council** over the Muscle Focus P0 regional plates (chest, shoulders, posterior) and produces
**deterministic** aggregate scores, objections, confidence and vetoes, plus an internal synthetic
verdict per plate. It replaces the *attempted external human-reviewer dispatch* with
`SYNTHETIC_MULTIMODEL_INTERNAL_REVIEW`.

## Governance distinction (non-negotiable)
- Synthetic multimodel internal review is **reusable internal QA**.
- It does **not** equal, and does **not** claim, a `QUALIFIED_PROFESSIONAL_ANATOMICAL_REVIEW`.
- Martin may accept the residual risk for **non-medical internal/product use**.
- **Professional anatomical / legal accuracy remains unclaimed.**
- The external review package (C1) is **retained**; its dispatch is **deferred by owner**, not passed.
- A future professional review may still **supersede** the synthetic verdict.
- This sprint authorizes **no runtime, no asset intake, no §5bis, no automatic global acceptance**.

## Council (5 blinded judges + arbiter)
J1 anatomy-consistency · J2 medical-illustration & product · J3 fitness-semantics ·
J4 adversarial-falsifier · J5 provenance & governance · arbiter (post-hoc; may only LOWER, never raise).
Judges are blind to each other, to aggregates, to Martin's product decision, and to any desired
outcome. They receive region constraints but **no suggested verdict**, and must return schema-valid
JSON only (`schemas/agent_review.schema.json`).

## Providers & run mode
Mandatory baseline: **Anthropic Claude vision via Claude Code auth** (`apiKeyRequired: false`; no
credential written to any file). Optional OpenAI / Gemini vision are used only if a valid credential
already exists. Run mode: `MULTI_FAMILY` (≥2 families) or `SINGLE_FAMILY_MULTI_AGENT`. In the C2 build
environment no promptfoo-usable vision-provider credential existed and the installed promptfoo line
required a newer Node engine than available, so the live council was executed via **independent,
blinded Claude Code subagents** (the mandated Claude-vision baseline); the versioned `promptfooconfig.yaml`
reproduces the identical council once a credential + supported Node runtime exist.

## Scoring (0-5 per criterion, ten criteria)
orientation_and_laterality, source_structure_completeness, anatomical_visual_consistency,
context_relationships, occlusion_integrity, silhouette_readability, mobile_readability,
product_semantic_clarity, provenance_honesty, scope_and_claim_discipline.

## Deterministic aggregation (`scripts/aggregate_reviews.py`, pure)
Normalize x*20 → 0-100; per criterion median/min/max/stddev + role & family medians; weighted regional
score (weights total 100, in `rubrics/common.yaml`); consensus HIGH/MEDIUM/LOW from composite stddev
(≤7 / ≤12) and verdict spread; **veto confirmation** = ≥2 independent roles at confidence ≥0.80, OR one
judge + arbiter with cited evidence. Status: `SYNTHETIC_ACCEPTED_INTERNAL` (≥85, HIGH/MEDIUM, no veto,
no unresolved major), `SYNTHETIC_ACCEPTED_WITH_CONSTRAINTS` (≥75, no veto), `REVISION_REQUIRED`, or
`BLOCKED` (any confirmed veto / calibration failure / evidence-integrity failure). **The arbiter can
never raise a score or status.**

## Region rules
- **Chest**: product candidate = whole bilateral pectoralis; the clavicular/sternocostal partition is
  **diagnostic only** (`REVIEW_PARTITION_UNRESOLVED`, NOT accepted for product use, Plan-B open/deferred)
  and is scored separately — it can never receive internal product acceptance in this sprint.
- **Shoulders**: source-segmented deltoid mapping must stay exact; front + back master views retained;
  runtime one-view-at-a-time is a future constraint only.
- **Posterior**: grouped-honest presentation permitted; individual hamstring provenance mandatory; bone
  context secondary.

## Calibration (`scripts/build_calibration_mutations.py`, 12 cases, external)
Evaluation-only mutated copies (never the accepted candidates). The council must detect 100% of CRITICAL
mutations and ≥90% overall, and every mirror/laterality, source-provenance, and false professional/runtime
claim. Prompt refinement may use calibration cases only — never the real candidate verdicts.

## Outputs (external only, not in Git)
`08_synthetic_review/` — toolchain lock, calibration, per-run raw outputs, results (raw + aggregate +
registers + findings + Martin decision form + offline HTML report + manifest). Candidate SVGs/PNGs/OBJ,
credentials, mutated copies and model outputs are **never** committed.

## Regression tests (`tests/test_auren_muscle_focus_synthetic_review.py`)
Roles present; schema rejects missing evidence / out-of-range scores / unknown verdicts; weights total
100; aggregation order-independent; calibration thresholds enforced; confirmed veto blocks; single judge
cannot silently confirm a veto; arbiter cannot raise score/status; chest partition cannot become accepted;
professional review cannot be marked completed; runtime blocked; no candidate binaries or external package
in Git; no credential serialized.
