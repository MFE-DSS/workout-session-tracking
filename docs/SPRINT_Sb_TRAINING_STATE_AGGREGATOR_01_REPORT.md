# SPRINT Sb_TRAINING_STATE_AGGREGATOR_01 — Agrégation en lecture seule (RAPPORT)

**Base canonique :** `c53ee7c` · **Branche :** `sb/training-state-aggregator-01` · **Tier :**
**ISOLATED** (`check_scope`) — traité **avec broad sweep ciblé sur toutes les dépendances importées**.
**Autorité de spec :** `Sx_RECOVERY_READINESS_01_SPEC.md` §2.5, §4, §12bis.
**Tranche 3/5 de la file P0.4.** **Dépendances :** `Sb_RECOVERY_CONTRACT_01`,
`Sb_CARDIO_FATIGUE_ADAPTER_01`, `Sb_32.4` — toutes mergées, canonique verte.
**0 migration · 0 table · 0 colonne · 0 UI · 0 modif `recommendation.py`/`behavioral.py` ·
0 estimation de récupération · 0 décision.**

## 1. Le défaut trouvé pendant le build — et pourquoi il compte

Le premier passage des tests a échoué sur *un utilisateur tout neuf* : `sufficiency = PARTIAL`
au lieu de `INSUFFICIENT`, parce que `strength_component` valait **0.5**.

Cause : `behavioral.compute_weighted_fatigue([])` rend `_DEFAULT_FATIGUE = 50.0` quand
**l'historique est vide**. Je l'avais fait passer tel quel par `normalize_legacy_fatigue`
→ 0.5 → « evidence présente ». **Un utilisateur sans une seule séance recevait une composante de
fatigue fabriquée.** C'est exactement le *fail-open* que tout ce train existe pour supprimer, et je
l'avais réintroduit.

### Pourquoi une sentinelle de valeur ne suffisait pas — mesuré, pas supposé

| Cas | Valeur rendue | Productible par de vraies déclarations ? |
|---|---|---|
| Historique vide | **50.0** | **NON** — l'ensemble productible est {15, 30, 45, 60, 75} et leurs combinaisons convexes |
| Séances présentes, **aucune déclaration** | **45.0** | **OUI** — `good` + `low` donne exactement 45.0 |

Donc `50.0` serait une sentinelle propre, mais **`45.0` est ambiguë** : la valeur seule ne distingue
pas « l'athlète a dit se sentir bien » de « personne n'a répondu ». Les deux cas sont des
fabrications, et un seul est détectable au nombre.

**Correctif** : `_has_recent_declaration` — une requête légère qui **miroite la sélection** du
producteur (ses 3 dernières séances complétées non exclues, **dans la fenêtre** — voir §7bis)
uniquement pour demander *« au moins une déclaration existe-t-elle ? »*. Si non,
`strength_component = None`. Le producteur n'est ni recalculé, ni repondéré, ni dupliqué.

Preuve que la garde mord : la retirer fait échouer **3 tests**.

## 2. Matrice de source — audit du code actif, avant d'écrire

| Signal | Table / modèle | Requête | Normaliseur canonique | Champ `TrainingState` | Donnée manquante |
|---|---|---|---|---|---|
| Readiness déclarée | `ReadinessEntry` | `ORDER BY recorded_on DESC LIMIT 1` | `normalize_readiness_scale` · `readiness_sufficiency_for_age` · `mean_of_present` | `readiness.*` | pas d'entrée ⇒ `INSUFFICIENT`, tout `None` |
| Fatigue accumulée | via `behavioral.compute_behavioral_state` | son propre `last_3` + **1 requête de garde** (§1) | `normalize_legacy_fatigue` | `fatigue.strength_component` | pas de déclaration / producteur en erreur ⇒ `None` |
| Déclaration post-séance | `WorkoutSession.global_state` / `.concentration` | la plus récente de la fenêtre | `normalize_session_feedback` | `fatigue.subjective_component` | les deux `None` ⇒ `None` |
| Cardio | `WorkoutSession.cardio_*` | la plus récente de la fenêtre | `cardio_load_estimate` | `fatigue.cardio_component` | pas de cardio ⇒ `None` |
| Exercice → zone | `ExerciseMuscleMapping` via `Sb_32.4` | `resolve_exercise_zones`, **mémoïsée par nom distinct** | contrat `Sb_32.4` | `_ZoneEvidence` (hors `TrainingState`) | non résolu ⇒ zone ignorée |
| Zones exposées par le cardio | table du `Sb_CARDIO_FATIGUE_ADAPTER_01` | `cardio_zone_exposure` | contrat cardio | `_ZoneEvidence` | modalité vague ⇒ aucune zone |
| Équipement | **aucune source** | — | — | `equipment = None` | voir §5 |
| Agenda | **aucune source** | — | — | `schedule = None` | voir §5 |

