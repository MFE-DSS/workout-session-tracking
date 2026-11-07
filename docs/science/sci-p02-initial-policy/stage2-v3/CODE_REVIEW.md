# Fresh whole-branch code review — SCI-P02 stage2

Reviewed read-only: `/private/tmp/auren-sci-p02-stage2-admission-v3`, base `97173680c1474bb906d413c192e6c120b97bfe5d`, HEAD `f17ce20`. Reviewer: `/root/stage2_whole_branch_code_review`. No subagents, checkout edits, commits, or branch mutations. External temporary probe files only.

## Strengths

- New modules isolate admission from historical empty authority and runtime. Existing schemas, APIs, SDKs, DB and historical modules are unchanged in this branch.
- The emitted plan is deterministic, fixed to the seven reviewed selections, with explicit observed prescriptions, qualitative unknowns, and a 750-second rest floor that never becomes a duration guarantee.
- Typed inputs are revalidated through strict serialization, authority content is recomputed, and real positive fixtures distinguish synthetic facts from admission authority.
- Ack fingerprints separate facts, observations, plan/time and policy. The new tests exercise actual admitted authority rather than fabricated test admission.

## Issues

### Critical

None found. This remains isolated NOT_SERVED code; the following are important correctness/publication defects, not claims of an active production security incident.

### Important

#### I1 — Recording order can certify an explicitly contradictory actual execution chronology

Locations: `tools/science_initial_policy/v3_producer.py:87` (especially 93–102), `tools/science_initial_policy/v3_validation.py:19` (especially 25–35).

Both new phase guards use `sequence` only. The inherited episode validator checks chronological `recorded_at`, but permits an event recorded later to have happened earlier. Therefore the trial can explicitly have happened before context confirmation and familiarization while both producer and validator certify it. This is a distinct untested input variation of the chronological precondition, not a re-audit of the scientific dose or policy.

Reproduced from `tests.test_science_initial_policy_v3.request(r)`:

```python
for event in raw['episodes'][0]['events'][:2]:
    event['provenance']['measured_at'] = event['provenance']['recorded_at']
raw['episodes'][0]['events'][2]['provenance']['measured_at'] = '2026-11-07T11:00:01Z'
out = produce_v3(raw, r)
validate_admitted_exchange_v3(raw, out, r)
```

Actual source times now say context happened at 11:01, familiarization at 11:02, trial at 11:00:01 (recorded at 11:03); result is still `SCIENTIFICALLY_READY`. With a newly generated exact ack, the same qualification can convey start eligibility. `PROTOCOL.md` requires preparation before the trial, and the SCI I1 closure expressly requires those facts to already apply to it.

Fix within the new profile: validate applicable event occurrence chronology as well as ledger ordering, considering explicit measured times and the meaning of direct declarations. Do this independently in the validator, retain legitimate delayed recordings, and preserve legacy helpers. Add a regression with explicitly contradictory measured times; existing sequence-only regressions are insufficient.

#### I2 — Publication source closure omits executed qualification and validation dependencies

Locations: `docs/science/sci-p02-initial-policy/stage2-v3/authority/sources.v1.json:36`, `tools/science_initial_policy/v3_admission.py:113`, `tools/science_initial_policy/v3_fixtures.py:72`.

The new manifest pins the top-level v3 producer/validator but omits runtime-imported helpers including `admission_calibration.py`, `load_calibration.py`, `calibration_time_contracts.py`, `blueprint_first_plan_v2.py`, `first_plan_v2_validation.py`, and `v2_registry.py`. The historical v2 policy's SOURCE_PINS predates these helpers and does not close this gap. The v3 contract source manifest contains such pins but is neither loaded nor pinned/validated by this admission loader. The final artifact manifest is built from the same incomplete source list, so it does not close the gap either.

