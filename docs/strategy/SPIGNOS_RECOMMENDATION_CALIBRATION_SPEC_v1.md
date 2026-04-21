# SPIGNOS Recommendation Calibration Spec v1

**Sprint ID :** Sx_13_recommendation_calibration_spec
**Date :** 2026-04-21
**Statut :** SPEC ONLY — aucun code engagé par ce document
**Prérequis :** Sb_12 livré (commit `91c54b1`), 683 tests verts, moteur déterministe en place sur `/` et `/launcher` step 1
**Successeur :** Sb_13_recommendation_telemetry_and_tuning (proposé §M)

---

## A. Statut du document

Spec courte, opérationnelle, alignée avec le moteur déjà en place. Objectif : définir **comment mesurer que la reco tape juste**, **quels paramètres ajuster**, et **quelle instrumentation minimale** ajouter pour rendre la calibration possible sans sur-ingénierie.

Pas de nouveau moteur. Pas de ML. Pas d'extension produit (programme-builder, squad v2) — spécifiquement hors scope.

## B. Contexte système actuel

[`app/services/recommendation.py`](../app/services/recommendation.py) expose aujourd'hui :

- `recommend_next_session(db, user_id, now) -> dict | None`.
- Scoring 4 composants : `WEIGHT_STALENESS=40`, `WEIGHT_ALTERNATION=20`, `WEIGHT_REDUNDANCY_PENALTY=-5`, affinité catalogue `15/10/20` + bonus cardio absent `+10`.
- Fenêtre staleness `7j`, fenêtre redundancy `48h`, fenêtre spécialisation `14j`.
- Filtres pré-scoring : `archived` exclu, fatigue > 70 → short/LISS only, redundancy > 8 hard_sets/48h → exclu.
- Fallback garanti : cold-start (< 3 séances lifetime) → premier core ; pool vide → premier LISS.
- Phrase d'explication composée dans `_build_phrase` depuis 7 slots, cap 140 chars, jamais vide.
- Surfaces : partial `_partials/next_session_reco.html` inclus sur `/` et `/launcher` step 1.
- POST `/sessions` (router `sessions.py:78-99`) crée la séance depuis un `template_slug` Form.

**Toutes les constantes de calibration sont déjà centralisées** en tête de `recommendation.py` (§D1 du rapport Sb_12). La barrière à l'ajustement est faible : changer un chiffre, relancer les tests.

Ce qui **manque** pour calibrer :

1. Aucune trace côté serveur de **comment** la séance a été créée (reco top, alternative, picker, `/library`, `?preselect=...`).
2. Aucune agrégation sur les taux d'acceptation / contournement.
3. Aucun seuil documenté pour juger « la reco marche » ou « elle déraille ».
4. Aucun protocole formalisé de passe dogfooding ciblée sur ce sujet.

## C. Problème produit

> Le moteur de recommandation vit ou meurt sur la qualité perçue de ses suggestions. Sans instrumentation, **on ne peut pas savoir** si les constantes par défaut (40/20/−5/15) sont bonnes, si une phrase revient trop souvent, ou si le filtre fatigue se déclenche à bon escient.

Symptômes potentiels qu'on ne détecte pas aujourd'hui :

- La suggestion principale est systématiquement ignorée au profit d'une alternative → signe que le scoring se trompe de top-1.
- Les alternatives sont rarement ouvertes → le `<details>` est peut-être trop discret, ou les phrases d'alternatives pas différenciantes.
- L'utilisateur passe par `/library` sans regarder la reco → la surface home n'est pas convaincante.
- La phrase « Suite naturelle après ton historique récent » revient 5 fois sur 7 → fallback générique trop fréquent, slots spécifiques mal calibrés.
- Le filtre fatigue (> 70) déclenche alors que l'utilisateur est en forme → fatigue_score mal calibré en amont ou trop agressif.

**Conséquence si non traité :** on ouvrirait un gros chantier suivant (programme-builder Sx_11b, 15-20h) au-dessus d'un moteur de reco dont on ignore s'il apporte de la valeur ou s'il fait du bruit.