**Aucun calcul n'est recopié.** Ce module possède les *requêtes* et l'*assemblage* ; jamais une
formule.

### Deux constats sur `behavioral` qu'un consommateur doit connaître

1. **Il n'existe aucun producteur de fatigue dérivé de la charge dans ce dépôt.**
   `behavioral.fatigue_score` vient de `global_state`/`concentration` — des **ressentis déclarés**,
   pas du tonnage ni des séries. `strength_component` est donc le producteur **subjectif accumulé**
   canonique, pas une lecture mécanique.
2. **Il n'est pas filtré « strength ».** Sa requête `last_3` n'applique **aucun filtre `kind`** :
   la déclaration d'une séance cardio l'alimente aussi.

Les deux sont inscrits dans la `basis` du signal plutôt que masqués. Les deux composantes d'origine
subjective diffèrent par leur **forme** — accumulation pondérée sur 3 séances contre déclaration la
plus récente — ce qui justifie de les garder séparées ; et comme `FatigueSignal` n'a **aucun
agrégat**, elles ne sont jamais sommées : le recouvrement est une information pour le lecteur, pas
un double comptage dans un nombre.

## 3. Sémantique de construction

`build_training_state(db, user_id, *, now, lookback_days=30)`.

`now` est **obligatoire et keyword-only** : un horodatage caché rendrait le résultat
irreproductible. Un test vérifie que le module ne lit **aucune horloge** (`datetime.now(`,
`date.today(`, `time.time(`).

**Fenêtre : 30 jours**, la notion de « récent » que ce dépôt utilise déjà
(`profile_metrics._eligible_sessions_in_window` et les `days: int = 30` autour). C'est un choix de
**périmètre**, pas une courbe de décroissance : rien ne s'estompe à l'intérieur, rien n'est pondéré
par l'âge.

**Cardio : sélection, pas agrégation.** Ni la spec ni le code actif ne définissent comment combiner
plusieurs séances cardio en un scalaire, et inventer des poids serait inventer une physiologie
cumulative. La **plus récente** est retenue — exactement comme la readiness retient la dernière
entrée — et le nombre d'autres séances en périmètre est **consigné** plutôt que replié dedans.

### Composition `sufficiency` / `confidence` — la règle exacte

Compte des **quatre preuves indépendantes** présentes : la déclaration de readiness *courante*, et
les trois composantes de fatigue.

| Preuves | `sufficiency` | `confidence` |
|---|---|---|
| 0 | `INSUFFICIENT` | `NONE` |
| 1 | `PARTIAL` | `LOW` |
| ≥ 2 | `SUFFICIENT` | `MEDIUM` |

**Aucune arithmétique sur les valeurs** : un `None` n'entre jamais dans une moyenne, une composante
absente n'est jamais lue comme zéro, et un chiffre flatteur ne peut rien remonter puisque le compte
ignore les valeurs. Monotone par construction ⇒ plus de preuves manquantes ne peut que maintenir ou
réduire. Une readiness **périmée n'est pas comptée** comme preuve (elle reste exposée comme
contexte) ⇒ elle ne peut pas remonter l'état. Le cardio seul plafonne à 1 preuve ⇒ jamais
`SUFFICIENT`.

**`Confidence.HIGH` n'est jamais produite.** Distinguer « élevée » de « moyenne » demanderait une
revendication d'exactitude que rien ici ne soutient ; la spec impose alors l'option la plus
conservatrice.

## 4. Preuves exécutées

### Lecture seule — deux garanties, pas une

1. **Niveau source** : aucun `db.add`, `db.delete`, `db.commit`, `db.flush`, `bulk_*`, `.merge(`,
   ni appel à un writer connu (`save_readiness`, `replace_draft_tree`, `publish_user_program`,
   `seed_reference_data`, `init_db`).
2. **Preuve exécutée en base** : snapshot des **comptes ET du contenu** de `users`,
   `readiness_entries`, `workout_sessions`, `session_exercises`, `set_logs`, `user_programs` →
   construction de l'état → re-snapshot → **égalité stricte**.

Planter un `db.commit()` dans l'agrégateur fait échouer **2 tests**.

### Discipline de requêtes — le N+1 qui avait déjà mordu en `Sb_32.4`

**Mesuré** : 8 séances × 9 exercices = **72 occurrences** de **3 noms distincts** ⇒ **13 requêtes**.

