# Design — minimal isolated ORM bootstrap

## Context
Canonical c454af8; historical QA image is b8fc63f and does not contain the reader. Experiments used its attested Linux/amd64 Debian13.3/Python3.11.14/SQLite3.46.1 environment with the exact canonical source mounted read-only. Docker Desktop runs on ARM64; no native-x86 or VPS equivalence is claimed.

## Brainstorming / Options / Risques / Choix retenu
1. Preferred: after install_limits(), set os.environ["DATABASE_URL"] = "sqlite:///:memory:" before any app import. This is a fixed bootstrap-only ORM setting; actual read DB remains argv-only. Cost: incidental ORM imports still exist, but cannot try to create a persistent state directory.
2. Precreate an empty var directory during packaging: smaller layout workaround, but preserves an unnecessary default file DB dependency and requires a deployment-recipe amendment. Not selected.
3. Refactor shared identity/config/database imports: larger consumer blast radius and unnecessary architecture change. Not selected.

## Proposed exact change
worker.main: install_limits() first, then stdlib os import and fixed DATABASE_URL assignment, then existing qualification/normal paths. Never inherit the parent's URL, use setdefault, or substitute the real capture URL. Do not remove isolation flags, lower gates, relax validation or increase budgets.

## Verification
Observed RED: 126PASS/1FAIL on the complete existing seven-file reader/API suite on the exact Linux candidate. Actual child exits1, reaped; trace EROFS /opt/auren/var. Targeted regression must reproduce bootstrap write attempt without changing SCI. After GO, prove GREEN on that regression and the actual source-readonly container, then broad SCI tests and required CI on the exact delivered HEAD. A trace diagnostic is separate from uninstrumented latency. Any remaining failure keeps HOLD.

## Trust and transfer
Candidate authorities are root-owned, no writable mode bits/ACLs, readonly mounts; UID10001/caps0 cannot write. All3337 source regular files match independent git archive,18 profile pins match Git. This is candidate evidence, not future deployment assurance. No qualified operational profile, activation, DATA or release is emitted by this preparation.
