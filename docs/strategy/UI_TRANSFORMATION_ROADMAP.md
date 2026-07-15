---
name: UI_TRANSFORMATION_ROADMAP
type: strategy-roadmap
status: HISTORICAL OPENING ROADMAP (docs-only) — source vivante = Sx_UI_12
superseded_by: docs/strategy/Sx_UI_12_UI_TRANSFORMATION_RESIDUAL_RECONCILIATION_SPEC.md
created: 2026-07-02
depends_on:
  - docs/strategy/brainstorm/UI_TRANSFORMATION_BRAINSTORM_V1_normalized.md
  - docs/strategy/brainstorm/UI_TRANSFORMATION_BRAINSTORM_V2_normalized.md
depends_on_gate:
  - docs/OPS_PROD_STABILIZATION_PROFILE_BODY_COACH_REPORT.md (verdict PROD STRUCTURALLY STABLE FOR UI RENOVATION ✅ signé 2026-07-02)
---

# UI Transformation Roadmap — Auren

> ⚠️ **HISTORICAL OPENING ROADMAP (2026-07-02).** Ce document a servi à **ouvrir** le programme
> `Sx_UI`. Il n'est **plus la source vivante** de l'état d'avancement. La **source actuelle de vérité**
> (ce qui est clos / partiel / superseded / à construire / à ne pas construire, + la build queue
> résiduelle) est **`docs/strategy/Sx_UI_12_UI_TRANSFORMATION_RESIDUAL_RECONCILIATION_SPEC.md`**.
> Ce document est **conservé tel quel** comme trace d'ouverture ; ne pas s'y fier pour les statuts.

Synthèse actionnable dérivée des brainstorms `brainstorm/UI_TRANSFORMATION_BRAINSTORM_V1_normalized.md` et `brainstorm/UI_TRANSFORMATION_BRAINSTORM_V2_normalized.md`. Ce document remplace les brainstorms comme **source unique** pour la roadmap. Les brainstorms restent archivés pour traçabilité et matière brute d'inspiration ; ils ne pilotent pas les specs directement.

## 1. Position actuelle

- Gate `PROD_STABILIZATION_PROFILE_BODY_COACH_REPORT` **signé** le 2026-07-02 : verdict `PROD STRUCTURALLY STABLE FOR UI RENOVATION` (cf. `docs/OPS_PROD_STABILIZATION_PROFILE_BODY_COACH_REPORT.md` §10).
- SHA `1e4cd4c` live en prod, `BODY_INTELLIGENCE_ENABLED=true`, smoke structurel externe vert.
- **UI renovation débloquée** au niveau autorisation.
- **Mini-gate `PROD_DOGFOOD_57KG_LIVE_CHECK` pending** (dette prod critique — Annexe D du gate OPS). Ne bloque **pas** les specs UI mais reste à jouer.
- **Aucun code UI applicatif n'a encore été modifié** dans cette phase.

## 2. Direction produit retenue

Direction fusionnée à partir des recommandations convergentes V1 et V2 :

- **Positionnement :** application de **performance corporelle minimaliste**, `strength-first`, langage clinique-instrumental (pas wellness, pas hardcore-gym).
- **Priorité fonctionnelle :** friction de logging quasi nulle (héritée de Strong / Hevy). Le mode séance reste le cœur.
- **Territoire visuel :** hybride **Clinical Lab + Quiet Instrument** (V2). Concrètement :
  - fond blanc / blanc cassé, gris pierre en surface secondaire ;
  - un seul accent froid (bleu minéral OU teal chirurgical OU vert menthe très désaturé — à trancher dans `Sx_UI_02`) ;
  - typographie hiérarchisée, peu de tailles, mono pour les métriques ;
  - zéro gradient « AI », zéro 3D, zéro illustration héroïque, motion très discrète ;
  - séparateurs fins, cartes qui ressemblent à des panneaux de mesure.
- **Contrainte de plateforme :** WCAG 2.2 tap targets `44×44` CSS px étendus au shell global (déjà présent dans le focus mode Sx_29).
- **Contrainte d'architecture :** SSR FastAPI + Jinja **conservé**, no-JS fallback **préservé**, aucun changement de stack (pas de React, pas de SPA, pas de bundler). PWA maturité via `Sx_UI_08`, pas via réécriture native.
- **Méthode :** migration par couches, **pas de big bang**. Aucun sprint UI ne modifie la logique métier (scoring, substitution, coach_report, body_intelligence, overload_engine, recommendation).

## 3. Nom / rebrand — Auren

