# SONAR-AUDIT-01 — Exhaustive Sonar feature and ROI audit

**Mode**: read-only analysis. No code changed, no configuration touched, no issue
suppressed/accepted/reopened in SonarQube, no PR opened.

**MEASURED AT**: `71d36cd` (`71d36cdb54b3e321382f7c8a6ad28bd41b1caa97`) — 2026-08-12 15:13 +0200
Every figure below carries the command that produced it. Anything not re-measured in this
session is marked as such.

**Corrections to prior state documents** are collected in §10.

---

## 1. Discovery — what is actually enabled

### 1a. CI job invoking a Sonar scanner — **ENABLED, OPPOSABLE**

`.github/workflows/ci.yml`, job `sonar` (lines 326-377).

```bash
grep -n -i 'sonar' .github/workflows/ci.yml
gh api repos/MFE-DSS/workout-session-tracking/branches/claude/sprint-reporting-fitness-app-V7Qr6/protection --jq '.required_status_checks'
```

| Property | Measured value |
|---|---|
| Scanner | `SonarSource/sonarqube-scan-action@v7.1.0` |
| Pinning | **mobile tag `v7.1.0`, not a digest/SHA** |
| Events | `pull_request` (all PRs) · `push` to trunk, with workflow-level `paths-ignore: ['docs/**']` |
| Secret gate | `SONAR_TOKEN`; job `if:` excludes fork PRs |
| Dependency | `needs: [test, lint]` — serialized after both |
| Opposable? | **YES.** Branch protection `required_status_checks.contexts = ["pytest + QA scripts", "SonarCloud"]` |

Enable dates, by commit:

```bash
git log --all -i --grep='sonar' --format='%h|%ad|%s' --date=short | tail -12
```

- `8c9244f` — 2026-05-08 — `feat(ci): Sb_20.4 SonarCloud integration — config + ci.yml job + runbook + triage template`
- `ef89420` — 2026-05-09 — `ci(sonar): require SonarCloud Quality Gate (Sb_20.5)` ← **becomes opposable here**

**Measurable period: 2026-05-08 → 2026-08-12 (96 days).**

> **Stale comment found.** `ci.yml:330-331` still reads *"ADVISORY in V1: continue-on-error keeps
> the merge unblocked. Sb_20.5 will turn this into a required status check."* There is no
> job-level `continue-on-error` (only on the two `download-artifact` steps), and Sb_20.5 landed
> 2026-05-09. The comment has been wrong for 95 days.

### 1b. `sonar-project.properties` — **PRESENT**

`sonar.projectKey=MFE-DSS_workout-session-tracking`, `sources=app`, `tests=tests`,
`python.version=3.11`, coverage from `coverage.xml`.

**External report ingestion is on** (lines 23-24) — this turns out to be the single most
consequential configuration decision in this repo (see §3, §6):

```properties
sonar.python.ruff.reportPaths=ruff-report.json
sonar.python.bandit.reportPaths=bandit-report.json
```

Exclusions: `migrations/**, scripts/**, deploy/**, data/**, var/**, **/__pycache__/**`.

**Is a business module excluded to force green?** No evidence of that motive — but the boundary
matters: `scripts/` holds **34 Python files** including the repo's own QA gates
(`check_scope.py`, `check_migration_patterns.py`, `check_spec_protocol.py`, `seed_db.py`,
`create_user.py`). These are unanalysed. `migrations/` is alembic-generated and guarded
elsewhere (§8c). Verdict: a defensible boundary, but a real blind spot rather than a neutral one.

**Two project keys exist in the org:**

```bash
sonar list projects
# {"key":"MFE-DSS_platret-ops-app"} {"key":"MFE-DSS_workout-session-tracking"} {"key":"workout-session-tracking"}
```

`workout-session-tracking` (unprefixed) is an **orphan** left by `4945c5a` (2026-05-08,
*"fix(sonar): use org-prefixed project key"*). It still exists and is still referenced — see 1d.

### 1c. Agent-side integration — **CLI + allowlisted HTTP, NO MCP, NO HOOKS, NO SKILL**

| Surface | Measured |
|---|---|
| `.mcp.json` | **absent** (`ls: No such file or directory`) |
| `.claude/settings.json` | permissions only — **no `PreToolUse`/`PostToolUse`/`UserPromptSubmit` hook** |
| `.claude/skills/**` | 2 skills, neither Sonar-specific; they name Sonar only as a gate to watch |
| `AGENTS.md` | **0 occurrences of "sonar"** (`grep -c -i sonar AGENTS.md` → `0`) |
| `CLAUDE.md` | no end-of-turn Sonar analysis protocol |
| `.claude/settings.local.json` | **~19 allowlist rules** for `curl https://sonarcloud.io/api/...` |

The de-facto integration is the allowlisted `curl`/`gh api` route, first appearing around PR #37
(2026-07-28) judging by the hardcoded `pullRequest=37` and `pullRequest=41` entries.

**A `sonar` CLI is installed and authenticated — and referenced nowhere in the repo:**

```bash
sonar --version   # 1.4.0
sonar auth status # [✓ Connected] https://sonarcloud.io · org mfe-dss · Source OS Keychain
git grep -l 'sonar list\|sonar api\|sonar analyze\|sonar remediate\|sonar context'   # exit 1 — no match
```

This is the largest unexploited capability found in this audit (§5, §10).

### 1d. IDE integration — **PRESENT, UNCOMMITTED, AND MISCONFIGURED**

`.vscode/settings.json` declares SonarQube-for-IDE connected mode:

```json
"sonarlint.connectedMode.project": { "connectionId": "mfe-dss", "projectKey": "workout-session-tracking" }
```

Two defects, both measured:

1. `projectKey` is the **orphan** key, not `MFE-DSS_workout-session-tracking`. Connected mode is
   binding to the abandoned project — so IDE-side issue status, suppressions and new-code
   context do not correspond to the project CI actually gates on.
2. The file is **not tracked**: `git ls-files .vscode/` returns nothing, and
   `git log -- .vscode/settings.json` is empty. So the answer to §2d ("any *committed* config?")
   is **no** — this is one machine's local state, invisible to every other clone.

### 1e. Automated remediation — **ENABLED, SERVER-SIDE, DAILY** → measured in §6

### 1f. Dependency / SCA — **ENABLED AND CONTRIBUTING TO A RED GATE**

```bash
sonar api GET '/api/measures/component?component=MFE-DSS_workout-session-tracking&metricKeys=sca_severity_any_issue,sca_rating_any_issue,new_sca_severity_any_issue'
```

