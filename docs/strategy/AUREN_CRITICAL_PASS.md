# `AUREN_CRITICAL_PASS` — deux voies, et le test qui les sépare

> **Statut : `NORMATIF` sur le classement, `PROVISOIRE` sur les gestes.**
> Écrit le 2026-09-06 sur direction d'opérateur, après deux passes de mesure
> — 105 sites cartographiés côté données, 88 données inventoriées côté séance
> active, chaque affirmation « facile » soumise à un contradicteur.
>
> Compagnons obligatoires : `AUREN_INSTRUMENTS.md` (l'ontologie cible) et
> `AUREN_VISUAL_BACKBONE.md` (le langage).

---

## ⚠ ÉTAT D'EXÉCUTION — mis à jour le 2026-09-07

Ce document a été **écrit le 2026-09-06 et versionné seulement le 2026-09-07**.
Il a passé une journée entière dans un worktree non commité, à un `git worktree
remove` de disparaître, alors qu'il porte le classement `NORMATIF` de la passe
critique. Le versionner est la première chose à faire d'un document dont on
dit qu'il fait autorité.

**Ce qui a été LIVRÉ depuis sa rédaction**, et qui rend certaines de ses
sections descriptives du passé plutôt que du présent :

| Tranche | PR | Ce qu'elle ferme dans ce document |
|---|---|---|
| **CP-0** — dead compute `/profile` | #222 | **Voie A (§1) en entier.** Les dix clés mortes et leurs 22 requêtes sur 27 sont retirées ; le cliquet `test_profile_query_budget` fige la route à **5 requêtes, strict dans les deux sens** |
| **CP-1** — lignée temporelle | #223 | **§6 en entier** (`6.A` à `6.H`). `HistoricalSetSignal` porte `performed_at`, `source_session_id`, `substituted_name` ; `OverloadHint` porte `reference_signal`. `BEHAVIOUR CHANGE = NONE` tenu par une garde AST qui interdit au moteur de lire le temps |
| **UI-CP1** — BODY_LEDGER | #226 | La disposition `ABSORB_IN_BODY_LEDGER` de la Voie B, pour la surface `/profile` |

**Ce qui reste OUVERT, et doit être lu comme tel :**

* **§2 Voie B** — la carte de confiance vaut toujours pour les **six autres
  surfaces** ; seule `/profile` est traitée ;
* **§3** — le « **Première fois** » faux du cas B (`exercise_card.html:396`)
  n'est **pas** corrigé : c'est une politique de sélection, hors périmètre de
  CP-1, et une garde fige le comportement en attendant l'arbitrage ;
* **§4 `DATA_TO_UI GAP`** — consigné, toujours non exposé ;
* **CP-3** — toute politique temporelle (seuil, décroissance, désentraînement)
  reste **fermée**. Aucune preuve dans ce dépôt ne fixe un seuil, et la garde
  de frontière l'y maintient.

**Une correction de fond apportée par la vérification adverse**, à ne pas
perdre : sur 60 affirmations de la passe, **29 ont été corrigées**, dont deux
dispositions de ce document même — la guidance de surcharge tombe 1 contre 3
(elle était notée `FIX_NOW`) et Delta est partagée 2 contre 2 (je l'avais dite
tombée). Voir la note de méthode en `§0`.

---

## 0. Le test qui décide de tout

> **CETTE DONNÉE PEUT-ELLE FAIRE PRENDRE À L'UTILISATEUR
> UNE DÉCISION D'ENTRAÎNEMENT DIFFÉRENTE ?**

| Réponse | Destination |
|---|---|
| **oui** | passe critique produit |
| non, et c'est présentationnel | passe d'affinage visuel, plus tard |
| non, et c'est du calcul inutilisé | **DEAD COMPUTE** |

Deux classes de défaut ont été trouvées. **Elles ne doivent pas être fondues
en un « nettoyage de fraîcheur ».** Elles suivent deux voies séparées.

---

## 1. Voie A — DEAD COMPUTE

Tranche d'**hygiène architecturale**, à **zéro changement produit**.

**Objectif** : retirer le calcul dont le résultat n'a aucun consommateur.

**Interdits de cette tranche** : redessiner `/profile` · changer une
information visible · introduire une abstraction produit · se mêler à la
consolidation cockpit.

### 1.1 Les quatre preuves exigées, rendues

| Preuve | Résultat |
|---|---|
| Requêtes SQL | **27 → 5** (−22) |
| Clés de contexte | **19 → 9** (−10) |
| Équivalence de rendu | 19 302 o → 19 302 o, **`SHA₂₅₆` identique** |
| Sweep de régression | **44 fichiers · 1 348 tests · 0 échec** |

La disparition des requêtes est **prouvée au runtime**, pas déduite du retrait
de variables : instrumentation de `before_cursor_execute`, attribution de
chaque requête à sa ligne par la pile d'appel, sur la route réelle.

### 1.2 Les dix clés, et ce qu'elles coûtent

| Ligne | Ce qu'elle calcule | Requêtes | Clé(s) |
|---|---|---|---|
| `:474` | dix courbes SVG, une par champ de mesure | **11** | `measurement_charts` |
| `:390` | qualité de chaque séance sur 30 j | **4** | `quality_svg` |
| `:373` `:384` | séances 30 j en cascade `selectinload` | **3** | `sessions_30d_count` |
| `:358` `:362` `:399` | compteurs et tendance 30 j vs 30 j | **3** | `session_count`, `completed_count`, `trend`, `trend_label` |
| `:485` | **la table des templates en entier** | **1** | `related_templates` |
| — | libellés et ordre d'affichage | 0 | `measurement_labels`, `measurement_fields` |

Les **5 requêtes restantes** sont toutes consommées : `:462` morphologie (2),
`:464` dernière mesure (1), `:517` séance ouverte — lue par `base.html` (1),
et la session d'authentification (1).

### 1.3 Ce n'est pas une découverte, c'est une récidive

Le routeur porte déjà, en commentaire, la trace du même défaut corrigé une
première fois — `UX4_03B` :

> *« `UX4_01` a retiré les modules analytiques du Profil sans retirer le calcul
> qui les alimentait. Le gabarit ne lisait plus aucun champ, mais chaque
> affichage exécutait quand même les requêtes du moteur. »*

**Même défaut, même route, déjà diagnostiqué et déjà réparé.**

### 1.4 Pourquoi le sweep vert est l'argument le plus fort

Aucun test ne tombe. Les fichiers qui *mentionnent* ces noms testent les
**fonctions de service** (`find_related_templates`, `_trend_label`), jamais les
clés de contexte de la route.

**Aucun test n'a jamais observé les dix clés.** Le calcul mort était invisible
à l'ensemble de la suite — c'est exactement pourquoi il a pu revenir, et
pourquoi la troisième occurrence est certaine sans garde.

### 1.5 Portes de non-régression

1. **Équivalence de rendu** — `SHA₂₅₆` du HTML de `/profile` inchangé, pour un
   utilisateur avec mesures et un sans.
2. **Budget de requêtes gelé sur la route** — instrumentation de
   `before_cursor_execute`, refus du dépassement. La plus petite garde
   défendable, et la seule qui attrape la *prochaine* récidive.
3. **Pas de framework « contexte Jinja inutilisé ».** Le dépôt montre pourquoi
   il serait peu fiable : `base.html` lit `active_session`, qu'un balayage
   statique du seul `profile.html` compterait comme morte.

### 1.6 La frontière de périmètre, tracée par la mesure

Neuf imports deviennent orphelins. Les retirer laisse **cinq fonctions de
service sans aucun appelant applicatif** :

| Symbole | Consommateurs `app/` après retrait |
|---|---|
| `build_measurement_timeline_svg` · `get_measurement_series` · `find_related_templates` · `MEASUREMENT_LABELS` · `MEASUREMENT_UNITS` | **0** |
| `build_quality_timeline_svg` · `TimelinePoint` | encore lus par `pages.py` |
| `compute_session_quality` | 16 |

**Signalé, non inclus.** Retirer un appel qui laisse sa fonction sans appelant
déplace le code mort d'un cran ; le retirer aussi est une autre décision, et
l'inclure sans le dire serait de la dérive de périmètre.

---

## 2. Voie B — INFORMATION TRUST

**Le constat de date n'est pas un défaut de gabarit.** Il n'y a pas sept
templates à corriger : il y a un modèle sémantique à poser d'abord.

### 2.1 Le contrat

Un fait d'information peut porter, **quand cela s'applique** :

`VALUE` · `SOURCE` · `OBSERVED_AT` / `PERFORMED_AT` · `WINDOW` ·
`COMPUTED_AT` · `UNKNOWN`

**Aucun champ n'est tenu de tout afficher.** La règle d'interface est unique :

> **NE MONTRER QUE L'INFORMATION TEMPORELLE OU DE PROVENANCE
> QUI PEUT CHANGER L'INTERPRÉTATION OU LA DÉCISION DE L'UTILISATEUR.**

### 2.2 La taxonomie

| Nature | Définition |
|---|---|
| `OBSERVATION` | valeur mesurée ou saisie, valide à un instant |
| `EVENT` | quelque chose qui **s'est produit** à un instant — une série, une séance |
| `DERIVED` | signal calculé sur une **fenêtre** d'observation définie |
| `STATIC_REFERENCE` | donnée dont l'âge n'affecte normalement pas l'interprétation |

### 2.3 La carte

| Datum | Surface | Nature | Poids | Instrument | Disposition |
|---|---|---|---|---|---|
| placeholder « kg » | `exercise_card:98` | `DERIVED` | **DECISION_CRITICAL** | EXECUTION | **FIX_NOW** |
| `Réf. 57,5 kg × 11` | `exercise_card:392` | `EVENT` | **DECISION_CRITICAL** | EXECUTION | **FIX_NOW** |
| relevé de progression | `progression:56` | `EVENT` | USEFUL | FLIGHT_RECORDER | ABSORB_IN_FLIGHT_RECORDER |
| trace 6 points | `progression:70` | `EVENT` | USEFUL | FLIGHT_RECORDER | ABSORB_IN_FLIGHT_RECORDER |
| table morphologique | `profile:241` | `OBSERVATION` | USEFUL | BODY_LEDGER | ABSORB_IN_BODY_LEDGER |
| **taille** | `profile:241` | `STATIC_REFERENCE` | TEMPORALLY_IRRELEVANT | BODY_LEDGER | *pas de date* |
| ratios corporels | `body_overview:33` | `DERIVED` | USEFUL | BODY_LEDGER | ABSORB_IN_BODY_LEDGER |
| `updated_at` programme | `user_programs/detail:15` | `EVENT` | USEFUL | LOADOUT | ABSORB_IN_MISSION |
| `Delta +2,5 kg` | `exercise_card:407` | `DERIVED` | *non tranché* | EXECUTION | DEFER |
| guidance de surcharge | `overload_hint:46` | `DERIVED` | *contesté* | — | **ouvre le MOTEUR** |
| dernier score public | `user_profile:53` | `DERIVED` | USEFUL | SQUAD_CHANNEL | DEFER |
| classement | `squad_detail:29` | `DERIVED` (14 j) | TEMPORALLY_IRRELEVANT | SQUAD_CHANNEL | DEFER |
| les 10 clés `/profile` | `auth_routes:493` | — | — | — | REMOVE_WITH_LEGACY_SURFACE |

### 2.4 Quatre surfaces sur sept ont une sœur qui affiche déjà la date

C'est le défaut « appliqué là où c'était commode », dans sa forme la plus nette
— même donnée, même dépôt, un écran la montre et son jumeau non :

* `body_overview:33` — **le même fichier** rend `measured_at` quatorze lignes plus bas ;
* `user_profile:53` — `days_ago` est rendu **cinquante-cinq lignes plus bas**, pour la même séance ;
* `squad_detail:29` — la sœur `squad_compare.html:44` le rend ;
* `user_programs/detail:15` — la sœur `list.html:41` le rend.

---

## 3. Historique consommé pendant une décision active

**88 données inventoriées · 17 étiquettes « décision-critique » · 29 tombées
sous contestation.**

### 3.1 Le plus grave n'est pas ce que l'utilisateur lit

**C'est ce que le produit propose.**

`overload_engine.py` contient **zéro** occurrence de `days`, `elapsed`,
`weeks`, `timedelta` ou `started_at`. **Le moteur qui suggère la charge est
structurellement aveugle au temps.** `overload_inputs.py:142` remonte
**50 séances sans aucun filtre temporel**.

Le nombre gris pré-inscrit dans le champ « kg » est donc calculé sur un socle
possiblement vieux de plusieurs mois, et présenté à l'identique.

> `Réf.` est une valeur que l'utilisateur **interprète**.
> Le placeholder est une valeur que le produit **propose**.

### 3.2 Pourquoi `Réf.` tient — et pas pour la raison évidente

La réfutation la plus forte est juste : *« personne ne revient sous la barre
après trois mois sans le savoir »*. Une interruption est un fait de vie.

**Ce qui la défait est la politique de substitution.** `stats.py:157-168`
*saute* les occurrences substituées et remonte jusqu'à la dernière occurrence
**prescrite**. L'utilisateur s'est entraîné sans interruption — avec un
substitut, machine occupée — et reçoit un repère de mai.

**L'âge de la référence est découplé de l'absence de l'utilisateur**, et cette
politique est invisible à l'écran. Aucune mémoire, même parfaite, ne permet de
la deviner.

### 3.3 Ce qui est tombé, et pourquoi

| Classe | Pour | Contre | Raison de la chute |
|---|---|---|---|
| `Delta` | 2 | 2 | `curr_done` ne retient que les séries **validées** — le delta n'existe pas encore quand se choisit la charge de S1, la seule décision réellement libre |
| guidance de surcharge | 1 | 3 | `HistoricalSetSignal` ne transporte **ni date ni écart de jours** — la guidance *ne peut pas* être datée ; et pour un verdict `deload`, vétusté et prescription pointent dans le **même sens** |

Le `Delta` reste **non tranché**. Il est consigné tel quel.

### 3.4 Un avertissement qui arrive trop tard

« +X % de charge vs dernière fois — prudence sur l'exécution »
(`hints.py:55`) n'est rendu que sous `cs.is_finished`
(`exercise_card:567`) — **après que la charge a été posée et la série
validée**. Il concerne une décision qu'il ne peut plus informer.

---

## 4. `DATA_TO_UI GAP` — consigné, non exposé

`Occurrence.at: datetime` existe sur **chaque** occurrence
(`progression_facts.py:80`, peuplé `:222` depuis `session.started_at`), et
`progression_view` **ne le lit jamais**.

La trace à six points n'est rendue que pour le `lead`, sous
`{% if L.trace | length > 1 %}` (`progression.html:69`). Les `rows` n'en ont
aucune et affichent « 24 × 10 → 23 × 10 » sans dire quand.

**Le système calcule plus riche qu'il ne montre. Ce n'est pas une raison
suffisante pour l'afficher.** Consigné pour arbitrage.

---

## 5. Ce qui protège la consolidation

L'architecture cible reste **BODY_LEDGER · MISSION + LOADOUT ·
FLIGHT_RECORDER**. Le prototype à trois cockpits est la **calibration macro**,
et ses réductions sont des **propriétés de produit à préserver**, pas des
accidents visuels :

| | 6 routes | 3 cockpits |
|---|---|---|
| Blocs perçus | 36 | **3** |
| Commandes visibles | 78 | **5** |
| Champs visibles au repos | 45 | **0** |

Un correctif sur une surface héritée n'est justifié que s'il **(1)** corrige
une ambiguïté décision-critique actuelle, **(2)** établit un contrat sémantique
réutilisable, ou **(3)** porte sur une surface qui survit à la consolidation.
Sinon : **différer vers l'instrument cible.**

### 5.1 La tranche `/profile` reclassée par la mesure

`weekly_planner` appelle `generate_program(priorities=…)` et **ne passe jamais
`facts=`**. Les faits morphologiques n'atteignent **aucun moteur de décision**
— ce que la page dit elle-même.

La tranche de fraîcheur échoue donc au **critère 1**. Elle ne tient que par le
**critère 2** : établir le contrat sémantique. Elle reste **non committée**,
comme **implémentation de référence**.

L'aperçu à porter dans BODY_LEDGER :

> **Provenance et fraîcheur sont un seul fait d'information, pas deux
> colonnes.**

Une quatrième colonne avait été essayée puis **réfutée par le rendu à 390 px** :
elle cassait « 179.0 / cm », « mesure / directe » et « Tour de / poitrine » sur
deux lignes chacune. Les tests étaient verts ; seul l'œil l'a dit.

---

## 6. CP-1 — TEMPORAL LINEAGE · paquet de conception

> **Correction d'un cadrage antérieur.** J'avais proposé « rendre le moteur de
> surcharge conscient du temps ». **C'est trop large, et l'arbitrage l'a
> refusé à raison** : une métadonnée temporelle est un **fait** ; une règle de
> décroissance temporelle est une **hypothèse de domaine**. Deux niveaux de
> maturité différents. CP-1 ne transporte que le fait.
>
> **`BEHAVIOUR CHANGE = NONE`** pour CP-1. Aucune prescription ne change.

### 6.A Le chemin du signal historique, de bout en bout

Il y a **deux chemins distincts**, et ils perdent le temps à **deux endroits
différents**. Les confondre serait la première erreur.

| Étape | Chemin 1 — le repère `Réf.` | Chemin 2 — la charge proposée |
|---|---|---|
| **Persistance** | `WorkoutSession.started_at` · `SessionExercise.substituted_name` · `SetLog` | *(identiques)* |
| **Requête** | `stats.last_time_by_exercise_code` — `started_at.desc()`, même gabarit, substitution appariée | `overload_inputs._history_signals_for_code` — `started_at.desc()`, **`.limit(50)`**, même gabarit, substitution appariée |
| **Transformation** | `_summarise_prior` → dict portant `relative`, `started_at`, `session_id`, `has_data`, `weights_str`, `reps_str`, `first_set`, `sets`, `n_work_sets`, `n_done`, `success_score` | → `HistoricalSetSignal(weight_kg, reps, quality_score, fatigue_signal)` |
| **Entrée moteur** | *(sans objet)* | `OverloadInputs(exercise_category, target_min, target_max, history)` |
| **Sortie moteur** | *(sans objet)* | `OverloadHint(state, engine_version, target_weight_kg, target_reps_min/max, reasons)` |
| **Gabarit** | `exercise_card.html:392-397` lit `refs[se.id]` | `exercise_card.html:98` — `placeholder` |

`CODE_TRACED` pour toute la ligne.

### 6.B Où le temps existe, et où exactement il tombe

| Chemin | Le temps existe | Il tombe | Nature de la perte |
|---|---|---|---|
| **1 · `Réf.`** | `_summarise_prior` produit `relative` **et** `started_at` (`stats.py:89-91`) | `sessions.py:348-351` — `refs[se.id] = condense_reference(prior["weights_str"], prior["reps_str"])` | **copie condensée parallèle.** Deux chaînes sur onze champs |
| **2 · charge proposée** | la requête trie par `started_at` | `HistoricalSetSignal` (`overload_engine.py:56-67`) — **aucun champ temporel** | **le contrat lui-même n'a pas de place pour le temps** |

**Découverte décisive, `CODE_TRACED` :** `last_time` **entier** est déjà dans le
contexte du gabarit (`sessions.py:617`). Le chemin 1 ne demande donc **aucun
changement de service** — la donnée est atteignable depuis le template
aujourd'hui. `refs` est une commodité qui a perdu ce que son voisin transporte.

Le chemin 2, lui, exige d'ouvrir le contrat : `overload_engine.py` ne contient
**aucune** occurrence de `days`, `elapsed`, `weeks`, `timedelta` ou
`started_at` (`RUNTIME_MEASURED` par comptage sur le fichier). Le moteur ne
peut pas *représenter* le temps, encore moins l'utiliser.

### 6.C Le comportement RÉEL de la lignée de substitution

`RUNTIME_MEASURED` — trois scénarios construits en base jetable, un processus
isolé par scénario, sur `last_time_by_exercise_code`.

Historique commun : **A** prescrit 100 kg il y a 100 j · **B** substitut
« Machine X » 80 kg il y a 14 j · **C** substitut « Machine X » 82 kg il y a 7 j.

| Séance courante | Repère rendu | Âge affiché | Substituts sautés |
|---|---|---|---|
| retour au **prescrit** | **100 kg** | **il y a 3 mois** | **oui — 2** |
| récurrence du **substitut** | 82 kg | il y a 1 sem | non |
| substitut **jamais pratiqué** | **aucun** | — | *(silence)* |

#### Et la question qui décide de CP-1

> Le système sait-il distinguer *« l'utilisateur n'a pas travaillé ce
> mouvement »* de *« il l'a travaillé, mais via un substitut »* ?

**Non.** Deux historiques dont la **seule** différence est l'existence de deux
séances substituées produisent une charge utile **identique champ par champ** :

```
A — s'est entraîné, dernier substitut il y a 7 j
B — ne s'est pas entraîné depuis 100 jours

{"has_data": true, "relative": "il y a 3 mois", "session_id": 26,
 "started_at": "2026-05-29T12:00:00", "weights_str": "100",
 "reps_str": "10", "n_work_sets": 1, "n_done": 1, "success_score": null}
```

`RUNTIME_MEASURED`, deux processus isolés, sorties comparées.

**Conséquence : l'âge seul est insuffisant.** Un repère « il y a 3 mois » peut
signifier un désentraînement réel ou une continuité parfaite par substitution.
Le produit ne peut pas le dire — et l'utilisateur non plus, la politique étant
invisible à l'écran.

⚠ Le silence du troisième cas est ambigu de la même manière : « aucun repère
comparable » confond *« jamais fait ce mouvement »* et *« jamais fait sous
cette substitution »*.

### 6.D Contrat de données minimal proposé

`DESIGN_PROPOSAL`. Chaque champ est justifié par un consommateur identifié en
`§6.F` — aucun n'est ajouté « parce qu'il pourrait servir ».

**`ReferenceSignal`** — ce sur quoi une recommandation s'appuie :

| Champ | Source existante | Pourquoi |
|---|---|---|
| `value`, `reps` | `SetLog.weight_kg`, `.reps` | déjà transporté |
| `performed_at` | `WorkoutSession.started_at` | **le fait manquant du chemin 2** |
| `source_session_id` | `WorkoutSession.id` | rend le repère vérifiable |
| `prescribed_exercise_id` / `actual_exercise_id` | `exercise_code_snapshot` / `substituted_name` | distingue prescrit et substitut |
| `substituted` (drapeau) | `substituted_name is not None` | le minimum pour `§6.C` |

**`Recommendation`** — ce que le moteur produit :

| Champ | État |
|---|---|
| `suggested_value` | existe — `OverloadHint.target_weight_kg` |
| `derivation_version` | **existe déjà** — `OverloadHint.engine_version` |
| `reference_signal` | **manque** |
| `computed_at` | **manque** |

**Ce que le contrat ne porte PAS**, et c'est délibéré : aucun seuil de
vétusté, aucun score de confiance, aucune fonction de décroissance, aucun état
rouge/vert, aucun pourcentage de repli. Ce sont des hypothèses de domaine —
elles relèvent de CP-3.

**Une lignée complète — « combien de séances substituées séparent ce repère de
maintenant » — n'est PAS proposée pour CP-1.** Un drapeau `substituted` sur le
repère retenu suffit-il à lever l'ambiguïté du `§6.C` ? **Non**, et c'est une
question ouverte, pas un oubli : voir `§6.H`.

### 6.E Compatibilité et données historiques

`CODE_TRACED`.

* **Aucune migration.** Tous les champs proposés sont **dérivés de colonnes
  existantes** — `started_at`, `id`, `exercise_code_snapshot`,
  `substituted_name`. Rien à écrire en base, rien à rétro-remplir.
* **`HistoricalSetSignal` est une dataclass `frozen`** sans consommateur
  externe au moteur (`CODE_TRACED`) : lui ajouter des champs **à valeur par
  défaut** ne casse aucun appelant.
* **Les snapshots protègent l'historique** : `template_slug_snapshot` et
  `exercise_code_snapshot` résistent aux renames. Un repère ancien reste
  résoluble.
* ⚠ **`substituted_name` est une chaîne libre**, normalisée à la comparaison
  par `exercise_identity.identity_key` (`stats.py:131-154`). Un
  `actual_exercise_id` stable **n'existe pas** — le contrat doit transporter la
  chaîne et sa clé normalisée, pas prétendre à un identifiant.

### 6.F Preuve que les champs proposés ont un consommateur

L'opérateur l'exige : *« Do not add fields without a consumer or an identified
trust need. »*

| Champ | Consommateur identifié |
|---|---|
| `performed_at` | le repère `Réf.` de la carte active — **déjà atteignable** côté chemin 1 (`sessions.py:617`), **absent** côté chemin 2 |
| `source_session_id` | déjà produit par `_summarise_prior` (`stats.py:91`) et **déjà jeté** par `refs` — consommateur = la traçabilité du repère |
| `substituted` | le cas `§6.C` — sans lui, deux situations opposées sont indistinguables. **C'est le seul besoin de confiance démontré par la mesure** |
| `computed_at` | CP-2 (Session Trust UI) — **pas encore de consommateur.** À ne PAS ajouter en CP-1 tant qu'il n'en a pas |
| `derivation_version` | **déjà présent** (`engine_version`) — rien à ajouter |

**Deux champs sur cinq n'ont pas encore de consommateur.** Ils sont nommés,
pas proposés.

### 6.G Tests exigés avant implémentation

`DESIGN_PROPOSAL`.

1. **Lignée, trois scénarios** — le `§6.C` transformé en gardes de capacité :
   retour au prescrit, récurrence du substitut, substitut jamais pratiqué.
   Chacune exerce `last_time_by_exercise_code` sur une base construite.
2. **La garde de l'indistinguabilité** — deux historiques ne différant que par
   des séances substituées doivent produire des charges utiles **différentes**
   après CP-1. C'est le test qui échoue aujourd'hui et qui doit passer demain,
   et il est le seul à prouver que CP-1 sert à quelque chose.
3. **Non-régression de prescription** — pour un jeu d'historiques donné,
   `OverloadHint.target_weight_kg` **inchangé** avant/après CP-1. C'est la
   garde qui tient `BEHAVIOUR CHANGE = NONE`.
4. **Le naïf de SQLite** — `started_at` revient sans fuseau (`RUNTIME_MEASURED`
   sur `BodyMeasurement`, même dialecte) ; toute arithmétique doit l'absorber.
5. **Aucun seuil** — une garde qui refuse l'apparition de `days >`, `elapsed`,
   `decay` ou d'un littéral de jours dans le moteur, tant que CP-3 n'est pas
   ouvert.

### 6.H `BEHAVIOUR CHANGE = NONE` — et la décision qui manque

**CP-1 ne change aucune prescription, aucun rendu, aucun texte.** Il fait
transporter au signal ce qu'il possède déjà à sa source. Le test 3 du `§6.G`
en est la garde mécanique.

**Question ouverte, qui n'est pas un oubli :** le drapeau `substituted` sur le
**repère retenu** ne lève qu'à moitié l'ambiguïté du `§6.C`. Il dit *« ce
repère est un prescrit »* — il ne dit pas *« et deux substituts existent
depuis »*. Lever complètement l'ambiguïté demande de transporter **l'existence
d'occurrences plus récentes écartées par la politique**, ce qui est un champ de
plus et un choix de sémantique :

* **option a** — un simple `has_more_recent_skipped: bool` ;
* **option b** — le compte et la date de la plus récente écartée ;
* **option c** — rien en CP-1, et la question passe à CP-2 avec l'UI.

Je ne tranche pas : les trois se défendent, et le coût de la (b) n'est pas nul.

---

## Verdict

Deux voies, et elles ne se mélangent pas.

**A** est une hygiène : prouvée, sans risque produit, sans filet existant — donc
elle part avec sa garde, sinon elle reviendra une troisième fois.

**B** est un contrat : il faut le poser avant de toucher un gabarit, et la
mesure a déjà corrigé deux de mes propres classements. La seule chose qui passe
le test du `§0` par l'affirmative aujourd'hui, c'est **ce que le produit propose
lui-même** — un nombre calculé par un moteur qui ne sait pas représenter le
temps.
