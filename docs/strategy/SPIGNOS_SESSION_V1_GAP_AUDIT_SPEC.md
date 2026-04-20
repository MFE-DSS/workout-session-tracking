# SPIGNOS Session V1 — Gap Audit Spec

**Sprint ID :** Sx_10_session_v1_gap_audit_spec
**Date :** 2026-04-20
**Statut :** SPEC ONLY — audit d'écart, pas de build engagé par ce document
**Prérequis :** cycle Session System V1 (Sb_05 → Sb_09) et catalogue v12 clos sur la branche `claude/sprint-reporting-fitness-app-V7Qr6`
**Successeur recommandé :** Sb_10_session_v1_polish (build minimal ciblé, voir §I)

---

## A. Statut du document

Audit factuel de l'écart entre l'intention produit formulée dans Sx_05 (Session Flow & Intelligence), Sx_06 (Scoring/Load/Time), Sx_07 (Machine Atlas + Substitution), Sx_08 (Review Intelligence), Sx_09 (Consolidation) et **ce qui est effectivement livré** sur la branche aujourd'hui. Pas de nouvelle décision produit. Pas de nouveau chantier catalogue. Pas de code.

## B. Contexte projet actuel

Branche : `claude/sprint-reporting-fitness-app-V7Qr6`.
Commits pertinents (ordre chronologique, `git log --oneline`) :

```
edd435e  fix(b01): accept comma separator in weight inputs (Sb_06 etape 1)
0183493  fix(b02): render session dates in Europe/Paris timezone (Sb_06 etape 2)
25bf65c  feat(b03): separate scoring for cardio vs strength (Sb_06 etape 3)
c0542d9  feat(c05): discrete load convention hint (Sb_06 etape 4)
cf842df  docs(sb_06): document load convention + scoring + timezone
6ca03a8  docs(sb_06): sprint report — scoring, load & time semantics build
33fabdf  docs(sx_07+sx_08): machine atlas + session review intelligence specs
d617ccb  docs(sx_09): consolidation transverse — phase spec close
054f016  feat(sb_05): session flow horizontal — save-on-prev + Precedent
6924f95  feat(atlas): Sb_07 machine knowledge + substitution surface v1
cb3341c  feat(review): Sb_08 session review intelligence v1
8a533f1  feat(history): Sb_09 visual & analytics alignment v1
b7a43ee  feat(catalog): v12 — balance Pull A per benchmark chantier 3
0110544  docs(catalog): document v12 Pull A balance in governance + fix test name
```

État tests : **635 passés**. `scripts/catalog_qa.py` : PASS (16 templates, 98 exercices, 0 erreur, 0 warning). `scripts/machine_atlas_qa.py` : PASS (8 familles, 29 machines).

## C. Résumé exécutif

Le cycle Session System V1 (Sb_05 → Sb_09) est **livré dans sa quasi-totalité**. Le doute exprimé par l'utilisateur sur le statut de Sb_06 est levé : **Sb_06 a été livré en 4 étapes entre `edd435e` et `6ca03a8`**, avant Sb_05 dans l'ordre chronologique de la branche. La confusion vient probablement d'une absence de Sb_06 dans les résumés récents de session — pas d'un manque de livraison.

Sur les 16 surfaces auditées (voir §F), **11 sont clairement couvertes**, **4 sont partielles** (petits écarts mineurs), **0 est manquante** au sens fort. Les partiels ne justifient pas un gros sprint build ; un polish d'~1-2h suffit (Sb_10 recommandé en §I).

## D. Ce qui est censé avoir été buildé dans Sb_05 → Sb_09 + catalog v12

| Sprint | Intention (rappel concis) |
|--------|--------------------------|
| **Sb_05** | Flow horizontal carte-par-carte, save-on-next, save-on-prev, bouton Précédent, jump bar 4 états, une seule carte active |
| **Sb_06** | Accepter `,`/`.` dans les poids, rendre les dates en Europe/Paris, séparer le scoring strength/cardio, ajouter un rappel discret C05 sur la convention de charge, documenter dans `/science` |
| **Sb_07** | `data/machine_atlas.json` V1 (8 familles), loader in-memory, champs `machine_slug` + `machine_family` sur `template_exercises`, panel `<details>` sur la carte active, drawer substitution avec count, page `/science/atlas` |
| **Sb_08** | 5 règles d'anomalies déterministes, 2 hints contextuels carte active, score de confiance logging 0–100, 4 nouveaux blocs sur `/done`, note exercice repliée en `<details>` |
| **Sb_09** | Timeline et sparkline kind-aware (dots colorés strength vs cardio), légende, export JSON + CSV v2 avec `session_kind` + `quality_score` + `confidence_score` + `confidence_level` |
| **catalog v12** | Pull A enrichi 5 ex / 15 sets → 7 ex / 20 sets (benchmark chantier 3) |

