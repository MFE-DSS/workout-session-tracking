# Human Review — Sb_SESSION_UX_01.2 — Active Console Priority (F1)

**Statut** : ✅ **HUMAN REVIEW ACCEPTED**
**Type** : HUMAN REVIEW — docs-only (aucun code touché)
**Date** : 2026-07-14
**Repo** : MFE-DSS/workout-session-tracking
**Branche** : `claude/sprint-reporting-fitness-app-V7Qr6`

---

## 0. Références vérifiées

| Élément | Valeur | Vérifié |
|---|---|---|
| Commit CODE | `901143f` — feat(session-ux): prioritize set console before technical cues | ✅ |
| CI code | run [`29335728163`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/29335728163) — **3/3 success** | ✅ |
| Audit source | `Sx_SESSION_UX_01` (`9925165`), friction F1 (P1) | ✅ |
| Build report | `SPRINT_Sb_SESSION_UX_01_2_ACTIVE_CONSOLE_PRIORITY_BUILD_REPORT.md` | ✅ |
| Working tree | **clean** | ✅ |

---

## 1. CI code `901143f` — 3/3 success (source de vérité)

| Job CI | Résultat |
|---|---|
| **pytest + QA scripts** | ✅ **success** |
| **lint** (ruff budget + bandit + actionlint + shellcheck) | ✅ **success** |
| **SonarCloud** | ✅ **success** |

- **Aucun timeout** : job pytest sous `timeout-minutes: 45` (aucun job `cancelled`).

---

## 2. Périmètre du commit CODE `901143f` (preuve)

Fichiers touchés (5) : `app/templates/_partials/exercise_card.html` ·
`tests/test_session_ux_console_priority.py` (nouveau) · build report + `SPEC_REGISTRY.md` +
`ROADMAP_AND_NEXT_STEPS.md`.

**Aucun** `app/routers/**`, `app/services/**`, `app/models/**`, `data/**`, `migrations/**`,
`schema_snapshot`, `app/static/js/**`, `.github/**`, `deploy/**`, **ni CSS** (`session_focus.css`
intact). Vérifié par grep sur `git show 901143f`.

---

## 3. Surface acceptée (revue fonctionnelle)

### 3.1 Réordonnancement carte active
- **Console de saisie déplacée AVANT les cues techniques** : les cues (bloc toujours-visible qui
  repoussait la saisie) sont **descendues après la console**.
- **Ordre livré** : `Intention → Zone travaillée → [machine] → Alternatives (replié) → **Console
  sets** → **Cues techniques** → Ressenti / note / up-next / CTA`.
- **Gain F1** : l'action principale (saisir) n'est plus reléguée sous les cues dépliées.

### 3.2 Choix techniques validés
- **Console partagée active/non-active** → non remontée dans le hero (sinon les cartes non-actives
  perdraient leur console). On **descend les cues** au lieu de remonter la console — **option la
  plus sûre, acceptée**.
- **`_machine` (hero) → `_cues_machine` re-résolu localement** depuis `atlas_data` (présentation,
  aucune logique métier) ; `_machine` orphelin **nettoyé** (pas de code mort).
- **Cues rendues 1 seule fois** (déplacées, pas copiées).

### 3.3 Écart assumé vs brief (documenté)
- **Alternatives NON déplacées** : le drawer `<details>` est **form-critical** (radios
  `substituted_name`, N1/N2/N3) et **replié par défaut** (1 ligne) → déplacement = risque de
  régression disproportionné. Laissé en **dette optionnelle
  `Sb_SESSION_UX_01.2b_alternatives_below_console`**, à rouvrir **si le dogfood le demande**.
  **Accepté par l'opérateur** (décision explicite au GO COMMIT).

---

## 4. Garde-fous — invariants respectés (vérifiés)

| Contrainte | État |
|---|---|
| Aucun router/service/model/data/migration/js touché | ✅ |
| Aucun CSS touché | ✅ (`session_focus.css` intact) |
| Mêmes POST / inputs `set_{id}_weight_kg`/`_reps` | ✅ |
| `value=""` strict · completion dérivée serveur | ✅ |
| Placeholders overload inchangés | ✅ |
| Rappel « dernière » (01.3) sur set actif inchangé | ✅ |
| Bloc « Référence précédente » conservé | ✅ |
| Silhouette BodyMap conservée | ✅ (`test_bodymap_silhouette_preserved`) |
| Alternatives fonctionnelles (radios présents) | ✅ |
| Machine panel · sticky CTA · rest timer intacts | ✅ |
| No-JS | ✅ |
| Body Intelligence OFF · Delt_lat pending capture | ✅ |
| Working tree clean | ✅ |

---

## 5. Tests (rappel build, verts en CI)

- **11** tests dédiés (`test_session_ux_console_priority.py`) : console < cues, worked-area <
  console, cues présentes/uniques, inputs, alternatives (source), sticky CTA, rest timer, silhouette,
  no-JS, pas de `_machine` orphelin.
- **98** non-régression (worked_area/console/ui06/bodymap/prev_load).
- Sweep large build : **516 passed / 0 échec**.
- Suite complète CI : ✅ (job pytest). ruff clean, budget **543 ≤ 548**.
- `check_scope` = ISOLATED → **promu SHARED_CODE** (carte séance active) ; CI réelle confirmée 3/3.

---

## Verdict

**Verdict :** ✅ **Sb_SESSION_UX_01.2 — HUMAN REVIEW ACCEPTED.**

Sur la carte active, la **console de saisie passe désormais avant les cues techniques** (Option A
adaptée : cues descendues après la console, `_cues_machine` re-résolu localement, `_machine`
orphelin nettoyé) — **acté humainement** après **CI verte 3/3** sur `901143f`. **Template only**
(aucun CSS) : routers / services / models / data / migrations / JS **intacts** ; POST / inputs /
`value=""` / completion serveur / placeholders overload / rappel « dernière » (01.3) / « Référence
précédente » / silhouette BodyMap / sticky CTA / rest timer / alternatives **préservés**. **Écart
assumé** : alternatives non déplacées (dette `01.2b`, dogfood-dependent) — accepté opérateur.
Body Intelligence OFF. Delt_lat pending capture. Working tree clean.

**Suites** (aucun code) :
1. **Dogfood F1 + F2 en salle** (recommandé) — 01.2 (console avant cues) + 01.3 (rappel « dernière »)
   sont mergés mais non confirmés terrain ; un seul passage valide les deux.
2. Selon dogfood : rouvrir `01.2b` (alternatives) et/ou F3 (`01.4` scroll).
3. Indépendant : capture irritant #1 (`Delt_lat`).
