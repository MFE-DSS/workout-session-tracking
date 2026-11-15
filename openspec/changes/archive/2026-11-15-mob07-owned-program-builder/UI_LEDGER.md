# MOB07 — Native consumer ledger

Task: IMPLEMENTATION_PLAN.md Task 4. Existing worktree/branch supplied by the coordinator; no commit, push, PR, service, native build or device action by this worker.

## Brainstorming / Options / Risques / Choix retenu

The operator-approved G1 and DA08 family are the implementation boundary. A second programme editor/navigation tab or a full stacked form would obscure the ordered programme and duplicate the existing hierarchy. Choice: one local management entry in Programmes, one active session instrument, secondary ordered session/movement selectors, and per-series explicit manual acquisition. Source facts, unsent draft and durable command intentions remain separate. Risks: historical slots, discarded unsent composition after rename, receipt/current-source confusion, lost responses and late account replies. Focused tests below cover those boundaries.

## Public interfaces and rulings

- `ProgramBuilderPorts = {client: ProgramBuilderClient; store: ProgramBuilderPendingCommands; current: () => boolean; newId: () => string}`. `ProgramBuilderHost({ports,onBack})` borrows the existing owned connection and auth; it creates neither.
- `LibraryHost` accepts optional `builderPorts`; `LibraryScreen` accepts optional `onBuilder`. No callback means no entry. `library-builder` opens the local host. Returning from the management index invokes the parent callback and a library GET refresh. Editor back returns to the management index first.
- Ruling: a single entry, “Mes brouillons · Créer un programme”, keeps the current Programmes hierarchy and avoids two adjacent actions opening the same index. Creation then requires `builder-create` and an explicit title.
- Ruling: title and tree are separate frozen commands. A confirmed RENAME preserves unsent composition; a confirmed SAVE_TREE preserves an unsent title. This prevents a narrow save from discarding unrelated unsent fields.
- Ruling: confirmed receipts are historical. Only a subsequent program GET updates status/version/digest/permissions. A newer source after recovery retains the unsent draft and exposes a conflict; no automatic overwrite, new key or POST.
- Historical slots project as read-only stored facts and exact `keep {slot_id,slot_digest}`. Reordering may move them; editing a prescription requires removing that slot and explicitly choosing a new canonical movement. No identity provenance is invented.
- Bounds 1–6 sets and 1–50 reps are transport validation only. Inputs begin empty; exact integer strings are required, with no trim, numeric normalization, recommendation or inferred value.
- AppState refresh is GET-only. UNKNOWN offers GET verification first; only that unknown verification reveals explicit exact replay, enforced again by Recovery. Current-account/host guards suppress late reads and mutation results.
- Scope guard: `python` is unavailable on this shell; `python3 scripts/check_scope.py` succeeded and reported MIGRATION for the shared branch. The coordinator owns branch-wide migration/full-sweep gates and scheduling. This worker runs only narrow serial Jest and TypeScript.

## Sources and field inventory

| Visible fact/control | Runtime source | Carrier |
| --- | --- | --- |
| Owned roots/title/status | client.programs GET page | Management rows |
| Current source status/version/digest/id | client.program GET envelope | State line and optional source disclosure |
| Unsent name/session names/order/kind | in-memory BuilderDraft, initialized from GET | Title/acquisition and ordered structure |
| Canonical exercise name/slug/EKB | client.exercises GET page | Picker; selection sends exact received triple |
| Number of sets / each min/max | Explicit manual input only | One active movement acquisition |
| Historical targets/name/notes/unknown identity | GET source exercise | Active historical fact readout and optional source disclosure |
| Session focus/notes/duration | GET source session, preserved verbatim | Optional source disclosure; retained on SAVE_TREE |
| Pending operation/root/key | Existing journal ProgramBuilderPendingCommands | Verification panel |
| Command outcome | Recovery exact owner/key/hash receipt/refusal | Outcome/verification panel, followed by fresh GET |
| Publication availability | Fresh program GET status | Published read-only state; library return advice |
| Workout launch | Existing MOB06 only | No builder launch control or new launch API |