## E. Audit des surfaces réellement inspectées dans le repo

Fichiers ouverts et relus pour produire cette spec :

**Routeurs**
- [app/routers/sessions.py](app/routers/sessions.py) — `session_detail` (calcul jump states, `prev_code_by_exercise`, `atlas_data`, `sb08_hints_by_exercise`), `update_exercise_card` (branche `nav=prev/next`), `session_done` (`prior_weight_by_code` + `_prior_summary`), `science_atlas`
- [app/routers/pages.py](app/routers/pages.py) — `home` (sparkline kinds), `progress` (timeline kinds)
- [app/routers/auth_routes.py](app/routers/auth_routes.py) — `/profile` (timeline kinds)

**Templates**
- [app/templates/session_detail.html](app/templates/session_detail.html) — carte par carte, jump bar, machine-panel, substitute-picker drawer, hints Sb_08, note exercice en `<details>`, footer prev/next
- [app/templates/session_done.html](app/templates/session_done.html) — 4 blocs Sb_08 (confidence badge, top progression, zones touchées, à vérifier)
- [app/templates/progress.html](app/templates/progress.html), [app/templates/profile.html](app/templates/profile.html) — légende timeline kind
- [app/templates/atlas.html](app/templates/atlas.html) — page atlas complète
- [app/templates/science.html](app/templates/science.html) — section « Atlas des machines » + « Convention de saisie des charges »

**Services**
- [app/services/quality_score.py](app/services/quality_score.py) — dispatcher `compute_session_quality` + `session_kind` alias public
- [app/services/anomalies.py](app/services/anomalies.py), [app/services/hints.py](app/services/hints.py), [app/services/confidence.py](app/services/confidence.py) — règles déterministes
- [app/services/session_recap.py](app/services/session_recap.py) — summary étendu
- [app/services/machine_atlas.py](app/services/machine_atlas.py) — loader + lookups
- [app/services/substitution.py](app/services/substitution.py) — `actual_exercise_name`, `can_substitute`
- [app/services/timeline.py](app/services/timeline.py) — `TimelinePoint.kind`, `KIND_COLORS`, sparkline `kinds=`
- [app/services/export_builder.py](app/services/export_builder.py) — `SCHEMA_VERSION = 2`, `session_kind` + confidence dans JSON + CSV
- [app/services/form_parsing.py](app/services/form_parsing.py) — `to_float` accepte virgule + point
- [app/templating.py](app/templating.py) — filtre Jinja `| local`, `local_weekday_iso`

**Modèles**
- [app/models/catalog.py](app/models/catalog.py) — `TemplateExercise.substitutes_json`, `machine_slug`, `machine_family`
- [app/models/session.py](app/models/session.py) — `substituted_name`, `success_score`, `free_note`, fields cardio

**Données**
- [data/reference_split.json](data/reference_split.json) — v12, 16 templates, 98 exercices, **63** avec `machine_slug`, **1** avec `machine_family` only, **34** non liés à l'atlas
- [data/machine_atlas.json](data/machine_atlas.json) — version `2026-04-15.v1`, 8 familles, 29 machines

## F. Matrice « couvert / partiel / manquant »

Légende : ✅ **couvert** = implémenté + testé + documenté | 🟡 **partiel** = présent mais avec écart mineur documenté ici | ❌ **manquant** = absent.

