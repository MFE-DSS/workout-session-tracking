# Sprint Report — Sb_ASSET_03B.2R-C2 · Synthetic Multi-Agent Review Council

## Outcome
`COMPLETE`. A reusable Promptfoo-based harness plus a **live blinded review council** over the three
Muscle Focus P0 plates. All accepted candidates are unchanged. No runtime, no asset intake, no §5bis.
**Professional anatomical review: NOT PERFORMED / NOT CLAIMED.**

## Verdict
**COMPLETE.** The synthetic single-family multi-agent review harness is delivered (reusable, versioned)
with a live blinded council: 45/45 valid judges, calibration 9/9 critical + 12/12 overall PASS,
order-independent deterministic aggregation, 22 regression tests. This is **internal synthetic QA only**
and does **not** constitute or claim a qualified professional anatomical review. Accepted candidates are
byte-unchanged; runtime / asset intake / §5bis are not enacted. The versioned harness, spec, report and
tests are delivered to canonical via PR under `GO DELIVER — AUTONOMY_MODE: BOUNDED_DELIVERY`; **merge
remains a separate human GO.**

## Brainstorming / Options / Risks / Choice retained (CLAUDE.md §3)
- **Options for the live provider**: (A) Promptfoo → Anthropic API key; (B) Promptfoo → Claude Code
  OAuth; (C) Claude Code **subagents** as the council, Promptfoo config versioned for later reuse.
- **Environment reality**: no provider credential in env, no `claude` CLI / OAuth token, and the
  current promptfoo line requires a newer Node engine than available. So (A)/(B) cannot run here.
- **Risk**: substituting the orchestrator could look like a methodology deviation. **Mitigation**:
  keep the Promptfoo harness fully versioned + structurally validated (reproducible once a credential
  exists), and run the live council via independent, blinded **Claude Code subagents** — the same
  mandated Claude-vision baseline — with full disclosure.
- **Choice retained**: (C). Because only the Claude family is available, the live run is a
  **SYNTHETIC SINGLE-FAMILY MULTI-AGENT REVIEW** (not "multimodel").

## Run
- **Framework**: Promptfoo 0.120.27 (MIT), pinned in an isolated external env (`08_synthetic_review/tooling`).
- **Provider mode**: `SINGLE_FAMILY_MULTI_AGENT` (Claude only).
- **Council**: 5 blinded judges (J1 anatomy, J2 illustration/product, J3 fitness-semantics,
  J4 adversarial-falsifier, J5 provenance/governance) + 1 arbiter/region.
- **Volume**: 3 regions × 5 roles × 3 runs = **45/45 valid** judge outputs; **24** calibration outputs;
  **3** arbiters. 72 subagents, 0 errors, 0 empty. ~4.26M subagent tokens.

## Calibration (blind mutation detection)
12 evaluation-only mutations (accepted candidates never touched). Council detected **critical 9/9
(100%)** and **overall 12/12 (100%)** — thresholds (100% critical, ≥90% overall, every
mirror/provenance/false-claim) met. Thresholds were fixed before seeing candidate results and not lowered.

## Regional results (deterministic aggregation)
| Region | Score | Consensus | Status | Major | Vetoes |
|---|---|---|---|---|---|
| chest | 87.6 | HIGH | SYNTHETIC_ACCEPTED_WITH_CONSTRAINTS | 2 | 0 |
| shoulders | 87.6 | HIGH | SYNTHETIC_ACCEPTED_INTERNAL | 0 | 0 |
| posterior | 85.2 | HIGH | SYNTHETIC_ACCEPTED_WITH_CONSTRAINTS | 1 | 0 |

No arbiter lowered a status; none requested Martin adjudication. **Constraints (the MAJOR findings):**
- **Chest**: (J2) medial sternal contour feathering reads as render/segmentation noise → smooth the
  medial border for edge legibility; (J2) unresolved edge overlap / z-layering at the sternal origin
  and humeral insertion interfaces. The clavicular/sternocostal diagnostic partition stays
  `REVIEW_PARTITION_UNRESOLVED / NOT ACCEPTED` (scored separately; never internally accepted this sprint).
- **Posterior**: (J1) distal hamstring tendon behaviour near the knee (medial/lateral divergence)
  should be tightened; grouped-honest presentation and individual provenance held.
- **Shoulders**: clean — source-segmented deltoid mapping exact, front/back shared scale, no major finding.

## Global synthetic recommendation
`SYNTHETIC_ACCEPTED_WITH_CONSTRAINTS` (internal) — no vetoes, no BLOCKED region, calibration PASS,
HIGH consensus everywhere; two regions carry explicit, testable constraints. **Pending Martin's decision**
(`08_synthetic_review/results/martin_decision_form.md`, no option preselected).

## Governance (unchanged by this sprint)
Synthetic multimodel internal review is reusable internal QA; it does **not** equal, and does **not**
claim, a qualified professional anatomical review. Martin may accept the residual risk for non-medical
internal/product use. Professional anatomical/legal accuracy remains unclaimed. The C1 external review
package is retained (`e1dc96e3…`, verified unchanged); its dispatch is **deferred by owner**, not passed.
A future professional review may still supersede the synthetic verdict. **Runtime / asset intake / §5bis:
BLOCKED / NOT STARTED / NOT ENACTED.**

## Versioned deliverables (in Git, this worktree)
`tools/evals/muscle_focus/` (README, promptfooconfig.yaml, 6 prompts, 2 schemas, 4 rubrics, 9 scripts,
fixtures) · `tests/test_auren_muscle_focus_synthetic_review.py` (22 tests) ·
`docs/strategy/Sb_ASSET_03B_2R_C2_SYNTHETIC_MULTIMODEL_REVIEW_SPEC.md` · this report.
**External only** (not in Git): toolchain lock, calibration mutations, per-run raw outputs, results
(raw + aggregate + registers + findings + decision form + offline HTML report + manifest).

## Validation
Ruff PASS (all added Python) · 22 regression tests PASS · Promptfoo config + schema validation PASS ·
calibration PASS · aggregation order-independence PASS (real data) · candidate hashes UNCHANGED ·
no credential serialized · `git diff --check` clean · no candidate binaries or external package in Git.

## Next
Martin reviews the synthetic council report, then GO COMMIT and internal closeout.

## Post-resolution (Sb_OPS — GO RESOLVE PR #46, 2026-08-09)
The synthetic council **result is historical** — it fed the C3 freeze → D1 intake (PR #48) → 04.1-P0
runtime (PR #49), all merged. What PR #46 ships is the **reusable eval harness only**
(`tools/evals/muscle_focus/` + `tests/test_auren_muscle_focus_synthetic_review.py`), still useful for
future plate reviews. Repo-triage found PR #46 **stale but NOT superseded** (`tools/evals/muscle_focus/`
absent from canonical). **Verdict: SALVAGE** — the branch was rebased **additively** onto current
canonical (`6037661`) by merging canonical in; the only conflict was `SPEC_REGISTRY.md` (resolved by
keeping canonical's D1/04.1/04.2 entries + the refreshed C2 entry); the shared roadmaps were refreshed.
**No candidate SVG/PNG/OBJ, no external review outputs, no credentials, no runtime/intake/§5bis** are
introduced; the harness is self-contained (no `app` coupling). Harness tests **22 passed**. PR #46 is
driven to green; **merge remains a human GO**.
