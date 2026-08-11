# SPRINT Sb_32.4 — Migration des consommateurs vers BodyZone (RAPPORT)

**Base canonique :** `0fd0502` · **Branche :** `sb/32-4-bodyzone-consumer-migration` ·
**Tier :** `check_scope` **SHARED_CODE**, **traité au tier pratique le plus élevé hors migration**
(SOURCE_OF_TRUTH) comme l'exige la spec — **full sweep obligatoire, aucun raccourci de sélection**.
**Autorité de spec :** `Sx_AUREN_ORCHESTRATOR_01_GAP_CONSOLIDATION_SPEC.md` **§P0.3** (§C.1).
**P0.3 du train `AUREN_P0_CORRECTNESS` — la tranche la plus risquée.**
**0 migration Alembic · 0 nouvelle table · 0 changement de schéma · 0 taxonomie publique modifiée ·
0 mutation de donnée utilisateur.**

## 1. Matrice des consommateurs — produite AVANT d'écrire du code

Audit en lecture seule du code actif (preuves `fichier:ligne`), pas des anciens rapports.

### A — lit déjà la table formelle

| Consommateur | Preuve | Lourd ? | `exercise_code` disponible ? |
|---|---|---|---|
| `body_map_descriptor._resolve_zones` | `:45-64` → `_classify_exercise_by_lookup` | oui (Worked Area) | **oui** (passé par le routeur) |
| `body_map_descriptor._label_for` | `:67-81` — **seule lecture de `BodyZone`** du repo | oui | n/a (clé = zone) |
| `routers/sessions.py` | `:339-343`, passe `actual_exercise_name(se)` | oui | **oui** |

### B — classifieur par sous-chaîne (le gros du parc)

| Consommateur | Preuve | Lourd ? | `exercise_code` ? |
|---|---|---|---|
| **`muscle_scoring._compute_tonnage_by_zone`** | `:89` | **oui — primitive racine du scoring** | **oui**, `db` déjà en portée |
| `profile_metrics._zone_session_counts` | `:205` | oui | oui |
| `recommendation._primary_zones_of` | `:181` | oui | oui **mais bloqué** : `@lru_cache` sur un tuple hashable, une `Session` ne peut pas entrer dans la clé |
| `recommendation.build_signals` | `:362` | oui | oui |
| `session_recap._zones_touched` | `:126` | moyen | oui **mais** `build_recap` n'a **pas** de `Session` en paramètre |
| `coach_report._zones` / `coach_inference` | `:183-196` / `:44-91` | oui | non (agrégats, plus d'identité d'exercice) |
| `body_intelligence` / `body_intelligence_inputs` | axes radar | oui | non |
| `dashboard._score_progression` | `:172-192` | oui | hérite de `muscle_scoring` |
| `scripts/catalog_qa.py` | `:212`, `:237`, `:303` | non | **à ne pas migrer** : c'est un garde *du classifieur* |

### C — EKB JSON · D — `exercise_properties` JSON

`program_quality_engine` (C, `zone_primary` détaillé) · `user_program_exercise_catalog` (C) ·
`substitution` (D, `zone_primary` **macro**) · `profile_metrics.dominant_pattern` (D) ·
`morpho_program_generator` (D).

⚠️ **Piège confirmé** : la clé `zone_primary` porte **deux vocabulaires différents** — 11 zones
détaillées dans l'EKB, 6 axes macro dans `exercise_properties`. Ne jamais les confondre.

### E — taxonomies à NE PAS migrer

`pattern_motor` / `chain` / `equipment_family` / `muscle_group` (substitution, morpho) ·
`focus_candidates` de `morphology_profile` · slots `E1…E7` · `machine_family` ·
`catalog_section` — dont la valeur `"core"` **collision de nom** avec la zone `core`.

### Le fait d'identité qui conditionne tout