No synthetic design JSON is imported. The runtime consumer uses the concrete frozen API/DTOs and root-owned command/recovery/journal ports.

## UI iteration safeguards

### 5.6 — Approved composition

UX_BOARD.md G1: ordered programme → session structure → one active movement → manual sets/ranges → explicit save → structural validation → separate publication. Implementation uses existing `InstrumentSurface`, `EmbeddedAction`, `CalibrationLink`, `CalibrationChoices`, AurenMark and theme roles. Frame C, W1, NumericReadout, tabs and locked primitives remain untouched.

### 5.7 — One fact, one carrier

Field inventory above distinguishes draft labels from current source facts and command outcomes. No active programme, calendar, weekdays, scientific score, inferred equipment/muscle or launchability is manufactured. Structural validation explicitly does not certify scientific efficacy/safety or permit launch.

### 5.8 — Comparison with accepted source

Read references: current LibraryScreen, InstrumentSurface, EmbeddedAction, AcquisitionInstrument, calibrationControls, theme and AUREN_VISUAL_CONTRACT. The open DA08 surfaces, source disclosures, manufacturer mark, ink hierarchy and signal action role are reused. No new palette/geometry primitive/asset/baseline. Actual before/after native/SSR board and operator pixel decision belong to the coordinator and are still required before a visible-UI commit.

### 5.9 — One change per iteration

This iteration implements only approved MOB07 G1 within the current Programmes hierarchy. No additional DA exploration. KeyboardAvoidingView, scrolling, 48dp minimum controls, large-font column flow, iOS Done accessory and Android keyboard-first/back handling follow current local controls. Their source/test coverage is not a physical-device or accepted-pixel claim.

## Verification evidence

- RED: new model, controller, Screen and Host suites each failed first because their corresponding consumer implementation did not exist.
- Model GREEN: exact keep tokens for unknown/out-of-bounds history; blank/manual exact integers; real reordered wire positions.
- Controller GREEN: GET-only initial/foreground reads; explicit CREATE; canonical selection; ordered SAVE_TREE with distinct per-series bounds; VALIDATE/PUBLISH/NEW_CYCLE/ARCHIVE separation and confirmation; published read-only; unknown → GET verify → explicit exact same-key replay; refusal/conflict retained draft; current/late reply guard.
- Two focused adversarial assertions failed against the initial controller and passed after the narrow fix: RENAME must retain unsent tree/SAVE_TREE retain unsent title; historical receipt followed by newer source must retain the local draft as conflict.
- Screen GREEN: one active DA08 instrument; empty inputs; stored 75–90 historical target with unknown identity; published read-only/new-cycle confirmation; verify/replay disclosure; touch controls >=48dp.
- Host GREEN: AppState GET-only; keyboard-first Android back; explicit unsent-draft discard; optional connected library entry.
- Existing LibraryHost/LibraryScreen suites remain green.
- Final command: `npm test -- --runInBand --runTestsByPath src/ui/programs/ProgramBuilderController.test.ts src/ui/programs/ProgramBuilderHost.test.ts src/ui/programs/ProgramBuilderScreen.test.ts src/ui/programs/programBuilderModel.test.ts src/ui/library/LibraryHost.test.ts src/ui/library/LibraryScreen.test.ts` → **6 suites / 35 tests passed**.
- `npm run typecheck` → passed. No full Jest, native/SSR render, device or service process run by this worker.

## Handoff / remaining gates

Root coordinator integrates ConnectedApp real owned ports and actual consumer HTTP/SQLite proof, produces the native/SSR comparison board, obtains the applicable pixel decision, performs whole-branch independent review and branch-wide required verification. No accepted pixels, native support beyond recorded proof, physical target validation, release or deployment is claimed here.
