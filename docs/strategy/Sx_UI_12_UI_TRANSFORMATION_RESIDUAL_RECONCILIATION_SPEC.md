# Sx_UI_12 — UI Transformation Residual Reconciliation & Final Build Queue — SPEC

**Type** : SPEC / AUDIT / RECONCILIATION ONLY — **NO CODE**, docs-only
**Statut** : ✅ **SPEC RÉDIGÉE** — source actuelle de vérité du programme `Sx_UI`
**Date** : 2026-07-15
**Baseline auditée** : `9a405a7`
**Remplace comme source vivante** : `UI_TRANSFORMATION_ROADMAP.md` (marquée **HISTORICAL OPENING ROADMAP**)

> Réconciliation finale du programme `Sx_UI_01 → Sx_UI_11` : ce qui est **réellement clos**, **partiel**,
> **superseded/absorbé**, **encore nécessaire**, **à ne plus construire**, et la **build queue résiduelle
> minimale** pour clôturer la transformation UI. **Aucun fichier applicatif touché.** Vérité établie par
> lecture de l'état **réel du code** (pas seulement des specs) + statut CI/review réel des commits.

---

## 0. Étape 0 — Brainstorming / Options / Risques / Choix retenu

### 0.1 Options
| Option | Description | Verdict |
|---|---|---|
| **A** | Réconciliation docs-only + queue résiduelle minimale + roadmap historique pointant vers Sx_UI_12 | ✅ **RETENU** |
| B | Déclarer le programme UI « complet » | ❌ faux : shell Sx_UI_03 non implémenté, a11y non specifiée |
| C | Rouvrir/relancer tous les cycles partiels en masse | ❌ overbuild ; certains résidus ne doivent PAS être construits |
| D | Ouvrir directement les builds sans spec de réconciliation | ❌ perte de traçabilité ; on ne saurait plus ce qui est absorbé/superseded |

### 0.2 Principe directeur
**« Human review acceptée ≠ build livré. »** Une spec `SPEC ACCEPTED` sans commit de build = **PARTIAL —
BUILD REQUIRED**, jamais CLOSED. La matrice §2 distingue systématiquement spec / build / CI / review /
état code réel.

### 0.3 Risques
| Risque | Parade |
|---|---|
| Déduire CLOSED d'une spec seule | vérifier l'état **réel du code** + commits CI (fait, §2) |
| Overbuild (05.2-.5, 06.4 sans preuve) | ne recommander que le résidu **démontré** (§3/§4) |
| Réécrire l'histoire | roadmap historique **conservée**, marquée HISTORICAL ; rapports build inchangés |
| Confondre absence de SW avec dette | no-JS assumé ; SW/offline = **décision explicite**, pas dette (§08) |

---

## 1. Canon d'état
- `CLOSED` : spec (si applicable) + build + CI verte + review, ou closeout formel.
- `PARTIAL — BUILD REQUIRED` : spec acceptée, build non fait (ou incomplet).
- `PARTIAL — REVIEW REQUIRED` : build/spec livré, human review formelle manquante.
- `SUPERSEDED` / `ABSORBED BY LATER SPRINT` : intention reprise/remplacée par un cycle ultérieur.
- `DOGFOOD PENDING` · `EXTERNAL BLOCK ONLY` · `NOT OPENED` · `NO LONGER RELEVANT`.

## 2. Matrice de réconciliation Sx_UI_01 → 11