`ExerciseMuscleMapping.exercise_code` contient le **nom** de l'exercice, pas un code
(`app/models/exercise_muscle_mapping.py:6-13` : « the current catalog has no stable per-exercise
code — `code` in `reference_split.json` is a training-day slot (E1…E7), reused across exercises »).
Donc **`SessionExercise.exercise_code_snapshot` est un leurre** : la clé de lookup est
`actual_exercise_name(se)`. C'est écrit dans l'adaptateur et dans le consommateur migré.

## 2. Brainstorming / Options / Risques / Choix retenu (`CLAUDE.md §3`)

### Le seed est-il nécessaire ? — **prouvé, pas supposé**

La spec pré-autorise un seed applicatif « **si le préflight prouve qu'il est nécessaire** ». Mesuré :

| Scénario | `body_zones` | `exercise_muscle_mappings` |
|---|---|---|
| `alembic upgrade head` seul | **11** | **87** |
| `create_all()` seul | **0** | **0** |
| `create_all()` **puis** alembic | l'upgrade **échoue** (`method_rules already exists`) — n'atteint jamais `head` |
| **Boot applicatif réel** (fixture `client`) | **0** | **0** |

Le dernier est décisif. `init_db()` fait `create_all()`, et `app/models/__init__.py` importe
`body_zone`, `muscle`, `exercise_muscle_mapping` — donc **tout boot crée les tables vides**, et les
backfills Alembic, gardés sur « est-ce moi qui viens de créer cette table ? », ne peuvent plus
jamais s'exécuter.