## D. Pourquoi calibrer avant d'étendre le produit

Trois raisons :

1. **Valeur produit marginal** — les 4-6h de Sb_13 livrent une boucle d'amélioration permanente pour la reco. Les 15-20h de Sx_11b livrent une feature orthogonale qui ne profite pas de la reco non-calibrée.
2. **Risque d'enraciner un défaut** — si la reco tape mal et qu'on empile par-dessus programme-builder, le `UserTemplate` futur héritera d'un moteur dont la qualité est inconnue. Debugger a posteriori est plus cher.
3. **Discipline Sx** — on ne sait pas encore si les 4 composants du scoring sont bien pondérés. Ouvrir un chantier produit avant cette validation, c'est ignorer un signal déjà annoncé dans Sx_12 §M (« calibrage V1 mal ajusté » est le premier risque listé).

**Ordre d'attaque correct :** Sb_13 d'abord, puis **une** passe de dogfooding structurée, puis arbitrage Sx_11b ou Sx_11c.

## E. Protocole de dogfooding recommandé

**Durée cible : 7 jours consécutifs.**

**Participants V1 :** l'utilisateur unique (toi) en mode observation structurée. Pas d'élargissement.

**Setup :**
- Sb_13 déployé avec l'instrumentation §J.
- Un fichier `docs/DOGFOOD_SB_12_NOTES.md` créé au démarrage de la passe, tenu chaque jour.
- Aucune modification du moteur pendant la passe — les constantes restent figées sur les valeurs V1.

**Rituel quotidien (< 2 min) :**
1. Ouvrir `/`, lire la reco, noter la phrase.
2. Décider : accepter, voir alternatives, ou ignorer.
3. Si contournement (`/library` ou `/launcher` direct), noter le template finalement choisi **et pourquoi**.
4. Après la séance, noter si le choix final a semblé juste en rétrospective.

**Métriques à produire à la fin :**
- 7 observations minimum.
- Taux brut d'acceptation reco top-1.
- Phrases répétées plus de 2 fois sur 7.
- Cas où la reco a paru clairement hors-piste (avec raison).

**Livrable de la passe :** 1 page `docs/DOGFOOD_SB_12_NOTES.md` listant les 7 observations et une conclusion qui oriente la calibration Sb_13.x suivante.

## F. Mesures / indicateurs minimaux

**Cible V1 : 4 indicateurs, lisibles, exploitables en lecture directe de la DB.**

### F.1 `reco_acceptance_rate`
Proportion de sessions créées via `reco_source = "reco_top"` sur l'ensemble des sessions créées dans la fenêtre. **Seuil sain indicatif : > 40 %** sur une semaine. < 20 % = moteur probablement hors cible.

### F.2 `alternatives_open_rate`
Proportion de pages home où le `<details>` alternatives a été déplié. **Non mesurable en SSR pur sans JS** — donc, en V1.5, **on ne mesure pas ce signal directement**. On l'infère via `alt_click_rate` (voir F.3).

### F.3 `alt_click_rate`
Proportion de sessions créées via `reco_source = "reco_alt"` sur le total des démarrages depuis home/launcher. **Seuil sain indicatif : 10–25 %**. Si > 40 %, le top-1 se trompe ; si < 5 %, les alternatives ne servent à rien ou ne sont pas explorées.

### F.4 `bypass_rate`
Proportion de sessions créées via `/library` ou `/launcher` step ≥ 2 (picker complet) **alors que la home offrait une reco non-expirée**. **Seuil sain : < 30 %**. > 50 % = la reco est perçue comme inutile.

**Métrique bonus, passive :**

### F.5 `phrase_repetition_rate`
Combien de fois la **même phrase exacte** revient sur les 10 dernières recommandations top-1 servies. **Seuil sain : ≤ 3 répétitions**. Au-delà, slot `signal_primaire` trop générique.

**Non retenu V1.5 :**
- Temps entre ouverture home et clic CTA (nécessiterait JS).
- Heatmap, scroll depth, dwell time (hors philosophie SSR).
- Satisfaction déclarative post-séance (friction cognitive).