| # | Sujet | Statut | Évidence | Écart (si partiel) |
|---|-------|--------|----------|--------------------|
| 1 | Flow horizontal (navigation carte-par-carte) | ✅ | `session_detail.html:54-66` — `<details>` par slot, `{% if is_active %}open{% endif %}` | — |
| 2 | Carte active unique à l'écran | ✅ | Router `sessions.py:251-265` — un seul `active_exercise_id` résolu par `?active={id}` ou premier incomplet | — |
| 3 | Précédent / Suivant explicites | ✅ | `session_detail.html:343-361` — boutons `name="nav" value="prev/next"` ; router branche dans `update_exercise_card` | — |
| 4 | Save behavior (save-on-next + save-on-prev) | ✅ | Router POST `update_exercise_card` sauve puis redirige avec `?active={target}#exercise-{target}`. Pas de bouton « Enregistrer » séparé sur la carte. | — |
| 5 | Compactage cartes done (recap line sur `<summary>`) | ✅ | `session_detail.html:59-66` — `.exercise-card--done` (CSS bordure verte, code vert), recap `N kg · N reps` visible sur `<summary>` dès `done > 0` | — |
| 6 | Substitution locale à la carte active (drawer + lock) | ✅ | `session_detail.html:140-166` — `<details class="substitute-picker--drawer">` ; `substitution.can_substitute()` lock après 1ʳᵉ série travail ; badge count « N alternatives » visible | — |
| 7 | Prévu vs réalisé préservé dans la donnée | ✅ | Modèle : `exercise_name_snapshot` (prévu, immuable) + `substituted_name` (réalisé, nullable). Export v2 renvoie les deux. | — |
| 8 | Panel info machine sur la carte active | ✅ | `session_detail.html:103-132` — `<details class="machine-panel">` avec `execution_cues`, `common_mistakes`, `load_semantics` depuis l'atlas. **Visible sur toutes les cartes**, pas uniquement la carte active (noté mais intentionnel — sert de « préparation » aussi). | — |
| 9 | Atlas machine livré + page de consultation | ✅ | `data/machine_atlas.json` v1 (8 fam / 29 machines) + route `/science/atlas` + lien depuis `/science` | — |
| 10 | Scoring séparé strength vs cardio | ✅ | `quality_score.compute_session_quality` dispatche sur `template.kind` ; `compute_session_quality_cardio` formule 4 composants (durée/intensité/completion abs/subjectif) ; tests `test_scoring_cardio.py` couvrent les deux branches | — |
| 11 | Timeline & sparkline distinguent strength et cardio | 🟡 | `timeline.KIND_COLORS` dispatche les dots. Légende présente sur `/progress` et `/profile`. | **Légende absente sur le sparkline home** — les dots sont colorés mais aucune explication visuelle sur `/` (voir §H gap G1). |
| 12 | Review `/done` enrichi (confidence, top progression, zones, à vérifier) | ✅ | `session_done.html` — 4 blocs conditionnels rendus depuis `build_recap` ; `confidence-badge` avec 3 niveaux (`eleve`/`moyen`/`faible`) | — |
| 13 | Anomalies + hints contextuels déterministes | ✅ | 5 règles (A/B/C/D/E) dans `anomalies.py` ; 2 hints (A/B) dans `hints.py`, rendus uniquement sur la carte active (`{% if is_active %}` à `session_detail.html:202-215`) | — |
| 14 | Notes / feedback simplifiés (C03 Sx_08) | 🟡 | **Note exercice** est repliée dans `<details class="exercise-card__note">` (`session_detail.html:331-334`). **Note session** reste un `<textarea rows="2">` pleine hauteur (`session_detail.html:450-457`). | Asymétrique : la réduction inline a été appliquée à la carte exercice mais pas au bloc feedback session (voir §H gap G2). |
| 15 | Charges / inputs (décimales + virgule, convention de saisie) | 🟡 | `form_parsing.to_float` accepte `,` et `.` (21 tests). Inputs `type="text" inputmode="decimal" pattern="…"`. Rappel discret C05 visible sur chaque carte. Convention documentée dans `/science`. `load_semantics` présent dans `machine_atlas.json` et surface sur la carte quand la machine est liée. | `load_semantics` **pas dans `data/reference_split.json`** — n'est donc disponible que pour les ~63 exercices liés à l'atlas (sur 98). Les 35 restants (curls, triceps accessoires, core, adducteurs) n'ont ni convention explicite ni rappel contextuel (voir §H gap G3). |
| 16 | Timezone (UTC stocké, rendu Europe/Paris) | ✅ | Filtre Jinja `\| local` défini dans `app/templating.py` ; appliqué dans 7 templates ; `local_weekday_iso` pour éviter les bugs frontière jour. `tests/test_timezone_rendering.py` couvre hiver/été/minuit. | — |

**Bilan matrice :** 12 ✅, 3 🟡 (11, 14, 15), 0 ❌.

## G. Statut explicite de Sb_06

**Verdict : LIVRÉ.**

Sb_06 a été découpé en 4 étapes d'implémentation, toutes commitées sur la branche **avant** Sb_05 dans l'ordre chronologique :

