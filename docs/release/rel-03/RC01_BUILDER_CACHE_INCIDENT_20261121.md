# REL-03 RC01 — Builder cache-header interoperability correction

21 November 2026. Base `3bd4099941f2affe77fb9c3cfa97b1450b49ee74`.
The approved build is preserved as source3bd, never relabelled with this fix.

## Brainstorming / Options / Risques / Choix retenu

Actual EAS build `6df72a9b-09c1-4dac-8965-44bacd195db2` finished under approved
GitHub run44758281534. APK SHA256
`3c637734e5a0eccf08458882bb8d96a6aad8c30608fc1cb2a45e4ad013ab0082`.
Signature/package/runtime/source passed independent artefact review and an
in-place QA02 upgrade. Real ConnectedApp Android login and Library work.
The first Builder CREATE remains UNKNOWN in the app: the server committed
programme2 and command `ad004854-b138-4fcc-acb9-a99bd51844c1` exactly once.
Authenticated GETs independently recover that exact receipt. The actual public
response contains two identical Cache-Control no-store field lines; Fetch exposes
`no-store, no-store`. The Builder transport incorrectly requires literal equality
with a single directive. This also blocks its programme reads and reconciliation.

Choices: rewriting the already-qualified edge/collector would alter infrastructure
for a valid combined HTTP field; relaxing response-policy validation would admit
unsafe responses. Chosen minimal correction: require a nonempty comma-separated
list containing only case-insensitive no-store directives, with SP/HTAB whitespace only. Empty tokens, missing
policy, other directives, malformed syntax, contract/content-type/body/owner/digest
errors remain refusals. No request retry, command mutation or new key is added.
The existing durable command and its real server receipt are retained for the next
installed reconciliation. This is an in-scope REL03/MOB07 corrective change under
the recorded GO and GOV-MERGE-01, not a new feature or UI composition.

## Bound execution plan and leases

Own only this receipt, the active REL03 OPS03 ledger and
clients/mobile/src/api/programBuilder.ts plus its existing test. The existing
owned linked worktree is reused; unrelated worktrees stay intact. Reproduce RED,
apply the minimal validator, run check_scope requirements and actual mobile
consumers/TypeScript, review independently, exact-HEAD CI and guarded merge.
No native dependency, lock, schema, science, UI, shared server or live config change.
Future binary/update classification and actual release approval stay separate.

## Validation and native limit

Execution results will be recorded from actual outputs. No corrected binary,
OTA, installed fix or physical acceptance is claimed by the source correction.
The first build remains useful diagnostic evidence and is not the completed MVP.
Visual decision: NOT_APPLICABLE; no visible composition is changed.

Local final evidence: check_scope ISOLATED; 25 targeted Builder tests PASS,
127 mobile suites / 1464 tests PASS and TypeScript PASS. 144 targeted backend,
release-contract and visual tests PASS. Ruff259≤548, spec protocol, OpenSpec
strict28/28, staged-diff secret scan and whitespace validation PASS. No Python
application file was added, no full backend sweep required for this tier.
The first budget invocation lacked Ruff on PATH; the correct existing toolchain
passed without a dependency change. Existing SQLite experimental and FastAPI
TestClient deprecation warnings are retained in logs.

Independent review found one Important: JavaScript trim accepts non-HTTP Unicode
whitespace. Two failing negative cases (NBSP/LF) were added before restricting
normalization to SP/HTAB. Final 25 tests include HTAB acceptance and malformed,
missing, conflicting-policy refusal. Request, owner/digest and no-retry behavior
are unchanged. [RFC9111 §5.2](https://www.rfc-editor.org/rfc/rfc9111.html#section-5.2)
defines the case-insensitive directive list; this client intentionally accepts
only the stricter no-store-only subset. Full review and correction evidence remain
in the private RC01 campaign, without raw account credentials in Git.