Reproduced without changing the checkout: trace and copy the 58 files actually read by `load_v3_registry(root)` into a temporary root, then write arbitrary replacement content at `tools/science_initial_policy/admission_calibration.py` in that root. `load_v3_registry(temp_root).admitted` still returns `True`. Indeed those omitted helpers need not exist in the supplied source root at all. A subsequent change to their effective qualification/validation behavior can retain the exact same admitted bundle identity.

Fix: explicitly close the executed scientific/helper dependency set in the successor's manifest (or verify an exact separately pinned closure). Include drift/missing-file probes for effective imported helpers. Do not rewrite historical pins. Preserve the deliberate loader/self-hash exception and pin it separately as designed.

#### I3 — Independent positive validation does not establish sufficient nonconflicting inputs

Locations: `tools/science_initial_policy/v3_validation.py:89` (95–101), `tools/science_initial_policy/v3_validation.py:182`.

The positive invariants inspect values but never independently recompute `assess_inputs` or enforce KNOWN empty limitations / conflict-free consumed exclusions. `limitations.value=None` is falsey, and `_slot` only inspects exclusion `.value`, which is also `None` for CONFLICT. The output schema trusts the response's declared sufficient assessment. Thus this mandatory independent guard depends entirely on replaying the potentially faulty producer for these cases.

Reproduced both directly and through the public validator:

1. Produce a good baseline output.
2. Change `excluded_exercise_ids` to CONFLICT with alternatives `[]` and `['leg-extensions-assises']`, distinct sources.
3. Recompute the response's three input fingerprints from that altered request, leaving the false positive assessment/plan intact.
4. Simulate the producer fault with `patch('tools.science_initial_policy.v3_producer.produce_v3', return_value=forged)`.
5. `validate_admitted_exchange_v3(raw, forged, r)` returns `SCIENTIFICALLY_READY`.

Also, `_positive_invariants(validated_request(raw), good_output, r)` succeeds when the required `limitations` fact becomes UNKNOWN/None. The ordinary current producer correctly refuses these inputs; this finding concerns the explicitly required independence against producer errors, not a claim that it currently generates that false positive unprompted.

Fix: independently derive the consumed field set and assessment from the request before inspecting a positive output; enforce exact agreement with `out.assessment`/`used_fields` and reject missing/conflicting required or consumed inputs. Add fault-injection tests that reach the public validator with an identically wrong replay, rather than relying only on output-vs-producer differences.

#### I4 — A valid incomplete context causes TypeError instead of the intended blocked result

Location: `tools/science_initial_policy/v3_producer.py:125` (similar unguarded comparison at `v3_validation.py:73`).

`Provenance.recorded_at` is nullable. A request with a current episode and `context_provenance.recorded_at=None` passes the request schema, but `_prescription` compares `None < ep.started_at` before the existing calibration helper can report `CONTEXT_NOT_CONFIRMED`.

Reproduction:

```python
raw = request(r)
raw['episodes'][0]['context_provenance']['recorded_at'] = None
produce_v3(raw, r)
```

Actual: `TypeError: '<' not supported between instances of 'NoneType' and 'datetime.datetime'`. Expected: the valid incomplete fact gives a negative/review result and `DENIED`, or an intentional documented boundary validation error, not an accidental comparison failure. Missing evidence is a normal supported input category in this isolated interface.

Fix: check presence before comparison in the new producer and applicable invariant, returning the existing context blocker; regression for nullable context provenance. No legacy model repair is necessary.

#### I5 — An unavailable confirmation in a different environment blocks a fully qualified current context

Location: `tools/science_initial_policy/v3_producer.py:133`.

The confirmations list filters only `canonical_exercise_id`. It ignores each confirmation's `context_ref`, although confirmations explicitly carry that field and the reused `_candidate` validator correctly filters both. Consequently an unavailable device at another gym is reported as contradictory current availability despite seven current observed qualified prescriptions.

Reproduction: add this confirmation to the baseline request:

```python
raw['blueprint']['environment']['exercise_confirmations'] = [dict(
    canonical_exercise_id=raw['episodes'][0]['context']['canonical_exercise_id'],
    context_ref='other-gym',
    state='UNAVAILABLE',
    provenance=raw['episodes'][0]['context_provenance'],
)]
```