| Cycle | Spec | Builds | CI | Human review | Dogfood | État code réel | Verdict |
|---|---|---|---|---|---|---|---|
| **Sx_UI_01** Brand Foundation | ✅ livrée (`Sx_UI_01_BRAND_FOUNDATION_SPEC`) | — (docs) | — | ⚠️ « READY FOR HUMAN REVIEW », **pas de review report distinct** | — | canon Auren posé (appliqué par 02b/10) | **PARTIAL — REVIEW REQUIRED** (volet interne clôturable ; OQ-A = gate externe séparé) |
| **Sx_UI_02** Design Tokens | ✅ SPEC ACCEPTED | — | — | ✅ (`SPRINT_Sx_UI_02_HUMAN_REVIEW_REPORT`) | — | **amendée par 02b** (tokens Auren Terminal) | **SUPERSEDED** by Sx_UI_02b |
| **Sx_UI_02b** Auren Terminal | ✅ ACCEPTED (`805f58b`) | ✅ | ✅ | ✅ | — | design system graphite/mono/ambre en place (`app.css`) | **CLOSED** (FINAL CLOSEOUT ACCEPTED) |
| **Sx_UI_03** App Shell / Navigation | ✅ SPEC ACCEPTED | ❌ **aucun** | — | ✅ (spec) | — | **shell NON implémenté** : topbar hamburger 10 entrées, **pas de bottom nav**, **pas de rail desktop**, active-session = banner persistant | **PARTIAL — BUILD REQUIRED** (03.1/03.2/03.3) |
| **Sx_UI_04** Focused Exercise Flow | ✅ ACCEPTED | ✅ .1–.5 | ✅ | ✅ | ✅ (DOGFOOD_SESSION_ACTIVE) | cockpit séance livré (`session_detail`) | **CLOSED** (FINAL CLOSEOUT) |
| **Sx_UI_05** Today/Readiness Home | ✅ SPEC ACCEPTED (`0d4be33`/`b0ff372`) | ❌ **0 lot** | — | ✅ (spec) | — | Home densifié **par 06.3** (cockpit décision) | **PARTIAL — BUILD REQUIRED** si résidu réel ; intention largement **ABSORBED BY Sx_UI_06.3** |
| **Sx_UI_06** Info Density/Dedup | ✅ SPEC ACCEPTED | ✅ .1/.2/.3 | ✅ 3/3 | ✅ ×3 | — | carte/worked-area/home dé-densifiés | **PARTIAL** : .1/.2/.3 **CLOSED** ; **.4 NOT OPENED** (duplication non démontrée) |
| **Sx_UI_07** Readability | (specs directes) | ✅ .1/.2/.3/.4 | ✅ 3/3 | ✅ + closeout | — | progress/history/library/launcher/template detail lisibilisés | **CLOSED** (cycle closeout) |
| **Sx_UI_08** PWA / Auth heads | (approche directe) | ✅ .1/.2 | ✅ 3/3 | ✅ ×2 | — | manifest baseline + heads publics alignés | **PARTIAL** : .1/.2 **CLOSED** ; **08.3 SW/offline NOT OPENED** (décision, pas dette) |
| **Sx_UI_09** Accessibility & Motion | ❌ **pas de spec** (⚪ roadmap) | ❌ | — | — | — | fort (nav/labels/landmarks/tap 44px/aria-current/no-JS) ; **gaps** : reduced-motion incomplet, form-errors sans `aria-live`, contraste `--fg-dim` non audité | **NOT OPENED** → **à OUVRIR** |
| **Sx_UI_10** Auren Visual Migration | ✅ | ✅ .1/.2/.3/.4/.4b + gate .2a | ✅ 3/3 ×5 | ✅ ×5 + closeout | — | rebrand visible complet + pack PWA | **CLOSED** (interne) ; clearance nom/domaine = **EXTERNAL BLOCK ONLY** (`BLOCKED FOR PROFESSIONAL CLEARANCE`) |
| **Sx_UI_11** Screenshot Baseline | ✅ SPEC ACCEPTED | ✅ tooling .1/.2 | ✅ | ✅ ×2 | — | outillage prêt ; **captures P0 non committées** ; pas de baseline finale post-Auren | **PARTIAL** : tooling **CLOSED** ; **Sb_UI_11.3 Final Auren Baseline** requis |

## 3. Cycles clos (ne rien reconstruire)
`Sx_UI_02b`, `Sx_UI_04`, `Sx_UI_07`, `Sx_UI_10` (interne). `Sx_UI_02` = **SUPERSEDED** par 02b (pas une omission).

## 4. Résidu réellement nécessaire vs à NE PAS construire

### 4.A — Nécessaire (build requis)
- **Sb_UI_03.1 Mobile Bottom Navigation** — le shell mobile n'existe pas ; friction structurelle réelle.
- **Sb_UI_03.2 Desktop Rail / Secondary Navigation** — aucune disposition desktop dédiée.
- **Sb_UI_03.3 Shell Hardening** — rétrograder les entrées secondaires + intégrer session active (pattern spec) + a11y shell.
- **Sx_UI_09 Accessibility & Motion (spec)** puis **builds** — gaps réels (reduced-motion, form-errors ARIA, contraste dim).
- **Sb_UI_11.3 Final Auren Baseline Refresh** — capturer la baseline visuelle **après** le rebrand Auren.
- **Sx_UI Global Final Closeout** — clore le programme une fois le résidu ci-dessus traité.

### 4.B — À NE PAS construire sans preuve / décision
- **Sx_UI_05 .2–.5** : le Home est déjà un cockpit de décision (via 06.3). Ne construire un `Sx_UI_05R Home Completion` **que si un résidu réel** est démontré (sinon : intention ABSORBED). `05.1` reste *ready-to-propose*, non prioritaire.
- **Sb_UI_06.4 Secondary Screens Dedup** : **duplication non démontrée** (R7 session_done « modéré, à évaluer »). Ouvrir **uniquement** si un doublon concret est observé (dogfood/audit ciblé).
- **Sx_UI_08.3 PWA Maturity (SW/offline/shortcuts)** : l'absence de service worker **n'est pas une dette** (no-JS assumé). Ouvrir seulement après **décision produit explicite** (`Sx_UI_08.3 PWA Maturity Decision` = décision, pas build imposé).

