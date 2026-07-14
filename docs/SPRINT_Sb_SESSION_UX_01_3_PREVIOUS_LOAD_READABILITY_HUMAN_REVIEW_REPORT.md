# Human Review — Sb_SESSION_UX_01.3 — Previous Load Readability (F2)

**Statut** : ✅ **HUMAN REVIEW ACCEPTED**
**Type** : HUMAN REVIEW — docs-only (aucun code touché)
**Date** : 2026-07-14
**Repo** : MFE-DSS/workout-session-tracking
**Branche** : `claude/sprint-reporting-fitness-app-V7Qr6`

---

## 0. Références vérifiées

| Élément | Valeur | Vérifié |
|---|---|---|
| Commit CODE | `015cdfe` — feat(session): surface previous load near active set | ✅ |
| CI code | run [`29329356785`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/29329356785) — **3/3 success** | ✅ |
| Audit source | `Sx_SESSION_UX_01` (`9925165`), friction F2 (P1) | ✅ |
| Build report | `SPRINT_Sb_SESSION_UX_01_3_PREVIOUS_LOAD_READABILITY_BUILD_REPORT.md` | ✅ |
| Working tree | **clean** | ✅ |

### Note sur le statut du build report
Le build report conserve son intitulé historique **« DELIVERED LOCALEMENT / non commité »** :
il décrit fidèlement l'état **au moment de la livraison locale** (LOCAL BUILD MODE). **Clarification
pour la traçabilité** : ce build a **ensuite été commité sous `015cdfe`** et **validé par la CI
`29329356785` (3/3 verte)**. Cette revue est l'acte qui grave ce passage à ACCEPTED.

---

## 1. CI code `015cdfe` — 3/3 success (source de vérité)

| Job CI | Résultat |
|---|---|
| **pytest + QA scripts** | ✅ **success** |
| **lint** (ruff budget + bandit + actionlint + shellcheck) | ✅ **success** |
| **SonarCloud** | ✅ **success** |

- **Aucun timeout** : job pytest sous `timeout-minutes: 45` (aucun job `cancelled`).

---

## 2. Périmètre du commit CODE `015cdfe` (preuve)

Fichiers touchés (6) : `app/templates/_partials/exercise_card.html` ·
`app/static/css/session_focus.css` · `tests/test_session_ux_prev_load.py` (nouveau) · le build
report + `SPEC_REGISTRY.md` + `ROADMAP_AND_NEXT_STEPS.md`.

**Aucun** `app/routers/**`, `app/services/**`, `app/models/**`, `data/**`, `migrations/**`,
`schema_snapshot`, `app/static/js/**`, `.github/**`, `deploy/**`. Vérifié par grep sur
`git show 015cdfe`.

---

## 3. Surfaces acceptées (revue fonctionnelle)

### 3.1 Console set actif
- **Rappel discret « dernière : X kg · Y reps »** (`session-focus__console-row-prev`).
- Affiché **au point de saisie** (sous le label du set actif).
- **Uniquement si historique disponible** (`_is_active_set and _ref.has_data`).
- **`aria-hidden="true"`** (décoratif).
- **Non impératif** (muted `--fg-dim`, mono/tabular).

### 3.2 Invariants conservés
- **Bloc global « Référence précédente »** (`console-ref--prev`) **intact** (test `test_console_ref_block_preserved`).
- **Placeholders overload inchangés** (set actif, `overload_placeholders`).
- **`value=""` strict** préservé (inputs non préremplis — `value` = `sl.weight_kg`/`reps` ou vide).
- **Completion dérivée serveur** (présence de weight/reps ; aucune checkbox).
- **Sticky CTA** intact · **rest timer** intact · **silhouette BodyMap** (`Sb_BODYMAP_01.1`) intacte.

### 3.3 Architecture
- **Template/CSS only** (`exercise_card.html` + `session_focus.css`).
- **Services inchangés** (`overload_*`, `last_time`) · **routes inchangées** · **modèles inchangés** ·
  **migrations absentes** · **aucun JS**. `_ref` = `last_time.get(...)` déjà calculé (aucune logique ajoutée).

---

## 4. Garde-fous — invariants respectés (vérifiés)

| Contrainte | État |
|---|---|
| Aucun router/service/model/data/migration/js touché | ✅ |
| `last_time` / overload / descriptor / ZONE_LABELS intacts | ✅ |
| Bloc « Référence précédente » conservé | ✅ |
| Rappel inline uniquement sur le set actif | ✅ (`test_prev_load_hint_only_on_active_row` == 1) |
| Silence si pas d'historique | ✅ (`test_prev_load_hint_absent_when_no_data`) |
| Inputs non préremplis | ✅ (`value=""` strict) |
| No-JS | ✅ (SSR pur) |
| Aucune nouvelle couleur | ✅ (`--fg-dim` ; `test_no_new_hex_colour_in_prev_hint_css`) |
| Body Intelligence OFF | ✅ |
| Delt_lat pending capture | ✅ (non traité) |
| Working tree clean | ✅ |

---

## 5. Tests (rappel build, verts en CI)

- **7** tests dédiés (`test_session_ux_prev_load.py`) — hint présent avec historique, absent sinon,
  aria-hidden, une occurrence, bloc console-ref préservé, pas de hex, pas de JS.
- Sweep ciblé build : **358 passed / 0 échec**.
- Suite complète CI : ✅ (job pytest). ruff clean (UP017 corrigé), budget **543 ≤ 548**.
- `check_scope` = ISOLATED → **promu SHARED_CODE** (carte séance active partagée) ; CI réelle
  confirmée 3/3.

> **Transparence** : un test initial ciblait E2 (exercice non actif sur push-a) → hint absent
> (comportement **correct**) ; le test a été **corrigé vers E1** (exercice actif). Correction de
> ciblage de test, pas un masquage de régression.

---

## Verdict

**Verdict :** ✅ **Sb_SESSION_UX_01.3 — HUMAN REVIEW ACCEPTED.**

Le rappel discret de la charge de la dernière séance **sur la ligne du set actif** (« dernière :
X kg · Y reps », au point de saisie) est **acté humainement** après **CI verte 3/3** sur `015cdfe`
(pytest + QA / lint / SonarCloud, aucun timeout). **Template/CSS only** : routers / services
(`overload_*`, `last_time`) / descriptor / `ZONE_LABELS` / modèles / data / migrations **intacts**
(`_ref` réutilisé). **Additif** (bloc « Référence précédente » conservé), **décoratif**
(`aria-hidden`), **silence** si pas d'historique (jamais de faux poids), **inputs non préremplis**,
completion dérivée serveur, **no-JS**, **aucune nouvelle couleur** (`--fg-dim`). Sticky CTA / rest
timer / silhouette BodyMap intacts. Body Intelligence OFF. Delt_lat pending capture. Working tree
clean.

**Suites** (aucun code) :
1. **Dogfood `Sb_SESSION_UX_01.5`** — confirmer le gain F2 en salle (la friction était *probable*,
   pas encore confirmée factuellement).
2. Si concluant → F1 (`01.2` priorité action) puis F3 (`01.4` scroll).
3. Indépendant : capture irritant #1 (`Delt_lat`).