`produce_v3` changes from `SCIENTIFICALLY_READY` to `REVIEW_REQUIRED` with a claimed current-context availability conflict. This is a false conflict between different contexts, not evidence that the selected observed execution is unavailable.

Fix: restrict consumed availability contradictions to the selected/current context, matching the existing validator's semantics. Preserve blocking behavior for genuine unavailable confirmations in that context and test both cases.

### Minor

None separately raised.

## Validation performed

- Read plan, design, BUILD_AUTHORIZATION, authority documents, ledger rulings, all four new modules, the three test files, and relevant inherited schema/calibration/validation/registry dependencies. Reviewed branch file statistics and source/manifest closure; generated fixtures verified through their real generator/test rather than rereading repetitive JSON rows.
- Executed `python scripts/check_scope.py` before probes/tests: ISOLATED, clean checkout; full local sweep forbidden/not run.
- `PYTHONDONTWRITEBYTECODE=1 .../python -m pytest -q -p no:cacheprovider tests/test_science_initial_policy_v3.py tests/test_science_initial_policy_v3_admission.py tests/test_science_initial_policy_v3_positive.py`: **62 passed**, two existing dependency deprecation warnings.
- Adverse targeted probes above reproduced I1–I5. `git status --short` remained empty.
- No CI or merge-readiness claim is made by this review.

## Declined to judge

- Scientific defensibility of dose, selection, C6 exploratory admission and clinical/optimality claims: delegated fresh SCI review is the authority; this pass checks implementation consistency and concrete data behavior only.
- API/UI/SDK/owned-session activation, authentication, current network revocation, and clinical screening: explicitly excluded from this isolated NOT_SERVED build; local publication cannot establish those properties.
- TTL/age expiration of otherwise current episodes: no arbitrary expiry is admitted; only explicit contradictory/currentness facts were assessed.
- Generic repair of historical validators/helpers: historical replay must remain unchanged; findings target new wrappers/invariants/manifest closure.
- Unused optional anthropometric conflicts, unrelated observations, and alternative exercise ranking: the approved producer does not consume those to establish this fixed limited plan, and no scientific interpretation of free text is authorized.
- Historical active OpenSpec paths already present in immutable v2 source inventories: not treated as permission to rewrite historical pins; the successor should preserve current behavior while avoiding newly introduced unstable dependencies.

## Recommendations and assessment

Address I1–I5 within the new modules and successor authority artifacts, with targeted RED→GREEN regressions. Repin/reproduce the successor authority and fixtures after fixes; preserve historical bytes. Record the executor's explicit ruling on the declined judgments.

**Ready to merge: No — with fixes.** The primary happy path and 62 targeted tests pass, but actual source chronology and independent input validation can incorrectly support a positive, source pins are not closed over effective helpers, and two ordinary input variations are mishandled. These are concrete gaps in the approved guarantees rather than requests to widen the scientific or runtime scope.

## Résolution auteur — après revue, avant merge

Les cinq Important ont été reproduits puis corrigés en une passe dans74d30b2.12tests RED puis15GREEN avec trois témoins ; broad551/551 repassé. I1 : occurrence explicite des phases plus ordre du ledger, enregistrements retardés légitimes conservés. I2 :55sources du graphe effectif pinées, six dérives de helpers refusées ; loader/self-cycle séparé dans manifeste. I3 : assessment/used_fields dérivés indépendamment ; public validator sous producteur fautif identique refuse missing/CONFLICT. I4 : provenance nullable retourne REVIEW_REQUIRED/DENIED. I5 : disponibilité filtrée par contexte sélectionné, autre salle sans faux conflit, même salle bloquée. Aucun helper historique modifié, aucun Critical ou mineur code différé. Le reviewer n’a pas exécuté une seconde revue ; la preuve de correction est RED→GREEN plus suite, conforme au protocole. Aucun nouvel avis scientifique ou preuve de temps/transport déduit.