Le test qui compte : occurrences **×25** (3 → 75) **à noms distincts constants** ⇒ **le nombre de
requêtes ne bouge pas**. Plus un espion : **60 occurrences ⇒ 3 résolutions**, une par nom distinct.

Mémoïsation **par invocation**, jamais globale : un cache de module sur un état venu de la base
deviendrait périmé dès que les tables de référence changent. Un test interdit `lru_cache`/`@cache`.

Planter la résolution non mémoïsée dans la boucle fait échouer **2 tests**.

### Identité d'attribution

L'attribution passe par le contrat formel `Sb_32.4`, clé = le **nom** de l'exercice.
`SessionExercise.exercise_code_snapshot` est un slot de journée (`E1`…`E7`) réutilisé entre
exercices : un test vérifie que la chaîne n'apparaît **pas** dans le code, et qu'une session dont
tous les slots valent `E1` produit bien des zones distinctes. `substituted_name` reste prioritaire.

## 5. Ce que cette tranche ne fait pas

**`zone_recovery` est vide, volontairement.** Produire un `ZoneRecoveryEstimate` signifie produire
une estimation, une bande et un modèle temporel — les trois appartiennent à
`Sb_ZONE_RECOVERY_ESTIMATE_01`. Les faits bruts dont cette tranche aura besoin sont **récoltés et
exposés séparément** (`zone_evidence_for`) : code de zone, dernier chargement daté, nombre
d'occurrences, exposition cardio évidencée, chemin de résolution. **Ce sont des faits, pas des
conclusions** — un test vérifie que l'objet n'a ni `estimate` ni `band`.

Exposer ces faits **hors** de `TrainingState` est délibéré : rien dans l'objet public ne doit
ressembler à une lecture de récupération. Aucun placeholder numérique n'est fabriqué non plus —
ce serait le *fail-open* du §4.

Un test interdit dans le module : `band_for_estimate`, `RecoveryBand`, `worst_zone_rollup`,
`never_trained_estimate`, `ZoneRecoveryEstimate`, `decay`, `half_life`. **OQ-5 n'est pas exercée** :
`radar_axis_for_zone`, `ZONE_TO_RADAR_AXIS`, `RADAR_AXIS_ORDER`, `MacroAxisRecovery` sont tous
absents — le roll-up macro est de la présentation et appartient aux sorties de récupération.

**Équipement** : `program_quality_engine.UserProfile.available_equipment` est une dataclass
**d'entrée**, sans persistance et **sans aucun constructeur dans l'application** (vérifié). Il
n'existe donc **aucune source autoritative à cette frontière** ⇒ `equipment = None`. Aucun profil de
salle n'est fabriqué. **Agenda** : aucune source persistée en V1 ⇒ `schedule = None`.

## 6. Matrice « données manquantes »

| Cas | Résultat |
|---|---|
| **Utilisateur neuf** (rien du tout) | `INSUFFICIENT` / `NONE` · readiness `None` · **0 composante** · `zone_recovery = ()` · `equipment`/`schedule` `None` |
| **Readiness seule** | readiness peuplée · **aucune** composante de fatigue |
| **Séances sans déclaration** | `strength` **et** `subjective` `None` (§1) |
| **Producteur en erreur** | `strength = None`, **jamais 0.0**, `basis` le dit |
| **Readiness périmée (≥ 3 j)** | conservée comme **contexte**, `STALE` ; `sufficiency`/`confidence` **inchangées** vs sans elle |
| **Cardio seul** | composante cardio peuplée ; jamais `SUFFICIENT` |
| **Dimension readiness hors 1-5** | exclue de la moyenne, **jamais lue comme 0** |
| **Modalité cardio inconnue** | comportement de l'adaptateur préservé, **aucune zone fabriquée** |
| **Hors fenêtre / non complétée / exclue** | ignorée |
| **Données d'un autre utilisateur** | jamais lues |

## 7. Vérifications locales

| Contrôle | Résultat |
|---|---|
| Tests dédiés | **61 passés** |
| Broad sweep ciblé (état · contrat · adaptateur cardio · readiness · behavioral · reco ×2 · fatigue P0.2 · BodyZone P0.3 · zones P0.1 · scoring · dashboard · profil · substitution) | **589 passés** |
| ruff (fichiers neufs) | **clean** |
| Budget ruff | **543 ≤ 548** — **neutre** |
| `check_spec_protocol` | **PASS** |
| `check_scope` | **ISOLATED** |