- **Nom cible :** **Auren** (V1 recommandation « plus premium, plus Apple Health que gym app »).
- **Statut :** direction de rebrand **documentée**. Aucun renommage code, aucun changement de marque dans les templates, la config, le manifest, les tests, la DB, systemd, DNS.
- **Rebrand réel :** réservé au sprint `Sx_UI_10_rebrand_migration_spec`, exécuté **après** validation de `Sx_UI_04` (Session Focus Reskin) au minimum. Un rebrand exécuté avant stabilisation du langage visuel casserait la reconnaissance sans bénéfice.
- **Alternatives brainstorm considérées :**
  - V1 finalistes : Teral / Nerva / **Auren** ← retenu
  - V2 finalistes : MYON / VYON / RATEL — non retenus (registre plus brut ou plus abstrait, moins aligné avec la posture « premium santé-tech » recherchée)
- **Disponibilité juridique / domaine :** hors-scope de ce document. À valider dans `Sx_UI_01_brand_foundation_spec` avant tout engagement copy/marketing.

## 4. Queue de specs UI

Ordre strict d'exécution. Chaque spec est docs-only jusqu'à son sprint `Sb_UI_NN.k` associé. Les sprints d'implémentation sont ouverts sous override explicite après validation de la spec.

| Ordre | Spec | Objet | Précondition | Peut modifier code ? |
|---|---|---|---|---|
| 1 | `Sx_UI_01_brand_foundation_spec` | Nom Auren, tone of voice, slogan court, principes visuels autorisés/interdits, disponibilité juridique/domaine à vérifier | Gate OPS ✅ | Non (docs) |
| 2 | `Sx_UI_02_design_tokens_spec` | Palettes (surfaces, texte, accent unique), typo, rayons, bordures, ombres, espacements, états, chart tokens, mono pour métriques | Sx_UI_01 | Non (docs) |
| 3 | `Sx_UI_03_app_shell_navigation_spec` | Top bar, bottom nav ≤ 4 entrées, safe areas, breadcrumb de contexte, réduction du chrome global | Sx_UI_02 | Non (docs) |
| 4 | `Sx_UI_04_session_focus_reskin_spec` | Refonte visuelle du flow séance existant (Sx_29). Aucun changement moteur/routes/données. Application des tokens Sx_UI_02 dans `session_focus.css`. | Sx_UI_03 | Oui, **surface uniquement** (CSS + templates rendu, jamais services) |
| 5 | `Sx_UI_05_today_readiness_home_spec` | Écran d'entrée orienté « quoi faire aujourd'hui » ; hiérarchie signal / contexte / interprétation | Sx_UI_04 validé | Oui (surface) |
| 6 | `Sx_UI_06_exercise_intelligence_presentation_spec` | Présentation recommendation, overload hint, historique récent, explainer — **présentation** de l'intelligence existante, jamais modification | Sx_UI_05 | Oui (surface) |
| 7 | `Sx_UI_07_history_progress_spec` | Historique, tendances, PR, volume, cycles, comparaisons — lecture calme, non gamer | Sx_UI_06 | Oui (surface) |
| 8 | `Sx_UI_08_portability_installability_spec` | Manifest PWA peaufiné, icônes propres, install prompt, offline ciblé sur séance active, raccourcis OS | Sx_UI_07 | Oui (manifest + service worker minimal, aucune SPA) |
| 9 | `Sx_UI_09_accessibility_motion_spec` | WCAG 2.2 contraste, tap targets, focus visible, reduced motion, aria, comportement no-JS. Peut être joué en **parallèle** dès `Sx_UI_04`. | parallèle possible | Oui (surface + attributs) |
| 10 | `Sx_UI_10_rebrand_migration_spec` | Mapping Spignos → Auren : templates, config, manifest, .env, docs, tests, DB (si applicable), systemd, CSS class prefixes, code applicatif. Écran de transition. | Sx_UI_04 minimum validé | Oui, **scope infra + code** |
| 11 | `Sx_UI_11_screenshot_regression_spec` | Golden screens mobile/desktop, critères de non-régression visuelle. Requis **avant** Sx_UI_04 pour baseline, puis maintenu en continu. | parallèle continu, requis avant Sx_UI_04 | Oui (tests/CI) |

**Note sur `Sx_UI_11`** : bien qu'énuméré en position 11, ce sprint doit produire une baseline de screenshots **avant** que `Sx_UI_04` ne modifie visuellement quoi que ce soit. C'est le seul chevauchement d'ordre autorisé.

## 5. Règles de gouvernance

