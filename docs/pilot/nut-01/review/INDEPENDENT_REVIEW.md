# NUT-01 whole integration review — 2026-11-15

## Review boundary and evidence

Read-only review of actual files in `/Users/martinfeldmann/auren-review/nut-01-recovered-20261112`, against canonical BODY + closeout `5b19dc77071a0bcab3d8048ed7a61e2e0b0e3084`. Git HEAD remains `ddcdd4b15c3639ba2b40c29eb5d615814e0cbc0c`; ordinary HEAD/base diff is not the source authority for untracked copied parent files. All 70 files in `NUT_REVIEW_MANIFEST.json` still match their frozen SHA256 values at review completion.

Reviewed canonical CLAUDE/standing merge authority, NUT design/persistence/wire/execution scope/implementation plan/ledger and functional/visual decision boundaries; actual server models, commands, consent, identity/schema probes, reads/API, migration and startup integration; native commands/DTO/client/resources, journal attachment/durability/recovery, ConnectedApp/Progress entry and workspace/surface; supporting domain/API/SQLite/client/controller/consumer tests.

`python3 scripts/check_scope.py` reports MIGRATION. No broad/full sweep was launched by this reviewer. Parent-reported mobile 1276 + TypeScript and migration checks are not recharacterized as final verification; backend sweep/CI/final HEAD and native pixel gates remain pending. Three controller defects below were additionally reproduced by importing the actual TypeScript through an in-memory Node transpilation loader, with synthetic client outcomes. This created no source, index, HEAD or worktree changes.

## Strengths

- Integer milli transport and decimal parsing preserve zero, null and absence; there is no 4/4/9 inference. Closed commands and Python/TS vectors make byte identity auditable.
- SQLite owner guard refreshes auth/device proof under its write reservation; current consent is reloaded before a fresh effect. Exact receipt lookup precedes fresh consent/CAS. Revisions and receipt commit together.
- Target selection resolves latest effective key and its latest revision under the same guard, rejects replaced/disabled references, and does not overwrite historical day references.
- Read snapshots capture both append-only watermarks; signed cursors bind owner/backend/schema/epoch/window. Client traversal rejects changed snapshots, duplicates and cursor loops and keeps interrupted traversal partial.
- Same owned journal/serial connection receives NUT commands, with explicit owner/backend/namespace partitioning, durable bytes before HTTP, atomic initial-send reservation and ACK before refresh. No automatic POST retry was introduced.
- Additive NUT migration follows actual BODY parent; startup exclusions retain PLAN/BODY/NUT. Empty-only downgrade refuses populated nutrition history. Existing BODY source files were preserved by the integration manifest approach.

## Issues

### Critical

None found.

### Important

1. **Authorization-boundary results from secondary reads leave personal facts visible and editable.**
   - `clients/mobile/src/ui/nutrition/NutritionWorkspace.ts:92` assigns `history()` results directly, bypassing `boundary()`. The same omission exists for target-head loading at line 61 and bound-target revision loading at lines 49–50.
   - Reproduction: load a confirmed day, have the versions request return `consent_required`, then call `history('DAY', day)`. State remains `status:'confirmed'`, the head and `consent.granted:true` remain, and `editDay()` returns true. The versions panel merely says “Versions à vérifier”. `changed` has the same omission; a detected account mismatch must not retain the prior account's facts.
   - Apply the common permission/identity boundary handling to every client/resource result before using it. Clear numeric facts, targets, editor and permission state on these outcomes; prevent an older in-flight request from repopulating them.
   - Add controller and rendered-surface witnesses for consent withdrawal/account mismatch during versions, target editing and bound-target reads, including a competing late response. Server write guards remain intact; this is a client disclosure/stale-authorization defect.

2. **Changing day can display another day's previous values under the selected date.**
   - `NutritionWorkspace.ts:53` changes `state.day` and clears `previousHead`, but retains `state.head`. `refresh()` at line 36 captures that old head as `prior`, and line 43 restores it after an unknown read.
   - Reproduced: confirmed 2026-11-12 → select 2026-11-11 → new head returns unknown. The selected date is 2026-11-11 while `previousHead.key.local_day` is 2026-11-12. `NutritionSurface.tsx:64` shows those previous numbers without their original date.
   - Only retain a fallback whose natural key matches the requested day; clear the old head before changing the logical day. Test failed A→B reads and overlapping A→B→C responses, as well as legitimate same-day offline fallback.