`sca_severity_any_issue = 10` · `sca_rating_any_issue = 2.0` (B) · `new_sca_severity_any_issue = 10`
— which trips the gate condition `> 9`. Dependabot runs in parallel (11 open `dependabot/*`
remote branches at HEAD).

---

## 2. Issues — measured, paginated, deduplicated

The CLI caps at 500/page and gives no warning when it truncates. Total is **779**, so a single
unpaginated call would have silently dropped **279 issues (35.8%)**.

```bash
for p in 1 2; do sonar list issues --project MFE-DSS_workout-session-tracking \
  --format json --page-size 500 --page $p > issues_p$p.json; done
# dedupe on .key → 779 unique
```

### Totals

| | Count |
|---|---|
| **TOTAL** | **779** |
| OPEN | 749 |
| CLOSED (`FIXED`) | 29 |
| CLOSED (`FALSE_POSITIVE`) | 1 |
| **Closure rate** | **30 / 779 = 3.85 %** |

> **Caveat that must not be dropped:** SonarQube Cloud purges closed issues after a retention
> window. **29 is a floor on lifetime closures, not the lifetime total.** The git record (§4) shows
> defects closed under Sonar rule ids that no longer appear in this inventory. Where the two
> disagree, both are measurements and both are reported.

### Per type

| Type | Total | Open | Closed |
|---|---|---|---|
| CODE_SMELL | 752 | 723 | 29 |
| **BUG** | **20** | **20** | **0** |
| **VULNERABILITY** | **7** | **6** | **1** |

### BUG and VULNERABILITY — every rule id

| Type | Rule | Total | Open | Closed |
|---|---|---|---|---|
| BUG | `Web:InputWithoutLabelCheck` | 13 | 13 | 0 |
| BUG | `Web:ItemTagNotWithinContainerTagCheck` | 5 | 5 | 0 |
| BUG | `Web:S7930` | 1 | 1 | 0 |
| BUG | `pythonbugs:S6466` | 1 | 1 | 0 |
| VULNERABILITY | `external_bandit:B112` | 3 | 3 | 0 |
| VULNERABILITY | `external_bandit:B110` | 3 | 3 | 0 |
| VULNERABILITY | `secrets:S8215` | 1 | 0 | 1 |

### How many REAL defects were found and closed?

**In Sonar's current inventory: zero.** 0 BUGs closed. The single closed VULNERABILITY
(`secrets:S8215`) was closed as **FALSE_POSITIVE**, not fixed.

The git record tells a different and more favourable story — see §4. Both are reported.

### The single highest-severity OPEN issue, and whether anyone adjudicated it

There is **no open BLOCKER**. Open severities: MAJOR 668 · CRITICAL 48 · MINOR 33.

**Trap 4 does not hold here.** The project's only BLOCKER was adjudicated on the day of
integration:

```json
{ "key": "AZ13bWFnTiMI7OSQ3cnh", "rule": "secrets:S8215", "severity": "BLOCKER",
  "issueStatus": "FALSE_POSITIVE", "component": "app/routers/auth_routes.py", "line": 104,
  "message": "Make sure this bcrypt password hash gets revoked...",
  "creationDate": "2026-04-09", "updateDate": "2026-05-08", "lastChangeSource": "USER" }
```

A human triaged it. The security rating is **not** held hostage by an unmade decision.

The two worst OPEN issues are the CRITICAL defects — **and I verified both against the source.
Both are false positives.**

**(i) `pythonbugs:S6466` — CRITICAL / RELIABILITY:HIGH — `app/services/body_intelligence.py:570`
— open since 2026-06-27, never adjudicated.**
Message: *"Fix this access on a collection that may trigger an 'IndexError'."*
`textRange` offsets 17-28 on line 570 point at `bullets[:4]` in `return tuple(bullets[:4])`.
Sonar's dataflow (visible in `flows`) correctly deduces `bullets` may hold one element — then
concludes a slice may raise. It cannot:

```bash
python3 -c "b=['x']; print(b[:4])"   # ['x'] — no exception. A slice is total; it clamps.
```

**(ii) `Web:S7930` — CRITICAL / MAINTAINABILITY:HIGH + RELIABILITY:HIGH — `app/templates/base.html:132`
— open since 2026-07-17, never adjudicated.**
Message: *"Duplicate id "main-content" found. First occurrence was on line 28."*

```bash
grep -n 'main-content' app/templates/base.html
# 28:       existants. Cible le <main id="main-content">. #}
# 29:    <a class="skip-link" href="#main-content">…</a>
# 132:    <main id="main-content" class="container">
```

Line 28 is **inside a Jinja comment** opened at line 26 (`{# … #}`). There is exactly one
`id="main-content"` in the file. Sonar's Web analyzer does not strip `{# #}` and parsed a
commented-out example as live HTML.

**The legitimate un-actioned stock is the a11y layer**, not the CRITICALs. Verified sample —
`_partials/exercise_card.html:353`: an `<input type="text" … placeholder="kg">` with no `id`, no
`aria-label`, no associated `<label>`. A placeholder is not an accessible name. **13
`Web:InputWithoutLabelCheck` are real defects, open, and nobody has adjudicated them either.**

### Noise concentration — a single mechanical family drowns the inventory

| Rule | Open | Share of open |
|---|---|---|
| `external_ruff:UP017` (use `datetime.UTC`) | 136 | **18.2 %** |
| `external_ruff:I001` (import block unsorted) | 135 | 18.0 % |
| `external_ruff:UP045` (`X \| None`) | 122 | 16.3 % |
| `external_ruff:F401` (unused import) | 63 | 8.4 % |
| `python:S9073` (composite assertion) | 46 | 6.1 % |
| `python:S3776` (cognitive complexity) | 27 | 3.6 % |
| `python:S8415` (undocumented HTTPException) | 26 | 3.5 % |
| `python:S1192` (duplicated literal) | 18 | 2.4 % |

**Top rule = 18.2 % of open stock. All `external_*` imports = 516 / 749 = 68.9 %.**

The consequence is exactly what §3 warns about: **the 20 BUGs are 2.7 % of the open inventory.**
The genuine a11y defects and the two false-positive CRITICALs are buried under 516 imported
lint findings that the project has already decided to tolerate — `.ruff-budget.json` exists
precisely to hold that debt at a threshold. **The `sonar.python.ruff.reportPaths` line imported a
consciously-budgeted backlog into Sonar as 516 MAJOR-weighted issues.**