## G. Paramètres calibrables

Tous déjà centralisés en tête de `recommendation.py`. Calibration = changer une valeur, relancer la suite.

| Constante | Valeur V1 | Effet si augmentée | Effet si diminuée | Priorité tuning |
|-----------|-----------|--------------------|-------------------|-----------------|
| `WEIGHT_STALENESS` | 40 | Pousse plus vite vers zones fraîches | Favorise les templates préférés récents | **Haute** |
| `WEIGHT_ALTERNATION` | 20 | Force cardio après 2 strength | Laisse l'utilisateur enchaîner strength | Moyenne |
| `WEIGHT_REDUNDANCY_PENALTY` | −5 | Coupe plus strict les zones fraîches < 48h | Permet redoubler une zone | Haute |
| `AFFINITY_CORE` | 15 | Biaise vers les 6 templates core | Laisse utility/specialization remonter | Moyenne |
| `AFFINITY_UTILITY` | 10 | Favorise short/LISS | Les cantonne davantage | Faible |
| `AFFINITY_SPECIALIZATION_OK` | 20 | Les catch-up remontent plus vite | Les catch-up sortent rarement du top-1 | Haute si peu de spec-hits observés |
| `STALENESS_SATURATION_HARD_SETS` | 8 | Zone jugée sat à partir de plus de sets | Zone jugée sat plus vite | Moyenne |
| `STALENESS_WINDOW_DAYS` | 7 | Mémoire plus longue | Mémoire plus courte, oublie plus vite | Basse — cohérent avec la semaine |
| `REDUNDANCY_WINDOW_HOURS` | 48 | Repousse tout re-stimulation à > 48h | Permet des pairings serrés | Moyenne |
| `REDUNDANCY_HARD_SETS_CUTOFF` | 4 | Pénalise plus de zones | Plus permissif | Moyenne |
| `FATIGUE_HIGH_THRESHOLD` | 70 | Dégrade moins souvent | Dégrade plus souvent | **Haute** — effet visible immédiat |
| `CARDIO_ABSENT_BONUS_DAYS` | 7 | LISS poussé moins agressivement | Pousse LISS plus tôt | Moyenne |
| `COLD_START_LIFETIME_SESSIONS` | 3 | Allonge la phase cold-start | Sort plus vite du fallback | Faible |
| `SPECIALIZATION_STALE_RATIO` | 0.5 | Spécialisation déclenche moins souvent | Déclenche plus souvent | Haute si catch-up jamais présent |
| `SOFT_RESTART_GAP_DAYS` | 14 | Reprise douce après plus longtemps | Plus rapidement en reprise | Basse |
| `ALTERNATIVES_COUNT` | 2 | Plus d'alternatives | Moins | Faible — 2 suffit pour V1.5 |

**Hors de ce tableau :** la structure même du scoring (les 4 composants) n'est pas calibrable via constante — la changer reviendrait à refaire le moteur. Si le dogfooding montre qu'un 5ᵉ composant est nécessaire (ex. prise en compte de la readiness quotidienne), ce serait un Sx_14 dédié, pas une calibration.

### G.1 Phrase explicative — calibration éditoriale

La phrase n'est pas paramétrable par constante, mais les **templates de slots** (§J de Sx_12) peuvent être réécrits. Points d'ajustement observés en dogfooding :
- Fréquence trop élevée de `"Suite naturelle après ton historique récent → {name}"` → ajouter un slot plus spécifique.
- Phrase cold-start toujours la même (acceptable — cold start est rare et court).
- Phrase cardio absente vs phrase fatigue haute — s'assurer qu'une seule se déclenche à la fois (priorité respectée dans `_build_phrase`).

## H. Options d'interaction utilisateur légère comparées

Trois pistes évaluées pour enrichir le signal de rejet.

### Option H1 — Rien ajouter (signal passif)

L'utilisateur qui ignore la reco et va dans `/library` envoie déjà un signal fort via `reco_source != "reco_top"`.