| Étape Sb_06 | Sujet | Commit | Fichiers |
|-------------|-------|--------|----------|
| 1 | Input virgule/point | `edd435e` | `app/services/form_parsing.py`, `app/templates/session_detail.html` (inputs), tests |
| 2 | Timezone Europe/Paris | `0183493` | `app/templating.py` (filtre `local`), 7 templates, `tests/test_timezone_rendering.py` |
| 3 | Scoring dispatcher cardio vs strength | `25bf65c` | `app/services/quality_score.py`, `tests/test_scoring_cardio.py` |
| 4 | Rappel convention de charge (C05) | `c0542d9` | `session_detail.html` (hint sous « Travail »), `science.html` (section complète), `PRODUCT_SPEC.md` |

Les deux commits de documentation (`cf842df`, `6ca03a8`) ferment le sprint. La confusion potentielle de l'utilisateur vient d'un résumé de conversation récent qui n'énumérait que Sb_05/07/08/09 — Sb_06 n'était simplement pas dans le fil visible.

**Rien à rebuilder sur Sb_06.** Un écart résiduel mineur est documenté en §H gap G3 (`load_semantics` absent du catalogue — positionné explicitement en V2 par la spec Sx_06).

## H. Gaps prioritaires

Aucun gap bloquant. Les trois points ci-dessous sont des polish de clôture de cycle — petits, indépendants, livrables en un seul Sb_10.

### G1 — Légende absente sur le sparkline home

**Observé :** `app/routers/pages.py` passe `sparkline_kinds` au builder, qui colore les dots orange (strength) / teal (cardio). `app/templates/index.html` affiche `{{ sparkline_svg|safe }}` **sans légende**.
**Impact :** l'utilisateur voit deux couleurs sans savoir laquelle est laquelle. Cohérent avec `/progress` et `/profile` qui, eux, ont la légende.
**Fix estimé :** 10 min — ajouter les 6 lignes de markup `.timeline-legend` sous le sparkline home, utiliser les CSS classes existantes.

### G2 — Note session non repliée (asymétrie avec note exercice)

**Observé :** `session_detail.html:450-457` rend la note session comme `<textarea rows="2">` visible d'emblée dans le bloc feedback. La note exercice (`session_detail.html:331-334`) est repliée dans `<details class="exercise-card__note">`. Sx_08 §6 recommandait de garder la note session « dans le feedback session (post-séance naturelle) » — c'est défendable, mais inconsistant avec la philosophie « demander moins ».
**Impact :** faible. Produit un bruit visuel sur la carte feedback ; l'utilisateur peut ignorer. Pas de régression analytique.
**Décision à prendre :**
- Option A : garder tel quel et marquer le gap comme « résolu par design » dans la doc.
- Option B : replier en `<details>` comme la note exercice (symétrie).
**Fix estimé si option B :** 10 min.

### G3 — `load_semantics` absent du catalogue pour 35 exercices

**Observé :** `data/machine_atlas.json` porte `load_semantics` ("total" / "per_side") sur les 29 machines. Via la liaison Sb_07, 63 des 98 exercices du catalogue récupèrent cette info et l'affichent sur la carte. Les 35 autres (isolation : curls, triceps, core, adducteurs, shrugs, skull crushers) **n'ont pas** cette métadonnée.
**Impact :** acceptable — ces 35 exercices sont pour la plupart à usage évident (curl haltère = poids d'un haltère). Sx_06 §1.6 avait **explicitement différé** l'ajout d'un champ `load_semantics` sur `reference_split.json` en V2.
**Décision à prendre :**
- Option A : conforme à la spec Sx_06 — ne pas rouvrir.
- Option B : ajouter le champ `load_semantics` sur `reference_split.json` pour les 35 exercices non liés à l'atlas, bump v12 → v13. ~30 min.
**Recommandation :** Option A, **ne pas rouvrir**. La spec Sx_06 a arbitré.

### G4 (information, pas un gap) — Volume de cartes rendues en DOM

**Observé :** `session_detail.html:50` rend **toutes** les cartes dans le DOM, pliées via `<details>`. Pour une séance à 7 exos c'est ~200 lignes HTML. Pas un problème perf (SSR, pas de JS), mais un choix architectural à noter : le lazy-render n'est pas nécessaire tant que les sessions restent ≤ 10 exercices.

## I. Recommandation du prochain build minimal utile

**Sprint proposé : Sb_10_session_v1_polish**

**Scope (<= 1h) :**
1. **G1 — Ajouter la légende kind sur le sparkline home** (`app/templates/index.html`).
2. **G2 option B — Replier la note session dans un `<details>`** pour cohérence avec la note exercice. Marquer le choix dans le commit pour qu'il soit reversible.
3. Pas d'ajout de code service, pas de migration, pas de modification du catalogue, pas d'ajout de tests nouveaux (un test rapide sur la présence de `.timeline-legend` sur `/` suffirait).

**Ce que Sb_10 ne fait pas :**
- Pas d'ajout de `load_semantics` au catalogue (G3 — conforme à Sx_06 qui l'a différé V2).
- Pas de lazy-render de cartes (G4 — pas un gap bloquant).
- Pas de nouvelle feature.