### Trap 3 — green PR gates, red project gate: not a contradiction, but not benign either

```bash
sonar api GET '/api/qualitygates/project_status?projectKey=MFE-DSS_workout-session-tracking'
```

Project gate = **ERROR**. Conditions:

| Metric | Actual | Threshold | Status |
|---|---|---|---|
| `new_coverage` | 91.7 | ≥ 80 | OK |
| `new_duplicated_lines_density` | 0.1 | ≤ 3 | OK |
| `new_bugs_severity` | 20 | ≤ 9 | **ERROR** |
| `new_code_smells_severity` | 20 | ≤ 14 | **ERROR** |
| `new_sca_severity_any_issue` | 10 | ≤ 9 | **ERROR** |
| `new_vulnerabilities_severity` | 10 | ≤ 9 | **ERROR** |

The usual explanation — "clean-as-you-code gates new code only, the legacy stock is out of
scope" — **is not the explanation here.** The new-code period is:

```json
"periods": [{"index": 1, "mode": "previous_version", "date": "2026-04-10T12:45:26+0000"}]
```

```bash
sonar api GET '…&metricKeys=new_lines,ncloc'   # new_lines = 79854 · ncloc = 25874
```

**The "new code" window has been open for 124 days and now contains 79,854 lines against a
25,874-line codebase — 3.1× the whole project.** No version was ever set, so `previous_version`
never rolled over. At project level, "new code" means "everything since April". That is why the
project gate is permanently red while every PR gate passes (the PR gate scopes to the PR diff).