- **Pour :** zéro friction UX, aucune nouvelle surface, cohérent avec la philosophie anti-interruption.
- **Contre :** on ne sait pas **pourquoi** l'utilisateur a bypass — mauvaise reco, envie du jour, mood, raison externe.

### Option H2 — Bouton discret « pas cette suggestion »

Un lien texte sous la reco, type `"Cette suggestion ne me convient pas aujourd'hui →"` qui redirige vers `/launcher` et enregistre un flag `reco_rejected` sur la session suivante (anonyme, agrégé).

- **Pour :** capture explicite du rejet, lisible, pas de scroll visuel.
- **Contre :** une nouvelle interaction à tester, ajoute du bruit au bloc reco. L'utilisateur peut développer une aversion au lien lui-même.

### Option H3 — Modale de raison après bypass

Si l'utilisateur a vu la reco puis a démarré via `/library`, à la création de la prochaine session, une modale courte propose 3 raisons (« pas envie aujourd'hui / déjà fait hier / autre »).

- **Pour :** signal riche.
- **Contre :** friction maximale, modale = anti-pattern SSR, risque d'agacement. **Rejeté d'office.**

## I. Arbitrage recommandé

**Option H1 retenue pour V1.5.** Le signal passif (`bypass_rate` + `alt_click_rate`) suffit pour distinguer « reco juste » de « reco mauvaise ». Ajouter H2 serait tentant mais :

- Le volume utilisateur V1 est faible (1 personne) — le signal passif est aussi clair qu'un signal explicite.
- Le bouton « pas cette suggestion » crée une surface de rejet qui biaise l'utilisation : on clique pour le principe, pas parce qu'on est vraiment contre.
- Peut être ajouté en V2 si le dogfooding montre que le bypass ne suffit pas à diagnostiquer.

**Décision :** pas de feedback actif en Sb_13. Instrumentation passive uniquement.

## J. Stratégie de build suivant

### J.1 Instrumentation minimale — ce qu'il faut ajouter

**Un seul champ DB sur `workout_sessions`** :

| Champ | Type | Nullable | Valeurs attendues |
|-------|------|----------|-------------------|
| `creation_source` | `String(16)` | oui | `"reco_top"`, `"reco_alt"`, `"launcher"`, `"library"`, `"replay"`, `NULL` |

**Migration alembic additive.** Nullable, pas de backfill requis (les séances pré-Sb_13 resteront `NULL` — traitées comme « inconnu » par les agrégations).

Route `POST /sessions` accepte un champ Form optionnel `creation_source` et le persiste tel quel si la valeur est dans l'enum toléré ; sinon `NULL`. Pas de validation stricte — c'est un signal analytique, pas un invariant.

### J.2 Templates à enrichir

- `_partials/next_session_reco.html` — ajouter un `<input type="hidden" name="creation_source" value="reco_top">` dans le formulaire CTA principal. Les liens alternatives pointent vers `/launcher?preselect={slug}&creation_source=reco_alt` (le router récupère et relaie).
- `launcher.html` step 3 (choix final du template) — ajouter `<input type="hidden" name="creation_source" value="launcher">`.
- `library.html` (si un CTA démarre une séance) — `name="creation_source" value="library"`.

### J.3 Nouvelle vue analytique (sans UI)

Un **script CLI** `scripts/reco_calibration_report.py` qui :
- Calcule `reco_acceptance_rate`, `alt_click_rate`, `bypass_rate` sur fenêtre (7j par défaut, paramétrable).
- Liste les 10 dernières phrases distinctes servies + leur compte (proxy pour `phrase_repetition_rate`).
- Produit un rapport texte court en stdout.
- Pas de nouvelle route, pas de dashboard.

**Pourquoi script CLI et pas page web** : la passe dogfooding V1 est une observation locale par l'utilisateur unique. Une page `/admin/reco` dégraderait le focus produit. Le script reste un outil offline, cohérent avec `catalog_qa.py` et `machine_atlas_qa.py`.

### J.4 Persistance de la phrase servie