**Sur le tier.** La mission demande d'escalader en cas de doute. `git status` ne montre que **deux
fichiers neufs** : **aucun fichier existant n'est modifié**, et le module n'est importé par
personne. Le rayon d'impact sur le comportement existant est donc **nul par construction**, et le
broad sweep sur **l'intégralité des dépendances importées** est le garde adéquat. Le full sweep
local n'apporterait aucune information — la CI de PR le joue de toute façon.

**Pré-scan Sonar avant push** (méthode validée en `Sb_CARDIO_FATIGUE_ADAPTER_01`) : un balayage AST
a trouvé le littéral `"completed"` répété 3 fois (`python:S1192`, CRITICAL). Résolu en réutilisant
l'**enum canonique** `SessionStatus.COMPLETED` de `app/enums.py` — meilleur code, pas seulement un
contournement. Zéro `S9073`, zéro `S1244`. Complexité cognitive de `_zone_evidence` signalée à 23
par l'IDE **pendant** l'écriture (`python:S3776`) et décomposée immédiatement en quatre helpers.

## 8. Interdits tenus

`recommendation.py` · `behavioral.py` · modèles · migrations · overload · substitution ·
morphologie · planner · flag Body Intelligence · UI · templates : **aucun touché**. Aucune table,
aucune colonne, aucun déploiement. Pas de force-push, pas de rebase, pas de squash, pas de merge
`--admin`, `AGENTS.md` non touché. **`Sb_ZONE_RECOVERY_ESTIMATE_01` n'est pas ouvert.**

## 7bis. Finding Gitar (PR #81) — un second fail-open, et il avait raison

**Constat** : `_strength_component` ignorait la fenêtre de 30 jours. `behavioral` n'a **aucun
filtre de date**, donc une seule déclaration vieille de 400 jours peuplait encore
`strength_component`, que `_compose_sufficiency` comptait comme preuve présente — faisant passer un
état par ailleurs vide de `INSUFFICIENT`/`NONE` à `PARTIAL`/`LOW`.

**C'est une contradiction directe avec ma propre règle.** J'avais délibérément écrit qu'une
readiness périmée ne compte pas comme preuve ; et je laissais un entraînement abandonné depuis plus
d'un an le faire. Gitar a aussi noté, à juste titre, que
`test_sessions_outside_the_window_are_ignored` n'assertait que sur `subjective_component` : le
chemin n'était **pas testé**.

**Vérifié avant de corriger** — une séance à J-400 avec `fatigued`/`low` donnait :

```
strength = 0.75 · subjective = None · sufficiency = partial · confidence = low
```

**Correctif** : la fenêtre borne aussi la garde (`_has_recent_declaration`). Même cas désormais :
`strength = None`, `INSUFFICIENT`/`NONE`. Deux tests ajoutés — celui du cas ancien, et celui qui
vérifie que la fenêtre **borne** la garde sans **désactiver** la composante quand une déclaration
récente existe. Retirer la borne fait échouer le test : la garde mord.

**Résidu, énoncé plutôt que masqué** : une fois qu'une déclaration récente existe, la portée
« 3 dernières séances » du producteur peut encore inclure une séance hors fenêtre. C'est la
sémantique du producteur canonique, et réimplémenter sa sélection pour la rogner dupliquerait la
formule que cette tranche ne doit pas toucher. Ce que la garde garantit, c'est que le producteur
n'est **consulté** que s'il existe une preuve déclarée récente.

**Deux fail-opens dans une seule tranche** — l'un trouvé par mes tests, l'autre par la revue. Les
deux ont la même forme : une donnée absente ou périmée rendue comme une preuve présente. C'est le
défaut que ce train combat, et il se réintroduit à chaque frontière si on ne le cherche pas.

## Verdict

**Livré.** Un point d'entrée unique, déterministe et en lecture seule, assemble les preuves vivantes
en `TrainingState` : la readiness déclarée avec son âge, trois composantes de fatigue séparées et
non agrégées, et des faits par zone récoltés pour la tranche suivante — sans une seule estimation.

Le résultat qui compte le plus n'est pas le service : c'est **le fail-open attrapé pendant le
build**. Un utilisateur sans aucune séance recevait une fatigue de 0.5, parce que le producteur
hérité fabrique 50.0 à partir d'un historique vide. Le corriger a demandé de **mesurer** quelles
valeurs sont réellement productibles, de constater que la valeur seule ne suffit pas à trancher
(45.0 est ambiguë), et d'aller vérifier l'existence d'une vraie déclaration. C'est précisément la
classe de défaut que `Sx_RECOVERY_READINESS_01` a été écrite pour éliminer, et elle s'est glissée
dans ma propre première version.

Statut : `Sb_TRAINING_STATE_AGGREGATOR_01 PR GREEN / MERGE PENDING` — puis merge permanent autorisé.