3. **Definitive fresh refusal discards the draft and is presented as an uncertain result with no recovery action.**
   - `NutritionWorkspace.ts:74–78` clears the editor for every non-boundary outcome. `rejected` is reduced to “Enregistrement à vérifier”; neither its code nor the rejected input is surfaced. The durable store has already made a fresh refusal terminal, so `pending()` omits it.
   - Reproduced `stale_head`: after saving 1500, `editor:null`, `pending:[]`, notice “Enregistrement à vérifier”. This loses the user's correction, gives no conflict explanation, and leaves the stale head available for another unsuccessful attempt. Invalid last-field clearing/no-op and stale-target selection have the same misleading presentation.
   - Treat a definitive fresh rejection separately from SENT_UNKNOWN: preserve or visibly retain the refused draft, explain the relevant refusal, and require an explicit refresh/review against the current head before a newly prepared command. Keep exact unknown-command recovery unchanged.
   - Test stale-head/stale-target/invalid-command refusal separately from timeout, local failure, confirmed receipt with failed readback, and consent refusal.

4. **Known zero targets disappear from the comparison, and the promised arithmetic difference is absent.**
   - `NutritionSurface.tsx:67–68` renders the entire comparison only when `target > 0`. A valid exact historical target of zero therefore shows no target value or comparison even when intake is known. Nonzero targets show only a ratio, not the field/day difference described in design N03/persistence.
   - Render the exact bound target and arithmetic difference whenever both values are known, including zero; suppress only division by zero. Preserve unknowns and the exact target reference/source. This is functional numeric behavior, not an artistic judgment.
   - Add rendered witnesses for intake 0 / target 0, nonzero intake / target 0, either value null, and an old target reference after correction/disable.

5. **The historical synthesis is narrower than the approved functional contract, with no recorded scope amendment.**
   - `NutritionSurface.tsx:74–75` renders totals/known-day counts and existing day rows only. It does not present absent/partial/complete coverage counts, nor the factual point history/graph and text alternative required by `design.md:60` and the accepted G1 UX board. Absent dates do not appear in its list.
   - Complete the agreed history/coverage behavior using the accepted composition, or explicitly obtain/record an applicable scope ruling before claiming NUT complete. DA07/DA08 acceptance alone does not document removal of these functional requirements.
   - Add a mixed 7/30-day surface witness (known zero, unknown field, absent, partial, complete, withdrawn, corrected head) and verify counts, factual points/text and lack of double counting. Do not silently amend the spec or invent an unapproved visual variant.

### Minor

1. **Read-only permission also disables day audit access.** `NutritionSurface.tsx:76` uses `locked`, which includes `!can_write`, for “Versions de ce jour”. With valid consent/can_read but acquisition flag off, current values are readable while their versions cannot be opened. Gate read actions by read authority, not fresh-write authority; test a read-only capability response. Historical targets also have no direct “versions” action from the bound historical reference when it has disappeared from `available` after disable/replacement (lines 70–73).

2. **Audit rows omit the operation's observable state.** `NutritionSurface.tsx:78` shows values/source/time/reference but neither DAY ACTIVE/WITHDRAWN and declared completeness nor TARGET enabled/disabled. Explicit withdrawal, completeness-only revisions and disabling are difficult to distinguish in their own audit. Show these factual states and test two revisions whose values are identical but completeness differs.

## Additional test limits

- Existing NUT SQLite concurrency tests cover duplicate absent-head creation, cached-consent revocation and epoch change; the public guard's device revocation path is visibly reused. A NUT HTTP/device-revocation-between-auth-and-write witness would make the plan's device clause explicit.
- `tests/test_nutrition_migration.py:11` preserves a populated BODY original plus sidecar, but does not seed BODY correction and erasure lineages before NUT upgrade. DDL inspection found no NUT operation touching BODY; extending that existing witness would substantiate the explicitly requested full lineage preservation.
- Native surface tests are synthetic renderer tests, and ConnectedApp tests use real local SQLite with a synthetic RPC boundary. They are not physical/native visual acceptance or proof that the composed UI has traversed real HTTP on both platforms.

## Declined to judge

- Artistic acceptability of final native NUT pixels: reserved to the operator's distinct pending pixel gate; master/family acceptance is not transferable final acceptance.
- Physical device behavior/accessibility and Android/iOS rendered acceptance: no physical/rendered proof was supplied for this exact composition; required evidence remains pending, not waived.
- Media/assisted capture, recommendation/scientific targets, real personal data activation, provider integrations, EAS/APK/OTA/deployment and global DATA erasure certification: explicitly outside this authorized synthetic manual-ledger scope.

No other considered behavior was set aside as outside scope.

## Assessment

**Ready to merge: No — functional fixes and applicable validation gates remain.**

The domain, persistence and recovery foundations are coherent, but the native consumer has reproducible stale-data/permission/refusal defects plus unfulfilled functional presentation requirements. Fix these with bounded regression witnesses, then finish the already required final verification/real CI and explicit native pixel decision. This review does not certify final green, physical acceptance or release readiness.
