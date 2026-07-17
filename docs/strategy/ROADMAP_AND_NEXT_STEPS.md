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
| Sx_UI_03 App Shell Navigation | ✅ **CYCLE CLOSED 2026-07-17** (`docs/SPRINT_Sx_UI_03_FINAL_CLOSEOUT_REPORT.md`) — spec accepted 2026-07-02 + **3 lots livrés/acceptés** : `Sb_UI_03.1` bottom nav (`5a35ba8`/CI `29484014891`/review `ea151b6`), `Sb_UI_03.2` rail desktop (`f89f765`/CI `29508124300`/review `a3a32c9`), `Sb_UI_03.3` hardening (`0569178`/CI `29564964557`/review `ac16d49`), chacun **CI 3/3**. Shell app-like : bottom nav 4 destinations, rail desktop ≥1024px, topbar secondaire, session active intégrée (Home hero Reprendre + indicateur onglet Séance), skip link. Objectifs spec ACHIEVED ; non-goals préservés (0 renommage route/métier, no-JS, Auren Terminal 0 nouvelle couleur, template+CSS only). Dettes a11y transverses → `Sx_UI_09`. **Ferme le résidu Sx_UI_03 de Sx_UI_12.** **Prochaine piste** : queue `Sx_UI_12` (`Sx_UI_09` spec, `Sb_UI_11.3` baseline, closeout global). |
| Sx_UI_11 Screenshot Regression Baseline | ✅ **SPEC ACCEPTED 2026-07-02 — human reviewed** (`docs/strategy/Sx_UI_11_SCREENSHOT_REGRESSION_BASELINE_SPEC.md` + `docs/SPRINT_Sx_UI_11_REPORT.md` + `docs/SPRINT_Sx_UI_11_HUMAN_REVIEW_REPORT.md`). Playwright Python binding confirmé. Matrice 18 écrans × 2 viewports (P0=14 obligatoires avant premier build visuel sauf dérogation, P1=16, P2=6). Fixture DB locale déterministe, jamais prod. Règle anti-secret hard. Revue humaine primaire. Storage V1 = artefacts CI + release tag, baseline locale gitignored. 8 OQ résolues V1. **Aucun Playwright installé, aucun screenshot capturé, aucun script écrit.** Choix opérateur : **Option A — ouvrir Sx_UI_04 SPEC ONLY** ensuite. Sb_UI_11.1 reste candidat futur non-ouvert. |
| Sx_UI_04 Session Focus Reskin | ✅ **SPEC ACCEPTED 2026-07-02 — human reviewed** (`docs/strategy/Sx_UI_04_SESSION_FOCUS_RESKIN_SPEC.md` + `docs/SPRINT_Sx_UI_04_REPORT.md` + `docs/SPRINT_Sx_UI_04_HUMAN_REVIEW_REPORT.md`). Périmètre reskin verrouillé (7 fichiers autorisés au futur build). Invariants métier verrouillés (services, routes, models, migrations intacts). Bottom nav visible mais discrète pendant focus mode (Option V1a). Build plan 5 sous-sprints séquentiels. 9 OQ tranchées V1, OQ-H hex pending merge `Sb_UI_04.1`. Choix opérateur : **Option A — ouvrir Sb_UI_11.1 BUILD** ensuite. **Arender dérogation baseline accordée.** |
| Sb_UI_11.1 Screenshot Tooling Build | ✅ **ACCEPTED 2026-07-02 — CI GREEN + human reviewed** (`docs/SPRINT_Sb_UI_11_1_SCREENSHOT_TOOLING_BUILD_REPORT.md` + `docs/SPRINT_Sb_UI_11_1_HUMAN_REVIEW_REPORT.md`). Commit `e8ba190`, CI run [`28595637219`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/28595637219) 3/3 jobs verts (lint 44s / pytest+QA 20min / SonarCloud 1min). Gitleaks / bandit / ruff / pip-audit / spec protocol tous PASS. Matrice P0/P1/P2, CLI Playwright + dry-run + strict-p0 + anti-secret hard, 92 tests unitaires, extra dep `[baseline]` optionnel. **Aucun app code touché. Aucun screenshot committé. Aucun compte prod utilisé. Aucun Chromium installé en CI.** |
| Sb_UI_11.2 Baseline Runtime Integration Patch | ✅ **ACCEPTED 2026-07-02 — CI GREEN + human reviewed** (`docs/SPRINT_Sb_UI_11_2_BASELINE_RUNTIME_PATCH_REPORT.md` + `docs/SPRINT_Sb_UI_11_2_HUMAN_REVIEW_REPORT.md`). Commit `a2846a2`, CI run [`28604484292`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/28604484292) 3/3 jobs verts. |
| **Baseline P0** | ✅ **CAPTURED locally 2026-07-04** — **16/16 PNG** (`docs/BASELINE_P0_CAPTURED_2026_07_04.md`) via Sb_UI_11.2 runtime CLI, ok=16 failed=0. |
| Sb_UI_04.1 CSS Foundation Build | ✅ **ACCEPTED** 2026-07-04 (commit `4451743`, CI [`28700626885`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/28700626885) ✅). Verdict visuel PASS. |
| Sb_UI_04.2 Header & Jump Bar Structure | ✅ **ACCEPTED WITH VISUAL DEPTH RESERVATION** 2026-07-04 (commit `8524851`, CI [`28702740118`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/28702740118) ✅ 3/3 jobs, ruff 542 ≤ 548, 106 tests session focus + 145 tests visual baseline verts). After-capture locale 16/16 ok=16 failed=0. Verdict opérateur : **PASS avec réserve** — écrans fonctionnels, aucune casse, mais transformation perçue trop superficielle (proche recolor / polish léger). Réserve visuelle transférée à `Sb_UI_04.3` comme charte d'ouverture : profondeur visuelle réelle exigée (refonte exercise cards, hiérarchie set logging / hint overload, séparation input/feedback/progression, visual grammar plus marquée, **logique métier intacte**). Report : `docs/SPRINT_Sb_UI_04_2_HUMAN_REVIEW_REPORT.md`. |
| Sx_UI_04 Focused Exercise Flow (RECAST SPEC) | ✅ **HUMAN REVIEW ACCEPTED** 2026-07-04 (commit `996c0c3`, `docs/SPRINT_Sx_UI_04_FOCUSED_EXERCISE_FLOW_HUMAN_REVIEW_REPORT.md` + `docs/strategy/Sx_UI_04_FOCUSED_EXERCISE_FLOW_SPEC.md` + `docs/SPRINT_Sx_UI_04_FOCUSED_EXERCISE_FLOW_REPORT.md`). OQ-A → OQ-G confirmées. Recadrage produit suite à la réserve visuelle Sb_UI_04.2 : passage d'une **liste verticale** à un **active exercise cockpit** (Live Exercise Expert Model §18). **7 couches** : orientation (X/Y · restants · progression · set courant) · exercise intent (pourquoi maintenant / rôle split) · worked area (zone principale / assistants / stabilisation) · technical cues (≤3 visibles) · set logging console (previous perf + target) · alternatives/substitution (surface) · up next (nom + rôle + zone). 7 OQ **tranchées direction produit** (§19 : mini-stepper cliquable · jump bar compressée · worked area sous titre · panel statique V1 · réouverture autorisée · up-next nom+rôle+zone · overview replié). Visual asset strategy §21 : pas de GIF/génération V1, placeholder clinique, contrat futur `exercise_code → primary_zone → asset_key`. Principes pédagogiques §22 (logging < 5 s · progressive disclosure). **Amendement final §23 — Body Representation System** : couche transverse (session card + program preview + profile body intelligence), taxonomie V1 (15 zones), rôles biomécaniques, contrat futur `exercise_code → body_map_descriptor`, visuel V1→V3, prudence anti-médical — **documentaire uniquement** (aucun modèle/migration/service/asset). Worked Area Panel de Sb_UI_04.3 = premier jalon ; profil/body intelligence = direction future. **Simple recolor / accordéon explicitement rejeté.** Invariants métier intacts. Spec parent conservée. |
| Sb_UI_04.3 Active Exercise Cockpit Shell | ✅ **DELIVERED + CI GREEN + HUMAN REVIEW ACCEPTED FOR CONTINUATION** 2026-07-05 (commit `611cda3`, CI [`28735809572`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/28735809572) ✅ 3/3, `docs/SPRINT_Sb_UI_04_3_HUMAN_REVIEW_REPORT.md`). Cockpit wrapper + orientation (X/Y + N restants) + mini-stepper compressé (OQ-B) + carte active hero dominante (cartes non-actives en index secondaire) + Worked Area Panel (zone principale = atlas family réelle, note anti-médicale) + exercise intent + technical cues (max 3) + up-next enrichi zone (OQ-F). SSR/CSS pur, aucun JS, invariants métier/a11y préservés. 285 tests focus/visual + 34 cockpit verts ; after-capture 16/16 (delta +27% session-detail-active). Verdict : **rupture topologique validée, profondeur interactionnelle logging/progression à construire en `.4`**. |
| Sb_UI_04.4 Set Logging Console + Progression Guidance | ✅ **DELIVERED + CI GREEN + HUMAN REVIEW ACCEPTED FOR CONTINUATION** 2026-07-06 (build `629262d` + patch CI `ad1c747`, CI [`28814745985`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/28814745985) ✅ 3/3, 1705 passed, `docs/SPRINT_Sb_UI_04_4_HUMAN_REVIEW_REPORT.md`). Zone set logging → console d'exécution : header + progression X/Y séries + **active set dominant** + **completed ledger** (`✓`) + **upcoming** secondaires + **reference** previous perf (fallback « Non disponible ») + **target** range (« Objectif à qualifier ») + **guidance** hint overload (présentation seule). Inputs noms/action/method **inchangés**. SSR/CSS pur, `overload_hint.html` non touché, invariants métier/a11y préservés. Run initial rouge `28737238524` (heading « Travail ») → Patch A (test non modifié) → vert. 317 focus/visual + 32 console verts ; after-capture 16/16. Verdict : **console validée, Body Representation System à compléter en `.5`**. |
| Sb_UI_04.5 Worked Area Visual Slot + Alternatives + Hardening | ✅ **DELIVERED + CI GREEN + HUMAN REVIEW ACCEPTED** 2026-07-07 (commit `6a49c05`, CI [`28850394732`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/28850394732) ✅ 3/3, 1735 passed, `docs/SPRINT_Sb_UI_04_5_HUMAN_REVIEW_REPORT.md`). Worked Area → **surface clinique SSR/CSS** : zone chip atlas réel + **body-map 100% CSS aria-hidden** (aucun asset/GIF/SVG) + pattern moteur + fallbacks « à qualifier » + note « **non diagnostic médical** ». **Alternatives Surface** (« Adapter l'exercice » + sous-label legacy préservé), substitution mécanisme/route **inchangés**. Hardening mobile/a11y/no-JS. 347 focus/visual + 30 worked area + 576 sweep verts ; after-capture 16/16. |
| **Sx_UI_04 Focused Exercise Flow — cycle** | ✅ **CLOSED — FINAL CLOSEOUT ACCEPTED** 2026-07-07 (`docs/SPRINT_Sx_UI_04_FINAL_CLOSEOUT_REPORT.md`). 5/5 sous-sprints livrés + acceptés (04.1 CSS · 04.2 Header/Jump · recast · 04.3 Cockpit · 04.4 Logging Console · 04.5 Worked Area/Alternatives). Écran séance : liste verticale → cockpit d'exécution biomécanique mobile-first. GO clôture accordé (CI verte, baseline P0 `ok=16`, aucun changement backend/JS/React, invariants préservés). |
| Sx_UI_05 Today / Readiness Home (SPEC) | ✅ **SPEC HUMAN REVIEW ACCEPTED** 2026-07-07 (commit `0d4be33`, `docs/SPRINT_Sx_UI_05_HUMAN_REVIEW_REPORT.md`). OQ-05-A → OQ-05-J confirmées. Home = **surface de décision quotidienne** (CTA unique), Readiness V1 = **bande qualitative self-report** (jamais score médical), progress snapshot + lien, body continuity léger. Data contract **existing data only**, aucun modèle/migration/service. Build split 5 sous-sprints. Sx_UI_04 non rouvert. |
| Sb_UI_05.1 Home IA + Hero Decision Surface | 🟢 **DELIVERED — pending CI + human review** 2026-07-07 (`docs/SPRINT_Sb_UI_05_1_REPORT.md`). Home `.today-home` + **Hero Decision Surface** (eyebrow « Aujourd'hui » + titre décisionnel + **CTA primaire unique** + lien secondaire + teaser readiness qualitatif non médical). Today Decision Model : session active domine (« Reprendre » → `/sessions/{id}`) sinon « Démarrer une séance ». Dashboard legacy **conservé, dé-priorisé**. `home.css` scoped (app.css **non touché**), SSR/no-JS, mobile 360×640. 182 tests home-route + 23 hero verts ; after-capture 16/16 (delta home +7KB, Focus Mode inchangé). Whitelist : 1 template + 1 CSS + 1 test. |
| Sb_UI_05.2 Active Session / Next Workout Cards | ⏸️ **next candidate, not opened** (post-Sb_UI_05.1 CI + review). Enrichir surfaces active/next sous le hero. |
| Sb_UI_05.3 → .5 | ⏸️ **BLOCKED**. Readiness/recovery snapshot · progress/body continuity · empty states/a11y/hardening. |
| **Sx_UI_02b Auren Terminal (RÉVISION DIRECTION)** | ✅ **SPEC HUMAN REVIEW ACCEPTED** 2026-07-07 (commit `805f58b`, `docs/SPRINT_Sx_UI_02b_HUMAN_REVIEW_REPORT.md`). Identité → **« Palantir du bodybuilding »** = graphite dense + tout-mono terminal + accent unique rare (ambre `#C8A24B` validé V1). **Révise Sx_UI_02** (teal retiré, dark = identité). **Re-skin, pas re-architecture** — invariants Sx_UI_04 intacts. OQ-02b-A → OQ-02b-H confirmées. Migration **Home + Focus Mode** en 3 builds : Sb_UI_02b.1 (tokens + Home), .2 (Focus Mode), .3 (hardening + nav). Le teal `#0F8A85` disparaît au re-skin. Patch teal Sb_UI_05.1 stashé (obsolète). |
| Sb_UI_02b.1 Tokens + Home Re-skin | 🟢 **DELIVERED — pending CI + human review** 2026-07-07 (`docs/SPRINT_Sb_UI_02b_1_REPORT.md`). Home re-skiné **Auren Terminal** : graphite `#0F1318` + tout-mono système + ambre `#C8A24B` rare, scoped `.today-home`, **app.css non touché**. Teal retiré du Home (vérifié par tests). AA vérifié (fg 15.7:1, amber 7.7:1). Hero decision IA préservée (CTA unique, active dominance, dashboard « Résumé » dé-priorisé). Stash teal droppé. 351 tests home-route + 34 hero (6 Auren Terminal) verts ; after-capture 16/16 ; **Focus Mode inchangé** (réservé .2). |
| Sb_UI_02b.2 Focus Re-skin | 🟢 **DELIVERED — pending CI + human review** 2026-07-07 (`docs/SPRINT_Sb_UI_02b_2_REPORT.md`). Focus Mode re-skiné **Auren Terminal** (graphite/mono/ambre) par redéfinition des tokens scoped `.session-focus` + remap mono + shadows none + marqueur `session-focus--terminal`. **CSS-only + 1 classe**, aucun partial touché, contrats Sx_UI_04 préservés (cockpit/console/worked-area/rest-timer/substitution/forms/no-JS). Teal retiré. AA vérifié. 380 focus/mobile/visual + 590 sweep + 19 terminal verts ; after-capture 16/16 (Home↔Focus cohérents). |
| Sb_UI_02b.3 Hardening + Shell/Nav | 🟢 **DELIVERED — pending CI + human review** 2026-07-07 (`docs/SPRINT_Sb_UI_02b_3_REPORT.md`). Coque globale → **Auren Terminal** : app.css tokens `:root` graphite + `--font` mono + orange `#f25f3a` → ambre `#C8A24B` ; webfont retiré de base.html ; hardening shell (focus/nav/CTA/banner ambre). Toutes les pages héritent via tokens. Nav/logout/routes préservés ; home.css/session_focus.css/index/session_detail/partials **non touchés**. AA vérifié. 818 sweep + 15 shell verts ; after-capture 16/16. Résidu : trait sparkline orange dans `timeline.py` (service, hors scope). |
| **Migration Auren Terminal V1 (Sx_UI_02b)** | ✅ **CLOSED — FINAL CLOSEOUT ACCEPTED** 2026-07-07 (`docs/SPRINT_Sx_UI_02b_FINAL_CLOSEOUT_REPORT.md`). Home + Focus + Shell cohérents graphite/mono/ambre ; transition à deux mondes supprimée ; identité « Palantir du bodybuilding » livrée V1. CI verte (Sb_UI_02b.2 `28875344109`, .3 `28882063535`) ; SonarCloud Java 21 OK. Invariants métier/no-JS/a11y préservés. Résidu : trait sparkline `timeline.py`. |
| Sb_UI_05.2 | ⏸️ **DEFERRED** derrière la migration visuelle. |
| Sb_OPS.sonar-java21 (CI infra fix) | 🟢 **DELIVERED — pending CI** 2026-07-07 (`docs/SPRINT_Sb_OPS_sonar_java21_REPORT.md`). Le job SonarCloud a échoué au push Sb_UI_02b.1 (`3b4ba91`) : **Java 17 déprécié par SonarQube Cloud** (repo-wide, lint+pytest verts / 1768 passed). Fix : bump `sonarcloud-github-action@v2` → `sonarqube-scan-action@v7.1.0` (Java 21). SonarCloud reste required. Aucun code applicatif touché. |
| **Sx_32 Deep Feature Refactor (Muscle/BodyZone) — ✅ TECHNICALLY CLOSED** | ✅ **CYCLE TECHNICALLY CLOSED / FOUNDATION CLOSED** 2026-07-09 (`docs/strategy/Sx_32_MUSCLE_BODYZONE_MODEL_CLOSEOUT_REPORT.md`). Refonte profonde des features/objets backend : chaîne relationnelle **BodyZone → Muscle → ExerciseMuscleMapping → body_map_descriptor** livrée + branchée dans l'UI (Worked Area). `Sb_32.1`→`.3` + `Sb_32.next` (UI) + `Sb_OPS.scope-guard` **tous HUMAN REVIEW ACCEPTED, CI 3/3**. **Invariance historique 91/91** (name-only ET db_lookup) ; **aucun consommateur métier migré** (scoring/coach/body intelligence intacts) ; migrations additive-only. `Sb_32.4` (bascule consommateurs) **deferred after closeout**. Branche **merge-ready** sous décision opérateur. Autres axes Tier 1 (readiness agg, identité exercice, substitution first-class) en backlog. |
| Sb_32.1 BodyZone + Muscle Foundation | ✅ **HUMAN REVIEW ACCEPTED** 2026-07-08 (commit `fa230fe`, CI [`28933861397`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/28933861397) ✅ 3/3, 1813 passed, `docs/SPRINT_Sb_32_1_HUMAN_REVIEW_REPORT.md`). Modèles `BodyZone`+`Muscle` (PK int + `code` unique) + migration `j1k6e2f3h54` additive-only : 2 tables neuves + **backfill des 11 zones dérivé à l'exécution** des constantes `muscle_mapping` (jamais recopié ; `core` off-radar → `radar_axis` NULL). `muscles` **vide V1** (aucune anatomie inventée). **Baseline non-régression** `classify_exercise` (91 exercices) figée + testée. `classify_exercise`/consommateurs **inchangés** (bascule DB = `.2`). ruff 542 ≤ 548 ; drift/snapshot/patterns/roundtrip/spec protocol verts ; SonarCloud Java 21 OK. Étape 0 Brainstorming documentée + **validée comme règle permanente**. |
| Sb_32.2 ExerciseMuscleMapping + classify lookup/fallback | ✅ **HUMAN REVIEW ACCEPTED** 2026-07-09 (commit `00450c7`, CI [`29001421131`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/29001421131) **attempt 2** ✅ 3/3, 1827 passed, `docs/SPRINT_Sb_32_2_HUMAN_REVIEW_REPORT.md`). Modèle `ExerciseMuscleMapping` + migration `k2l7f3g4i65` additive-only : 1 table neuve + backfill **87 lignes statiques générées au build** depuis la baseline `.1` (65 primary + 22 secondary ; `unknown` non inséré). `exercise_code = name` (seule identité stable ; `code`=slot jour E1…E7). `classify_exercise(name, *, exercise_code=None, db=None)` : lookup DB **optionnel** + fallback substring, **name-only byte-identique**. **Invariance prouvée : DB lookup ET name-only == baseline 91/91.** **Aucun consommateur muté** (7 callers intacts), aucune UI. ruff 541 ≤ 548 ; drift/snapshot/patterns/roundtrip/spec protocol verts. **Note CI** : attempt 1 rouge sur job SonarCloud `cancelled` (bruit infra, lint+pytest déjà verts) → re-run des jobs échoués seuls (sans nouveau commit) → vert. |
| Sb_32.3 body_map_descriptor | ✅ **HUMAN REVIEW ACCEPTED** 2026-07-09 (commit `63a4e74`, CI [`29010584067`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/29010584067) ✅ 3/3, 1843 passed, `docs/SPRINT_Sb_32_3_HUMAN_REVIEW_REPORT.md`). Service **pur, non persistant** `build_body_map_descriptor(name, *, exercise_code=None, db=None) -> dict` (JSON-sérialisable, shape fixe 10 clés). **Aucun modèle/migration/schema/consommateur/UI**. `resolution_path` **honnête** (`db_lookup`/`substring_fallback`/`unknown`) sans modifier `classify_exercise` → zones **== baseline**. Unknown → `"À qualifier"` (aucune anatomie/allégation médicale). **Invariance prouvée : name-only ET db_lookup == baseline 91/91.** Full sweep local skippé (tier `isolated` du garde-fou) → CI réelle a confirmé. Étape 0 Brainstorming documentée. |
| Sb_OPS.scope-guard (garde-fou anti-overcheck) | ✅ **HUMAN REVIEW ACCEPTED** 2026-07-09 (commit `a43ce85`, CI [`29015557948`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/29015557948) ✅ 3/3, full sweep local 1852 passed, `docs/SPRINT_Sb_OPS_scope_guard_HUMAN_REVIEW_REPORT.md`). `scripts/check_scope.py` + `.check-policy.json` + `CLAUDE.md` (versionnés, non aliénables par prompt) : classe le diff en tier (docs/isolated/shared_code/migration/ci_infra) via **détection réelle d'imports** et impose le niveau de check LOCAL minimal. **La CI réelle (3 jobs) reste TOUJOURS source de vérité** ; le garde-fou ne réduit que les checks locaux redondants (full sweep local skippé seulement pour `isolated`/`docs`). Précédence conservative. 9 tests. **Aucun comportement applicatif modifié.** S'applique à tous les sprints suivants. |
| Sb_32.next.worked-area-descriptor-ui | ✅ **HUMAN REVIEW ACCEPTED** 2026-07-09 (build `9dd28a1` + fix CI `8559e8b`, CI [`29029149976`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/29029149976) ✅ 3/3, **1865 passed**, `docs/SPRINT_Sb_32_next_WORKED_AREA_DESCRIPTOR_UI_HUMAN_REVIEW_REPORT.md`). **Premier consommateur visible** de `body_map_descriptor` : route `session_detail` injecte le descriptor ; Worked Area (carte active) rend **primary/secondary labels réels** (Chest Press → Pectoraux/Triceps), unknown → `"À qualifier"`, `resolution_path` en `data-*`, note prudente non médicale. **SSR/no-JS.** Aucun service métier/modèle/migration/schema/endpoint/JS/asset touché ; contrats Focus Mode préservés. **Note CI** : run initial rouge sur 1 test garde-fou caduc (`test_scope_guard` : `body_map_descriptor.py` désormais importé → `shared_code`, classifieur correct) → fix CI-only `8559e8b` (fixture synthétique) → vert. Leçon : éviter les fixtures réels mouvants dans les tests du garde-fou. |
| Sx_32 closeout | ✅ **CLOSED** 2026-07-09 (`docs/strategy/Sx_32_MUSCLE_BODYZONE_MODEL_CLOSEOUT_REPORT.md`). Fondation métier + 1er consommateur UI actés ; bascule consommateurs lourds différée. Branche merge-ready sous décision opérateur. |
| Sb_32.4 | 🟡 **READY TO BE PROPOSED, deferred after closeout** 2026-07-09. Migration consommateurs (coach/body_intel/scoring) vers lookup DB + descriptor. Sprint le plus à risque du cycle → différé volontairement post-closeout. Review-gated, prouve la non-régression (classify old=new) avant bascule. Sur override explicite opérateur. |
| **Sx_32 PROD** | ✅ **LIVE en production** 2026-07-09 (deploy run [`29039000866`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/29039000866) success, tag `deploy/prod/2026-07-09-1759-3e69706`). `/healthz/strict` confirme `deploy.sha=3e69706`, `db.ok`, 63 sessions live préservées, migrations Sx_32 appliquées sans casse. Smokes publics verts (`/healthz` 200, `/healthz/strict` 200, `/` 303, `/login` 200). Smokes UI authentifiés en attente (creds opérateur). |
| Sx_UI_06 dé-densification UI | ✅ **SPEC ACCEPTED** 2026-07-09 (`Sx_UI_06_INFO_DENSITY_DEDUP_SPEC.md`). ✅ **`Sb_UI_06.1 Exercise Card De-densification` HUMAN REVIEW ACCEPTED** 2026-07-10 (commit `2ea53db`, CI [`29080671534`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/29080671534) ✅ 3/3, **1873 passed**, `docs/SPRINT_Sb_UI_06_1_HUMAN_REVIEW_REPORT.md`) : **D1** charge dernière séance retirée **uniquement sur carte active** (portée par la console « Référence précédente ») ; **conservée sur les cartes non-actives → aucune perte d'info**. **D2** scheme en tête + row console « Cible » retirés ; cible = placeholder de la case uniquement. Contrat de saisie intact ; aucun métier/service/modèle/migration/JS. Tests asservis ré-orientés (non affaiblis) + `test_ui06_dedup` ; 2 régressions casse « à/À qualifier » attrapées + corrigées avant commit. **Note** : full sweep local non concluant (test préexistant hang localement, absent en CI) → CI réelle a fait le full (1873 passed). |
| Sb_UI_06.2 Worked Area Density Cleanup | ✅ **HUMAN REVIEW ACCEPTED** 2026-07-11 (build `365da9f` + fix CI `ea72572`, CI [`29102910795`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/29102910795) ✅ 3/3, **1880 passed**, `docs/SPRINT_Sb_UI_06_2_WORKED_AREA_CLEANUP_HUMAN_REVIEW_REPORT.md`). Chip de zone décoratif retiré ; body-map discret conservé ; **« À qualifier » 1× max** (rows vides masquées ; stabilisation permanente retirée) ; note « Estimation indicative, non médicale. » ; `data-resolution-path` conservé. Template-only ; `body_map_descriptor`/route/D1/D2 inchangés ; logging/SSR/no-JS intact. **Note CI** : run initial rouge sur 1 test anti-régression textuel (mot « Repère » réintroduit) → fix CI-only `ea72572`. |
| Sb_UI_06.3 Home Teaser/KPI Density Cleanup | ✅ **HUMAN REVIEW ACCEPTED** 2026-07-11 (commit `f5288a4`, CI [`29149281028`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/29149281028) ✅ 3/3, **1887 passed**, `docs/SPRINT_Sb_UI_06_3_HOME_DENSITY_CLEANUP_HUMAN_REVIEW_REPORT.md`). Home = cockpit de décision unique : CTA hero démarre la reco **directement** (form POST, même contrat) ; bloc reco redondant retiré de la home (gardé au launcher) ; teaser readiness hero retiré (widget unique) ; dernière séance compacte (nom+date) ; KPI réduits à « cette sem. » (score/complétion 30j → /progress). Contrat création session inchangé ; aucun route/service/modèle/Sx_32/Body Intelligence/JS. **Cycle Sx_UI_06 : 3 surfaces principales (carte exercice `.1` + Worked Area `.2` + home `.3`) dé-densifiées et acceptées.** |
| Sx_DOGFOOD_01 Load Hint / Substitution Coherence | ✅ **AUDIT + SPEC ONLY DELIVERED** 2026-07-11 (`Sx_DOGFOOD_01_LOAD_HINT_SUBSTITUTION_COHERENCE_SPEC.md` + `SPRINT_Sx_DOGFOOD_01_LOAD_HINT_SUBSTITUTION_COHERENCE_AUDIT_REPORT.md`). **Constat** : `last_time_by_exercise_code` **N'EST PAS** substitution-aware → contamine 5 surfaces (Référence précédente, Dernière fois, Delta, Hints Sx_08, Chip/Peek) qui affichent une charge d'un **exercice différent** dans les scénarios S2/S3/S5. `overload` est **déjà sûr** (silence si substitué). Règle : **« silence plutôt que faux poids »**. Reco **Option A** (aligner `last_time` sur la politique de substitution d'overload) build minimal, **Option B** (service central) future, **Option D** (transfert de charge) rejetée. Split build `.1` source + `.2` consommateurs + `.3` mobile placeholder. 12 sujets clivants tranchés. **Docs-only, aucun code.** Build sur override séparé. |
| Sb_DOGFOOD_01.1 last_time substitution-aware | ✅ **HUMAN REVIEW ACCEPTED** 2026-07-11 (commit `b5776fb`, CI [`29160746462`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/29160746462) ✅ 3/3, **1896 passed**, `docs/SPRINT_Sb_DOGFOOD_01_1_LAST_TIME_SUBSTITUTION_AWARE_HUMAN_REVIEW_REPORT.md`). `last_time_by_exercise_code` (`stats.py`) applique la **même politique substitution que l'overload** (prescrit↔prescrit, substitué↔même substitut, sinon **absence** = silence). Contrat de retour inchangé → 5 surfaces héritent. Matrice S1→S5 (9 tests). Aucun router/overload/modèle/migration/template/CSS/`value=`/Body Intelligence. Full sweep local hang (préexistant) → CI réelle a fait le full. |
| Sb_DOGFOOD_01.2 consumer propagation verification | ✅ **HUMAN REVIEW ACCEPTED** 2026-07-11 (commit `306620e`, CI [`29164774428`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/29164774428) ✅ 3/3, **1904 passed**, `docs/SPRINT_Sb_DOGFOOD_01_2_CONSUMER_PROPAGATION_VERIFICATION_HUMAN_REVIEW_REPORT.md`). **Verification-only, aucun code applicatif** : 8 tests prouvent que delta/hints/console héritent du fix `.1` (S2/S3/S5 → « Non disponible », jamais la charge d'un autre exercice ; S3 → prescrit ancien ; S1/S4 → référence visible). Cycle Sx_DOGFOOD_01 (audit → fix `.1` → vérif `.2`) cohérent de bout en bout. |
| Sb_DOGFOOD_01.3 mobile placeholder proportion | ✅ **HUMAN REVIEW ACCEPTED** 2026-07-11 (build `e7dd1e1` + fix CI `3474b0c`, CI [`29169942718`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/29169942718) ✅ 3/3, **1913 passed**, `docs/SPRINT_Sb_DOGFOOD_01_3_MOBILE_PLACEHOLDER_PROPORTION_HUMAN_REVIEW_REPORT.md`). **Option B légère** : formatter compacté (`"≈ 102.5"` → `"102.5"`, `"≈ 6-10"` → `"6-10"`) **+** règle CSS `@media (max-width: 380px)` ciblant `::placeholder` de la ligne d'overload (typo réduite ; tap target 44 px + anti-zoom iOS 16 px **intacts**). Aucun `value=`/span unité/engine/historique/substitution/modèle/migration/BI/JS. 23 tests (14 màj + 9 nouveaux) ; broad sweeps 310 + 173 verts ; ruff 543 ≤ 548. **Fix CI `3474b0c`** (`timeout-minutes: 25 → 35`, infra-only) : build valide, seul le job dépassait 25 min. Dernier volet du cycle Sx_DOGFOOD_01. |
| Sx_DOGFOOD_01 CLOSEOUT | ✅ **CLOSED / READY FOR FIELD DOGFOOD** 2026-07-11 (`docs/SPRINT_Sx_DOGFOOD_01_CLOSEOUT_REPORT.md`, docs-only). Cycle bouclé de bout en bout : audit/spec → `.1` fix source `last_time` → `.2` vérif consommateurs → `.3` mobile placeholder, tous **HUMAN REVIEW ACCEPTED**, CI verte 3/3 à chaque étape. Règle **« silence plutôt que faux poids »** implémentée à la source + prouvée sur 5 surfaces + placeholders cible lisibles mobile. Aucun modèle/migration/engine/substitution graph/JS/`value=`/BI touché. Checklist terrain dans le closeout report (§7). |
| Sx_BI_01 Body Intelligence Activation | ✅ **HUMAN REVIEW ACCEPTED** 2026-07-11 (spec/audit docs-only, commit `d081f41`, CI skipped, `docs/SPRINT_Sx_BI_01_BODY_INTELLIGENCE_ACTIVATION_HUMAN_REVIEW_REPORT.md`). **Constat** : BI **pas un greenfield** — composer `/body/intelligence` **flag-off**, `/physique` **LIVE avec score A/B/C opaque**, fondations Sx_32 prêtes (11 zones, 91 exos mappés, Muscle vide), `body_map_descriptor` câblé. **Choix acté : Option A — Zone Intelligence Cards** (par zones, traçable, confidence-aware, non médical ; **pas de 2e score opaque** ; réutilise `muscle_scoring ZoneScore` ; aucun nouveau score ; pas de home widget). 15 sujets clivants tranchés. Build minimal futur `Sb_BI_01.1`. **Aucun code/modèle/migration/JS/deploy/claim médical.** |
| Sx_TRANSFORM_01 App Transformation Consolidation | ✅ **HUMAN REVIEW ACCEPTED** 2026-07-11 (spec/audit docs-only, commit `8b0f449`, CI skipped, `docs/SPRINT_Sx_TRANSFORM_01_APP_TRANSFORMATION_CONSOLIDATION_HUMAN_REVIEW_REPORT.md`). **Document maître** (Option A) = porte d'entrée directionnelle ; sources conservées. Vocabulaire fixé (SPIGNOS repo / Auren produit / Auren Terminal identité ; « Spinos » inexistant). Direction active **Auren Terminal dark/mono/amber** (white clinical déjà tranché Sx_UI_02b). Architecture figée (SSR/Jinja, **no React**, no-JS fallback, PWA-first). Priorités réalignées (mode séance › Home › cohérence charge › BI zones › Progress › PWA › Rebrand) + principes actionnables (silence plutôt que faux poids, pas de score opaque, confidence, non-médical, ne pas re-densifier, un seul accent, placeholder léger). Contradictions résolues, interdits explicités. **Aucun code/rebrand/deploy.** |
| Sb_BI_01.1 Zone Intelligence Cards | ✅ **HUMAN REVIEW ACCEPTED** 2026-07-11 (commit `f0cc60b`, CI [`29192711453`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/29192711453) ✅ 3/3, **1925 passed**, `docs/SPRINT_Sb_BI_01_1_ZONE_INTELLIGENCE_CARDS_HUMAN_REVIEW_REPORT.md`). Section « Lecture par zones » sur `/body/intelligence` : cards par zone (volume/tendance/contribution dérivée/confidence), état vide sobre, mention non médicale. Réutilise `muscle_scoring ZoneScore` en lecture — **aucun nouveau score** ; score opaque/A-B-C/radar jamais surfacés. Aucun modèle/migration/JS/Home/`/physique`/nouvelle couleur ; **flag OFF prod (surface invisible)**, activé en test seulement. 12 tests dédiés + broad sweep 284 verts. check_scope isolated → promu SHARED_CODE (router main.py), CI complète = source de vérité. |
| Sb_BI_01.2 Zone Drill Detail | ✅ **HUMAN REVIEW ACCEPTED** 2026-07-11 (commit `31bb62a`, CI [`29194461683`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/29194461683) ✅ 3/3, **1935 passed**, `docs/SPRINT_Sb_BI_01_2_ZONE_DRILL_DETAIL_HUMAN_REVIEW_REPORT.md`). Drill inline `<details>` no-JS par zone card : exercices principaux (noms réutilisés de `ZoneScore.top_exercises`), état vide « Détail insuffisant ». Disclosure SSR natif, **zéro JS**, no-JS fallback préservé, mobile-first. Aucun volume/exercice (différé) / score / grade / radar / nouvelle route / nouvelle couleur ; `/physique`, Home, `muscle_scoring.py` non touchés ; **flag OFF prod (surface invisible)**. 10 tests dédiés + `.1` intact 12/12 + broad sweep 305 verts. check_scope isolated → promu SHARED_CODE (router main.py). |
| Sb_BI_01.next Physique Score Decision | ✅ **HUMAN REVIEW ACCEPTED** 2026-07-11 (commit `0404aca`, CI skipped, `docs/SPRINT_Sb_BI_01_NEXT_PHYSIQUE_SCORE_DECISION_HUMAN_REVIEW_REPORT.md`). **Choix : Option B prudente** — `/body/intelligence` = future surface principale ; `/physique` (score A/B/C + radar) déprécié **progressivement** (route + service conservés, score encadré jamais renforcé). **Point critique** : `compute_physique_dashboard` alimente leaderboard + user_profile → **service intact**, on déprécie la surface pas le service. Séquence : `Sb_BI_01.3` encadrement AVANT `Sb_BI_01.activation` flag. Aucun code/deploy/suppression. |
| Sb_BI_01.3 Physique Surface Guardrails | ✅ **HUMAN REVIEW ACCEPTED** 2026-07-11 (commit `fa7d63e`, CI [`29201970643`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/29201970643) ✅ 3/3, **1944 passed**, `docs/SPRINT_Sb_BI_01_3_PHYSIQUE_SURFACE_GUARDRAILS_HUMAN_REVIEW_REPORT.md`). Bloc `.physique-guardrails` sous score/grade/radar (inchangés) : microcopy « Lecture synthétique · Score indicatif, non médical » + lien « Voir la lecture par zones » → `/body/intelligence` **conditionnel au flag** (jamais un lien mort). `compute_physique_dashboard` NON touché (leaderboard/user_profile préservés, tests sentinelles) ; aucun nouveau score/radar/couleur/JS/modèle/migration/suppression ; flag OFF prod. 9 tests dédiés + broad sweep 301 verts. check_scope isolated → promu SHARED_CODE (`pages.py` main.py). Ordre `.next` respecté (encadrement AVANT activation). |
| Sb_BI_01.activation-readiness | 🟢 **PLAN + AUDIT LIVRÉS — activation deferred until after dogfood + explicit GO** 2026-07-11 (`docs/strategy/Sb_BI_01_ACTIVATION_READINESS_PLAN.md` + `docs/SPRINT_Sb_BI_01_ACTIVATION_READINESS_REPORT.md`, docs-only). Procédure d'activation contrôlée **entièrement cadrée** : flag par env prod (`BODY_INTELLIGENCE_ENABLED=1`, défaut repo reste False), deploy `workflow_dispatch` (`ref=<SHA réel>` jamais `main`), smoke **sans compte prod** (`/body/intelligence` 404→303), rollback flag en secondes, monitoring `/healthz/strict`, critères GO/NO-GO. Manque identifié : ajouter `/body/intelligence` au smoke lors du build d'activation. Rien activé/déployé/modifié. |
| Sx_UI_08.1 PWA Installability Baseline | ✅ **HUMAN REVIEW ACCEPTED** 2026-07-11 (commit `d2519a4`, CI [`29209091349`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/29209091349) ✅ 3/3, **1958 passed**, `docs/SPRINT_Sx_UI_08_1_PWA_INSTALLABILITY_BASELINE_HUMAN_REVIEW_REPORT.md`). **Option A** : manifest resserré (`id`/`lang`/`dir` ; couleurs/noms inchangés) + `base.html` `apple-mobile-web-app-title="SPIGNOS"`. **Pas** de service worker/offline/cache/SPA/JS/nouvelle icône/nouvelle couleur ; assets existants seulement ; no-JS fallback préservé. Session/BI/physique/services/models/migrations/deploy/nginx **non touchés**. 14 tests dédiés + broad sweep 733 verts. check_scope isolated → promu SHARED_CODE (`base.html` partagé). Limite → `Sx_UI_08.2` : pages auth publiques (head standalone). |
| Sx_UI_08.2 Public Auth Heads Alignment | ✅ **HUMAN REVIEW ACCEPTED** 2026-07-11 (commit `275efe5`, CI [`29230227896`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/29230227896) ✅ 3/3, **1967 passed**, `docs/SPRINT_Sx_UI_08_2_PUBLIC_AUTH_HEADS_ALIGNMENT_HUMAN_REVIEW_REPORT.md`). **Option A** : patch minimal des 3 heads standalone (welcome/login/register) — bloc meta d'installabilité identique à `base.html` + manifest + favicon. Aucun changement de formulaire/route/wording/couleur/SW/JS/offline/rebrand ; `base.html` + manifest **non modifiés**. 9 tests dédiés (rendu réel HTTP non-authentifié). check_scope=ISOLATED (templates standalone). |
| Sx_UI_07.1 Progress Surface Auren Readability | ✅ **HUMAN REVIEW ACCEPTED** 2026-07-13 (build `98d679d` + fix CI `01fb142`, CI [`29242663710`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/29242663710) ✅ 3/3, **1978 passed**, `docs/SPRINT_Sx_UI_07_1_PROGRESS_AUREN_READABILITY_HUMAN_REVIEW_REPORT.md`). **Option A pure** (template-only sur `/progress`) : lede utile, section « Rythme récent », titres timelines sobres, note « Lecture indicative ». Tous les blocs conservés ; **aucun service touché** (`kpis.py`/`timeline.py`/`weekly_loop.py`/`pages.py` non ouverts) ; aucune valeur/calcul changé ; aucun JS/score/lien BI-physique/couleur/rebrand. Labels KPI « sessions » **conservés** (périmètre respecté, `test_kpis.py` non modifié). **Fix CI `ci_infra`** `timeout-minutes: 35 → 45` (run initial cancelled par timeout 35:17 malgré 1978 passed ; aucun gate retiré). check_scope=ISOLATED. |
| Sx_UI_07.2 History Surface Auren Readability | ✅ **HUMAN REVIEW ACCEPTED** 2026-07-13 (commit `afc2f5f`, CI [`29251434702`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/29251434702) ✅ 3/3, **1991 passed**, `docs/SPRINT_Sx_UI_07_2_HISTORY_AUREN_READABILITY_HUMAN_REVIEW_REPORT.md`). **Option A pure** (template-only sur `/history`) — ajouts **additifs** (lede, aria-label explicite, note « Lecture indicative »). Aucun texte existant modifié → filtres/badges/`<details>`/forms POST/confirm **conservés** ; **55 tests asservis existants verts (0 cassé)**. `pages.py`/`sessions.py`/services non touchés ; aucune valeur/JS/lien BI-physique/score/rebrand. 13 tests dédiés. check_scope=ISOLATED. Run à 32:11 (validé sous timeout 45). |
| Sx_CAT_01 Catalog Integrity Cleanup | ✅ **HUMAN REVIEW ACCEPTED** 2026-07-13 (batch local mergé, CI code `8e969f8` 3/3 ; `docs/SPRINT_LOCAL_BATCH_2026_07_13_HUMAN_REVIEW_REPORT.md`). **Option A data-only** : 3 incohérences sémantiques CLEAR corrigées (E5/E4 upright row épaules ; E3 leg press postérieur) — seuls `machine_slug`(→null)/`machine_family` changent ; aucun slug/code/position/scheme/rep/nom/service/modèle/migration touché ; snapshots historiques inchangés. catalog_qa + atlas_qa PASS ; 9 tests dédiés. En attente **GO batch** (continue ou commit+CI). |
| Sx_FB_01 Exercise Feedback Rationalization | ✅ **HUMAN REVIEW ACCEPTED — VERIFIED (already done, no code)** 2026-07-13 (batch local mergé, commit docs `fb13c4a`). Objectif déjà atteint (build Sb_01, acté Sx_04 §13) : `execution_quality`/`reps_target` absents du form, colonnes+export conservés, 0 consumer analytique. Aucun code touché (éviter régression). |
| Sx_SUB_01 Substitution Graph Verification | ✅ **HUMAN REVIEW ACCEPTED — VERIFIED (already conformant, no code)** 2026-07-13 (batch local mergé, commit docs `fb13c4a`). Moteur N1/N2/N3 conforme (garde anti-cross-pattern hard-enforced, bridges N3-only, caps/dedup) ; **Sx_CAT_01 = impact NUL** (substitution ne lit pas machine_family/slug) ; 41 tests verts ; historique stable. Aucun code/data/test touché. Recommandation : GO BATCH COMMIT + CI. |
| Sx_BATCH_CLOSEOUT_01 Local Batch Closeout | ✅ **HUMAN REVIEW ACCEPTED** 2026-07-13 (batch local mergé — CI code `8e969f8` 3/3 + commit docs `fb13c4a`). Synthèse batch : Sx_CAT_01 (code) + FB_01/SUB_01 (verify). Plan commit 2-commits (code→CI, docs→skip), checklist pré-commit, chemins interdits vérifiés. |
| Sx_UI_07.3 Library / Launcher Catalogue Readability | ✅ **HUMAN REVIEW ACCEPTED** 2026-07-13 (batch local mergé, CI code `8e969f8` 3/3 ; `docs/SPRINT_Sx_UI_07_3_LIBRARY_LAUNCHER_READABILITY_REPORT.md`). **Option A pure** (template-only `/library`+`/launcher`) — ledes enrichis additifs. Aucun texte asservi cassé (71 tests verts) ; sections/cartes/CTA/creation_source/reco conservés ; `pages.py`/`sessions.py`/services/data non touchés. 12 tests dédiés + sweep 57 passed. |
| Sx_UI_07.4 Template Detail Readability | ✅ **HUMAN REVIEW ACCEPTED** 2026-07-13 (batch local mergé, CI code `8e969f8` 3/3 ; `docs/SPRINT_Sx_UI_07_4_TEMPLATE_DETAIL_READABILITY_REPORT.md`). **Option A pure** (template-only `/library/{slug}`) — 3 ajouts additifs (fiche programme / structure de séance / note charges-reps). 8 insertions / 0 suppression ; données/POST/route/service inchangés ; aucun test asservi cassé (19 verts, garde-fou cardio préservé). 11 tests dédiés + sweep 68 passed. |
| Sx_UI_07_CLOSEOUT Readability Cycle | ✅ **HUMAN REVIEW ACCEPTED** 2026-07-13 (batch local mergé, commit docs `fb13c4a` ; `docs/SPRINT_Sx_UI_07_CLOSEOUT_READABILITY_CYCLE_REPORT.md`). Cycle readability des 5 surfaces de consultation (progress/history/library/launcher/template detail) : 07.1+07.2 mergés, 07.3+07.4 en batch. Invariants : Option A pure, additif, textes asservis préservés (0 cassé), aucun métier touché. Aucun code touché par le closeout. |
| Sx_TPL_01 Template Detail Start CTA | ✅ **HUMAN REVIEW ACCEPTED** 2026-07-13 (batch local mergé, CI code `8e969f8` 3/3 ; `docs/SPRINT_Sx_TPL_01_TEMPLATE_DETAIL_START_CTA_REPORT.md`). CTA « Démarrer cette séance » sur `/library/{slug}` — form POST `create_session`+`creation_source=library` (whitelisté → `sessions.py` non touché, template-only). Renversement assumé de la décision 07.4 « pas de CTA » (test 07.4 ré-orienté). 10 tests dédiés (dont end-to-end) + 38 asservis + sweep 100 passed. |
| Sx_LIB_01 Library Card Action Semantics | ✅ **HUMAN REVIEW ACCEPTED** 2026-07-13 (batch local mergé, CI code `8e969f8` 3/3 ; `docs/SPRINT_Sx_LIB_01_LIBRARY_CARD_ACTION_SEMANTICS_REPORT.md`). Correction structurelle : `<form>` de démarrage sorti du lien `<a>` (était imbriqué = HTML invalide + hacks stopPropagation retirés). Comportement inchangé (lien→détail, Démarrer→create_session, creation_source=library), prouvé end-to-end. Template-only ; 11 tests dédiés + 50 asservis + sweep 95 passed. |
| DOGFOOD_DEBRIEF_01 Session Active (terrain 2026-07-13) | 🟢 **DÉBRIEF RÉDIGÉ (docs-only)** 2026-07-13 (`docs/dogfood/DOGFOOD_SESSION_ACTIVE_2026_07_13_REPORT.md`). Séance réelle en salle (mobile iOS). **2 irritants carte d'exercice active** : #1 libellé zone « Delt_lat » → **NON REPRODUIT** (code : `ZONE_LABELS["delt_lat"]="Deltoïdes latéraux"` ; « Delt_lat » casse Title ≠ toute sortie code → probable artefact dictée vocale) → **attendre capture** avant fix ; #2 visuel « Zone travaillée » → **CONFIRMÉ** (body-map décorative volontairement non-anatomique, `session_focus.css:1547`) → **spec dédiée `Sx_BODYMAP_01`** (direction : vraie silhouette + zone surlignée). Verdict : GO corriger friction mineure (sous conditions). Aucun code/commit/deploy. |
| Sx_NAV_01 Active Navigation Semantics | ✅ **HUMAN REVIEW ACCEPTED** 2026-07-13 (batch local mergé, CI code `8e969f8` 3/3 ; `docs/SPRINT_Sx_NAV_01_ACTIVE_NAVIGATION_SEMANTICS_REPORT.md`). Topbar partagée (`base.html`) : **état actif** dérivé de `request.url.path` (SSR, no-JS) — lien courant `is-active` + `aria-current="page"` (exactement 1/route, jamais `"false"`). Mapping des 9 surfaces (dont `/library/{slug}`→Programmes, `/body/intelligence`→Physique, `/coach…`→Coach). Template-only (routers/services/data non touchés) ; 9 liens + logout POST + active-banner + brand + PWA préservés ; CSS minimal 1 règle réutilisant `var(--fg)` (aucune nouvelle couleur). Pas de conflit avec `aria-current="location"` du header séance (65 tests asservis verts). 15 tests dédiés + **broad sweep 532 passed / 0 échec**. check_scope=ISOLATED → **promu SHARED_CODE** (base.html partagé). |
| Sx_SESSION_UX_01 Active Session Friction Audit | 🟢 **AUDIT RÉDIGÉ (commit `9925165`)** 2026-07-14. Aucun P0 ; P1 F1/F2/F3, P2 F4/F5 ; build recommandé `Sb_SESSION_UX_01.3` (F2). |
| Sb_UI_10.1 Visible Product Strings (SPIGNOS → Auren) | ✅ **HUMAN REVIEW ACCEPTED** 2026-07-15 (commit `e035259`, CI [`29403226554`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/29403226554) ✅ 3/3, **2138 passed**, pytest 25:07 sous timeout 45, `docs/SPRINT_Sb_UI_10_1_VISIBLE_PRODUCT_STRINGS_HUMAN_REVIEW_REPORT.md`). Nom produit **visible** migré SPIGNOS → **Auren** sur les 4 chaînes de `base.html` (apple-title, `<title>`, brand topbar, footer). SPIGNOS reste interne (commentaire ; 0 visible). Diff **strings-only prouvé** : routes/classes/static/manifest/nav/logout intacts ; auth standalone + manifest différés (`10.3`/`10.2`). Zéro Orion, aucun asset. 14 dédiés + 50 asservis + sweep 386 verts. check_scope ISOLATED→**promu SHARED_CODE** (base.html = 37 pages). **Suite : `Sb_UI_10.2` (manifest+icons, nécessite assets) ou `Sb_UI_10.3` (auth standalone).** |
| Sb_UI_10.4b Method Rules User-Facing Data String Pass | ✅ **HUMAN REVIEW ACCEPTED** 2026-07-15 (build `bbfbe32`, CI [`29420622692`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/29420622692) 3/3 ; `docs/SPRINT_Sb_UI_10_4b_METHOD_RULES_DATA_STRING_PASS_HUMAN_REVIEW_REPORT.md`). Seed audité (base préexistante→Auren prouvé, idempotence prouvée, aucune migration) ; /science rend 0 SPIGNOS/0 Orion ; sentinelle ré-orientée. **Jalon : plus aucune surface utilisateur ne rend SPIGNOS.** Ferme l'occurrence OPEN de 10.4 : `data/method_rules.json` (règle `plages-repetitions`, seedée + rendue /science) « dans SPIGNOS » → « dans Auren ». Data-only, aucune migration (table re-seedée au boot). Texte scientifique intact ; identifiants internes conservés ; zéro Orion. Test sentinelle ré-orienté (/science == 0 SPIGNOS). **Après ce pass : 0 surface utilisateur ne rend SPIGNOS.** 20 + sweep 25 verts. CI/merge au push. |
| Sb_UI_10.2 PWA Manifest + App Icons Auren | ✅ **HUMAN REVIEW ACCEPTED** 2026-07-15 (build `9203e4c`, CI [`29429846469`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/29429846469) 3/3 ; `docs/SPRINT_Sb_UI_10_2_PWA_MANIFEST_APP_ICONS_AUREN_HUMAN_REVIEW_REPORT.md`). Glyphe path byte-identique (couleur seule), 4 PNG dimensions exactes + opaques, manifest Auren + 3 icônes, apple-touch 4 heads, `sips` déterministe 0 dépendance, tests portables. **10.2 = dernier bloqueur du closeout Sx_UI_10 — levé ; `Sx_UI_10` désormais CLOSED** (cf. `docs/SPRINT_Sx_UI_10_AUREN_VISUAL_MIGRATION_FINAL_CLOSEOUT_REPORT.md`). | (`docs/SPRINT_Sb_UI_10_2_PWA_MANIFEST_APP_ICONS_AUREN_REPORT.md`, branche `work/auren-pwa-assets`). Gate débloqué (glyphe haltère approuvé, recoloré `#f25f3a`→`#C8A24B`, path inchangé). Livré : `auren-mark.svg` + `favicon.svg` recoloré + PNG 192/512/maskable-512/apple-touch-180 (dimensions exactes, fond opaque, `sips` déterministe, **0 dépendance**). Manifest → name/short_name « Auren » + 3 icônes PNG (champs core préservés). apple-touch sur 4 heads. 0 #f25f3a/SPIGNOS/Orion. Aucun backend/route/CSS/JS/dépendance/SW. 39+94+sweep 263 verts. check_scope ISOLATED. **Dernier bloqueur du closeout Sx_UI_10 levé (sous réserve CI+review).** |
| Sb_UI_10.2a PWA Asset Decision Gate | ✅ **GO — HUMAN SOURCE APPROVED** (initialement BLOCKED, débloqué par décision opérateur) 2026-07-15 (`docs/SPRINT_Sb_UI_10_2a_PWA_ASSET_DECISION_GATE_REPORT.md`). Audit assets PWA : **aucune source graphique Auren canonique** dans le repo. Seul asset = `favicon.svg` (Sprint 0) legacy SPIGNOS `#f25f3a` (orange abandonné ≠ ambre `#C8A24B`) ; manifest générique « Workout » ; 0 PNG/apple-touch/maskable. Options A/B/C rejetées. **Décision D : fournir un asset source Auren maître** (SVG carré, symbole approuvé, graphite+ambre only, lisible/maskable, licence propre). Pack cible + transformations + plan tests 10.2 spécifiés. **`Sb_UI_10.2` reste BLOCKED ; Closeout bloqué par 10.2.** Prochaine action (hors gate) : fournir/approuver la source graphique. |
| Sb_UI_10.4 User-Facing Docs / Labels Auren Pass | ✅ **HUMAN REVIEW ACCEPTED** 2026-07-15 (build `7bdf4ba` + alignement arbitrage `57a6d5f`, CI [`29416674199`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/29416674199) ✅ 3/3, **2164 passed**, `docs/SPRINT_Sb_UI_10_4_USER_FACING_LABELS_AUREN_PASS_HUMAN_REVIEW_REPORT.md`). String-only pass : 8 chaînes produit visibles migrées SPIGNOS → Auren (science ×5, atlas lede, coach-report note, SVG diagramme `<title>` a11y). Sens scientifique/coach/atlas inchangé ; SVG structure+`id`s intacts ; routes/backend/manifest/assets/CSS/JS/`data/` non touchés ; zéro Orion. **1 occurrence OPEN** : `data/method_rules.json` (hors périmètre `data/**`, sentinelle == 1 ; micro-pass **`Sb_UI_10.4b`** sur GO). 12 dédiés (conservés par arbitrage, doublon supprimé) + science_page ré-orienté ; ruff 543 ≤ 548 ; spec PASS. **Jalon : plus aucun template ne rend SPIGNOS.** *(Historique au moment du build : `10.4b` restait à jouer sur GO, `10.2` était BLOCKED BY ASSETS, closeout non ouvert.)* **Résolu depuis** : `Sb_UI_10.4b` ✅ ACCEPTED (occurrence `method_rules.json` fermée), `Sb_UI_10.2` ✅ ACCEPTED, **`Sx_UI_10` CLOSED**. |
| Sb_UI_10.3 Public Auth / Welcome Auren Pass | ✅ **HUMAN REVIEW ACCEPTED** (code `d22b316` + CI `29408336175` 3/3 ; `docs/SPRINT_Sb_UI_10_3_PUBLIC_AUTH_WELCOME_AUREN_PASS_HUMAN_REVIEW_REPORT.md`) 2026-07-15 (`docs/SPRINT_Sb_UI_10_3_PUBLIC_AUTH_WELCOME_AUREN_PASS_REPORT.md`). Ouvert avant `10.2` (décision opérateur : `Sb_UI_10.2` **BLOCKED BY ASSETS**, aucun manifest/icon avant gate assets). 8 chaînes visibles migrées sur welcome/login/register (standalone) : apple-titles, titles (dont legacy « · Workout » → « · Auren »), h1 welcome, titre SVG a11y. SPIGNOS = commentaires internes seulement (0 rendu, prouvé client anonyme). Formulaires/routes/erreurs/meta PWA/manifest/CSS intacts ; aucun asset ; zéro Orion. 3 assertions asservies réalignées (invariant Sx_UI_08.2 levé). **14 dédiés** (« 15 » = erreur de comptage corrigée en review) + 35 affectés + sweep 180 verts + CI **2152 passed** (2138 + 14) ; ruff 543 ≤ 548 ; spec PASS ; check_scope **ISOLATED non promu** (3 pages bornées, justifié). **Suite : `10.2` dès gate assets (BLOCKED BY ASSETS) ; `10.4` sur GO explicite.** |
| Sx_UI_10 Auren Visual Migration Closeout & Rebrand Readiness | ✅ **CLOSED / HUMAN REVIEW COMPLETE** 2026-07-15 (spec `49fa7d3` ; closeout final `docs/SPRINT_Sx_UI_10_AUREN_VISUAL_MIGRATION_FINAL_CLOSEOUT_REPORT.md`). **Cycle clos** : 5 builds (`Sb_UI_10.1`/`.3`/`.4`/`.4b`/`.2`) human-review accepted, chacun CI 3/3 verte (SHA exacts) ; gate `10.2a` débloqué (glyphe haltère → Auren, `#f25f3a`→`#C8A24B`, path inchangé). Migration visible SPIGNOS→Auren **complète** : shell, auth/welcome, science/atlas/coach + SVG, donnée seedée rendue, manifest+pack PWA. **Non-goals préservés** (0 renommage code/repo/route/model/table ; SPIGNOS = interne). 0 Orion applicatif. Résidus internes non-bloquants documentés (`machine_atlas.json` `.title` = donnée morte non rendue ; `#f25f3a` pré-existant dans SVG illustratifs, hors pack PWA). **Gate externe OUVERT** : due diligence juridique/commerciale/domaine Auren avant lancement public. **Prochaine piste (non commencée)** : due diligence nom/domaine, puis Dogfood Focus (UX séparé). |
| Sb_UI_09.1 Reduced-Motion Global | 🟢 **CODE COMPLETE — CI PENDING — HUMAN REVIEW PENDING** 2026-07-17 (baseline `79957f1` ; `docs/SPRINT_Sb_UI_09_1_REDUCED_MOTION_GLOBAL_REPORT.md`). 1er lot de `Sx_UI_09`. Bloc universel `@media (prefers-reduced-motion: reduce) { *, ::before, ::after { animation/transition-duration 0.01ms !important } }` en fin d'app.css — neutralise les transitions/animations décoratives (9 transitions auditées, toutes décoratives ; 0 animation active). Pattern WCAG 2.2 de référence, robuste aux ajouts futurs, blocs scopés (session_focus/body_intelligence) préservés. Motion only : 0 perte d'info, 0 display:none, 0 changement contenu/couleur/layout. CSS only (additif) ; 0 template/route/service/model/migration/manifest/asset/JS/contrat/Custom. 9 tests dédiés, 0 réorienté. Local : 9 + broad sweep 808 verts ; ruff clean, budget 543 ≤ 548, spec PASS, check_scope ISOLATED. **Prochaine étape : `GO VALIDATE — Sb_UI_09.1`** (non commencé). Suite : `09.2` form-errors ARIA, `09.3` contrast guard, closeout. |
| Sx_UI_09 Accessibility & Motion | ✅ **SPEC RÉDIGÉE 2026-07-17** (docs-only ; `docs/strategy/Sx_UI_09_ACCESSIBILITY_MOTION_SPEC.md` + `docs/SPRINT_Sx_UI_09_ACCESSIBILITY_MOTION_REPORT.md`). Option A : socle WCAG 2.2 AA ciblé, non médical, SSR/no-JS, tokens Auren (0 nouvelle couleur). Audit code réel (`e1d7df2`) : 2 gaps — reduced-motion absent d'`app.css` (→ `Sb_UI_09.1`), form-errors login/register sans role=alert/aria-live/aria-invalid (→ `Sb_UI_09.2`, SSR-only) — + 1 axe verrouillé par test : contraste `--fg-dim` #8A94A0 = **6.06:1 sur --bg = AA PASS** (hypothèse Sx_UI_12 infirmée) → `Sb_UI_09.3` test de garde, pas de correction. Acquis préservés (skip-link/aria-current/landmarks/tap/no-JS). Non-goals : charts/BodyMap/auth refonte/AAA/JS/nouvelle couleur. Split `09.1→.2→.3→closeout`. Ferme la dette a11y de la queue `Sx_UI_12`. **Prochain build : `GO BUILD — Sb_UI_09.1 Reduced-Motion Global`** (non commencé). |
| Sx_UI_12 UI Transformation Residual Reconciliation | ✅ **Sx_UI RESIDUAL QUEUE: READY** 2026-07-15 (docs-only ; `docs/strategy/Sx_UI_12_UI_TRANSFORMATION_RESIDUAL_RECONCILIATION_SPEC.md` + `docs/SPRINT_Sx_UI_12_UI_TRANSFORMATION_RESIDUAL_RECONCILIATION_REPORT.md`). Réconciliation vérifiée sur l'état **réel du code** de `Sx_UI_01→11`. CLOSED : 02b/04/07/10-interne ; 02 SUPERSEDED par 02b. PARTIAL : 01 (review interne), 05 (0 build, absorbé par 06.3), 06 (.4 non ouvert), 08 (08.3 SW non ouvert), 11 (11.3 baseline finale). **Sx_UI_03 non implémenté** (topbar 10 entrées, ni bottom nav ni rail → 03.1/.2/.3 BUILD REQUIRED). **Sx_UI_09 a11y à ouvrir** (gaps reduced-motion/form-errors ARIA/contraste dim). À NE PAS construire par défaut : 05.2-.5, 06.4 (duplication non démontrée), 08.3 (décision, pas dette). Gate Auren nom/domaine = EXTERNAL BLOCK. `UI_TRANSFORMATION_ROADMAP.md` → HISTORICAL. **Prochain prompt : `GO BUILD — Sb_UI_03.1 Mobile Bottom Navigation`** (non commencé). |
| Sb_UI_03.3 App Shell Hardening | ✅ **HUMAN REVIEW ACCEPTED** 2026-07-17 (build `0569178`, CI [`29564964557`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/29564964557) 3/3 premier coup ; `docs/SPRINT_Sb_UI_03_3_APP_SHELL_HARDENING_HUMAN_REVIEW_REPORT.md`). Revue : index.html byte-identique ; topbar rétrogradée (0 primaire, secondaires + Contact + logout POST, is-subactive) ; active-banner + CSS mort + @keyframes pulse retirés → Home hero unique Reprendre, indicateur onglet Séance (has-active-session + dot statique + sr-only « En cours ») ; skip link 1er interactif ; breakpoints/bottom nav/rail intacts ; 26 dédiés + réorientations intent preserved ; CI 3/3 ; sweep revue 1013 verts. **`Sx_UI_03` = 3 lots acceptés (03.1/03.2/03.3) → prêt pour closeout.** **Prochaine action : `GO CLOSEOUT — Sx_UI_03`** (non commencé). — 3ᵉ et dernier lot applicatif de `Sx_UI_03`. (1) Topbar rétrogradée en nav secondaire (4 primaires retirés → bottom nav + rail ; secondaires + Contact + logout POST conservés ; is-subactive, jamais 2ᵉ aria-current ; 0 route supprimée). (2) active-banner globale supprimée (CSS mort + @keyframes pulse retirés) → Home hero (index.html byte-identique) = unique surface Reprendre, état actif porté par l'onglet Séance (has-active-session + point ambre statique + sr-only « En cours », href / inchangé). (3) Skip link `#main-content` (1er interactif, hors écran → visible au focus, tokens Auren, 0 hex neuf ; pas sur auth standalone). Template+CSS only ; 0 backend/route/service/model/migration/data/manifest/asset/JS/contrat/logique Home/Custom ; index.html intact. 26 dédiés + réorientations honnêtes (active_nav topbar 0 aria-current, mobile_polish banner→indicateur, sentinelles 03.1/03.2) ; full sweep local (SHARED_CODE, mandat) ; ruff clean, budget 543 ≤ 548, spec PASS. Breakpoints/bottom nav/rail intacts. **Dettes différées à `Sx_UI_09`** (reduced-motion, aria-live, aria-invalid, contraste, auth, charts). **Prochaine étape : `GO VALIDATE — Sb_UI_03.3`** (puis closeout `Sx_UI_03`). |
| Sb_UI_03.2 Desktop Rail / Secondary Shell | ✅ **HUMAN REVIEW ACCEPTED** 2026-07-16 (build `f89f765`, CI [`29508124300`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/29508124300) 3/3 premier coup ; `docs/SPRINT_Sb_UI_03_2_DESKTOP_RAIL_SECONDARY_SHELL_HUMAN_REVIEW_REPORT.md`). Revue : `f89f765` ancêtre du HEAD `3eb8d99` (merges Custom PR #22/#23, 0 drift shell) ; rail ≥1024px, 4 destinations + parité mapping + 1 actif/région + secondaires `<details>` + logout POST + topbar masquée desktop + Focus 720px vérifiés ; 1 test réorienté (769→1024) intent preserved ; CI 3/3 ; sweep revue 1013 verts. **Prochaine action : `GO BUILD — Sb_UI_03.3 Shell Hardening`** (non commencé ; rétrogradation topbar + intégration active-session + skip link Sx_UI_09). — 2ᵉ lot de `Sx_UI_03`. Rail latéral gauche persistant ≥1024px : marque + 4 destinations (même ordre/href/mapping que la bottom nav, variables partagées), 1 actif/région (jamais "false"), actif ≠ couleur seule (bordure+poids). Secondaires (Historique/Physique/Coach/Squads/Classement) dans `<details>` « Plus » ; Contact + logout POST en pied. Breakpoint unifié 1024px (bottom-nav 769→1024, spec ; tablette portrait garde la bottom nav) ; topbar masquée desktop (Option A) ; contenu décalé `margin-left: --app-rail-w` + max-width 960px ; Focus Mode resserré 720px. Tokens Auren (0 nouvelle couleur), tap ≥44px, focus-visible. Template+CSS only ; 0 backend/route/service/model/migration/manifest/asset/JS/contrat/Custom. 46 dédiés + 1 réorienté (769→1024) ; broad sweep 795 verts ; ruff clean, budget 543 ≤ 548, spec PASS, check_scope ISOLATED. Bottom nav 03.1 intacte. **Différés à `03.3`** : rétrogradation topbar + intégration active-session + skip link (Sx_UI_09). **Prochaine étape : `GO VALIDATE — Sb_UI_03.2`** (non commencé). |
| Sb_UI_03.1 Mobile Bottom Navigation | ✅ **HUMAN REVIEW ACCEPTED** 2026-07-16 (build `5a35ba8` + fix `4cd512a`, CI [`29484014891`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/29484014891) 3/3 sur `4cd512a` ; `docs/SPRINT_Sb_UI_03_1_MOBILE_BOTTOM_NAVIGATION_HUMAN_REVIEW_REPORT.md`). Revue : `4cd512a` ancêtre du HEAD `fd875fa` (merge Custom PR #22, 0 drift shell) ; 4 destinations + mapping (1/région) + secondaires + logout POST + no-JS + Focus offset + active-banner vérifiés ; 3 tests réorientés intent preserved ; CI 3/3 (SonarCloud 504 infra résolu par re-run) ; sweep revue 738 verts. **Prochaine action : `GO BUILD — Sb_UI_03.2 Desktop Rail / Secondary Shell`** (non commencé). Différés inchangés : `03.3`/`Sx_UI_09` NOT OPENED, `Sb_UI_11.3` PENDING, `Sb_SESSION_UX_01.5` FIELD TEST READY. — Premier lot de `Sx_UI_03`. Bottom nav mobile app-like, 4 destinations (Séance/Programmes/Progression/Profil), SSR/no-JS, liens natifs, SVG décoratifs, actif dérivé du path (1 par région, jamais "false"), tokens Auren existants (0 nouvelle couleur), tap ≥44px, safe-area, masquée ≥769px (topbar = fallback desktop). Routes secondaires toutes préservées (menu topbar + Contact footer), logout POST/active-banner/heads PWA intacts. Focus Mode : sticky CTA décalé via token partagé (0 desktop). Template+CSS only (base.html/app.css/session_focus.css) ; 0 backend/route/service/model/migration/manifest/asset/JS. 33 dédiés + 69 nav + 133 focus/heads + broad sweep 586 verts ; 1 test réorienté (1 actif par région, non affaibli) ; ruff clean, budget 543 ≤ 548, spec PASS, check_scope ISOLATED. **Différés** : `03.2` rail desktop · `03.3` hardening · `Sx_UI_09` a11y · `Sb_UI_11.3` baseline. **Prochaine étape : `GO VALIDATE — Sb_UI_03.1`** (non commencé). |
| AUREN Name Gate — Trademark / Domain Due Diligence | ⛔ **BLOCKED FOR PROFESSIONAL CLEARANCE** 2026-07-15 (screening préliminaire interne, docs-only ; `docs/research/AUREN_NAME_TRADEMARK_DOMAIN_DUE_DILIGENCE_REPORT.md` + `docs/research/AUREN_NAME_CLEARANCE_EVIDENCE_REGISTER.md`). **PAS un avis juridique.** Domaines (RDAP vérifié) : `auren.com/.fr/.ch/.app/.io/.fit/.health` + fallbacks `get/use/aurenapp/aurenfitness.com` = **tous enregistrés** (`.eu` = MANUAL CHECK) → aucun candidat/fallback libre. Marques (EUIPO/INPI/WIPO/Swissreg/TMview) = **MANUAL CHECK REQUIRED** (API non accessibles, non substituées). Signal tiers : réseau « Auren » audit/conseil (classe distincte, à qualifier). **Ni clairable ni rejetable en interne → CPI requis.** Nom **non déclaré libre/disponible**. **La due diligence Auren reste un EXTERNAL OPEN GATE.** Prochaine décision (non exécutée) : mandater un CPI (recherche marque FR/UE/CH cl. 9/41/42/44 + stratégie domaine alternative). Aucun dépôt/réservation/compte. Dogfood Focus F1/F2/F3 indépendant, non commencé. |
| Sb_SESSION_UX_01.5 Active Card F1/F2/F3 Dogfood | 🟡 **FIELD TEST READY / OPERATOR EVIDENCE PENDING** 2026-07-15 (`docs/dogfood/DOGFOOD_Sb_SESSION_UX_01_5_ACTIVE_CARD_F1_F2_F3_PROTOCOL.md`). Protocole terrain docs-only pour valider en salle : F1 console prioritaire (`901143f`/01.2), F2 rappel charge précédente (`015cdfe`/01.3), F1-compl alternatives + F3 cues repliées (`4fdcb71`/01.2b+01.4) — tous CI 3/3 verts (SHA vérifiés). Fiche mobile-first + verdicts PASS/PARTIAL/FAIL/NOT OBSERVED par friction + non-régressions + Delt_lat indépendant + matrice décision. **Aucune observation inventée** (champs vides). **Ne PAS marquer PASS/ACCEPTED/CLOSED avant la séance.** Aucun code/test/template/CSS/donnée. **Prochaine action (post-séance)** : `GO RECORD & CLOSEOUT — Sb_SESSION_UX_01.5` sur observations opérateur uniquement. |
| Sb_SESSION_UX_01.4 Post-Console Cues Density (F3) | ✅ **HUMAN REVIEW ACCEPTED** (batch CI code `4fdcb71` 3/3 ; `docs/SPRINT_Sb_SESSION_UX_01_2B_01_4_BATCH_HUMAN_REVIEW_REPORT.md`) 2026-07-14 (`docs/SPRINT_Sb_SESSION_UX_01_4_POST_CONSOLE_CUES_DENSITY_REPORT.md`). Cues post-console **repliées dans `<details>` natif** (replié par défaut, no-JS) → densité mobile réduite. Contenu + fallback inchangés (info repliée, pas supprimée) ; classes préservées. Template + CSS minimal (affordance summary, aucun hex). Console/previous-load/BodyMap/substitutions/sticky CTA/rest timer intacts. Ordre final : worked-area → console → alternatives → cues. 17 dédiés + 115 batch/asservis + sweep 397 verts. check_scope ISOLATED→**promu SHARED_CODE**. **Reste** : dogfood F1+F2+F3 puis fermer batch en CI. |
| Sb_SESSION_UX_01.2b Alternatives Below Console (F1) | ✅ **HUMAN REVIEW ACCEPTED** (batch CI code `4fdcb71` 3/3 ; `docs/SPRINT_Sb_SESSION_UX_01_2B_01_4_BATCH_HUMAN_REVIEW_REPORT.md`) 2026-07-14 (`docs/SPRINT_Sb_SESSION_UX_01_2B_ALTERNATIVES_ORDER_REPORT.md`). Dette `01.2` réalisée : drawer « Adapter l'exercice » déplacé **sous la console** (worked-area → console → alternatives → cues). **Purement structurel** : radios `substituted_name`/N1-N2-N3/legacy/`elif`/form POST **byte-identical** (prouvé par diff). Template only (aucun CSS, substitution logic intacte). 17 dédiés + 56 substitution + 63 adjacents + sweep 371 verts. check_scope ISOLATED→**promu SHARED_CODE**. **Reste** : dogfood F1+F2 puis fermer batch en CI. |
| Sb_SESSION_UX_01.2 Active Console Priority (F1) | ✅ **HUMAN REVIEW ACCEPTED** 2026-07-14 (CI code `901143f` 3/3 run [`29335728163`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/29335728163) ; `docs/SPRINT_Sb_SESSION_UX_01_2_ACTIVE_CONSOLE_PRIORITY_HUMAN_REVIEW_REPORT.md`). Carte active : **console de saisie déplacée AVANT les cues techniques** (Option A adaptée : cues descendues après la console, `_cues_machine` re-résolu localement). **Template only** (routers/services/models/data/CSS intacts, no-JS) ; POST/inputs/`value=""`/completion serveur/rappel « dernière »/« Référence précédente »/silhouette/sticky CTA/rest timer/alternatives préservés. **Écart assumé** : alternatives non déplacées → dette optionnelle **`Sb_SESSION_UX_01.2b`** (dogfood-dependent). 11 dédiés + 98 non-régression + sweep 516 verts. **Reste** : dogfood F1+F2 en salle. |
| Sb_SESSION_UX_01.3 Previous Load Readability (F2) | ✅ **HUMAN REVIEW ACCEPTED** 2026-07-14 (CI code `015cdfe` 3/3 run [`29329356785`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/29329356785) ; `docs/SPRINT_Sb_SESSION_UX_01_3_PREVIOUS_LOAD_READABILITY_HUMAN_REVIEW_REPORT.md`). Rappel discret charge dernière séance (« dernière : X kg · Y reps ») **sur la ligne du set actif**, au point de saisie ; additif (bloc « Référence précédente » conservé), `aria-hidden`, silence si pas d'historique. Template/CSS only (`overload_*`/`last_time`/descriptor/services/data intacts, `_ref` réutilisé), no-JS, 0 nouvelle couleur (`--fg-dim`). 7 dédiés + sweep 358 verts. **Reste** : dogfood `Sb_SESSION_UX_01.5` (confirmer F2 en salle) → puis F1 (`01.2`) / F3 (`01.4`). |
| **Prochaine action** | ✅ **BATCH LOCAL 2026-07-13 FERMÉ & ACTÉ** — les 10 sprints (Sx_CAT_01 · 07.3 · 07.4 · TPL_01 · LIB_01 · NAV_01 · FB_01 · SUB_01 · CLOSEOUT_01 · 07_CLOSEOUT) sont **HUMAN REVIEW ACCEPTED** : commit code `8e969f8` **CI 3/3 verte** (run [`29268204599`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/29268204599)) + commit docs `fb13c4a` (paths-ignore, CI skipped) + revue `docs/SPRINT_LOCAL_BATCH_2026_07_13_HUMAN_REVIEW_REPORT.md`. Working tree clean, aucun deploy/tag/migration. **Dogfood terrain 2026-07-13 (DOGFOOD_DEBRIEF_01) réalisé** → 2 irritants carte d'exercice active : **#1 libellé zone « Delt_lat » NON REPRODUIT** (attendre capture) ; **#2 visuel « Zone travaillée » CONFIRMÉ** → futur **`Sx_BODYMAP_01`** (silhouette + zone surlignée). **Suites (aucun code)** : (a) **attendre capture écran** pour trancher #1 → si prouvé, micro-fix label isolé ; (b) ✅ **`Sb_BODYMAP_01.1` HUMAN REVIEW ACCEPTED** 2026-07-14 (CI code `0485469` 3/3 + docs `98d1cc5` ; `SPRINT_Sb_BODYMAP_01_1_INLINE_BODYMAP_HUMAN_REVIEW_REPORT.md`) — silhouette SVG inline face+dos (partial `worked_area_body_map.html`), 6 macro-régions, primaire plein + secondaires faibles, `unknown` neutre ; template-only+CSS (descriptor/muscle_mapping/ZONE_LABELS/services/data intacts), non-médical, no-JS, 0 nouvelle couleur ; `delt_lat`→« Deltoïdes latéraux » préservé. **Reste** : dogfood mobile 360px (densité 2 silhouettes) ; spec `Sx_BODYMAP_01` (`9cbc787`) ; (c) **Dogfooding BI Sx_DOGFOOD_01** (différé) — valider surfaces BI **avant** activation publique ; (d) **CI optimization / pytest-xdist** (deferred — timeout 25→35→45, run ~32 min). Autres pistes hors batch : nettoyage CSS inline `/history` (app.css), `Sx_UI_08.3` SW/offline ⏸️ deferred, **CI optimization / pytest-xdist** (deferred — timeout monte 25→35→45, run à 32:11). **Séquence recommandée** : (1) **Dogfooding terrain Sx_DOGFOOD_01** (pending, en différé) — valider les surfaces BI + cohérence charge **avant** de les rendre publiques ; (2) si dogfood concluant → **GO activation** : futur build/ops `Sb_BI_01.activation` (poser `BODY_INTELLIGENCE_ENABLED=1` en prod + ajouter `/body/intelligence` au smoke + deploy `ref=<SHA réel>`) — **GO deploy explicite requis**, smokes jamais sur compte prod. Le plan readiness est prêt (`Sb_BI_01_ACTIVATION_READINESS_PLAN.md`). Autres pistes GO : volume/exercice drill (future spec), corpus improvement (non bloquant). Body Intelligence activation / deploy **deferred until explicit GO**. Pistes hors cycle : `Sb_UI_06.4`, `Sb_32.4`, `Sx_UI_07` (Progress), `Sx_UI_08` (PWA), release tag, smokes UI auth prod. Deferred : release tag, deploy, mini-gate 57 kg, smokes UI auth prod, fix trait sparkline `timeline.py`, `Sb_UI_05.2`, closeout dogfoods Sx_30/31, activation `/body` Manual Profile, rebrand `Sx_UI_10`. À investiguer (non urgent) : hang d'un test au full sweep **local** (n'affecte pas la CI). |
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

## 1bis. Track parallèle — Custom Program Builder (`Sx_CUSTOM_PROGRAM`, SPEC ACCEPTED)

- **`Sx_CUSTOM_PROGRAM_01` — ✅ HUMAN REVIEW ACCEPTED / SPEC ONLY / BUILD NOT AUTHORIZED**
  2026-07-15 (`docs/SPRINT_Sx_CUSTOM_PROGRAM_01_INTELLIGENT_PROGRAM_BUILDER_HUMAN_REVIEW_REPORT.md` ;
  spec : `docs/strategy/Sx_CUSTOM_PROGRAM_01_INTELLIGENT_PROGRAM_BUILDER_SPEC.md`,
  branche `spec/sx-custom-program-01-intelligent-builder` rebasée sans conflit).
- **Architecture cible actée : Option C hybride** (drafts `UserProgram*` isolés → publication
  en `WorkoutTemplate` custom protégé) + 4 contrats durs (wipe-guard seed pré-matérialisation,
  slugs namespacés, versions publiées immuables, reco/librairie filtrées).
- Vit **en parallèle du cycle UI/Auren** actif : **worktree isolé**
  (`workout-session-tracking-custom`), aucun fichier partagé, zéro concurrence `Sb_UI_10.4b`,
  rebase obligatoire avant toute PR/build.
- **`Sx_CUSTOM_PROGRAM_02 — Exercise Knowledge Base Spec` : ✅ HUMAN REVIEW ACCEPTED /
  SPEC ONLY / BUILD NOT AUTHORIZED** 2026-07-15
  (`docs/SPRINT_Sx_CUSTOM_PROGRAM_02_EXERCISE_KNOWLEDGE_BASE_HUMAN_REVIEW_REPORT.md`,
  spec `cbba7d9`). Audit chiffré accepté comme référence (53 properties vs 103 noms →
  52 absents, gap assumé jusqu'à `EKB_02` ; socle Sx_32 prêt, `Muscle` vide), identité =
  noms historiques invariants + `variant_group`, taxonomie V1 18 champs, **Option C
  séquencée** (JSON canonique → seed DB optionnel gaté), QA 8 checks obligatoires avant
  tout seed, OQ-EKB-A→I = questions des builds/specs suivantes.
  **Next : `Sx_CUSTOM_PROGRAM_03 — Program Quality Scoring Spec` (NEXT SPEC CANDIDATE,
  sur GO explicite).** `Sb_CUSTOM_PROGRAM_EKB_01→04` NOT AUTHORIZED.
- **`Sx_CUSTOM_PROGRAM_03 — Program Quality Scoring Spec` : ✅ HUMAN REVIEW ACCEPTED /
  SPEC ONLY / BUILD NOT AUTHORIZED** 2026-07-15
  (`docs/SPRINT_Sx_CUSTOM_PROGRAM_03_PROGRAM_QUALITY_SCORING_HUMAN_REVIEW_REPORT.md`,
  spec `e082b17`). Moteur pur/déterministe/versionné acté (pattern Sx_30) → `QualityReview`
  (A/B/C + 8 sous-scores explicables + assumptions/missing_data) ; grade hybride plafonné
  jamais opaque, sous-scores visibles avant la lettre ; microcopy non-médicale sans
  « tu dois » ; C publiable avec avertissement (défaut) ; persistance = à la volée + trace
  versionnée figée à la publication ; historique réel = V2 strict. OQ-SCORE-A→H = questions
  des specs/builds suivants. `Sb_CUSTOM_PROGRAM_SCORING_01→04` NOT AUTHORIZED.
  **Next : `Sx_CUSTOM_PROGRAM_04 — User Program Persistence Spec` (NEXT SPEC CANDIDATE,
  sur GO explicite).**
- **`Sx_CUSTOM_PROGRAM_04 — User Program Persistence Spec` : ✅ HUMAN REVIEW ACCEPTED /
  SPEC ONLY / BUILD NOT AUTHORIZED** 2026-07-15
  (`docs/SPRINT_Sx_CUSTOM_PROGRAM_04_USER_PROGRAM_PERSISTENCE_HUMAN_REVIEW_REPORT.md`,
  spec `263810d`). Modèle 5 tables `UserProgram*` accepté (source de vérité d'édition,
  Option C) ; statuts + nouveau cycle obligatoire post-publication (artefact immuable) ;
  ownership dur + soft delete ; quotas V1 (10/5/7/10) ; trace scoring figée par version ;
  `exercise_name` = nom EKB invariant ; migrations futures additive-only une par build.
  OQ-PERS-A→J = questions spec 05/builds. `Sb_CUSTOM_PROGRAM_PERSISTENCE_01→05`
  NOT AUTHORIZED.
  **Next : `Sx_CUSTOM_PROGRAM_05 — Session Instantiation Compatibility Spec` (NEXT SPEC
  CANDIDATE, dernière spec fille — matérialisation + wipe-guard + filtres, sur GO explicite).**
- **`Sx_CUSTOM_PROGRAM_05 — Session Instantiation Compatibility Spec` : ✅ HUMAN REVIEW
  ACCEPTED / SPEC ONLY / BUILD NOT AUTHORIZED** 2026-07-15
  (`docs/SPRINT_Sx_CUSTOM_PROGRAM_05_SESSION_INSTANTIATION_COMPATIBILITY_HUMAN_REVIEW_REPORT.md`,
  spec `b61f4c9`). Contrats de lançabilité actés : wipe-guard seed (`LAUNCH_01` strictement
  premier, test bump-survie), slugs `up{uid}-{base}-v{n}` immuables, matérialisation
  1 session → 1 template, session_builder inchangé V1, codes figés par version, historique
  étanche par slug versionné, filtres reco/librairie + tests anti-pollution, publication
  idempotente, lancement ownership-gated. OQ-LAUNCH-A→K = décision de build.
- **🏁 SPEC QUEUE `Sx_CUSTOM_PROGRAM` 01→05 : COMPLETE** (2026-07-15) — les 5 specs sont
  HUMAN REVIEW ACCEPTED. **Prochaine frontière : décision opérateur séparée de build
  (GO/override explicite, build par build). `Sb_CUSTOM_PROGRAM_LAUNCH_01 — seed wipe-guard`
  = FIRST BUILD CANDIDATE, NOT OPENED. Tous les builds (`Sb_*`, `EKB_*`, `SCORING_*`,
  `PERSISTENCE_*`, `LAUNCH_*`) restent NOT AUTHORIZED.**
- **`Sx_CUSTOM_PROGRAM_BUILD_GATE_00 — Spec Queue Closeout & Build Entry Plan` :
  ✅ HUMAN REVIEW ACCEPTED / BUILD DECISION PENDING / LAUNCH_01 NOT OPENED** 2026-07-15
  (`docs/SPRINT_Sx_CUSTOM_PROGRAM_BUILD_GATE_00_HUMAN_REVIEW_REPORT.md`, gate `8df0af6`).
  Gouvernance de build actée : ordre contraignant (`LAUNCH_01` wipe-guard d'abord — build de
  sécurité — puis persistence ∥ EKB ∥ scoring, wizard, launch), pré-périmètre LAUNCH_01
  cadré (5 tests obligatoires, aucun schema change sauf STOP explicite), branching plan
  (`sb/custom-program-launch-01-seed-wipe-guard` depuis canonique propre, jamais de code sur
  la branche spec), Go/No-Go criteria préflight (canonique clean, aucun agent sur `seed.py`,
  CI 3/3). **Prochaine commande possible, séparée : `GO BUILD Sb_CUSTOM_PROGRAM_LAUNCH_01`
  (opérateur uniquement) ; tout le reste reste NOT AUTHORIZED.**
- **`Sb_CUSTOM_PROGRAM_LAUNCH_01 — Seed Wipe-Guard` : ✅ MERGED + CANONICAL CI GREEN**
  2026-07-16 (build `248af1c` + review `56f77a2`, **PR #22 MERGED**, merge commit
  **`fd875fa`** ; `docs/SPRINT_Sb_CUSTOM_PROGRAM_LAUNCH_01_SEED_WIPE_GUARD_HUMAN_REVIEW_REPORT.md`
  + appendice post-review). Garde `catalog_section != 'user'` sans migration ; custom +
  arbre survivent, système reconstruit à l'identique ; garde d'entrée du namespace.
  **CI canonique `29494384156` : 3/3 GREEN** — pytest ✅ **2223 passed** · lint ✅ ·
  SonarCloud ✅ (panne upstream 504 **résolue**, re-runs sans commit ; CI PR `29488023234`
  aussi 3/3). **Le trunk est protégé — premier build du track livré et vérifié.**
  **`PERSISTENCE_01` = FIRST NEXT BUILD CANDIDATE, NOT OPENED** (première migration du
  track, préflight tier `migration` requis, sur GO explicite).
- **`Sb_CUSTOM_PROGRAM_PERSISTENCE_01 — User Program Root Persistence` : ✅ MERGED +
  CANONICAL CI GREEN** 2026-07-16 (build `14804a6`, **PR #23 MERGED**, merge **`3eb8d99`** ;
  `docs/SPRINT_Sb_CUSTOM_PROGRAM_PERSISTENCE_01_USER_PROGRAMS_REPORT.md`). Table racine
  `user_programs` (ownership CASCADE testé, `slug_base` unique par user, zéro FK
  catalogue). Migration `l3m8g4h5j76` = head canonique. 9 dédiés + 36 adjacents +
  **full sweep 2232 passed** ; **CI PR `29514324922` 3/3 premier coup (2272 passed) ·
  CI canonique `29520029077` 3/3.** 2e build du track livré et vérifié.
- **`Sb_CUSTOM_PROGRAM_PERSISTENCE_02 — User Program Children Persistence` : ✅ MERGED +
  CANONICAL CI GREEN** 2026-07-17 (build `819f17c`, **PR #24 MERGED**, merge **`0056baf`** ;
  `docs/SPRINT_Sb_CUSTOM_PROGRAM_PERSISTENCE_02_CHILDREN_REPORT.md` + appendice
  post-merge). 3 tables enfants (sessions/exercises/rep_targets) en 1 migration
  `m4n9h5i6k87` = **head Alembic canonique** — cascade d'arbre testée, uniques par
  parent, `exercise_name` = nom EKB invariant, **zéro FK catalogue/EKB**. **CI PR
  `29571272500` 3/3 premier coup · CI canonique `29574276201` 3/3 (pytest 2308 passed,
  lint, SonarCloud).** L'**arbre de persistance Option C complet** est livré et vérifié
  sur le trunk ; **29 tests sentinelles track cumulés** (wipe-guard 10 + racine 9 +
  enfants 10). **`PERSISTENCE_03` = FIRST NEXT BUILD CANDIDATE / NOT OPENED**
  (`user_program_quality_reviews`, dernière migration de persistance, sur GO explicite).
- **`Sb_CUSTOM_PROGRAM_PERSISTENCE_03 — User Program Quality Review Persistence` :
  🟢 PATCH COMPLETE / REVIEW PENDING (non commité)** 2026-07-17
  (`docs/SPRINT_Sb_CUSTOM_PROGRAM_PERSISTENCE_03_QUALITY_REVIEWS_REPORT.md`, branche
  `sb/custom-program-persistence-03-quality-reviews` rebasée sur `edcad4e` — closeout 02
  poussé d'abord, séquence opérateur). Table `user_program_quality_reviews` = **réceptacle
  figé** : une trace immuable par version publiée (unique nommée), grade + scoring_version
  NOT NULL, ekb_version dédiée, 5 payloads JSON opaques, computed_at server_default.
  **Zéro moteur/calcul/seuil** — le sens = `SCORING_01+`. Migration `n5o0i6j7l98` ADD TABLE
  ONLY. 10 dédiés premier coup + 41 sentinelles ; 4 QA verts premier coup ; snapshot +6 ;
  check_scope MIGRATION. **La persistance du track est complète.** Suite : full sweep →
  GO COMMIT → PR (CI 3/3) → merge sur GO. **`PERSISTENCE_04+` NOT AUTHORIZED.**
- **`Sb_CUSTOM_PROGRAM_PERSISTENCE_04 — Draft CRUD Repository Service` : 🟢 PATCH
  COMPLETE / REVIEW PENDING (non commité)** 2026-07-17
  (`docs/SPRINT_Sb_CUSTOM_PROGRAM_PERSISTENCE_04_DRAFT_CRUD_REPORT.md`, branche
  `sb/custom-program-persistence-04-draft-crud`, base `007c428`). **Premier service du
  track, zéro migration** : `user_program_drafts.py` — CRUD de brouillon owner-scoped
  (inexistant/non-possédé indistinguables), soft-delete-only, `validated`→`draft` à
  l'édition, `published` verrouillé, `replace_draft_tree` avec purge d'orphelins prouvée.
  12 dédiés + 67 sentinelles + broad sweep 192 verts ; check_scope ISOLATED (leaf).
  Quotas = `PERSISTENCE_05`. Suite : GO COMMIT → PR (CI 3/3) → merge sur GO.
  **`PERSISTENCE_05+` NOT AUTHORIZED.**
- **`Sb_CUSTOM_PROGRAM_*` (tous les autres : `LAUNCH_02+`, `PERSISTENCE_*`, `EKB_*`,
  `SCORING_*`, `WIZARD_*`) : NOT AUTHORIZED** — chacun sur GO/override explicite, dans
  l'ordre du gate.

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