## 5. Build queue résiduelle finale (ordonnée, minimale)

| Ordre | Sprint | Type | Dépendance | Fichiers probables | Valeur | Risque |
|---|---|---|---|---|---|---|
| 1 | **Sb_UI_03.1** Mobile Bottom Nav | build (template+CSS) | Sx_UI_11 baseline (ou dérogation) | `base.html`, `app.css`, tests nav | haute (UX mobile core) | moyen (tests nav à ré-orienter) |
| 2 | **Sb_UI_03.2** Desktop Rail/Secondary | build (template+CSS) | 03.1 | `base.html`, `app.css` | moyenne | faible/moyen |
| 3 | **Sx_UI_09** Accessibility & Motion **spec** | spec docs-only | — | `Sx_UI_09_*_SPEC.md` | haute (verrouille WCAG AA) | faible |
| 4 | **Builds Sx_UI_09** (03.3 a11y inclus) | build (CSS+template) | Sx_UI_09 spec | `app.css`, partials forms, `base.html` | haute | faible/moyen |
| 5 | **Sx_UI_05R** Home Completion | build | **seulement si résidu réel** | `index.html`, `home.css` | conditionnelle | faible |
| 6 | **Sb_UI_06.4** Secondary Screens Dedup | build | **seulement si duplication démontrée** | `session_done`, partials | conditionnelle | faible |
| 7 | **Sx_UI_08.3** PWA Maturity **Decision** | décision docs + build opt. | décision produit | `manifest`, éventuel SW | conditionnelle | moyen (SW = surface nouvelle) |
| 8 | **Sb_UI_11.3** Final Auren Baseline Refresh | ops (captures) | rebrand Auren clos ✅ | tooling `Sx_UI_11` (local, `.gitignore`) | moyenne | faible |
| 9 | **Sx_UI Global Final Closeout** | docs closeout | 1–8 traités | docs | clôture | faible |

*Note : `Sb_UI_03.3 Shell Hardening` peut être fusionné dans les builds Sx_UI_09 (ordre 4) ou joué en 2bis — c'est une décision d'ordonnancement au moment du build, pas un blocage.*

## 6. Non-goals
- ❌ Aucun code / `app/**` / `tests/**` / `static/**` / CSS modifié dans ce cycle.
- ❌ Aucun renommage code/repo/package/route/model/table (canon Sx_UI_10 préservé).
- ❌ Aucune réouverture de `Sx_UI_10` (interne CLOSED) ni du gate Auren juridique (EXTERNAL BLOCK, déjà audité).
- ❌ Aucun build lancé ici (les builds de la queue §5 exigent un GO explicite ultérieur).
- ❌ Aucune construction de `05.2-.5`, `06.4`, `08.3` **par défaut** (résidu conditionnel, preuve requise).
- ❌ Aucun PASS/ACCEPTED sur le dogfood `Sb_SESSION_UX_01.5` (reste FIELD TEST READY).
- ❌ Aucune réécriture des rapports build historiques ni de la roadmap d'ouverture (marquée HISTORICAL).

## Non-goals (rappel structurel)
Aucun code · aucun renommage interne · aucune réouverture Sx_UI_10 / gate Auren · aucun build par défaut ·
aucun résidu conditionnel construit sans preuve · dogfood 01.5 non conclu · histoire préservée.

## Verdict

**Verdict :** ✅ **Sx_UI RESIDUAL QUEUE: READY.** Le programme `Sx_UI_01→11` est **substantiellement livré**
(`02b`/`04`/`07`/`10`-interne **CLOSED** ; `02` **SUPERSEDED** par `02b`) mais **pas complet** : le **shell
de navigation `Sx_UI_03` n'est pas implémenté** (topbar 10 entrées, ni bottom nav ni rail desktop, session
active en banner), l'**accessibilité `Sx_UI_09` n'a pas de spec** (gaps reduced-motion / form-errors ARIA /
contraste dim), et la **baseline visuelle finale post-Auren `Sb_UI_11.3`** reste à capturer. Résidu **à ne
PAS construire par défaut** : `Sx_UI_05 .2-.5` (Home déjà couvert par `06.3`), `Sb_UI_06.4` (duplication non
démontrée), `Sx_UI_08.3` SW/offline (décision produit, pas dette). Le gate nom/domaine **Auren** reste
**EXTERNAL BLOCK ONLY**. **Queue finale minimale** (§5) : `03.1 → 03.2 → Sx_UI_09 spec → builds 09 →
[05R si résidu] → [06.4 si duplication] → 08.3 décision → 11.3 baseline → closeout global`.

**Prochain prompt exact (non commencé)** : `GO BUILD — Sb_UI_03.1 Mobile Bottom Navigation`.