Applicables à **tous** les sprints du cycle Sx_UI :

- **Specs first :** aucun `Sb_UI_NN.k` d'implémentation n'est ouvert avant validation de la spec `Sx_UI_NN` correspondante.
- **Docs-only pour l'ingestion :** l'ouverture d'un cycle et le premier sprint SPEC restent docs-only.
- **Aucune mutation métier :** un sprint UI ne modifie **jamais** `scoring/`, `substitution.py`, `coach_report.py`, `body_intelligence.py`, `overload_engine.py`, `overload_inputs.py`, `overload_explainer.py`, `recommendation.py`, `reco/`, `implicit_signal.py`, `quality_score.py`, `body_tracking.py`. Sanity check obligatoire via `git diff --name-only` en fin de sprint.
- **Screenshot regression obligatoire** avant toute refonte visuelle large. `Sx_UI_11` produit la baseline.
- **Préserver SSR + Jinja + no-JS fallback.** Aucun sprint UI n'introduit React, framework SPA, bundler applicatif, ou dépendance runtime lourde. JS vanilla progressive enhancement uniquement, comme `Sx_29`.
- **44 × 44 tap targets** conservés et étendus. Tout composant nouveau doit passer ce seuil.
- **Un accent unique.** Aucun sprint UI n'introduit une deuxième couleur d'accent. Un ajout d'accent nécessite un amendement `Sx_UI_02bis` explicite.
- **Rebrand exécuté à `Sx_UI_10` uniquement**, jamais par touches successives.
- **Mini-gate `PROD_DOGFOOD_57KG_LIVE_CHECK`** reste dette prod critique en parallèle. Un échec de ce mini-gate suspend le cycle UI courant jusqu'à correction Sx_30.

## 6. Interaction avec les autres cycles

- **Sx_30 (Progressive Overload Engine)** : TECHNICALLY CLOSED + DOGFOOD PASS local. Mini-gate live-data (57 kg) pending. `Sx_UI_06` doit consommer les données Sx_30 sans modifier l'engine.
- **Sx_31 (Body Intelligence v2)** : TECH CLOSED. Route `/body/intelligence` + snapshot coach + carte profile-body-intel-link livrés. `Sx_UI_07` doit préserver les 7 blocs + badges Mesuré/Dérivé/Inféré/Hors de portée.
- **Cycle Body Intelligence (Sb Body 01, 02, 03+)** : indépendant. `Sb Body 02.1` shell mergé, flag OFF. Aucun sprint UI ne touche `BODY_ASSESSMENT_ENABLED` ni `BODY_CAPTURE_QUALITY_ENABLED`.
- **Sx_32 / PWA / Health API / Sb Body 02.2** : restent **BLOQUÉS** (override séparé requis pour chaque). `Sx_UI_08` (PWA maturity) ne préempte pas Sx_32.

## 7. Points de décision restants avant `Sx_UI_01`

À trancher avant l'ouverture de la première spec :

1. **Registration du nom Auren** — vérifier disponibilité domaine (`.com`, `.app`) et bases marques (INPI/EUIPO/USPTO) avant de figer le nom dans `Sx_UI_01`.
2. **Accent unique final** — bleu minéral vs teal chirurgical vs vert menthe désaturé. Décision `Sx_UI_02` mais préférence à indiquer dans `Sx_UI_01`.
3. **Order de bottom nav ≤ 4 entrées** — quelles 4 destinations survivent (candidates V2 : Séance, Programmes, Progression, Profil ; les autres passent en menu secondaire). Décision `Sx_UI_03`.
4. **Baseline screenshots** — outils (Playwright, puppeteer, autre) et périmètre (mobile 360×640 + desktop 1440×900 ?). Décision `Sx_UI_11`.

## 8. Références brainstorm

- Diagnostic complet + benchmarks (Strong, Hevy, Levels, Oura, WHOOP, Apple Health, Ultrahuman, Fitbod) : `brainstorm/UI_TRANSFORMATION_BRAINSTORM_V1_normalized.md` et `brainstorm/UI_TRANSFORMATION_BRAINSTORM_V2_normalized.md`.
- Traçabilité mojibake + doublon V3 : `brainstorm/INDEX.md`.

## 9. Pointeurs registry

- Cycle enregistré dans `docs/strategy/SPEC_REGISTRY.md` sous « Cycle Sx_UI — Auren Visual & Product Transformation (SPEC PENDING) ».
- Position dans `docs/strategy/ROADMAP_AND_NEXT_STEPS.md` : UI renovation débloquée avec caveat mini-gate 57 kg.
