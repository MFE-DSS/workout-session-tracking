# Sx_UI_04 Focused Exercise Flow — Final Closeout Report

**Cycle :** `Sx_UI_04_FOCUSED_EXERCISE_FLOW`
**Type :** FINAL CLOSEOUT REVIEW — docs-only
**Date :** 2026-07-07
**Auteur :** opérateur (Martin Feldmann) + agent Claude Code
**Branche :** `claude/sprint-reporting-fitness-app-V7Qr6`
**Verdict :** ✅ **Sx_UI_04 CLOSED — FINAL CLOSEOUT ACCEPTED**

---

## 1. Verdict final

✅ **Sx_UI_04 Focused Exercise Flow est CLÔTURÉ.**

Les 5 sous-sprints (+ le recast spec) ont été livrés, testés en CI complète verte, et acceptés en human review. L'écran séance est passé d'une **liste verticale d'exercices / accordéon / recolor** à un **cockpit d'exécution biomécanique mobile-first**, sans aucun changement backend métier, sans JS ajouté, sans React/SPA/bundler, invariants métier / a11y / no-JS intacts, et baseline P0 capturable (`ok=16`) à chaque étape.

## 2. Executive summary

Le cycle a converti la surface la plus utilisée du produit (le Focus Mode session) vers l'identité Auren (Clinical Lab / Quiet Instrument) **et** vers un nouveau paradigme d'interaction : le **Live Exercise Expert** rendu comme un **active exercise cockpit**. Après la réserve visuelle de Sb_UI_04.2 (« trop proche d'un recolor »), le cycle a été **recadré** (recast spec, brainstorm PO + lead architecte) autour d'un single active exercise flow enrichi de 7 couches (orientation, intent, worked area, cues, logging console, alternatives, up next) et d'une direction transverse **Body Representation System**.

Résultat : une carte active dominante, un mini-stepper compressé, une console de logging instrumentale, un worked area clinique et des alternatives lisibles — le tout en SSR/CSS pur.

## 3. Scope initial vs scope final

| Aspect | Scope initial (Sx_UI_04 reskin spec) | Scope final (recast + builds) |
|---|---|---|
| Nature | Reskin visuel du Focus Mode | Refonte du paradigme d'interaction (cockpit) |
| Topologie | Liste verticale conservée, restylée | Single active exercise flow (carte active dominante) |
| Navigation | Jump bar dense restylée | Mini-stepper compressé secondaire (OQ-B) |
| Logging | Formulaire de lignes restylé | Console d'exécution (active set / ledger / upcoming) |
| Worked area | Non prévu | Surface biomécanique clinique CSS-only (§23) |
| Alternatives | Substitution existante conservée | Surface « Adapter l'exercice » (mécanisme intact) |
| Découpage | 5 sous-sprints (CSS → polish) | 5 sous-sprints recadrés (cockpit → worked area) |

Le scope final **dépasse** le reskin initial : c'est une transformation produit, pas seulement esthétique — motivée par la réserve visuelle de Sb_UI_04.2.

## 4. Timeline des sous-sprints

| # | Sprint | Date | Statut |
|---|---|---|---|
| 1 | Sb_UI_04.1 CSS Foundation | 2026-07-04 | ✅ accepté |
| 2 | Sb_UI_04.2 Header & Jump Bar Structure | 2026-07-04 | ✅ accepté **avec réserve visuelle** |
| — | Recast Focused Exercise Flow Spec (+ Live Expert §18 + Body Representation §23) | 2026-07-04 | ✅ accepté (docs) |
| 3 | Sb_UI_04.3 Active Exercise Cockpit Shell | 2026-07-05 | ✅ accepté pour continuation |
| 4 | Sb_UI_04.4 Set Logging Console + Progression Guidance | 2026-07-06 | ✅ accepté pour continuation |
| 5 | Sb_UI_04.5 Worked Area Visual Slot + Alternatives + Hardening | 2026-07-07 | ✅ accepté |

## 5. Décisions produit consolidées

- **Paradigme** : active exercise cockpit (une carte dominante) remplace la liste verticale.
- **Live Exercise Expert Model** (§18) : 7 couches d'information au bon moment.
- **Body Representation System** (§23) : couche transverse (session card + program preview + profile futur), documentaire, sans modèle.
- **OQ-A → OQ-G tranchées** : mini-stepper cliquable, jump bar compressée, worked area sous le titre, panel statique V1, réouverture autorisée, up-next nom+rôle+zone, overview replié.
- **Visual asset strategy** (§21) : V1 = placeholder/CSS clinique, pas de GIF/pipeline média ; V2/V3 futurs avec fallback obligatoire.
- **Principes pédagogiques** (§22) : 1 décision principale, ≤3 cues, « pourquoi » en 1 phrase, logging < 5 s, progressive disclosure.
- **Rejet explicite** du simple recolor / accordéon pour les builds .3+.

## 6. Transformation UI obtenue

**Avant** (pré-Sx_UI_04) : dark cockpit / orange branding, liste verticale de `<details>`, jump bar dense, formulaire de séries brut.

**Après** (post-Sb_UI_04.5) :
- **Orientation** en tête (X/Y exercices + N restants).
- **Mini-stepper** compressé (ancres préservées, `aria-current="location"` sur l'actif).
- **Carte active hero dominante** ; cartes non-actives en index secondaire (restent dans le DOM).
- **Exercise intent** + **technical cues** (≤3, source atlas).
- **Worked Area Visual Slot** : zone chip atlas réel + body-map CSS-only + pattern + rôles + note anti-médicale.
- **Console de logging** : active set dominant, completed ledger `✓`, upcoming secondaires, reference/target, guidance overload.
- **Up-next** (nom + rôle + zone).
- **Alternatives Surface** : « Adapter l'exercice » (substitution N1/N2/N3 intacte).

Palette Auren (teal chirurgical `#0F8A85`, fond blanc, mono/tabular metrics) appliquée, scoped `.session-focus`.

## 7. Preuves CI consolidées

| Sprint | Commit(s) | Run CI | Conclusion | Notes |
|---|---|---|---|---|
| Sb_UI_04.1 | `4451743` | [`28700626885`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/28700626885) | ✅ SUCCESS | 3/3 jobs |
| Sb_UI_04.2 | `8524851` | [`28702740118`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/28702740118) | ✅ SUCCESS | 3/3 jobs |
| Sb_UI_04.3 | `611cda3` | [`28735809572`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/28735809572) | ✅ SUCCESS | 3/3 jobs |
| Sb_UI_04.4 | build `629262d` + patch `ad1c747` | [`28814745985`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/28814745985) | ✅ SUCCESS | 1705 passed (run initial `28737238524` rouge → Patch A → vert) |
| Sb_UI_04.5 | `6a49c05` | [`28850394732`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/28850394732) | ✅ SUCCESS | 1735 passed |

Ruff budget **542 ≤ 548** maintenu sur tous les builds. Spec protocol OK sur tous les commits docs.

## 8. Preuves visual baseline / after-captures

- **Baseline P0** capturée localement 2026-07-04 : 16/16 PNG (`docs/BASELINE_P0_CAPTURED_2026_07_04.md`), pré-Sx_UI_04.
- **After-captures** à chaque build : `var/visual-after/Sb_UI_04_1/` … `Sb_UI_04_5/`, chacun **ok=16 failed=0**, anti-404 vérifié.
- **Deltas mesurés** (session-detail-active/mobile, proxy byte-size) :
  - baseline → 04.1/04.2 : reskin Auren
  - 04.2 → 04.3 : **+27 %** (bascule cockpit topologique)
  - 04.3 → 04.4 : +9,9 KB (console de logging)
  - 04.4 → 04.5 : +11,4 KB (worked area visual slot + alternatives)
- Screenshots **jamais committés** (`/var/` gitignored), révision humaine locale via Preview.app.

## 9. Invariants préservés

- ✅ FastAPI SSR + Jinja2 only — **React/SPA/bundler interdits** respectés.
- ✅ Aucun changement route / service / model / migration.
- ✅ Aucun JS ajouté (aucun fichier ; `preview.js` + `session_focus.js` inchangés).
- ✅ Macros Jinja (`segmented`, `field_group`) non modifiées.
- ✅ Rest timer non touché ; contrats `data-*` (`data-start-rest`, `data-rest-duration`, `data-rest-skip`, `data-rest-display`) intacts.
- ✅ `overload_hint.html` non modifié (présenté, jamais réécrit).
- ✅ `app.css` non touché (CSS scoped `session_focus.css` uniquement).
- ✅ Logging : inputs `set_*_weight_kg` / `set_*_reps` noms / id / value / action / method **inchangés**.
- ✅ Substitution : radios `substituted_name`, drawer, tiers N1/N2/N3, route/action **inchangés**.
- ✅ Anchors `#exercise-N` + `#session-feedback` préservés ; exercices non-actifs restent dans le DOM.
- ✅ Aucun rebrand SPIGNOS → Auren dans le code (réservé Sx_UI_10).
- ✅ Aucun asset / font / package / PNG ajouté.

## 10. Accessibilité / no-JS / mobile-first

- **No-JS fallback** intact à chaque build (SSR + `<details>` natifs + forms POST).
- **WCAG 44×44** tap targets préservés (stepper, alternatives summary, CTA).
- **Focus visible universel** (outline 2px teal) préservé.
- **`prefers-reduced-motion`** préservé.
- **`aria-current="location"`** sur l'item actif uniquement ; `aria-live="polite"` rest timer intact ; body-map `aria-hidden`.
- **Mobile-first 360×640** : media queries dédiées (orientation, hero, console refs, body-map, pattern) — pas de mur de texte, logging prioritaire.
- **Desktop 1440×900** utilisable, surfaces équilibrées.

## 11. Body Representation System — état V1 et limites

**Livré V1** : Worked Area Visual Slot dans la carte active — zone principale (atlas `family.name`), zone chip (`family.zone`), pattern moteur (`family.description`), body-map décoratif CSS-only, note anti-médicale.

**Limites assumées** :
- Body-map V1 = **surface CSS abstraite**, pas une anatomie réelle (choix délibéré : pas d'asset, pas de claim).
- **Assistants / stabilisation** restent souvent « à qualifier » (aucun muscle inventé sans source).
- Pas de **`body_map_descriptor` persistant** (contrat §23.5 reste documentaire).
- Pas de **profil Body Intelligence** dans ce cycle.
- Pas de **moteur biomécanique réel** ni de calcul d'activation.

## 12. Alternatives / substitution — état V1 et limites

**Livré V1** : surface « Adapter l'exercice » (+ sous-label « Remplacer cet exercice » préservé) autour de la substitution existante Sb_03/Sb_07/Sb_22a (N1/N2/N3, rationales, badges). Rôle explicité (même zone / même pattern).

**Limites** : le mécanisme, les radios `substituted_name`, la route et le form **restent ceux existants** — Sb_UI_04.5 n'a fait qu'améliorer la présentation. Aucune alternative inventée ; si `can_substitute` est faux, rien n'est rendu.

## 13. Logging console — état V1 et limites

**Livré V1** : console d'exécution — header + progression X/Y séries, active set dominant (premier non complété), completed ledger `✓`, upcoming secondaires, reference (previous perf), target (overload placeholder / set_scheme), guidance overload.

**Limites** :
- Reference / target ne s'affichent que si la donnée existe déjà en contexte ; sinon fallback sobre.
- Le bloc legacy `.last-time` coexiste avec la reference console (consolidation possible en polish futur).
- L'active set est dérivé de `sl.completed` (présentation, aucun état backend).

## 14. Risques résiduels

- **Faible.** Builds additifs, scoped, sans logique métier ; suites de tests vertes (jusqu'à 1735 passed en CI finale).
- Risque esthétique : densité des surfaces sur mobile — mitigé par media queries et priorité maintenue à la console de logging.
- Perception finale à confirmer en dogfood device réel (track indépendant, non bloquant pour la clôture spec/CI).

## 15. Dette technique non bloquante

- Consolidation `.last-time` legacy ↔ reference console.
- Qualification assistants/stabilisation via un futur mapping `exercise_code → zones`.
- Warning infra **Node 20 → 24** (annotations GitHub, transverses, non bloquant).
- Warnings locaux **`.vscode`** (`test_v1_acceptance.py` **ignoré en CI** via `--ignore`, échecs uniquement en run local complet — non CI, non bloquant).
- Warning passlib/bcrypt (candidat `Sb_OPS.passlib-bcrypt-compat`, si encore observé).

## 16. Décisions explicitement différées

- **Sx_UI_05 Today / Readiness Home** — next candidate, not opened.
- **Sx_UI_06 Exercise Intelligence Presentation** — future.
- **Contrat `exercise_code → body_map_descriptor`** persistant — future (V2 Body Representation).
- **Profile Body Intelligence** (surface C §23.2) — future.
- **Release tag baseline/preauren** — deferred.
- **Cleanup warnings infra** (Node, `.vscode`, passlib/bcrypt) — si utile, non urgent.

## 17. Go / No-Go final

**GO — CLÔTURE ACCORDÉE.**

Critères remplis :
- ✅ 5/5 sous-sprints livrés et acceptés.
- ✅ CI verte à chaque build final.
- ✅ Baseline P0 capturable à chaque étape (`ok=16`).
- ✅ Aucun screenshot / runtime / DB committé.
- ✅ Aucun changement backend métier.
- ✅ Aucun JS ajouté ; aucun React / SPA / bundler.
- ✅ Routes, services, models, migrations intacts.
- ✅ Logging forms / input names / rest timer `data-*` / substitution route+radios préservés.
- ✅ No-JS fallback intact ; mobile 360×640 maintenu.
- ✅ Transformation perceptive validée (cockpit, mini-stepper, logging console, worked area clinique, alternatives lisibles).

## 18. Prochaine étape recommandée

**`Sx_UI_05 Today / Readiness Home`** — **next candidate, not opened**. Cet écran pourra réutiliser la couche Worked Area / Body Representation (surfaces B/C §23.2) sur le program/session preview et, plus tard, le profil.

Ouverture sur override explicite opérateur uniquement.

## 19. Non-goals confirmés

- ❌ Pas de Body Map complète / anatomie réelle.
- ❌ Pas de modèle / migration / service métier modifié.
- ❌ Pas de calcul biomécanique réel ni recalcul progression / overload.
- ❌ Pas d'asset / image / GIF / SVG / pipeline média.
- ❌ Pas de génération d'image dans l'app.
- ❌ Pas de profil modifié dans ce cycle.
- ❌ Pas de React / SPA / bundler / dépendance front lourde.
- ❌ Pas de rebrand SPIGNOS → Auren dans le code.
- ❌ Pas de diagnostic médical ni claim d'activation.
- ❌ Pas de release tag dans ce closeout.

## 20. Annexes / références

**Specs**
- `docs/strategy/Sx_UI_04_SESSION_FOCUS_RESKIN_SPEC.md` (spec parent)
- `docs/strategy/Sx_UI_04_FOCUSED_EXERCISE_FLOW_SPEC.md` (recast, §18/§20/§21/§22/§23)

**Reports de sprint**
- `docs/SPRINT_Sb_UI_04_1_REPORT.md` + `docs/SPRINT_Sb_UI_04_1_HUMAN_REVIEW_REPORT.md`
- `docs/SPRINT_Sb_UI_04_2_REPORT.md` + `docs/SPRINT_Sb_UI_04_2_HUMAN_REVIEW_REPORT.md`
- `docs/SPRINT_Sx_UI_04_FOCUSED_EXERCISE_FLOW_REPORT.md` + `..._HUMAN_REVIEW_REPORT.md`
- `docs/SPRINT_Sb_UI_04_3_REPORT.md` + `docs/SPRINT_Sb_UI_04_3_HUMAN_REVIEW_REPORT.md`
- `docs/SPRINT_Sb_UI_04_4_REPORT.md` + `docs/SPRINT_Sb_UI_04_4_HUMAN_REVIEW_REPORT.md`
- `docs/SPRINT_Sb_UI_04_5_REPORT.md` + `docs/SPRINT_Sb_UI_04_5_HUMAN_REVIEW_REPORT.md`

**Baseline / tooling**
- `docs/BASELINE_P0_CAPTURED_2026_07_04.md`
- Runtime CLI : `scripts/visual_baseline_runtime.py` (Sb_UI_11.2)

**Gouvernance**
- `docs/strategy/SPEC_REGISTRY.md`
- `docs/strategy/ROADMAP_AND_NEXT_STEPS.md`

---

## Verdict de clôture

✅ **Sx_UI_04 Focused Exercise Flow : CLOSED — FINAL CLOSEOUT ACCEPTED.**

**Sx_UI_05 Today / Readiness Home : next candidate, not opened.**
**Sx_UI_06 Exercise Intelligence Presentation : future.**
**Release tag : deferred.**
