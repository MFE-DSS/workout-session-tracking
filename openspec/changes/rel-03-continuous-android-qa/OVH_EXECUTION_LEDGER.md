# REL-03 OVH execution ledger

GO recorded before code; base 683e88313b0c2c5866f0594766213569628d1659.

Brainstorming / Options / Risques / Choix retenu: approved OVH amendment, strict v2 alongside preserved Render v1. No product/visual scope.

Task 1 in progress; 2–4 pending. Python resolved via existing venv; shell has no python alias.

Task 1 RED import missing then GREEN 2/2, server/bootstrap broad 54/54. Task 2 image provenance 10/10, observer 19/19. No remote operation.
Ruling: GitHub artifact ID is acquired after upload (cannot be embedded in its own immutable ZIP); producer payload becomes normalized qa-image-build receipt only after acquisition. Same source/run/attempt verified. Cost if wrong: evidence mismatch blocks release.
Ruling: PREPARE_IMAGE metadata preparation discards local image bytes without separately authorized private custody. No image availability/deployment inferred; private image transport remains an explicit operational prerequisite.
Regression diagnosed: applying OVH ancestry check to old Render synthetic fixtures caused invalid Git SHA; scope it to OVH and preserve Render v1 unchanged. Also preserve null-target refusal rather than AttributeError.

Real supervised canonical backend/facade HTTP: explicit four profiles, actual login, BODY consent absent/read403, NUT available/writefalse, owned library and builder reads200. 302 backend targeted/broad PASS. Root collector rejects extra mounts and changed routing generation. Node streaming image staging authenticates before final plaintext path; DB caps unchanged.
Ruling: SSH key/known_hosts paths are private runtime references, not paths embedded in the immutable proof; the proof pins host/user/port/known_hosts hash. Cost if wrong: source/host credential mismatch refuses observation.
Ruling: nginx routing is pinned to an administrator-qualified loaded master/worker generation plus the full current config digest and closed QA vhost. A reload/worker replacement fails closed until requalified. Cost: planned or ordinary worker replacement can interrupt delivery readiness; never treat on-disk nginx config alone as a loaded proof.

Final independent review: rel03_ovh_code_review (fresh context), no Critical or confirmed Important reported; 2 Minor. Regraded FIFO as Important: private reference open could block before the 15s SSH bound. Repro test_private_feature_fifo_refuses_without_blocking_before_ssh_deadline RED (2s timeout) then O_NONBLOCK regular-file admission fix. Current status documentation is already part of Task4, clarified without changing historical receipts.
Final: Ruling: real deployment/host installation/collector permissions/cloud image custody/installed-client proofs declined by reviewer remain unexecuted operational gates, never assumed from synthetic tests. Cost if wrong: no external release can be claimed.

Final: fixed FIFO reference refusal — named-FIFO subprocess test RED→GREEN, O_NONBLOCK plus retained fstat. No second independent review claimed. Final minor documentation correction: new current-authority paragraphs distinguish original NO_GO snapshots from technical GO received.
Task3 mobile: 127 suites /1449 tests PASS, TypeScript PASS; actionlint PASS. Required Bandit app scan PASS; optional tools scan reports low fixed subprocess warnings and two Medium locations (pre-existing facade all-interface bind, new literal /tmp container-tmpfs policy comparison), no confirmed vulnerability. Gitleaks scoped snapshot0; broad accidental scan historical Sonar issue key false positive independently reviewed. Ruff259≤548, baseline untouched. OpenSpec28/28 strict and protocol PASS. Bounded CI_INFRA sweep underway; no result prematurely claimed.

Final local CI_INFRA sweep PASS: 456/456 files, 8801 tests passed /1 skipped; 132 accepted batches. One memory adaptation4→2 after3108MiB; accepted peak2826MiB, budget3000. Zero file omitted; refused batch is not counted twice. No full sweep rerun after success. Mandatory remote CI remains pending.

Post-review correctness witness before merge: the correct image could be run with an overridden entrypoint/command (facade-only), while local version/health still describes valid private state. Root confirmed this missing collector refusal with RED test (DID NOT RAISE); collector now pins exact bootstrap entrypoint/config/activation argv from the existing Dockerfile. No Env read added, no deployment performed. This small leaf fix is checked on its own effective ISOLATED tier; original CI_INFRA full sweep remains recorded, no redundant full local replay. New remote HEAD CI required before merge; initial CI results will not stand in for it. No additional independent review claimed.

Exact-command guard GREEN: 247 targeted/broad transport/release/observer/image tests PASS; Ruff/budget259≤548 and protocol PASS. The new witness deliberately changed the inspected command to facade-only while retaining image identity. No second full local sweep or second independent review claimed; final-HEAD remote CI will replay the complete suite.
