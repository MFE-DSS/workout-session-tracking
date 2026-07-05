# SPIGNOS — Roadmap & Next Steps (Reference Document)

**Auteur :** opérateur SPIGNOS + Claude Code (Opus 4.7).
**Créé :** 2026-06-15 (post-clôture technique Sx_27).
**Statut :** **document de référence vivant** — à relire à chaque reprise de session pour savoir quoi prompter ensuite.
**Source de vérité officielle :** `docs/strategy/SPEC_REGISTRY.md` (la table des sprints livrés). Ce document est la **lecture éditoriale** par-dessus.

---

## 1. Position actuelle (verrouillée)

| Item | Valeur |
|---|---|
| Sx_26 — Engineering Control Plane | ✅ clôturé 2026-06-14 (cf. `Sx_26_CLOSURE_REPORT.md`) |
| Sx_27 — Coaching Loop & Product Activation | ✅ **technically closed** 2026-06-15 (cf. `Sx_27_CLOSURE_REPORT.md`) |
| Sx_28 — Product Roadmap Reconciliation | ✅ **SPEC AMENDED** sous override humain 2026-06-15 (cf. `Sx_28_PRODUCT_ROADMAP_RECONCILIATION_SPEC.md`) |
| Sx_29 — Mobile Session Focus Mode & Visual Interaction Layer | ✅ **TECHNICALLY CLOSED + DOGFOOD ✅ PASS** 2026-06-16 |
| Sx_30 — Progressive Overload Engine | ✅ **TECHNICALLY CLOSED** 2026-06-27 (Sb_30.0 → Sb_30.5 livrés, cf. `Sx_30_CLOSURE_REPORT.md`) — dogfood device réel pending (cf. `dogfood/DOGFOOD_Sx_30_OVERLOAD_ENGINE_TEMPLATE.md`) |
| Sx_31 — Body Intelligence v2 | ✅ **TECHNICALLY CLOSED** 2026-06-28 (Sx_31 spec + Sb_31.1 → Sb_31.5 livrés, cf. `Sx_31_CLOSURE_REPORT.md`) — dogfood device réel pending (cf. `dogfood/DOGFOOD_Sx_31_BODY_INTELLIGENCE_TEMPLATE.md`) |
| Product validation Sx_27 | ⏳ **pending real dogfood** (cf. `docs/dogfood/DOGFOOD_Sx_27_DEFERRED.md`) — non simulé, peut reverser Option A si livré plus tard |
| Product validation Sx_29 | ✅ **dogfood PASS** 2026-06-16 |
| Product validation Sx_30 | ⏳ **pending real dogfood** sur ≥ 2 semaines d'usage réel — track indépendant |
| Product validation Sx_31 | ⏳ **pending real dogfood** sur ≥ 2 semaines / ≥ 4 consultations `/body/intelligence` + ≥ 2 `/coach-report` — bloque ouverture automatique de Sx_32/33+ |
| Build authorization | ✅ Override #4 (Sx_31 Body Intelligence v2) **consommée** par Sx_31 closed 2026-06-28. `Sb_31.next.profile-link` (OQ-G) livré 2026-06-29 sous override séparé. Aucune nouvelle option de cycle autorisée : Sx_32/33+ restent bloquées (override séparé requis pour chacune). Sprints `Sb_31.next.home-card` / `Sb_31.next.overload-compliance` candidats discrétionnaires post-dogfood. |
| Dernier CI run vert | [28454376953](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/28454376953) (PR #21 Sb_Body_02.1 Capture Quality Shell) — 3/3 jobs verts |
| Tests | 122 tests critiques (Sx_30 bugfix + Sx_31 body + shell 02.1) verts localement sur HEAD `1e4cd4c` |
| Dogfood Sx_30 | ✅ PASS 2026-07-01 (`docs/dogfood/DOGFOOD_Sx_30_OVERLOAD_ENGINE_REPORT.md`) — engine v1 validé, bug identity guard non reproduit |
| Prod stabilization gate | ✅ **SIGNÉ** 2026-07-02 — verdict `PROD STRUCTURALLY STABLE FOR UI RENOVATION` (`docs/OPS_PROD_STABILIZATION_PROFILE_BODY_COACH_REPORT.md` §10, commit `ddd476b`). SHA `1e4cd4c` live via run [28527679621](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/28527679621), tag `deploy/prod/2026-07-01-1511-1e4cd4c`. `BODY_INTELLIGENCE_ENABLED=true` en prod. Smoke structurel externe vert (S1-S5 + S8 + S9). |
| Mini-gate `PROD_DOGFOOD_57KG_LIVE_CHECK` | ⏳ **pending** — DB prod initialement vide au signage, test live-data différé après premières séances réelles. Ne bloque pas UI renovation. Annexe D du rapport OPS. |
| UI renovation | 🔓 **DÉBLOQUÉE avec caveat** — cycle `Sx_UI` ouvert (cf. `docs/strategy/UI_TRANSFORMATION_ROADMAP.md` + `SPEC_REGISTRY.md §1quinquies`). Rebrand cible **Auren** documenté, aucun renommage code avant `Sx_UI_10`. Mini-gate 57 kg à jouer en parallèle après données réelles. |
| Sx_UI_01 Brand Foundation | 🟢 **SPEC delivered 2026-07-02 — pending human review** (`docs/strategy/Sx_UI_01_BRAND_FOUNDATION_SPEC.md` + `docs/SPRINT_Sx_UI_01_REPORT.md`). Auren = working brand candidate, due diligence juridique/domaine pending (OQ-A). Aucun code UI n'est autorisé avant `Sx_UI_04`. Baseline `Sx_UI_11` (screenshots) est requise avant `Sx_UI_04`. |
| Sx_UI_02 Design Tokens | ✅ **SPEC ACCEPTED 2026-07-02 — human reviewed** (`docs/strategy/Sx_UI_02_DESIGN_TOKENS_SPEC.md` + `docs/SPRINT_Sx_UI_02_REPORT.md` + `docs/SPRINT_Sx_UI_02_HUMAN_REVIEW_REPORT.md`). Accent principal = **teal chirurgical désaturé**, fallback = bleu minéral. Orange SPIGNOS `#f25f3a` exclu. OQ-B tranché. Aucun token implémenté, aucun CSS. Dark mode hors-scope V1. |
| Sb_OPS.ci-path-filter | ✅ **DELIVERED 2026-07-02** (commit `a9ab10c`, CI run `28582551168` ✅ success). Validé en conditions réelles au push Sx_UI_02 `b4ed2c6` : aucun run CI déclenché. `paths-ignore: ['docs/**']` sur trigger `push`. Économie CI ~90% sur les 9 specs Sx_UI docs-only restantes. `pull_request` et `deploy-production.yml` non affectés. |
| Sx_UI_03 App Shell Navigation | ✅ **SPEC ACCEPTED 2026-07-02 — human reviewed** (`docs/strategy/Sx_UI_03_APP_SHELL_NAVIGATION_SPEC.md` + `docs/SPRINT_Sx_UI_03_REPORT.md` + `docs/SPRINT_Sx_UI_03_HUMAN_REVIEW_REPORT.md`). Bottom nav V1 = 4 entrées (Séance / Programmes / Progression / Profil). Coach contextualisé, Squads/Classement dans Profil, Historique/Physique sous Progression. Desktop = rail latéral gauche. Session active = bloc dominant Today + point teal bottom nav. 10 OQ résolues V1. OQ-R (sous-nav Progression) reste pending pour Sx_UI_04. |
| Sx_UI_11 Screenshot Regression Baseline | ✅ **SPEC ACCEPTED 2026-07-02 — human reviewed** (`docs/strategy/Sx_UI_11_SCREENSHOT_REGRESSION_BASELINE_SPEC.md` + `docs/SPRINT_Sx_UI_11_REPORT.md` + `docs/SPRINT_Sx_UI_11_HUMAN_REVIEW_REPORT.md`). Playwright Python binding confirmé. Matrice 18 écrans × 2 viewports (P0=14 obligatoires avant premier build visuel sauf dérogation, P1=16, P2=6). Fixture DB locale déterministe, jamais prod. Règle anti-secret hard. Revue humaine primaire. Storage V1 = artefacts CI + release tag, baseline locale gitignored. 8 OQ résolues V1. **Aucun Playwright installé, aucun screenshot capturé, aucun script écrit.** Choix opérateur : **Option A — ouvrir Sx_UI_04 SPEC ONLY** ensuite. Sb_UI_11.1 reste candidat futur non-ouvert. |
| Sx_UI_04 Session Focus Reskin | ✅ **SPEC ACCEPTED 2026-07-02 — human reviewed** (`docs/strategy/Sx_UI_04_SESSION_FOCUS_RESKIN_SPEC.md` + `docs/SPRINT_Sx_UI_04_REPORT.md` + `docs/SPRINT_Sx_UI_04_HUMAN_REVIEW_REPORT.md`). Périmètre reskin verrouillé (7 fichiers autorisés au futur build). Invariants métier verrouillés (services, routes, models, migrations intacts). Bottom nav visible mais discrète pendant focus mode (Option V1a). Build plan 5 sous-sprints séquentiels. 9 OQ tranchées V1, OQ-H hex pending merge `Sb_UI_04.1`. Choix opérateur : **Option A — ouvrir Sb_UI_11.1 BUILD** ensuite. **Arender dérogation baseline accordée.** |
| Sb_UI_11.1 Screenshot Tooling Build | ✅ **ACCEPTED 2026-07-02 — CI GREEN + human reviewed** (`docs/SPRINT_Sb_UI_11_1_SCREENSHOT_TOOLING_BUILD_REPORT.md` + `docs/SPRINT_Sb_UI_11_1_HUMAN_REVIEW_REPORT.md`). Commit `e8ba190`, CI run [`28595637219`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/28595637219) 3/3 jobs verts (lint 44s / pytest+QA 20min / SonarCloud 1min). Gitleaks / bandit / ruff / pip-audit / spec protocol tous PASS. Matrice P0/P1/P2, CLI Playwright + dry-run + strict-p0 + anti-secret hard, 92 tests unitaires, extra dep `[baseline]` optionnel. **Aucun app code touché. Aucun screenshot committé. Aucun compte prod utilisé. Aucun Chromium installé en CI.** |
| Sb_UI_11.2 Baseline Runtime Integration Patch | ✅ **ACCEPTED 2026-07-02 — CI GREEN + human reviewed** (`docs/SPRINT_Sb_UI_11_2_BASELINE_RUNTIME_PATCH_REPORT.md` + `docs/SPRINT_Sb_UI_11_2_HUMAN_REVIEW_REPORT.md`). Commit `a2846a2`, CI run [`28604484292`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/28604484292) 3/3 jobs verts. |
| **Baseline P0** | ✅ **CAPTURED locally 2026-07-04** — **16/16 PNG** (`docs/BASELINE_P0_CAPTURED_2026_07_04.md`) via Sb_UI_11.2 runtime CLI, ok=16 failed=0. |
| Sb_UI_04.1 CSS Foundation Build | ✅ **ACCEPTED** 2026-07-04 (commit `4451743`, CI [`28700626885`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/28700626885) ✅). Verdict visuel PASS. |
| Sb_UI_04.2 Header & Jump Bar Structure | ✅ **ACCEPTED WITH VISUAL DEPTH RESERVATION** 2026-07-04 (commit `8524851`, CI [`28702740118`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/28702740118) ✅ 3/3 jobs, ruff 542 ≤ 548, 106 tests session focus + 145 tests visual baseline verts). After-capture locale 16/16 ok=16 failed=0. Verdict opérateur : **PASS avec réserve** — écrans fonctionnels, aucune casse, mais transformation perçue trop superficielle (proche recolor / polish léger). Réserve visuelle transférée à `Sb_UI_04.3` comme charte d'ouverture : profondeur visuelle réelle exigée (refonte exercise cards, hiérarchie set logging / hint overload, séparation input/feedback/progression, visual grammar plus marquée, **logique métier intacte**). Report : `docs/SPRINT_Sb_UI_04_2_HUMAN_REVIEW_REPORT.md`. |
| Sx_UI_04 Focused Exercise Flow (RECAST SPEC) | ✅ **HUMAN REVIEW ACCEPTED** 2026-07-04 (commit `996c0c3`, `docs/SPRINT_Sx_UI_04_FOCUSED_EXERCISE_FLOW_HUMAN_REVIEW_REPORT.md` + `docs/strategy/Sx_UI_04_FOCUSED_EXERCISE_FLOW_SPEC.md` + `docs/SPRINT_Sx_UI_04_FOCUSED_EXERCISE_FLOW_REPORT.md`). OQ-A → OQ-G confirmées. Recadrage produit suite à la réserve visuelle Sb_UI_04.2 : passage d'une **liste verticale** à un **active exercise cockpit** (Live Exercise Expert Model §18). **7 couches** : orientation (X/Y · restants · progression · set courant) · exercise intent (pourquoi maintenant / rôle split) · worked area (zone principale / assistants / stabilisation) · technical cues (≤3 visibles) · set logging console (previous perf + target) · alternatives/substitution (surface) · up next (nom + rôle + zone). 7 OQ **tranchées direction produit** (§19 : mini-stepper cliquable · jump bar compressée · worked area sous titre · panel statique V1 · réouverture autorisée · up-next nom+rôle+zone · overview replié). Visual asset strategy §21 : pas de GIF/génération V1, placeholder clinique, contrat futur `exercise_code → primary_zone → asset_key`. Principes pédagogiques §22 (logging < 5 s · progressive disclosure). **Amendement final §23 — Body Representation System** : couche transverse (session card + program preview + profile body intelligence), taxonomie V1 (15 zones), rôles biomécaniques, contrat futur `exercise_code → body_map_descriptor`, visuel V1→V3, prudence anti-médical — **documentaire uniquement** (aucun modèle/migration/service/asset). Worked Area Panel de Sb_UI_04.3 = premier jalon ; profil/body intelligence = direction future. **Simple recolor / accordéon explicitement rejeté.** Invariants métier intacts. Spec parent conservée. |
| Sb_UI_04.3 Active Exercise Cockpit Shell | ✅ **DELIVERED + CI GREEN + HUMAN REVIEW ACCEPTED FOR CONTINUATION** 2026-07-05 (commit `611cda3`, CI [`28735809572`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/28735809572) ✅ 3/3, `docs/SPRINT_Sb_UI_04_3_HUMAN_REVIEW_REPORT.md`). Cockpit wrapper + orientation (X/Y + N restants) + mini-stepper compressé (OQ-B) + carte active hero dominante (cartes non-actives en index secondaire) + Worked Area Panel (zone principale = atlas family réelle, note anti-médicale) + exercise intent + technical cues (max 3) + up-next enrichi zone (OQ-F). SSR/CSS pur, aucun JS, invariants métier/a11y préservés. 285 tests focus/visual + 34 cockpit verts ; after-capture 16/16 (delta +27% session-detail-active). Verdict : **rupture topologique validée, profondeur interactionnelle logging/progression à construire en `.4`**. |
| Sb_UI_04.4 Set Logging Console + Progression Guidance | 🟡 **READY TO BE PROPOSED, not opened** 2026-07-05. Saisie sets instrumentale (console) + previous perf + target range + présentation hint overload + flow exercice suivant. Aucune logique métier touchée. |
| Sb_UI_04.5 Worked Area Visual Slot + Alternatives + Hardening | ⏸️ **BLOCKED until .4 delivered and reviewed**. Enrichissement visuel muscle/zone + surface alternatives + polish + **préparation du futur Body Map System** (contrat §23.5 prêt à brancher). |
| **Prochaine action** | Sb_UI_04.3 **accepté pour continuation** ✅. **Ouvrir `Sb_UI_04.4 Set Logging Console + Progression Guidance` SPEC-then-BUILD** sur override explicite opérateur (console de saisie instrumentale, previous perf, target range, présentation hint overload — profondeur interactionnelle). Options différables : release tag baseline preauren, mini-gate 57 kg, cleanup warning bcrypt. |
| Ruff budget | **534 ≤ 548** |
| Architecture | FastAPI SSR + Jinja2 + SQLite (inchangée) — **React production INTERDIT dans Sx_29** |

> ⚠️ **Note double override 2026-06-15** :
> 1. Override #1 (matin) : ouverture Sx_28 en SPEC ONLY sans dogfood reçu.
> 2. Override #2 (sprint `Sb_28.override-build-authorization`, après-midi) : bascule `BUILD AUTHORIZED FOR OPTION A` sans attendre le dogfood.
>
> **Le dogfood Sx_27 reste PENDING** : il n'est ni simulé, ni considéré acquis. Son arrivée future peut **reverser** Option A si elle révèle qu'une autre friction est prioritaire (cf. Sx_28 §15.2).
>
> **Limites strictes de l'override #2** (verbatim Sx_28 §20) :
> - Option A uniquement (Sx_29 Mobile Session Focus Mode)
> - Options B/C/D/E restent bloquées (override séparé requis)
> - FastAPI SSR + Jinja2 conservé ; React production INTERDIT dans Sx_29
> - Lab React exploratoire acceptable séparément, jamais dans le build principal Sx_29
> - Hard contracts Sx_26/Sx_27 inchangés
> - Sx_29 doit produire sa spec d'abord (SPEC ONLY), comme tout cycle Sx_

## 2. Protocole spec-driven — règle d'or

> **On ne développe plus de nouveau cycle produit tant que la boucle livrée n'a pas été vécue en conditions réelles.**

`docs/strategy/SPEC_DRIVEN_ENGINEERING_PROTOCOL_v1.md §9` (dogfooding) : *"Pas de dogfood report ⇒ pas de cycle suivant."*

Conséquences directes :
- **Ne PAS ouvrir Sx_28** avant `Sb_27.dogfood-1`.
- **Ne PAS ouvrir un nouveau Sx_** sur la base d'hypothèses produit non vérifiées.
- L'ancienne roadmap historique S0→S10 (cf. `SPIGNOS_EXERCISE_SYSTEM_ROADMAP.md`, daté 2026-04-14) **n'est plus la source de vérité** — elle a été partiellement absorbée par les cycles Sx_24 / Sx_26 / Sx_27 (cf. §4).

## 3. Roadmap réelle (post-réconciliation + post-override #2 2026-06-15)

```
   ┌──────────────────────────┐
   │  Sb_27.dogfood-1         │  ⏳ PENDING — peut arriver et reverser
   │  Real Product Dogfood    │     Option A si friction différente révélée
   └──────────────┬───────────┘
                  │ (parallèle, non bloquant après override #2)
                  ▼
   ┌──────────────────────────┐
   │  Sx_28 SPEC AMENDED ✅   │  Override #1: spec only sans dogfood
   │  + Sb_28.override-       │  Override #2: BUILD AUTHORIZED Option A
   │    build-authorization   │  Options B/C/D/E restent BLOQUÉES
   └──────────────┬───────────┘
                  │
                  ▼
   ┌──────────────────────────┐
   │  Sx_29 — Mobile Session  │  ✅ AUTORISÉ par override #2
   │  Focus Mode / Visual     │  📋 SPEC ONLY d'abord (protocole §4)
   │  Interaction Layer       │  🔒 FastAPI SSR + Jinja2 ; React INTERDIT
   └──────────────┬───────────┘
                  │
                  ▼
       ┌──────────────────────────────┐
       │ 🔴 Sx_30 (Overload)          │  Override séparé requis
       │ 🔴 Sx_31 (Body v2)           │  Override séparé requis
       │ 🔴 Sx_32 (PWA)               │  Override séparé requis
       │ 🔴 Sx_33+ (Health/API)       │  Override séparé requis
       └──────────────────────────────┘

       ↳ Sb_28.dogfood-integration (optionnel) :
         si dogfood arrive a posteriori, met à jour Sx_28 §15/§20.
         Peut reverser Option A → Option B/C/D selon signal réel.
```

## 4. Mapping ancienne roadmap S0→S10 vs repo réel

| Ancienne phase | Statut réel | Sprint(s) absorbant | Reste à faire |
|---|---|---|---|
| S0 Baseline repo + benchmark | partiel / obsolète | Sx_26 (Control Plane) | rien — réconcilier dans Sx_28 |
| S1 Signal exercice | ✅ largement fait | Sx_24 (implicit signal + quality V2), Sb_01 | clarifier dettes subjectives résiduelles |
| S2 Mode séance focus | partiel | session detail existant, mobile partials | **Sx_29 candidat fort** (focus mode + friction) |
| S3 Catalogue + taxonomie | partiel | catalog QA + machine atlas + substitution graph | normalisation taxonomie musculaire si dogfood le demande |
| S4 Substitution | ✅ V1 fait | Sx_22 substitution graph + `substituted_name` | option canonique différée |
| S5 Recommandation surcharge | partiel | Sx_27 (reco + explainer + narrative) | surcharge progressive stricte → **Sx_30 candidat** |
| S6 Body tracking | partiel | body metrics + readiness (Sb_22+) | photos / progression photos → **Sx_31 candidat** |
| S7 Body Engineering dashboard | réorienté | `/dashboard` déprécié Sb_27.6, valeur déplacée vers `/`, `/progress`, `/physique` | rien |
| S8 PWA premium | partiel | manifest + meta présents | service worker / offline / Lighthouse → **Sx_32 candidat** |
| S9 Health integrations prep | ❌ pas fait | — | reporté post-stabilisation → **Sx_33 candidat** |
| S10 API mobile prep | ❌ pas fait | — | reporté post-dogfood → **Sx_33+ candidat** |

**Conclusion** : la moitié de S0→S10 est déjà absorbée par les cycles Sx_24/26/27. Le reste devient des cycles Sx_29-33 **conditionnés par le dogfood Sx_27** et tranchés dans **Sx_28**.

## 5. Étape 1 — `Sb_27.dogfood-1` (PROCHAINE ACTION)

### 5.1 Objectif
Vérifier en usage réel si la boucle Sx_27 répond bien aux 5 questions :
1. Quoi faire aujourd'hui ?
2. Pourquoi cette séance ?
3. Que signifie ma dernière séance ?
4. Comment ajuster la suite ?
5. Est-ce que je progresse ou je dérive ?

### 5.2 Pré-requis
- Aucun (Sx_27 livré, runbook documenté dans `DOGFOOD_Sx_27_DEFERRED.md`)

### 5.3 Prompt à utiliser (copier verbatim)

```
GO Sb_27.dogfood-1 — Real Product Dogfood Report.

Repo :
MFE-DSS/workout-session-tracking

Contexte :
Sx_27 est technically closed mais product validation pending real dogfood.
Ne pas ouvrir Sx_28 avant ce dogfood.

Objectif :
Préparer et produire le cadre de dogfood réel pour valider la boucle de
coaching livrée par Sx_27.

Important :
Si aucun usage réel n'a encore été exécuté, ne pas inventer de résultats.
Créer seulement le protocole opérationnel et le template de saisie terrain.
Si l'opérateur fournit ensuite ses retours réels, produire le report final.

Livrables :
1. Vérifier docs/dogfood/DOGFOOD_Sx_27_DEFERRED.md.
2. Créer docs/dogfood/DOGFOOD_Sx_27_RUNBOOK.md si absent.
3. Créer docs/dogfood/DOGFOOD_Sx_27_FIELD_NOTES_TEMPLATE.md.
4. Ne modifier aucun code applicatif.
5. Ne modifier aucun test applicatif.
6. Ne pas créer de migration.
7. Ne pas ouvrir Sx_28.

Le runbook doit contenir :
- durée : 10-14 jours ;
- cible : 5-7 séances ;
- viewport : mobile 360×640 ;
- surfaces : /, /launcher, /sessions/{id}/done, /progress ;
- questions à noter avant / pendant / après séance ;
- critères de succès ;
- critères d'échec ;
- décision finale possible :
  A. Sx_28 peut être ouvert ;
  B. Sb_27.next.<fix> requis ;
  C. Product validation still deferred.

DoD :
- documentation only ;
- check_spec_protocol passe ;
- pytest reste vert ;
- CI verte ;
- verdict final explicite :
  DOGFOOD READY TO EXECUTE
  ou
  DOGFOOD REPORT PRODUCED si données réelles fournies.
```

## 6. Étape 2 — `Sx_28` (après dogfood)

### 6.1 Objectif
Réconcilier l'ancienne roadmap S0→S10, l'état réel du repo, les cycles déjà livrés, les résultats de dogfood Sx_27, et les dettes restantes. Trancher le prochain axe unique.

### 6.2 Pré-requis bloquants
- `Sb_27.dogfood-1` livré (runbook + report ou DEFERRED explicite)
- Si dogfood fait : retours réels documentés
- Si pas de dogfood dans 14-30 jours : décision explicite "indefinitely deferred"

### 6.3 Prompt à utiliser (copier verbatim)

```
GO Sx_28 — Product Roadmap Reconciliation & Next Cycle Selection.

Repo :
MFE-DSS/workout-session-tracking

Contexte :
Sx_26 est clôturé.
Sx_27 est technically closed.
Dogfood Sx_27 doit être pris en compte s'il existe.
La roadmap historique S0→S10 existe comme document conceptuel, mais elle
n'est pas la source de vérité actuelle.
La source de vérité actuelle est docs/strategy/SPEC_REGISTRY.md.

Objectif :
Produire une spec de réconciliation entre :
1. l'ancienne roadmap vNext S0→S10,
2. l'état réel du repo,
3. les cycles déjà livrés,
4. les résultats de dogfood Sx_27,
5. les dettes techniques et produit restantes.

Contraintes :
- SPEC ONLY.
- Ne modifie aucun code.
- Ne modifie aucun test.
- Ne crée aucune migration.
- Ne crée aucun modèle.
- Ne démarre aucun build.
- Distingue ce qui est déjà fait, partiellement fait, obsolète, ou encore pertinent.
- Ne pas réouvrir des décisions déjà tranchées sauf preuve dogfood.

Fichiers à inspecter :
- docs/strategy/SPEC_REGISTRY.md
- docs/strategy/Sx_26_CLOSURE_REPORT.md
- docs/strategy/Sx_27_CLOSURE_REPORT.md
- docs/strategy/ROADMAP_AND_NEXT_STEPS.md
- docs/dogfood/*
- docs/SPRINT_SYNTHESIS.md
- docs/strategy/SPIGNOS_EXERCISE_SYSTEM_CONSOLIDATION_SPEC.md
- docs/strategy/SPIGNOS_EXERCISE_SYSTEM_ROADMAP.md
- app/routers
- app/services
- app/templates
- tests

Livrable :
Créer docs/strategy/Sx_28_PRODUCT_ROADMAP_RECONCILIATION_SPEC.md

Structure obligatoire :
1. Executive summary.
2. Source de vérité actuelle.
3. Ancienne roadmap S0→S10.
4. Mapping ancienne roadmap vs repo réel.
5. Ce qui est déjà fait.
6. Ce qui est partiellement fait.
7. Ce qui est obsolète.
8. Ce qui reste produit-relevant.
9. Résultats dogfood Sx_27 si disponibles.
10. Options de prochain cycle :
    - Option A : Focus Mode / Logging Experience
    - Option B : Progressive Overload Engine
    - Option C : Body Tracking v2
    - Option D : PWA Premium
    - Option E : Cleanup only
11. Matrice impact / risque / valeur.
12. Recommandation.
13. Build queue proposée.
14. Non-goals.
15. Open questions.
16. Verdict :
    READY FOR HUMAN DECISION
    ou
    WAIT FOR DOGFOOD.

Ne code rien.
```

## 7. Étape 3 — `Sx_29` (recommandation par défaut post-Sx_28)

### 7.1 Pourquoi `Sx_29` Focus Mode et pas autre chose ?
Verbatim Product Owner / Prompt Engineer (rapport de planning) :

> Si le logging en salle n'est pas excellent, toute la couche recommandation/body analytics reposera sur un usage fragile.
> D'abord rendre le mode séance imbattable, ensuite enrichir le signal, ensuite seulement corps/graphes/imports santé.

Donc l'ordre logique post-dogfood (si pas de blocker majeur découvert) :
1. **Sx_29** Mobile Session Focus Mode — qualité du logging en salle
2. Sx_30 Progressive Overload Engine — meilleure reco après meilleur signal
3. Sx_31 Body Tracking v2 — photos / progression / source confidence
4. Sx_32 PWA Premium — service worker / offline / Lighthouse
5. Sx_33+ Health / API mobile — exports / intégrations

### 7.2 Pré-requis bloquants pour ouvrir Sx_29
- `Sb_27.dogfood-1` livré (✅ ou ❌ tranché)
- `Sx_28` validé par revue humaine
- Recommandation Sx_28 = Option A (Focus Mode) **ou** humain override explicite

### 7.3 Prompt à utiliser (copier verbatim)

```
GO Sx_29 — Mobile Session Focus Mode & Logging Friction Reduction.

Repo :
MFE-DSS/workout-session-tracking

Contexte :
Sx_27 a livré la boucle coaching.
Sx_28 a réconcilié la roadmap.
Le prochain axe retenu est l'expérience de logging en séance.

Objectif :
Spécifier une refonte mobile-first du mode séance pour réduire la
friction en salle :
- une carte exercice active,
- navigation rapide E1/E2/E3,
- dernier historique visible,
- delta visible,
- gros tap targets,
- CTA sticky,
- timer repos simple,
- fallback no-JS acceptable.

Contraintes :
- FastAPI SSR + Jinja2 conservé.
- Pas de SPA.
- JS progressif autorisé uniquement pour focus/timer/collapse local.
- Aucune rupture de route existante.
- Aucun changement historique destructif.
- Ne pas toucher au scoring core sauf nécessité explicitement justifiée.
- Mobile 360×640.
- Pas de scroll horizontal.
- No-JS fallback fonctionnel.

Livrable :
docs/strategy/Sx_29_MOBILE_SESSION_FOCUS_MODE_SPEC.md

Structure :
1. Audit de la page session actuelle.
2. Problèmes observés ou issus dogfood.
3. User flow cible en salle.
4. États UI : active, pending, done, skipped, substituted.
5. Header compact.
6. Jump bar.
7. Exercise card active.
8. Set rows.
9. Timer repos.
10. CTA sticky.
11. No-JS fallback.
12. Accessibilité.
13. Fichiers impactés.
14. Tests attendus.
15. Build queue :
    - Sb_29.1 template skeleton
    - Sb_29.2 active exercise navigation
    - Sb_29.3 sticky CTA
    - Sb_29.4 rest timer progressive enhancement
    - Sb_29.5 tests + dogfood report
16. Non-goals.
17. Verdict.
```

## 8. Ce qu'on NE fait PAS maintenant

Verbatim Product Owner :

> Je ne lancerais pas tout de suite :
> - S5 Progressive Overload Engine
> - S6 Photos/body tracking v2
> - S8 PWA premium
> - S9 Health integrations
> - S10 API mobile

Justification : le produit vient de recevoir une couche coaching complète. Il faut d'abord savoir si elle marche en vrai, puis améliorer la friction principale (le logging), puis seulement enrichir.

## 9. Erreurs à éviter à la reprise

| Tentation | Pourquoi NE PAS le faire |
|---|---|
| « GO Sx_28 directement » | Spec-driven §9 : pas de dogfood ⇒ pas de cycle suivant. Sx_28 doit consommer le dogfood report comme input. |
| « GO Sx_29 directement, on connaît déjà la friction » | Mêmes raisons. Et Sx_28 peut révéler qu'un autre cycle est prioritaire. |
| « Réouvrir l'ancienne S0→S10 telle quelle » | Obsolète : 5/11 phases déjà absorbées, le reste doit être réconcilié par Sx_28. |
| « Skip Sb_27.dogfood-1 si dogfood déjà fait » | Le dogfood doit avoir produit un report formel (`DOGFOOD_Sx_27_REPORT_<date>.md`). Sans le report, pas de signal exploitable par Sx_28. |
| « Coder direct sans spec » | Protocole §4 : `Sx_NN` ne livre jamais de code. Le code arrive dans `Sb_NN.k`. |
| « Modifier `recommendation.py` / scoring core » | Verrouillé par les hard contracts Sx_26 + Sx_27. Wrapper externe obligatoire (pattern `recommendation_explainer.py` Sb_27.4). |

## 10. Plan d'action immédiat (TL;DR) — révisé post-override #2 2026-06-15

**État au 2026-06-15 (après-midi) :**
- Sx_28 SPEC AMENDED (override #2 → Option A AUTORISÉE)
- Dogfood Sx_27 toujours PENDING (non simulé, peut reverser Option A si livré)
- Build Sx_29 (Mobile Focus Mode) **AUTORISÉ**
- Options B/C/D/E restent bloquées

**Séquence révisée :**

1. ~~**Prochaine action immédiate** : copier le prompt §7.3 → ouvrir Sx_29 SPEC ONLY~~ **✅ FAIT 2026-06-15**
2. ~~**Prochaine action maintenant** : trancher OQ-A à OQ-E (§19) puis ouvrir `Sb_29.1`~~ **✅ FAIT 2026-06-15/16 : Sb_29.1 → Sb_29.5 livrés**
3. ~~**Prochaine action maintenant** : exécuter le dogfood Sx_29 device réel~~ **✅ FAIT 2026-06-16 : verdict opérateur satisfaisant**
4. ~~Ouvrir Sx_30 SPEC ONLY~~ **✅ FAIT 2026-06-16 : `Sx_30_PROGRESSIVE_OVERLOAD_ENGINE_SPEC.md` livrée, Sb_30.0 livré**
5. ~~**Prochaine action maintenant** : revue OQ-A→OQ-E de Sx_30, validation build queue, bascule explicite `BUILD AUTHORIZED FOR Sx_30`~~ **✅ FAIT 2026-06-16/27 : Sb_30.1 → Sb_30.5 livrés, Sx_30 TECHNICALLY CLOSED**
6. ~~**Prochaine action maintenant** : exécuter le dogfood Sx_30 device réel~~ — track indépendant, toujours pending
7. ~~**Option intermédiaire** : `Sb_30.next.placeholder` (OQ-E)~~ **✅ LIVRÉ 2026-06-27**
8. ~~Ouvrir Sx_31 SPEC ONLY~~ **✅ FAIT 2026-06-27 : `SPIGNOS_BODY_INTELLIGENCE_V2_SPEC.md` livrée**
9. ~~Sb_31.1 → Sb_31.5 : composer + route + snapshot + a11y + closure~~ **✅ FAIT 2026-06-27/28 : Sx_31 TECHNICALLY CLOSED**
10. **Prochaine action maintenant** : **exécuter les dogfoods en parallèle** :
    - Sx_31 Body Intelligence v2 sur ≥ 2 semaines (≥ 4 consultations `/body/intelligence` + ≥ 2 `/coach-report`) — cf. `docs/dogfood/DOGFOOD_Sx_31_BODY_INTELLIGENCE_TEMPLATE.md`
    - Sx_30 Progressive Overload Engine — toujours pending
    - Sx_27 Coaching Loop — toujours pending
    Les trois dogfoods sont indépendants.
11. **Options intermédiaires** discrétionnaires sous override séparé :
    - ~~`Sb_31.next.profile-link` (lien `/profile → /body/intelligence`, OQ-G)~~ **✅ LIVRÉ 2026-06-29**
    - `Sb_31.next.home-card` (carte home mini-summary, OQ-F)
    - `Sb_31.next.overload-compliance` (agrégation 30j des hints Sx_30)
12. **Stack contrainte** : FastAPI SSR + Jinja2 conservé ; React production INTERDIT
13. **Track parallèle Body Signal Model** (`SPIGNOS_BODY_SIGNAL_MODEL_SPEC.md`, photos/scans) reste indépendant de Sx_31
14. **Options Sx_32/33+** : restent bloquées tant qu'aucun override séparé n'est documenté ou qu'aucun dogfood Sx_31 PASS n'est livré

**Anti-patterns à éviter (post-override #2) :**
- Ouvrir Sx_29 directement en BUILD `Sb_29.k` sans produire la spec d'abord — **interdit**, Sx_29 doit suivre le protocole spec-driven (§4 protocole)
- Étendre l'override à Options B/C/D/E sans documentation séparée — **interdit**, override #2 borné à Option A
- Introduire du React production dans Sx_29 — **interdit**
- Réouvrir OQ Sx_27 tranchées sans preuve dogfood — **interdit**
- Considérer Sx_27 comme product-validé — **interdit**, dogfood reste PENDING

**Ce document est la première chose à relire quand tu reprends une session.** Il évite de redécouvrir la position et de poser des questions déjà tranchées.

## 11. Maintenance du document

| Quand | Action |
|---|---|
| À la clôture d'un nouveau Sx_ | Mettre à jour §1 (Position actuelle) + §3 (Roadmap réelle) + §4 (Mapping si pertinent) |
| À la livraison d'un dogfood | Mettre à jour §5.3 (`Sb_27.dogfood-1` → ✅), avancer §6 en "PROCHAINE ACTION" |
| Si OQ tranchée modifie la queue | Mettre à jour §3 + §7-8 |
| Si un cycle est annulé | Documenter la raison dans §4 et §11 |

Ce document **n'est pas figé** — il évolue. Mais il est la source unique de "quoi prompter ensuite", et toute évolution doit être traçable dans un commit.

---

**Co-Authored-By :** Claude Opus 4.7