**Conséquence** : sans seed, migrer un consommateur vers la table formelle, c'est le migrer vers
une **table vide** — il retomberait sur le substring dans **100 %** de la suite de tests et sur
tout environnement où l'app crée son schéma. La migration serait **inerte et improuvable**. La
production n'est correcte que par **accident d'ordonnancement** (`deploy_prod.sh` lance alembic
avant l'app).

**Seed nécessaire : PROUVÉ.** Coût mesuré : **~1 ms** par base neuve (0,30 ms de classification +
0,62 ms d'insertion groupée). Pas de régression de coût CI.

### Options de migration

| # | Option | Verdict |
|---|---|---|
| A | Chaque consommateur interroge la DB lui-même | **Rejetée.** C'est la maladie actuelle (5 tables de zones dupliquées, dont une déjà divergente). La spec l'interdit : « Do NOT duplicate DB query logic across consumers ». |
| B | Big-bang : migrer les 12+ consommateurs | **Rejetée.** La spec préfère explicitement « one correctly migrated vertical slice + reusable adapter + exhaustive parity proof ». Deux consommateurs sont d'ailleurs **structurellement bloqués** (§1). |
| C | Étendre `body_map_descriptor` en service central | **Rejetée.** La spec interdit de le reconstruire ; c'est le chemin étroit qui marche, on n'y touche pas. |
| D | **Adaptateur unique + seed + parité exhaustive + UN consommateur lourd migré** | **Retenue.** |

### Consommateur migré : `muscle_scoring._compute_tonnage_by_zone`

C'est **la primitive racine du scoring** : elle alimente le tableau de bord physique, les cartes
de zones Body Intelligence et le KPI du dashboard. Elle a `db` en portée et le nom à l'appel —
**zéro plomberie**. Les deux autres candidats évidents sont bloqués : `recommendation` par son
`@lru_cache` (une `Session` ne peut pas entrer dans une clé de cache), `session_recap` par
l'absence de `Session` dans sa signature. Les migrer aurait demandé de changer leur architecture,
ce que la spec n'autorise pas ici.

### Risques et traitement

| Risque | Traitement |
|---|---|
| Migrer vers une table vide | Seed prouvé nécessaire, testé, idempotent |
| Le seed écrase des données utilisateur | **Impossible par construction** : il n'importe que `BodyZone` et `ExerciseMuscleMapping`. Un test lit la **source** et échoue si un modèle possédé ou un `delete(` y apparaît. Plus deux tests de comptage sur sessions/exercices/séries/utilisateurs/programmes. |
| Le seed corrompt une base déjà peuplée | Insert-only + réconciliation **bornée** à la liste revue. Rien d'autre n'est jamais réécrit. |
| Regeler les erreurs connues | Corrigées, avec **preuve issue du repo** (§3) |
| Divergence inexpliquée | La parité échoue et c'est un **HARD STOP** — un test injecte une correction périmée pour prouver que le harnais mord |
| Retomber en silence sur le substring | Chaque réponse porte son `resolution_path` ; un test pinne que le chemin migré lit bien `db_lookup` |

## 3. Les deux erreurs connues — corrigées, avec preuve du repo

La spec interdit de regeler aveuglément une erreur connue et impose de classer chaque divergence.
Les deux sont **catégorie 1 — correction intentionnelle appuyée par des preuves canoniques** ; les
preuves sont des **données du repo**, pas mon avis.

### « Rear delt fly machine (pec deck inversé) » : `pecs` + `triceps` → **`delt_post`**

`_EXERCISE_PATTERNS` est une liste **ordonnée** et le groupe `pecs` (index 0) contient
`"pec deck"` : la parenthèse décide avant que le groupe `delt_post` (index 2) soit atteint.
**Le repo se contredit lui-même** : l'entrée EKB porte `machine_slug: rear-delt-fly-machine` et
`machine_family: shoulders-lateral-posterior` — **identiques** à l'entrée « Rear delt fly machine »
tout court, que l'EKB classe `zone_primary: delt_post`. Même machine, même famille, deux verdicts :
la différence est un **artefact de nommage**, pas de l'anatomie.

### « Relevé de jambes suspendu » : `calves` → **`core`**

Le groupe `calves` (index 9) contient le jeton nu `"relevé"`, préfixe de `"relevé de jambes"` ; le
groupe `core` (index 10) liste `"relevé de jambe"` **et** `"hanging"` mais n'est jamais atteint.
**Le catalogue tranche** : `reference_split.json` place cet exercice dans le template `liss-abs`,
dont le `focus` est littéralement **« Core / Abdos »** (== `ZONE_LABELS["core"]`), aux côtés de
`Roulette abdominale`, `Crunch câble à genoux` et `Pallof press câble` — **tous trois** classés
`core`.

**Aucune divergence inexpliquée n'a été rencontrée**, donc la condition de HARD STOP de la spec
n'a pas été atteinte.

## 4. Ce qui est livré

### 4.1 `app/services/body_zone_source.py` — le contrat de lecture canonique

`resolve_exercise_zones(db, name) -> ZoneResolution`. Ordre : **correction revue → ligne formelle
`ExerciseMuscleMapping` → classifieur substring**. Le repli est conservé (le référentiel n'est pas
couvert à 100 %, et les consommateurs non migrés en dépendent) mais il **ne peut jamais écraser**
la table formelle : il ne s'exécute que si celle-ci n'a rien à dire.

Chaque réponse porte son `resolution_path` (`reviewed_correction` / `db_lookup` /
`substring_fallback` / `unknown`) : le repli est **visible**, jamais silencieux.

**La requête n'est pas dupliquée** : le module **réutilise**
`muscle_mapping._classify_exercise_by_lookup`. Prouvé **par comportement** (espion monkeypatch),
pas par un grep fragile.

`find_ambiguous_mappings` est la seule requête propre au module — un **audit d'intégrité**, pas un
second chemin de classification : la clé unique étant `(exercise_code, body_zone_code, role)`, deux
zones **différentes** peuvent coexister en `primary`, et le lookup choisirait alors la première par
`position, id` — stable, mais arbitraire. On le signale au lieu de le trancher.

### 4.2 `KNOWN_MAPPING_CORRECTIONS` — liste de divergences revue et testable

Deux entrées, chacune portant `legacy_primary/secondary`, la valeur corrigée et son **evidence**.
Machine-testable : un test vérifie que chaque entrée **cite fidèlement** ce que le classifieur rend
réellement — une correction qui décrit mal ce qu'elle remplace n'est plus revuable et casse.

### 4.3 `app/services/reference_data_seed.py` — le chemin de peuplement

**Déterministe** (aucune horloge, aucun aléa, référentiel trié) · **idempotent** (rejouable à
chaque boot et à chaque déploiement) · **données de référence uniquement** · **dérivé de la
taxonomie canonique** : les zones viennent des dicts de `muscle_mapping` (la dérivation *exacte* du
backfill Alembic, donc les deux s'accordent par construction et non par copie), les exercices du
classifieur canonique sur le référentiel canonique.

**Rien n'est inventé pour gonfler la couverture** : un exercice que le classifieur rend `unknown`
est **laissé non couvert** (2 cas, §5).

**Réconciliation bornée** : une base déjà peuplée par Alembic porte les deux lignes fausses ;
l'insert-only les laisserait en place pour toujours. La réconciliation ne touche **que** les
exercices nommés dans la liste revue — ce n'est délibérément **pas** un « aligne toute la table sur
la dérivation », qui effacerait en silence une future curation manuelle. Les lignes périmées sont
**désactivées, pas supprimées** : l'attribution historique reste auditable dans la table.

### 4.4 `app/database.py` — appel du seed après `create_all()`

Douze lignes de commentaire expliquant *pourquoi*, avec les chiffres mesurés.

### 4.5 `app/services/muscle_scoring.py` — le consommateur migré

`_compute_tonnage_by_zone` lit le contrat au lieu d'appeler le classifieur. Rien d'autre ne bouge :
pondération des zones secondaires à 0,3, filtres de session, tonnage, `hard_sets` — inchangés.

### 4.6 `scripts/bodyzone_parity_qa.py`

Sort en non-zéro sur divergence inexpliquée (1) ou mapping ambigu (2). Les mappings manquants sont
**rapportés, pas échoués**. Pas de modification de workflow CI (ce serait un tier `ci_infra`) : les
mêmes assertions tournent dans les tests, donc la CI couvre le contrat.

### 4.7 Garde retargetée dans `tests/test_exercise_muscle_mapping.py`

`test_no_consumer_service_file_changed` comparait `git diff --name-only HEAD` : il **passait au
vert dès le commit** et n'assertait donc **rien** en CI. Il datait de `Sb_32.2` et sa docstring
désignait `Sb_32.4` comme le sprint qui migrerait les consommateurs — **c'est ce sprint**.
Il est **renforcé, pas affaibli** : la nouvelle forme lit la source et pinne que `muscle_scoring`
lit le contrat et que **les six autres consommateurs listés ne le lisent pas**. Une future
migration devra être une décision revue, pas une dérive. Contrairement à l'ancienne, cette garde
mord en CI, pour toujours.

## 5. Preuve de parité — référentiel complet

Référentiel canonique = union `exercise_knowledge_base.json` ∪ `exercise_properties.json` = **105**
exercices distincts.

```
total exercises        : 105
exact matches          : 103
intentional divergences: 2      (les deux corrections revues)
unexplained divergences: 0      ← critère d'acceptation
missing formal mapping : 2
ambiguous mappings     : 0      ← critère d'acceptation
```

**Couverture formelle : 103/105.** Les deux non couverts sont `Incline DB Press 30°` et
`Incline Dumbbell Press` : le classifieur, francophone, les rend `unknown`. Ils sont **rapportés
comme manquants**, pas mappés — leur inventer une zone pour afficher 105/105 est exactement ce que
la spec interdit. Ils continuent de passer par le repli substring, donc **rien ne régresse** ; ils
n'y gagnent simplement pas encore d'attribution formelle.

**Point de contexte important** : le backfill Alembic avait été produit **bug pour bug** depuis le
classifieur — mesuré, **0 divergence** entre le substring et les 65 lignes DB. La parité n'est donc
pas une coïncidence : les seules divergences possibles sont celles que ce sprint introduit
**volontairement**, et elles sont les deux corrections documentées.

## 6. Vérifications locales

| Contrôle | Résultat |
|---|---|
| Tests dédiés `test_bodyzone_consumer_migration.py` | **39 passés** |
| Substitution + morphologie + Martin + dogfood | **144 passés** |
| Coach · BI · profil · scoring · dashboard · worked area · P0.1 · P0.2 | **250 passés** |
| **Full sweep parallélisé** (exigé, aucun raccourci) | **3147 passés, 0 échec** |
| `scripts/bodyzone_parity_qa.py` | **OK** — 0 inexpliquée, 0 ambiguë |
| ruff (fichiers neufs + touchés) | **clean** |
| Budget ruff | **544 ≤ 548** |
| `check_spec_protocol` | **PASS** |

**Zéro régression sur 3146 tests** pour la tranche la plus risquée du train. Cohérent avec la
parité : hors les deux corrections délibérées, la sortie est inchangée partout.

*Note de mesure : le wall-clock du full sweep passe de 2:20 à 3:23, mais la suite gagne aussi
38 tests et cette machine est bruitée (des écarts de 279/386/533 s ont déjà été observés sur une
charge comparable pendant `Sb_CI_02_2`). Le coût du seed a été mesuré isolément à **~1 ms par base
neuve** ; le chiffre qui fait foi reste la CI GitHub.*

## 7. Non-régressions et interdits tenus

**Interdits de la spec, tous tenus** : `body_map_descriptor` **non reconstruit** (un test pinne
qu'il ne passe pas par l'adaptateur) · `substitution.py` non modifié · comportement du générateur
morpho non modifié · structure EKB non modifiée · `recommendation.py` non modifié ·
**0 nouvelle table · 0 migration · 0 changement de schéma · 0 changement de taxonomie publique** ·
aucune mutation de donnée utilisateur · aucune duplication de la logique de requête · pas de repli
substring silencieux dans le chemin migré · pas de migration de plusieurs consommateurs « pour
faire du chiffre ».

**Interdits du train, tous tenus** : pas de force-push, pas de rebase, pas de squash, pas de merge
`--admin`, `AGENTS.md` non touché, flag Body Intelligence inchangé, aucun déploiement, aucune
incertitude scientifique affaiblie, aucune revendication médicale.

### 7bis. Finding Sonar traité in-scope (PR #77)

**Gate externe `SonarCloud Code Analysis` en ÉCHEC** au premier passage :
`new_code_smells_severity 15 > 14`, **une seule** issue — `external_ruff:F401`,
`subprocess imported but unused` dans `tests/test_exercise_muscle_mapping.py`.

Vrai résidu de ma part : en retargetant la garde du §4.7, j'ai supprimé le **seul** usage de
`subprocess` du fichier sans retirer l'import. Le **budget ruff local ne l'a pas attrapé** parce
que F401 fait partie de la dette tolérée (70 occurrences pré-existantes) — Sonar, lui, le compte
comme un smell **neuf**. Import retiré ; budget **544 → 543**, donc strictement **neutre** vs la
canonique. Un diagnostic, un correctif.

*Leçon : le budget ruff plafonne un **total**, il ne protège pas contre l'ajout d'une occurrence
d'une règle déjà en dette. Sur du code neuf, c'est le gate Sonar qui fait foi.*

### 7ter. Finding Gitar traité in-scope (PR #77) — régression N+1 réelle

**Constat, et il est juste** : en migrant `_compute_tonnage_by_zone`, j'ai remplacé un classifieur
**purement en mémoire** par un appel qui **interroge la base**, à l'intérieur de la boucle
`for s in sessions / for se in s.session_exercises`. Sur la primitive racine du scoring, c'est un
**N+1 manuel** : le même nom d'exercice est re-requêté à chaque série de chaque séance de la
fenêtre. Une fenêtre de 90 jours à 40 séances × 6 exercices, c'est ~240 requêtes pour une
vingtaine de noms distincts.

**C'est une régression que j'ai introduite**, pas un défaut préexistant : l'ancien chemin ne
coûtait aucune requête.

**Correctif** : mémoïsation **par nom distinct**, **par invocation**. Le cache vit le temps d'un
appel, donc il ne peut pas servir un mapping périmé d'une requête HTTP à l'autre. Test ajouté :
3 séances × 2 exercices = **6 séries pour 2 noms distincts** ⇒ **exactement 2 résolutions**
(espion sur l'adaptateur). Avant le cache, ce test comptait 6.

## Verdict

**Livré.** `ExerciseMuscleMapping` / `BodyZone` deviennent la source de vérité d'un **vrai
consommateur lourd** — la primitive racine du scoring — à travers **un contrat unique et
réutilisable**, avec un **chemin de peuplement fiable** dont la nécessité a été **prouvée par la
mesure** et non supposée, et une **preuve de parité exhaustive** sur les 105 exercices du
référentiel canonique.

Les deux erreurs d'attribution connues **ne sont pas regelées en silence** : elles sont corrigées,
chacune adossée à une contradiction interne du repo, et la liste des divergences est courte,
revue et machine-testable.

| Critère d'acceptation de la spec | État |
|---|---|
| ≥ 1 consommateur lourd migré sur le contrat DB | ✅ `muscle_scoring._compute_tonnage_by_zone` |
| Chemin de peuplement fiable | ✅ seed déterministe et idempotent, nécessité prouvée |
| Preuve de couverture/parité complète | ✅ 105 exercices, 103 exacts, 2 corrections |
| Zéro divergence inexpliquée | ✅ 0 |
| Aucune mutation de donnée utilisateur | ✅ gardes de source + de comptage |
| 0 schéma / 0 table / 0 taxonomie publique | ✅ |
| Erreurs connues non regelées en silence | ✅ 2 corrigées avec preuve |
| `body_map_descriptor` intact | ✅ pinné par un test |
| Sémantique de substitution intacte | ✅ 144 tests |

**Surfaces restant en source de vérité partagée** (non migrées, délibérément) : `recommendation`
(bloqué par `@lru_cache`), `session_recap` (pas de `Session` en signature), `profile_metrics`,
`coach_report` / `coach_inference`, `body_intelligence*`, `dashboard`, plus les consommateurs EKB
et `exercise_properties`. Chacun reste un pas suivant **explicite**, protégé par la garde
retargetée du §4.7.

## Closeout — ✅ MERGED + CANONICAL CI GREEN

**PR #77 MERGÉE.** Base canonique `0fd0502` → build `aa04bd3` → correction Sonar `f64acd4` →
correction Gitar N+1 `46126ab` → **merge `246ed0a`** via `--merge --match-head-commit 46126ab…` —
**sans squash, sans `--admin`, sans force**. Gate re-vérifié **autoritativement juste avant** le
merge : head SHA confirmé, `CLEAN` / `MERGEABLE`, **5/5 checks** (dont le gate **externe**
`SonarCloud Code Analysis`), gate Sonar **`OK`**, **0 thread non résolu**.

**CI canonique `31495540887` — 3/3 GREEN** sur `246ed0a`.

**Deux findings, deux corrections réelles** — aucun n'a été justifié plutôt que corrigé :
le smell Sonar (§7bis, import mort laissé par le retarget de la garde) et surtout la **régression
N+1 que ce sprint avait introduite** (§7ter), signalée par Gitar et confirmée : j'avais remplacé un
classifieur en mémoire par une requête DB **dans une double boucle**, sur la primitive racine du
scoring. Mémoïsation par nom distinct, par invocation, plus un test qui compte les résolutions.

**Statut final : `Sb_32.4_BODYZONE_CONSUMER_MIGRATION MERGED + CANONICAL GREEN + CLEANED`.**
P0.3 close. **Train `AUREN_P0_CORRECTNESS` COMPLET.** Canonique : `246ed0a`.
