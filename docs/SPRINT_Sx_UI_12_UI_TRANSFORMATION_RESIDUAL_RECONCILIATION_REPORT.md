# Sprint Sx_UI_12 — UI Transformation Residual Reconciliation — REPORT

**Verdict** : ✅ **Sx_UI RESIDUAL QUEUE: READY**
**Type** : AUDIT / RECONCILIATION — docs-only (aucun code/test/asset touché)
**Date** : 2026-07-15
**Baseline** : `9a405a7`
**Spec** : `docs/strategy/Sx_UI_12_UI_TRANSFORMATION_RESIDUAL_RECONCILIATION_SPEC.md`

---

## 1. Baseline Git
HEAD local = origin = `9a405a7`, branche canonique, working tree **clean**, 0/0. Aucun `Sx_UI_12`
préexistant.

## 2. Worktree
Isolé `work/sx-ui-12-residual-reconciliation` sur `9a405a7`. Autres worktrees (sb-body-01, sb-body-02-1,
custom) **non touchés**.

## 3. Collisions
`origin` contrôlé au début + avant écriture ; stable sur `9a405a7`. **Aucune collision.**

## 4. Matrice Sx_UI_01 → 11
Voir spec §2 (matrice complète spec/build/CI/review/dogfood/code réel/verdict). Établie par lecture de
l'**état réel du code** (base.html, app.css, manifest, partials, tests) **+** vérification des commits
build + runs CI, pas seulement des résumés roadmap. Synthèse des verdicts :

| Cycle | Verdict |
|---|---|
| Sx_UI_01 Brand Foundation | PARTIAL — REVIEW REQUIRED (interne clôturable ; OQ-A externe) |
| Sx_UI_02 Design Tokens | **SUPERSEDED** by 02b |
| Sx_UI_02b Auren Terminal | **CLOSED** |
| Sx_UI_03 App Shell / Nav | **PARTIAL — BUILD REQUIRED** (03.1/.2/.3) |
| Sx_UI_04 Focused Exercise Flow | **CLOSED** |
| Sx_UI_05 Today/Readiness Home | PARTIAL — BUILD REQUIRED / largement **ABSORBED by 06.3** |
| Sx_UI_06 Info Density | .1/.2/.3 **CLOSED** ; .4 **NOT OPENED** |
| Sx_UI_07 Readability | **CLOSED** |
| Sx_UI_08 PWA / Auth heads | .1/.2 **CLOSED** ; 08.3 SW **NOT OPENED** |
| Sx_UI_09 Accessibility & Motion | **NOT OPENED** → à ouvrir |
| Sx_UI_10 Auren Visual Migration | **CLOSED** (interne) ; nom/domaine **EXTERNAL BLOCK ONLY** |
| Sx_UI_11 Screenshot Baseline | tooling **CLOSED** ; **Sb_UI_11.3** requis |

## 5. Contradictions roadmap ↔ code
- **Sx_UI_03 (majeure)** : la spec décrit un shell bottom-nav 4 entrées + rail desktop + session active
  intégrée. Le code réel (`base.html:40-68`, `app.css`) = **topbar hamburger 10 entrées**, **pas de bottom
  nav**, **pas de rail**, **active-session en banner persistant**. → 0 % implémenté. (Les tests
  `test_active_navigation_semantics` **codifient les 10 entrées** → à ré-orienter lors du build 03, PAS ici.)
- **Sx_UI_05** : roadmap « ready to be proposed » ; en réalité l'intention Home est **déjà couverte par
  `Sb_UI_06.3`** (Home = cockpit de décision). Pas une contradiction bloquante, mais un **résidu
  largement absorbé**.
- **Sx_UI_09** : listé ⚪ dans la roadmap historique ; **aucune spec écrite**.

## 6. Cycles clos
`Sx_UI_02b` · `Sx_UI_04` · `Sx_UI_07` · `Sx_UI_10` (interne). `Sx_UI_02` = SUPERSEDED (par 02b).

## 7. Cycles partiels
`Sx_UI_01` (review interne manquante) · `Sx_UI_03` (build shell) · `Sx_UI_05` (0 build, absorbé 06.3) ·
`Sx_UI_06` (.4 non ouvert) · `Sx_UI_08` (SW non ouvert) · `Sx_UI_11` (captures/baseline finale).

## 8. Cycles superseded / absorbés
`Sx_UI_02` **SUPERSEDED** by `Sx_UI_02b`. Intention `Sx_UI_05` (Home) **ABSORBED** en grande partie par
`Sb_UI_06.3`. Pack d'icônes PWA « Auren » = livré sous `Sb_UI_10.2` (pas sous `Sx_UI_08`).

## 9. Builds réellement nécessaires
`Sb_UI_03.1` Mobile Bottom Nav · `Sb_UI_03.2` Desktop Rail · `Sb_UI_03.3` Shell Hardening ·
`Sx_UI_09` spec + builds a11y (reduced-motion, form-errors ARIA `aria-live`/`aria-invalid`/`aria-describedby`,
audit contraste `--fg-dim`) · `Sb_UI_11.3` Final Auren Baseline · closeout global.

## 10. Builds à NE PAS faire (par défaut)
- `Sx_UI_05 .2-.5` — Home déjà cockpit (06.3) ; construire **seulement si résidu réel** démontré.
- `Sb_UI_06.4` — **duplication non démontrée** (R7 session_done « à évaluer ») ; preuve requise.
- `Sx_UI_08.3` SW/offline/shortcuts — **absence de SW ≠ dette** (no-JS assumé) ; **décision produit** requise.

## 11. Queue finale
Voir spec §5 (9 lignes ordonnées avec type/dépendance/fichiers/valeur/risque) :
`03.1 → 03.2 → Sx_UI_09 spec → builds 09 → [05R si résidu] → [06.4 si duplication] → 08.3 décision →
11.3 baseline → closeout global`.

## 12. Fichiers docs créés/modifiés
- **créés** : `docs/strategy/Sx_UI_12_..._SPEC.md` + `docs/SPRINT_Sx_UI_12_..._REPORT.md`
- **modifiés** : `SPEC_REGISTRY.md`, `ROADMAP_AND_NEXT_STEPS.md`, `UI_TRANSFORMATION_ROADMAP.md`
  (marquée **HISTORICAL OPENING ROADMAP** pointant vers Sx_UI_12).
- **non touché** : tout `app/**`, `tests/**`, `data/**`.

## 13-16. Hash / FF / push / état final
Renseignés dans la section clôture de ce sprint (voir SPEC_REGISTRY + git). Docs-only, CI skippée
`paths-ignore: docs/**`.

## Non-goals
Aucun code · aucun build lancé · aucune réouverture Sx_UI_10 / gate Auren · aucun résidu conditionnel
construit sans preuve · histoire préservée (roadmap historique conservée, rapports build inchangés).

---

## Verdict

**Verdict :** ✅ **Sx_UI RESIDUAL QUEUE: READY.** Programme substantiellement livré (`02b`/`04`/`07`/`10`
CLOSED ; `02` SUPERSEDED) mais **pas complet** : **shell `Sx_UI_03` non implémenté**, **a11y `Sx_UI_09`
sans spec**, **baseline finale `Sb_UI_11.3`** à capturer. Résidu **à ne pas construire par défaut** :
`05.2-.5` (absorbé 06.3), `06.4` (duplication non démontrée), `08.3` (décision, pas dette). Gate
nom/domaine Auren = **EXTERNAL BLOCK ONLY**. Queue minimale établie (§5).

**Prochain prompt exact** (non commencé) : **`GO BUILD — Sb_UI_03.1 Mobile Bottom Navigation`**.