Pour calculer `phrase_repetition_rate` sans réinventer l'historique, **on ne persiste pas** la phrase servie dans la DB (trop spécifique, biaise la structure). On la **recalcule** à la demande dans le script : pour chaque session avec `creation_source='reco_top'`, on rejoue `recommend_next_session` à la date `started_at` et on lit la phrase du résultat.

**Limite assumée :** la phrase recalculée peut différer légèrement de celle réellement affichée (si les signaux ont bougé entre l'affichage et le POST). Acceptable pour une calibration qualitative. Si ce flou gêne, persister la phrase dans un champ optionnel dédié serait envisageable V2.

### J.5 Calibration — boucle manuelle

Aucun tuning automatique. Le processus est :
1. Laisser le système tourner 7 jours avec les constantes V1 figées.
2. Exécuter `scripts/reco_calibration_report.py` à J+7.
3. Lire les 4 indicateurs + les notes de dogfooding.
4. Décider **une ou deux** modifications de constantes (pas plus — changer trop de choses à la fois détruit la lisibilité du signal).
5. Commiter les nouvelles valeurs dans `recommendation.py`, relancer la suite, re-déployer.
6. Boucle suivante de 7 jours.

Trois exemples de décisions-types que la calibration pourrait produire :

- `alt_click_rate > 45 %` → le top-1 tape faux. Probable cause : `WEIGHT_STALENESS` trop haut ou `AFFINITY_CORE` dominant. Action : baisser `AFFINITY_CORE` de 15 → 10 ou `WEIGHT_STALENESS` de 40 → 30.
- `bypass_rate > 50 %` → la reco est invisible ou mauvaise. Action : revoir la surface (pas la logique) ou investiguer un bug d'affichage via une observation directe.
- `"Suite naturelle après ton historique récent"` apparaît 4/10 → le fallback de `_build_phrase` se déclenche trop souvent. Action : ajouter un slot spécifique avant le fallback (ex. « 3 zones fraîches → X »).

### J.6 Tests

- `tests/test_recommendation_telemetry.py` — 4–5 tests :
  - Création de session via reco_top persiste `creation_source='reco_top'`.
  - Via picker → `'launcher'`.
  - Via library → `'library'`.
  - Valeur invalide → `NULL`.
  - Champ absent → `NULL` (backward-compat).
- `tests/test_reco_calibration_report.py` — 2–3 tests sur le script (fixture 10 sessions, vérifier les taux calculés).

## K. Risques

| Risque | Probabilité | Impact | Mitigation |
|--------|-------------|--------|-----------|
| Instrumentation biaise le comportement (utilisateur adapte son usage en sachant qu'il est tracké) | Moyen | Faible | Signal passif, pas de UI supplémentaire, pas de retour visible côté utilisateur |
| Volume V1 insuffisant pour statistiquement significatif | Élevé | Moyen | Accepter les indicateurs comme qualitatifs, pas quantitatifs. 7 jours × 1 utilisateur = signal indicatif, pas statistique |
| Changement de constantes qui casse la reco (effet boule de neige) | Faible | Moyen | Tests unitaires figés (11 de Sb_12) capturent la logique cœur. Si un changement de constante casse un test, on relit avant de commit |
| Migration `creation_source` pose problème en prod | Faible | Faible | Additive, nullable, pas de backfill — risque rollback trivial |
| Script CLI devient un substitut à l'observation utilisateur | Moyen | Faible | Le protocole §E impose les **notes manuelles** d'abord, le script vient valider numériquement |
| On calibre trop finement et on overshoot dans l'autre sens | Élevé | Faible | Règle §J.5 : **une ou deux** modifs de constantes par cycle, jamais plus |
| La phrase recalculée post-hoc diverge de la phrase affichée | Moyen | Faible | Limite assumée §J.4. Persister la phrase possible en V2 si nécessaire |

## L. Acceptance criteria Sx_13

| Critère | Statut |
|---------|--------|
| Problème produit articulé (§C) | ✓ |
| Justification calibration > extension (§D) | ✓ |
| Protocole dogfooding 7j documenté (§E) | ✓ |
| 4 indicateurs minimaux définis avec seuils (§F) | ✓ |
| 16 constantes calibrables cartographiées (§G) | ✓ |
| 3 options d'interaction comparées, 1 retenue (§H, §I) | ✓ |
| Stratégie build Sb_13 cadrée : 1 migration additive, 1 script CLI, ~5 tests (§J) | ✓ |
| Risques listés et mitigés (§M) | ✓ |
| Zéro IA, zéro refonte, zéro extension produit parallèle | ✓ |
| Aligné avec moteur Sb_12 déjà en place | ✓ |

## M. Recommandation explicite du build suivant

### Sb_13 — Recommendation Telemetry & Tuning

**Scope (≤ 6h) :**
- **New migration** `20260421_add_creation_source.py` — colonne `creation_source String(16) NULL` sur `workout_sessions`.
- **Modify** `app/models/session.py` — champ correspondant.
- **Modify** `app/routers/sessions.py::create_session` — accepter et persister `creation_source` optionnel (whitelist stricte : ignore si invalide).
- **Modify** `app/templates/_partials/next_session_reco.html` — hidden input `creation_source="reco_top"` sur CTA principal, `"reco_alt"` dans les liens alternatives (via query string pré-câblée + relais côté router).
- **Modify** `app/templates/launcher.html` step 3 — hidden `"launcher"`. `app/templates/library.html` si CTA démarrage → hidden `"library"`.
- **New** `scripts/reco_calibration_report.py` — CLI qui consomme les constantes centralisées + sessions récentes, produit le rapport 4 métriques + top phrases.
- **New** `tests/test_recommendation_telemetry.py` (5 tests) + `tests/test_reco_calibration_report.py` (3 tests).
- **New** `docs/SPRINT_Sb_13_recommendation_telemetry_and_tuning_BUILD_REPORT.md`.

**Hors scope Sb_13 :**
- Aucun tuning effectif des constantes (on laisse 7 jours tourner avant).
- Pas de dashboard admin.
- Pas de persistance de phrase.
- Pas de bouton « pas cette suggestion » (Option H2 différée).
- Pas de reco V2 ni d'ajout de composants au scoring.

**Effort estimé Sb_13 :** 4–6h (migration + model + router 1h30, templates 1h, script CLI 2h, tests 1h, report 30 min).

**Critères d'acceptation Sb_13 :**
1. Création via CTA reco top persiste `creation_source='reco_top'`.
2. Création via alternative persiste `'reco_alt'`.
3. Création via picker complet `'launcher'`, via library `'library'`.
4. Valeur absente ou invalide → `NULL`.
5. `scripts/reco_calibration_report.py` renvoie un texte lisible avec les 4 métriques + top 10 phrases.
6. Full suite verte (attendu 683 → ≈ 691).
7. Migration testée en local avec `alembic upgrade head` et `alembic downgrade -1`.

**Après Sb_13 :** passe dogfooding 7j (§E), puis arbitrage produit :
- Si la reco est perçue juste → **Sx_11b programme-builder** (extension fonctionnelle).
- Sinon → **Sx_13.1 calibration cycle** (nouveau passage de constantes).

---

## Annexe — Terminologie stricte

| Terme | Sens |
|-------|------|
| **reco top** | La suggestion principale, unique, servie au-dessus du picker |
| **alternative** | Une des 2 propositions dans le `<details>` sous la reco top |
| **bypass** | Lancer une séance sans passer par la reco (via `/library` ou `/launcher` step ≥ 2) |
| **creation_source** | Chaîne persistée sur `workout_sessions` indiquant d'où la séance a été lancée |
| **calibration** | Ajustement manuel des constantes de `recommendation.py` après observation |
| **instrumentation** | Ajout minimal permettant de tracer l'origine d'une session sans changer la logique du moteur |
| **passe dogfooding** | Période fixée (7j) d'observation structurée par l'utilisateur unique, débouchant sur un document de conclusions |