**The plan for the stock** — there is none recorded. `docs/SONARCLOUD_TRIAGE_TEMPLATE.md` and
`docs/SPRINT_Sb_OPS_SONAR_HYGIENE_P1_REPORT.md` show one hygiene batch was run (2026-08-08, PR
#55); no standing burn-down exists. Concrete proposal in §6.

Ratings at HEAD: `reliability_rating 4.0` (D) · `security_rating 2.0` (B) ·
`security_review_rating 3.0` (C) · `coverage 92.2` · `security_hotspots 4`, 66.7 % reviewed.
The D reliability rating is produced by 20 bugs of which **2 are provably false and 18 are HTML
a11y**.

---

## 3. Impact on the code

```bash
git log --all -i --grep='sonar' --format='%h' | wc -l          # 111
git log --all --format='%B' | grep -oE '\b[a-zA-Z_]+:S[0-9]+' | sort | uniq -c | sort -rn
git grep -c 'NOSONAR' -- app tests scripts                     # exit 1 — no match
git grep -ci 'noqa.*sonar' -- app tests scripts                # exit 1 — no match
```

**111 Sonar-referencing commits** over 96 days.

Rules that actually caused a change, from commit bodies:

| Rule | Commits | Rule | Commits |
|---|---|---|---|
| `python:S9073` | 9 | `python:S1764` | 2 |
| `python:S5863` | 3 | `python:S1244` | 2 |
| `python:S1192` | 3 | `python:S5778` | 1 |
| `Web:S6819` | 3 | `python:S2245` | 1 |
| `python:S5145` | 2 | `css:S4657` | 1 |

### Top Sonar-driven commits — mechanical, or better abstraction?

**`0a34d9a` — `fix(security): hash email addresses before logging (CWE-117 / S5145)` — BETTER ABSTRACTION**
> *"Logging raw recipient addresses lets a malicious user inject CRLF into log files via the email
> field. EMAIL_REGEX (Sb_20.3) already rejects whitespace in registration, but the defense-in-depth
> fix is to never log user-controlled strings verbatim. `_redact_email()` returns the first 8 hex
> chars of SHA-256, enough for support correlation without leaking PII."*

The rule flagged one log line. The response was a **reusable PII-redaction boundary** with a
stated correlation-vs-leakage trade-off. This is the high-value case.

**`6b95ac4` — `fix(morphology): raise instead of assert for slot-intent load invariants (bandit B101 on PR #63)` — BETTER ABSTRACTION**
> *"3 external_bandit:B101 'use of assert' on the module-load invariant loop in slot_intent.py
> (asserts are stripped under python -O). Converted the three asserts to explicit ValueError
> raises, **matching substitution.py's load-time validation convention**. Behaviour unchanged; the
> same invariant is also pinned by test_intents_use_valid_taxonomy."*

The fix made a new module conform to an **existing architectural convention** and named the
runtime failure mode (`-O` strips asserts). Not mechanical.

**`9efcf7a` — `fix(programs): dedupe 404 detail literal into a constant (S1192)`** and
**`039f52b` — `refactor(recovery): name the registry's shared descriptor vocabulary`** — S1192
duplicated literals converted into named vocabulary. Mildly abstraction-producing.

**`f5097c9`, `f8d160e`, `95113e7`, `fa4fd9b`, `8f1925c` — `python:S9073` composite-assertion
splits — MECHANICAL.** Five commits, one rule, no abstraction. This is the rule that most often
breaks the gate and produces the least value per fix — which is precisely why it belongs to the
remediation agent (§6), not to a human sprint.

**`bb3a656`** (invite code → `secrets.choice`, S2245), **`d869c14`** (CSS shorthand + a11y
keyboard), **`61dab46`** (`math.isnan` instead of self-comparison), **`6184647`**
(`is_integer()` instead of float equality) — genuine correctness/security fixes.

### Suppression discipline — **MATURE**

**Zero `NOSONAR`. Zero Sonar-directed `noqa`.** 13 ruff `noqa` in `app/`, each carrying an inline
rationale, e.g. `app/services/home.py:54`:

```python
except Exception:  # noqa: BLE001, S110 — narrative is best-effort, never blocks
```

Findings that were refused are **argued in commit messages and in code comments**, never hidden
behind a blanket suppression. On the measured evidence this project is using static analysis
maturely, not using it to get green.

---

## 4. The PR channel — attributing the bots

Sampled 6 merged PRs spread across the measured period: **#19** (2026-06-29), **#37**
(2026-07-28), **#47** (2026-08-05), **#55** (2026-08-08), **#67** (2026-08-10), **#82**
(2026-08-12).

```bash
gh api repos/:owner/:repo/issues/<N>/comments --jq '.[] | "\(.user.login) | \(.created_at)"'
gh api repos/:owner/:repo/pulls/<N>/comments  --jq '[.[] | .user.login] | group_by(.) | map({(.[0]): length}) | add'
```

| PR | Conversation comments | **INLINE review comments** |
|---|---|---|
| #19 | `sonarqubecloud[bot]` ×1 | *(none)* |
| #37 | `sonarqubecloud[bot]` ×1 | *(none)* |
| #47 | `gitar-bot[bot]` ×1, `sonarqubecloud[bot]` ×1 | *(none)* |
| #55 | `gitar-bot[bot]` ×1, `sonarqubecloud[bot]` ×1 | *(none)* |
| #67 | `gitar-bot[bot]` ×1, `sonarqubecloud[bot]` ×1 | `gitar-bot[bot]`: 2, `MFE-DSS`: 1 |
| #82 | `gitar-bot[bot]` ×1, `sonarqubecloud[bot]` ×1 | `gitar-bot[bot]`: 2 |

**Two bots comment. `sonarqubecloud[bot]` posted 0 inline comments across all 6 PRs.
`gitar-bot[bot]` is the only bot that posts located findings.** Crediting Sonar for
inline-review value would have been wrong; Gitar arrived ~2026-08-05 (first seen on #47).

### Full body of a Sonar bot comment (PR #82)

> **Quality Gate passed** — Issues: 0 New issues · 0 Accepted issues · 0 New dependency risks.
> Measures: 0 Security Hotspots · 98.6 % Coverage on New Code · 0.0 % Duplication on New Code.
> *[See analysis details on SonarQube Cloud]*

**No located code finding. No file. No line. No rule id.** A Quality Gate summary with links.

### Timestamp relative to the last commit

```bash
gh api repos/:owner/:repo/pulls/82/commits --jq '.[] | "\(.sha[0:8]) \(.commit.committer.date)"'
# 5433ff5c 2026-08-12T11:00:59Z · f5097c9e 11:18:51Z · fda8a2ee 12:02:50Z
gh api repos/:owner/:repo/issues/82/comments --jq '… | "created=\(.created_at) updated=\(.updated_at)"'
# created=2026-08-12T12:16:13Z updated=2026-08-12T12:16:13Z
```

**The Sonar comment arrives 13 min 23 s after the final push, and is never edited.**

**Conclusion, on evidence: the Sonar PR comment carries no findings and post-dates the last
commit. It cannot have driven any code change. It ratifies; it does not trigger.**

### The real interop channel is LOCAL — and here is the proof

Commit `f5097c9`, authored **11:18:51Z — 57 minutes before the Sonar comment existed**:

> **`test(recovery): split the composite assertion Sonar flags as S9073`**
>
> *Sonar external gate failed on PR #82: new_code_smells_severity 15 > 14, a single MAJOR.*
>
> *Diagnosed in two queries with no guessing, using the route established on PR #79.
> `api/measures/component_tree` with `qualifiers=FIL` returned empty — the known signal that the
> finding sits in a TEST file, which that qualifier does not return. Querying the test path
> directly gave `new_major_violations=1`, severity 15, in `tests/test_zone_recovery.py`. **The
> MAJOR = 15 calibration held again.***
>
> *The cause was `python:S9073`, a composite assertion (`assert case and legacy and here`) — and,
> more to the point, a hole in my own method. The pre-scan I ran before pushing covered only the
> two app modules, not the test files. The previous slice passed by luck: it happened to contain
> no composite assertion.*
>
> *Fixed with one assert per condition, each carrying the case as its message. **The pre-scan is
> now re-run across all four touched files and reports S9073 NONE everywhere**, and the lesson is
> recorded in session memory with the AST snippet so the next slice scans tests from the start.*

This is a complete **measure → fix → RE-MEASURE** loop performed locally before the commit
existed. The trigger was the **CI required-check failure**, the diagnosis was **local API
queries**, the verification was a **local re-scan**. The PR bot comment played no part.

The method itself is documented in `4ef0c9f` (*"record the Sonar diagnosis route and the two
wasted guesses"*), which is candid about its cost:

> *"api/issues/search returns TOTAL 0 for this PR under every parameter combination, via gh api and
> via WebFetch alike; **it needs a Sonar auth I do not have**. So the gate number was all I had, and
> I twice changed code on a supposition… the next red gate costs one query rather than three CI
> cycles."*

---

## 5. That documented constraint is now obsolete — measured this session

The workaround above (`measures/component_tree` + `qualifiers=FIL` trap + local AST inference +
a MAJOR=15 / CRITICAL=10 severity-weight calibration) exists **only because unauthenticated
`issues/search` returns 0**. The installed CLI holds a keychain token and does not have that
problem:

```bash
sonar list issues --project MFE-DSS_workout-session-tracking --pull-request 82 --format json
# total: 1
# python:S9073  MAJOR  MFE-DSS_workout-session-tracking:tests/test_zone_recovery.py
```

**One command returns the exact rule, severity and file** that `4ef0c9f` records as having cost
two wrong guesses and three CI cycles to infer. The capability that closes the documented gap is
installed, authenticated, and **cited nowhere in the repo, in any skill, or in `AGENTS.md`.**

---

## 6. The remediation agent — measured, then valorised

### It exists and it runs daily

```bash
git branch -r | grep -c 'remediate-claude'    # 13
```

13 branches named `remediate-claude/sprint-reporting-fitness-app-V7Qr6-<YYYYMMDD>-09012x-<sha>`,
one per day, **2026-07-31 → 2026-08-12, ~09:01 daily**. There is no workflow for it in the repo
(`grep -rl -i 'remediat' .github/` → no match), so it is **server-side SonarQube Cloud
remediation acting through the GitHub App**, not a committed pipeline.

### Yield — three numbers

```bash
for b in $(git branch -r | grep 'remediate-claude' | tr -d ' '); do
  echo "$(git rev-list --count origin/claude/sprint-reporting-fitness-app-V7Qr6..$b) $b"; done
gh pr list --repo MFE-DSS/workout-session-tracking --state all --search "remediat" --json number,state,title
# []
```

| Runs | Branches with ≥1 commit | PRs opened | Merged |
|---|---|---|---|
| **13** | **0** | **0** | **0** |

**YIELD = 0 / 13.** Every branch head is an ancestor of trunk with zero commits ahead. Over 13
days the feature produced no diff, no PR, and no merge.

### Diagnosis — testing each hypothesis against evidence

| | Hypothesis | Verdict |
|---|---|---|
| **H5** | Not enabled for this tier | **REJECTED** — it is enabled and ran 13/13 days on schedule. |
| **H1** | Only targets new code, and new code is already clean | **REJECTED** — the new-code period has been open since 2026-04-10 and holds 79,854 lines with 547 new code smells and 19 new bugs. There is abundant "new code" with issues. |
| **H4** | Nobody reviews/merges its branches | **REJECTED as cause** — there is nothing to review. 0 commits means no PR could exist. It is a *consequence*, not the cause. |
| **H3** | Cuts from a stale base and drifts | **PARTIALLY HOLDS** — runs 1-6 (Jul 31 → Aug 5) all cut from `5a85d67` (2026-07-30) while trunk advanced 7 commits. From Aug 6 it tracks trunk (latest cut 5 commits behind). Staleness is real but cannot explain zero output. |
| **H2** | Its eligible-rule set does not intersect the project's top rules | **✅ HOLDS — this is the cause.** |

**H2, quantified.** The agent can only fix issues Sonar's own analyzers raise. It cannot fix
`external_*` issues — those are verbatim imports from third-party JSON reports with no Sonar rule
engine and no Sonar fix behind them.

```
OPEN total                                     749
  external_* (imported, NOT remediable)        516   68.9 %
  Sonar-native (remediable in principle)       233   31.1 %
```

**The four highest-volume rules in this project — `UP017` (136), `I001` (135), `UP045` (122),
`F401` (63) — are all `external_ruff`. The remediation agent is structurally blind to 69 % of the
inventory,** including everything at the top of it.

### Now make it pay — the productive configuration is the inverse of the default

The PR gate already keeps new code clean (every sampled PR gate passed). What no gate will ever
close, and no human will ever prioritise, is the **Sonar-native legacy stock: 233 issues,
24.3 h of Sonar-estimated effort.** That is the agent's proper target.

**First productive batch — mechanical, Sonar-native, zero production-logic risk:**

| Rule | Open | Sonar effort | Location | Nature |
|---|---|---|---|---|
| `python:S9073` — split composite assertion | **46** | 230 min | 100 % `tests/` | purely mechanical |
| `python:S5778` — one invocation per exception test | **13** | 65 min | 100 % `tests/` | mechanical |
| `css:S4666` — duplicate CSS selector | **11** | 11 min | 2 CSS files | mechanical |
| `python:S9083` — empty parens on decorator | **10** | 10 min | 100 % `tests/` | trivial |
| **TOTAL** | **80** | **316 min (5.3 h)** | **46 files, 0 production-logic modules** | |

`sonar remediate --issues` accepts max 20 keys per call → **4 invocations**.

**Review effort this would cost a human:** 80 mechanical hunks across 46 files (44 test files +
2 CSS files). No business logic, no app module. A diff of that shape reviews at roughly 1-1.5
minutes per hunk once the pattern is established — **≈1.5-2 h of review against 5.3 h of
Sonar-estimated authoring.** That ratio is the argument for the feature.

**`python:S9073` is the strongest single candidate on independent grounds:** it is the rule that
has broken this project's gate more than any other — **9 commit-body mentions, 5 dedicated
commits, 2 of them in the last 48 hours** (`f8d160e` 2026-08-11, `f5097c9` 2026-08-12), each
costing a CI cycle.

**Honest caveat, stated because it changes what the batch buys you:** clearing the legacy S9073
backlog does **not** prevent future S9073 gate failures, because the PR gate scopes to the PR
diff and future composite assertions will be newly written. The recurring-failure fix is the
local AST pre-scan the agent already built (`f5097c9`). **The batch buys the project-level rating
and the burn-down, not PR stability.** Both are worth having; conflating them would overstate it.

**Second batch (needs judgment, not mechanical):** `python:S8415` ×26 (document HTTPException
status codes in FastAPI `responses=` — genuine OpenAPI value), `python:S1192` ×18 (duplicated
literals → named constants).

**Never delegate:** `python:S3776` ×27 (cognitive complexity, 407 min) — that is business-logic
refactoring and needs a human with the domain spec.

---

## 7. Cost

### CI wall-clock — measured on run `31594615616` (PR #82, 2026-08-12)

```bash
gh api repos/:owner/:repo/actions/runs/31594615616/jobs --jq '.jobs[] | "\(.name) | \(.started_at) | \(.completed_at)"'
```

| Job | Start | End | Duration |
|---|---|---|---|
| lint (ruff budget + bandit + actionlint + shellcheck) | 12:02:59Z | 12:03:40Z | **41 s** |
| pytest + QA scripts | 12:03:00Z | 12:14:52Z | **11 m 52 s** |
| **SonarCloud** | 12:14:55Z | 12:16:13Z | **1 m 18 s** |
| **Total run** | 12:02:59Z | 12:16:13Z | **13 m 14 s** |

**Does it duplicate work another job already does? No — and this is a deliberate, documented
design.** The Sonar job re-runs neither the test suite nor the linters. It downloads their
artifacts:

```yaml
- name: Download coverage report     # coverage-xml artifact from `test`
- name: Download linter reports      # ruff-report.json + bandit-report.json from `lint`
- uses: SonarSource/sonarqube-scan-action@v7.1.0
```

`sonar-project.properties:20-22` states the intent: *"Sonar enriches its analysis with ruff +
bandit findings **instead of re-running them**, so the gate stays coherent with the linters job."*
No services stood up, no system libraries reinstalled.

**The measurable cost is serialization, not duplication.** `needs: [test, lint]` puts Sonar on
the critical path after the longest job: the run ends at 12:16:13 instead of 12:14:52 —
**+81 s, ≈10 % of PR wall-clock.** Unavoidable while it consumes `test`'s coverage artifact.
`fetch-depth: 0` is required for blame/new-code detection.

### Commits that reduced this cost

- **`42` / `ci: parallelize pytest full sweep with xdist`** (2026-07-30) — cut the `test` job,
  which gates Sonar's start. `CLAUDE.md §1` records 37 → 11 min; the run above measures the
  `test` job at **11 m 52 s**, consistent.
- **`9a3760f` / `Sb_CI_02_1_PATH_AWARE_GATING`** (2026-08-10) — path-aware gating without
  weakening branch protection. The Sonar job deliberately **still runs** on non-runtime changes
  (`ci.yml:346-351`) so the required external check `SonarCloud Code Analysis` is still emitted;
  the artifact downloads are `continue-on-error: true` to tolerate a missing `coverage.xml`.
  Verified on PRs #69/#70 per the inline comment.
- **`Sb_OPS.ci-path-filter`** — workflow-level `paths-ignore: ['docs/**']`, **push only**. Every
  PR still runs the full Sonar job.
- **`47` / `ci: fix SonarCloud coverage path mapping`** (2026-08-05) — removed a coverage-path
  rewriting step in favour of correct sensor resolution against `sonar.sources=app`.

### Token/verbosity mechanisms in the agent protocol

Mechanisms that exist, with the commits that introduced them:

- **Targeted metric queries instead of issue dumps** — `qualitygates/project_status?pullRequest=N`
  and `measures/component_tree` with per-severity violation metrics, rather than fetching issue
  lists (`4ef0c9f`, and the ~19 narrowly-scoped `curl` allowlist entries in
  `.claude/settings.local.json`).
- **Severity-weight calibration cached in session memory** (MAJOR = 15, CRITICAL = 10) so a gate
  delta is interpreted arithmetically instead of by re-querying (`4ef0c9f`).
- **Local AST pre-scan before push**, to avoid discovering S9073 through a CI cycle (`f5097c9`).
- **Tiered local verification** — `scripts/check_scope.py` + `.check-policy.json` classify the
  diff and prescribe the minimum sufficient local check set (`CLAUDE.md §1`).

**Token savings: not measurable from this repository.** There is no token telemetry in git. No
percentage, delta or saving is claimed.

---

## 8. The limit of the tool

### (a) A rule right in general, wrong here because a project contract requires the construct

**`external_bandit:B110` — `app/services/home.py:54` — VULNERABILITY, SECURITY:MEDIUM.**
`try/except/pass` is a legitimate security smell in general. Here the contract is explicit three
lines above:

```python
# Sb_27.5 — attach a deterministic narrative phrase per tile. The
# narrative helpers are pure (no DB, no LLM) and never raise on
# missing fields, so we don't need a try/except guard here.
try:
    today["narrative"] = narrate_reco(today)
except Exception:  # noqa: BLE001, S110 — narrative is best-effort, never blocks
    pass
```

The module docstring states the invariant the construct implements: *"one tile never breaks the
others."* The dashboard is a composition of independently-degrading tiles; swallowing a narrative
failure **is** the requirement.

**And this exposes the dual-adjudication problem §8 asks about.** `pyproject.toml` runs
flake8-bandit through ruff (`select = [… "S" …]`) **and** bandit standalone, and
`sonar-project.properties` ingests **both** reports. The argued `noqa: S110` silences ruff. It
has no effect on bandit's `B110`. So the same finding is **adjudicated in one tool and left open
in another** — and the Sonar copy is the one that counts:

> **These 6 issues — 3× `external_bandit:B110` + 3× `external_bandit:B112` — are 100 % of the
> project's open VULNERABILITY count and the sole driver of `security_rating = 2.0` (B).** Every
> one of them sits on a deliberate best-effort degradation boundary (verified at
> `home.py:54`, `body_intelligence_inputs.py:87` and `:103`, `session_review.py:72`,
> `weekly_loop.py:62` and `:229` — all `try/…/except Exception: continue|pass` around a
> per-item scoring call inside an accumulate loop).

### (b) A finding where the tool sees the FORM and misses the SUBSTANCE

**`pythonbugs:S6466` — `body_intelligence.py:570` — CRITICAL, RELIABILITY:HIGH.** Detailed in §2.
Sonar's dataflow reasoning is *correct* right up to the conclusion: it proves `bullets` may hold a
single element, then sees a subscript-shaped token `bullets[:4]` and reports a possible
`IndexError`. It read the **form** (a subscript on a short collection) and missed the
**substance** (a slice is total — it clamps, it does not raise).

Meanwhile the real question on that line — *is truncating the user's readout to 4 bullets the
right product behaviour, and why is `4` an unnamed literal in a function whose contract is
"déterministe : à input égal, output bit-à-bit identique"?* — **no rule asks.** The tool is
loudly wrong about a non-problem on the exact line where a genuine, silent design question sits.

### (c) Something important Sonar cannot see, because no rule detects an ABSENCE

**The additive-only migration contract — this project's stated constraint #1.**

`CLAUDE.md §2` names it in those terms: *"Migrations : **additive-only** … Invariance historique =
contrainte #1 des cycles métier."* A migration that drops a column silently destroys the
historical record every business cycle depends on.

**No Sonar rule detects it.** There is no rule for *"this Alembic `upgrade()` drops a column"* —
and `sonar.exclusions` puts `migrations/**` and `scripts/**` outside analysis regardless. The
guard is entirely outside Sonar:

- **`.migration-policy.json`** — 7 arbitrated rules: `drop_column_in_upgrade: fail`,
  `drop_table_in_upgrade: fail`, `execute_delete_in_upgrade: fail`,
  `add_column_not_null_no_default: fail`, three more at `warn_requires_justify`, plus a
  `# migration-justify:` escape hatch and 17 grandfathered pre-Sb_26.2 files.
- **Enforcement**: `scripts/check_migration_patterns.py`, `check_migration_roundtrip.py`,
  `check_alembic_drift.py`, `check_schema_snapshot.py` — all in the excluded `scripts/` tree.
- **Doctrine**: `docs/MIGRATION_HARDENING.md §4`.

Static analysis raises what exists. It cannot raise a missing guard, an unenforced architectural
boundary, or a destroyed invariant.

**Where arbitration is recorded** for this project: `CLAUDE.md` (versioned execution contract,
prioritaire), `.check-policy.json`, `.migration-policy.json`, `.spec-protocol-allowlist.json`,
`docs/strategy/SPEC_REGISTRY.md` + `SPEC_DRIVEN_ENGINEERING_PROTOCOL_v1.md`, and
`docs/strategy/AGENTIC_DELIVERY_PROTOCOL.md`. **Sonar is not among them and has no authority
over them** — correctly so.

---

## 9. FINAL VERDICT

```
MEASURED AT            71d36cd / 2026-08-12  (all figures re-derived this session)

FEATURES ENABLED       CI scanner job          2026-05-08 (8c9244f)   OPPOSABLE  (required check since 2026-05-09, ef89420)
                       Quality Gate (PR-scope) 2026-05-09 (ef89420)   OPPOSABLE
                       Quality Gate (project)  2026-05-09             ADVISORY   (ERROR at HEAD, blocks nothing)
                       ruff+bandit ingestion   2026-05-08 (Sb_20.4)   ADVISORY   (but drives 69% of inventory)
                       SCA / dependency risks  active at HEAD          ADVISORY   (10 > 9, contributes to red project gate)
                       Remediation agent       2026-07-31 (server-side) ADVISORY (0 output — see below)
                       SonarLint connected mode  uncommitted, MISCONFIGURED (bound to orphan project key)
                       Sonar CLI v1.4.0        installed + authenticated, REFERENCED NOWHERE
                       MCP / hooks / Sonar skill / AGENTS.md protocol   ABSENT

ISSUES                 total 779 / open 749 / closed 30 / closure rate 3.85%
                       (29 FIXED + 1 FALSE_POSITIVE; closed count is a FLOOR — Sonar purges closed issues)
                       CODE_SMELL 752/723 open · BUG 20/20 open · VULNERABILITY 7/6 open

REAL DEFECTS CLOSED    Per Sonar's live inventory: ZERO. 0 BUGs closed; the 1 closed
                       VULNERABILITY (secrets:S8215) was closed as FALSE_POSITIVE, not fixed.
                       Per the git record (survives the purge): at least 6 genuine defects —
                       python:S5145 ×2 (CWE-117 log injection), python:S2245 (predictable RNG on
                       squad invite codes), external_bandit:B101 ×3 (load-time asserts stripped
                       under -O), python:S1244 ×2 (float equality), python:S1764 ×2, python:S5863 ×3.

WORST OPEN ISSUE       No open BLOCKER. The only BLOCKER (secrets:S8215) WAS adjudicated —
                       FALSE_POSITIVE by a USER, 2026-05-08. Trap 4 does not hold.
                       Both open CRITICAL defects are NEVER-ADJUDICATED and BOTH ARE WRONG:
                         pythonbugs:S6466 body_intelligence.py:570 — flags `bullets[:4]`; a slice
                           cannot raise IndexError (proven). Open since 2026-06-27.
                         Web:S7930 base.html:132 — "duplicate id" whose first occurrence is inside
                           a Jinja {# … #} comment the Web analyzer failed to strip (proven).
                           Open since 2026-07-17.
                       The legitimate un-actioned stock is 13× Web:InputWithoutLabelCheck
                       (verified real: inputs with a placeholder and no accessible name).

NOISE CONCENTRATION    Top rule external_ruff:UP017 = 136/749 = 18.2% of open stock.
                       ALL external_* = 516/749 = 68.9%. The 20 BUGs are 2.7% of the inventory —
                       drowned by a lint backlog the project already budgets in .ruff-budget.json.

SONAR-DRIVEN COMMITS   111 commits (git log --all -i --grep='sonar').
                       Top rules in bodies: S9073 ×9, S5863 ×3, S1192 ×3, Web:S6819 ×3,
                       S5145 ×2, S1764 ×2, S1244 ×2.
                       Best abstraction produced: 0a34d9a — S5145 on one log line became
                       _redact_email(), a reusable SHA-256-prefix PII boundary with a stated
                       correlation-vs-leakage trade-off. Runner-up: 6b95ac4 — bandit B101 asserts
                       converted to explicit raises "matching substitution.py's load-time
                       validation convention", i.e. conformed to an existing architecture.

SUPPRESSION DISCIPLINE 0 NOSONAR. 0 sonar-directed noqa. 13 ruff noqa in app/, each with an
                       inline argued rationale. Refusals are argued in commit messages and code
                       comments, never hidden. MATURE USAGE.

PR CHANNEL             sonarqubecloud[bot] posts exactly ONE conversation comment per PR
                       containing ONLY a Quality Gate summary — pass/fail, counts, coverage,
                       links. ZERO located findings. ZERO inline review comments across all 6
                       sampled PRs (#19 #37 #47 #55 #67 #82).
                       gitar-bot[bot] is the ONLY bot posting located inline findings
                       (#67: 2, #82: 2), active since ~2026-08-05.
                       Timing on #82: last commit 12:02:50Z, Sonar comment created 12:16:13Z and
                       never edited → +13m23s. It ratifies; it cannot trigger.

INTEROP CHANNEL        LOCAL. Trigger = CI required-check failure; diagnosis = local API queries;
                       verification = local re-scan — all before the commit exists.
                       Proof: f5097c9 (2026-08-12, 57 min BEFORE the Sonar comment) —
                       "Sonar external gate failed on PR #82: new_code_smells_severity 15 > 14…
                        Diagnosed in two queries with no guessing… The pre-scan is now re-run
                        across all four touched files and reports S9073 NONE everywhere."
                       Method documented in 4ef0c9f, including its cost: "two wasted guesses",
                       "three CI cycles".

REMEDIATION YIELD      13 runs / 0 commits / 0 PRs / 0 merged = 0/13.
                       Daily since 2026-07-31, ~09:01, server-side (no workflow in repo).
                       H5 rejected (enabled, ran 13/13). H1 rejected (new-code window holds
                       79,854 lines, 547 new smells). H4 rejected as cause (nothing to review).
                       H3 partial (runs 1-6 all cut from stale 5a85d67 while trunk moved 7
                       commits; tracks trunk from Aug 6) — real but not causal.
                       H2 HOLDS AND IS THE CAUSE: 68.9% of open issues are external_* imports the
                       agent structurally cannot fix, including the four highest-volume rules
                       (UP017 136, I001 135, UP045 122, F401 63 — all external_ruff).

REMEDIATION PROPOSAL   Point it at the Sonar-native legacy stock the gate will never close:
                         python:S9073  46 issues  230 min  100% tests/
                         python:S5778  13 issues   65 min  100% tests/
                         css:S4666     11 issues   11 min  2 CSS files
                         python:S9083  10 issues   10 min  100% tests/
                         = 80 issues, 316 min (5.3 h) Sonar effort, 46 files, 0 app modules.
                       4 invocations (sonar remediate caps at 20 keys). Human review cost:
                       ~1.5-2 h for 80 mechanical hunks with no business logic.
                       S9073 is the strongest candidate: 9 commit-body mentions, 5 dedicated
                       commits, 2 in the last 48h, each costing a CI cycle.
                       Caveat: this buys the project rating and the burn-down, NOT PR stability —
                       clean-as-you-code gates the PR diff, so future composite assertions still
                       need the local AST pre-scan from f5097c9.
                       Batch 2 (judgment): S8415 ×26, S1192 ×18. Never delegate: S3776 ×27.

COST                   Sonar job 1m18s on run 31594615616 (12:14:55→12:16:13Z).
                       NO duplicated work — downloads coverage.xml + ruff/bandit JSON as
                       artifacts instead of re-running (sonar-project.properties:20-22).
                       Cost is SERIALIZATION: needs:[test,lint] adds +81s ≈10% to PR wall-clock
                       (run ends 12:16:13 vs test's 12:14:52).
                       Reducing commits: PR#42 xdist (test job 37→11 min, measured 11m52s here),
                       9a3760f path-aware gating, Sb_OPS.ci-path-filter (push only — every PR
                       still runs Sonar), PR#47 coverage path mapping.
                       Token mechanisms present: targeted metric queries over issue dumps,
                       cached severity weights, local AST pre-scan, tiered check_scope policy.
                       Token savings: NOT MEASURABLE FROM THIS REPOSITORY.

TOOL LIMITS            (a) external_bandit:B110 home.py:54 — try/except/pass required by the
                           stated contract "one tile never breaks the others". Argued in a noqa
                           that silences ruff but NOT bandit, whose copy Sonar also ingests.
                           Same finding adjudicated in one tool, open in another — and those 6
                           issues are 100% of open VULNERABILITIES and the sole cause of
                           security_rating B.
                       (b) pythonbugs:S6466 — sees the FORM (a subscript on a short list), misses
                           the SUBSTANCE (a slice clamps). Loudly wrong on the exact line where a
                           real unexamined question sits: why is 4 an unnamed literal in a
                           function contracted to be bit-for-bit deterministic?
                       (c) THE ABSENCE: nothing in Sonar can detect a violation of the
                           additive-only migration contract — CLAUDE.md's stated "contrainte #1
                           des cycles métier". No such rule exists, and migrations/** + scripts/**
                           (34 py files) are excluded anyway. Arbitration lives in
                           .migration-policy.json (7 rules), scripts/check_migration_*.py, and
                           docs/MIGRATION_HARDENING.md §4 — never in Sonar.

────────────────────────────────────────────────────────────────────────────────────────────
RENEW / RECONFIGURE / DROP — per feature, with the measurement that decides it
────────────────────────────────────────────────────────────────────────────────────────────

RENEW      CI scanner + PR Quality Gate (required check)
           → Decided by: it is the ONLY opposable Sonar surface, it costs 78s and duplicates
             nothing, and it is the trigger for a documented local measure→fix→re-measure loop
             (f5097c9). 111 Sonar-referencing commits and at least 6 genuine defects fixed.

RENEW      External ruff+bandit ingestion — BUT SEE RECONFIGURE #2
           → Decided by: it keeps the gate coherent with the linters job at zero extra CI cost.
             The defect is not the ingestion, it is the unbudgeted severity it assigns.

RECONFIGURE #1 — HIGHEST VALUE, LOWEST EFFORT: set a project version / roll the new-code period.
           → Decided by: new_lines = 79,854 vs ncloc = 25,874, period `previous_version` frozen
             at 2026-04-10. The project gate is red only because "new code" means "4 months of
             everything". Four of six conditions clear the moment the period is meaningful.

RECONFIGURE #2 — bring external_* severity in line with the ruff budget the project already keeps.
           → Decided by: 516/749 = 68.9% of the inventory is imported lint debt that
             .ruff-budget.json already governs, and it buries 20 BUGs at 2.7% of the stock.

RECONFIGURE #3 — repoint the remediation agent at the Sonar-native legacy stock.
           → Decided by: yield 0/13 with cause H2 confirmed. The 80-issue batch above is its
             first productive run. Do NOT drop this feature on its yield alone — it has never
             been pointed at work it can actually do.

RECONFIGURE #4 — adopt the authenticated `sonar` CLI as the agent's diagnosis route; record it in
           AGENTS.md / a Sonar skill, and consider `sonar integrate claude` for MCP+hooks.
           → Decided by: `sonar list issues --pull-request 82` returns the exact rule, severity
             and file in ONE call — the finding 4ef0c9f records as costing two wrong guesses and
             three CI cycles to infer. The workaround is documented; the tool that obsoletes it is
             installed, authenticated, and cited nowhere.

RECONFIGURE #5 — fix SonarLint connected mode (orphan projectKey) and commit it, or delete it.
           → Decided by: projectKey `workout-session-tracking` ≠ the gated project
             `MFE-DSS_workout-session-tracking`, and `git ls-files .vscode/` is empty.

ADJUDICATE (not a feature decision — an unmade decision, 3 items)
           → The two CRITICALs are false positives, proven in this session; mark them as such and
             reliability_rating stops being driven by them. Then decide the 13 real
             Web:InputWithoutLabelCheck a11y defects, and the 6 external_bandit try/except
             findings that are contract-required (accept with the argument already written in the
             code, so Sonar stops reporting security_rating B on a decided question).

DROP       Nothing. No measured Sonar feature is worthless — but three of them
           (remediation, external ingestion, project gate) are currently pointed at the wrong
           target, and that is a configuration verdict, not a value verdict.
```

---

## 10. Corrections to prior state documents (measurement wins)

| Prior statement | Source | Measured at `71d36cd` |
|---|---|---|
| *"ADVISORY in V1: continue-on-error keeps the merge unblocked. Sb_20.5 **will** turn this into a required status check."* | `ci.yml:330-331` | **Stale by 95 days.** No job-level `continue-on-error`; branch protection lists `SonarCloud` as required since `ef89420` (2026-05-09). |
| *"api/issues/search returns TOTAL 0 … it needs a Sonar auth I do not have"* | `4ef0c9f` commit body | **No longer true.** `sonar` CLI v1.4.0 with an OS-Keychain token returns the PR-scoped finding in one call. The documented `component_tree` + AST-inference workaround is obsolete. |
| *"gate Sonar canonical ERROR = dette repo préexistante"* | session memory | **Directionally right, mechanically wrong.** The project gate is ERROR because the new-code period froze at 2026-04-10 (`previous_version`, never rolled), so 79,854 lines count as "new" against a 25,874-line codebase. It is a period-configuration artefact, not an irreducible legacy debt. |
| *"issues/search renvoie 0, utiliser measures/component_tree"* | session memory | **Superseded** — see row 2. The route is still correct for unauthenticated access; it is no longer necessary. |
| Implicit assumption that the Sonar PR bot surfaces findings | agent skills reference "watch CI/Gitar/Sonar" | **Measured false.** 0 inline comments across 6 PRs; the conversation comment is a gate summary posted after the last push. `gitar-bot[bot]` is the only source of located inline findings. |

---

### Reproducibility

Every figure above was produced at `71d36cd` on 2026-08-12 with the commands shown inline.
Issue counts derive from a two-page paginated fetch deduplicated on `.key` (779 unique). No
number in this document was copied from a pre-existing document without re-measurement.
