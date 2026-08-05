# Sprint Report — Sb_ASSET_03B.2R-D1 · P0 Muscle Focus Plate Intake + §5bis Enactment

## Outcome
`COMPLETE (design-source intake)`. The three frozen P0 regional plate candidates are intaken **byte-exact**
into `design/auren/source/muscle-focus/`, §5bis is enacted atomically with a co-written guard, and the
descriptor registry / manifest / provenance / attribution / preview are added. **NOT AUTHORIZED FOR APP
INTEGRATION**; no app runtime; **professional anatomical review NOT PERFORMED / NOT CLAIMED**.

## Brainstorming / Options / Risks / Choice (CLAUDE.md §3)
- **Discovery**: the frozen candidates are the C3-freeze authority (owner ACCEPT_WITH_CONSTRAINTS) but the
  intake hit two locked-contract frictions — (1) the candidate path-id scheme (`--context-NNN` / `--hero-NNN`
  / `--front-delt-anterior-NNN`) differs from the ID Contract `geom-*` authoring grammar; (2) the descriptor
  `mode` enum (`muscle-heads | grouped-honest`) has no honest value for chest (whole pectoralis, partition
  excluded).
- **Options**: (A) governed additive contract evolution; (B) intake with a non-conformance note only;
  (C) stop and defer to a contract-reconciliation GO.
- **Risk**: bending a locked, versioned contract silently inside an intake commit would violate governance
  (contracts change only by a commit modifying them, never by prompt).
- **Choice (owner-directed)**: **(A) governed additive evolution.** ID Contract → **v0.2.0** (§3bis: the P0
  pipeline id-scheme is an accepted bounded variant that satisfies every hard anti-collision rule; `geom-*`
  stays the authoring target). Descriptor Schema → **v0.2.0** (adds mode `whole-region` for N2 whole-muscle
  plates; clarifies N2 mode usage). Additive: no field removed, no invariant weakened. **No geometry rewrite.**

## Intake (design/auren/)
- 3 SVGs byte-exact: chest `7a4167ea…` (whole pec, partition EXCLUDED) · shoulders `5eb7bedf…`
  (source-segmented deltoid, front+back) · posterior `b84c8bce…` (grouped-honest hamstring). All == C3 freeze.
- `source/muscle-focus/auren_muscle_focus_registry.yaml` — 3 descriptors (schema v0.2.0), owner constraints
  (C1–C5 / S1–S5 / P1–P5), freeze + owner-decision authority, `ai_usage: NONE`.
- Manifest §5ter + provenance entry (BodyParts3D CC BY 4.0, attribution required, status
  `technical-intake-accepted-human-review-pending`, 0 `approved`).
- Attribution: existing `LICENSES/CC-BY-4.0.txt` + `LICENSES/bodyparts3d-NOTICE.md` (no LICENSES change).
- Offline preview `previews/muscle-focus/auren-muscle-focus-plates-v0.2.0.html` (silhouette + metadata).

## §5bis enactment (atomic with guard)
`AUREN_STYLE_RULES.md §5bis` enacted (exact clause from the governance amendment): fibre direction /
origin-insertion markers / functional-shortening / schematic `section` — **bounded to `auren-plate-*`
surfaces only**; measured activation / EMG / viscera stay forbidden; **§5 (master silhouette) unchanged**;
caption in adjacent HTML. The first P0 geometry is **clean** (no fibre/insertion/section overlay produced).

## Guards (co-written)
- New `tests/test_auren_muscle_focus_plates.py` — freeze-sha byte-integrity, root ∈ P0 roots, no `zone-*`/
  master id, prefix isolation, no forbidden attr/business-hex, **no text inside the plate SVG**, descriptor
  invariants (non_medical/scored/caption literals, parts ⊆ registry, mode/zone/exercise-granularity), chest
  partition excluded, posterior individual provenance, §5bis bounded scope, gate BLOCKED, no lying/measurement token.
- Extended `tests/test_auren_asset_governance.py` allowlist (SVG + structured) — governed evolution.

## Validation
44 plate+governance guard tests PASS · (see CI for full suite + Sonar). check_scope + ruff + gitleaks below.

## Governance (unchanged)
`ASSET INTEGRATION GATE: BLOCKED` · professional anatomical / legal / medical: NOT CLAIMED · owner decision
is an internal product-risk acceptance (synthetic QA), NOT a professional review · no app runtime · candidates
byte-unchanged. Chest partition never accepted; forbidden at runtime.

## Verdict
**COMPLETE (design-source intake).** Three frozen P0 plates intaken byte-exact, §5bis enacted atomically with
a co-written guard, contracts additively evolved to v0.2.0 (owner-directed) with no geometry rewrite and no
weakened invariant. Internal synthetic review only — **NOT a qualified professional anatomical review**;
`ASSET INTEGRATION GATE: BLOCKED`; no app runtime; no legal/medical claim. Delivered via PR under
`GO DELIVER — AUTONOMY_MODE: BOUNDED_DELIVERY`; **merge remains a separate human GO.**