**Critères d'acceptation Sb_10 :**
- [ ] `/` affiche une légende « Musculation / Cardio » sous le sparkline si plus d'une couleur est présente.
- [ ] La note session est dans un `<details>` replié par défaut (ouvert si déjà remplie).
- [ ] Full suite verte (635 inchangé, ou 636 avec un test légende).
- [ ] Sprint report `docs/SPRINT_Sb_10_REPORT.md`.

## J. Risques si on saute les gaps et on ouvre directement un nouveau cycle

| Risque | Probabilité | Impact |
|--------|-------------|--------|
| L'utilisateur découvre G1/G2 en dogfooding et perçoit le cycle V1 comme « inachevé » | Moyen | Moyen — crée de la dette cognitive |
| Un nouveau chantier produit (ex. programme-builder) construit au-dessus d'un flow perçu comme incomplet | Faible | Moyen — rework possible si G2 option B est choisi plus tard |
| `load_semantics` oublié, on recroise le sujet dans 2 sprints sans contexte | Moyen | Faible — bien documenté ici |
| Audit non-fait, intuition utilisateur reste floue, décisions produit suivantes prises sur une base incertaine | Élevé | Élevé — c'est la raison d'être de Sx_10 |

**Recommandation :** faire Sb_10 avant d'ouvrir un Sx_11 sur un nouveau sujet produit.

## K. Acceptance criteria Sx_10

| Critère | Statut |
|---------|--------|
| Intention produit rappelée par sprint Sb_05 → Sb_09 + catalog v12 (§D) | ✓ |
| Surfaces réelles inventoriées avec chemins de fichiers (§E) | ✓ |
| Matrice 16 sujets couvert / partiel / manquant (§F) | ✓ |
| Statut explicite de Sb_06 résolu (§G) | ✓ |
| Gaps prioritaires listés et chiffrés (§H) | ✓ |
| Recommandation prochain build (§I) | ✓ |
| Risques documentés (§J) | ✓ |
| Rapport compagnon `docs/SPRINT_Sx_10_..._REPORT.md` | ✓ |
| Matrice compagnon `docs/strategy/SPIGNOS_SESSION_V1_GAP_MATRIX.md` | ✓ |
| Zéro build engagé par ce document | ✓ |

---

## Annexe — Terminologie stricte utilisée

| Terme | Sens dans ce document |
|-------|----------------------|
| **prévu** | `exercise_name_snapshot` sur `SessionExercise` — figé à la création de la séance |
| **réalisé** | `substituted_name or exercise_name_snapshot` (via `actual_exercise_name`) |
| **carte active** | exercice dont la carte est ouverte dans le DOM (`is_active=True`, `<details open>`) |
| **done** | toutes les séries travail prescrites sont `completed=True` |
| **future** | aucune série travail n'est complétée (et la carte n'est pas active) |
| **substitution** | remplacement de l'exercice prévu par une alternative listée dans `substitutes_json`, persisté dans `substituted_name`, lockable après la première série travail |
| **scoring strength** | `compute_session_quality_strength` — formule à 4 composants (completion, success_score, concentration, global_state) |
| **scoring cardio** | `compute_session_quality_cardio` — formule à 4 composants (durée, intensité BPM, completion abs, subjectif) |
| **confidence** | score 0–100 produit par `compute_confidence_score` évaluant la qualité du logging, indépendant de la performance |
| **review** | la page `/done` et les 4 blocs synthèse qu'elle rend (confidence, top progression, zones touchées, à vérifier) |
| **atlas machine** | `data/machine_atlas.json` + le loader `app/services/machine_atlas.py` + le panel `<details>` sur la carte + la page `/science/atlas` |
