# Sx_DECISION_ANALYTICS_01 — Contrat de trace de décision (SPEC)

> **SPEC ONLY.** Aucun code runtime, aucune migration, aucun modèle n'est livré par ce
> document. Il tranche ce qu'un futur système d'observabilité devra faire, sur la base
> d'un **audit du code actif** au SHA canonique `64a6e75`.

**Train :** `AUREN_MORPHO_RUNTIME_FOUNDATION_01`, tranche 3/3.
**Consommateur aval :** non ouvert.

---

## 1. Le problème, énoncé précisément

AUREN prend aujourd'hui des décisions **traçables individuellement** et
**incomparables entre elles**. Chaque moteur expose sa propre justification —
`basis`, `evidence`, `rationale`, `unmet_reason`, `gap_kind`, `overshoot_kind` —
dans un vocabulaire qui lui est propre, et rien ne relie la décision « cette
zone reçoit 8 séries » à la décision « cet exercice occupe ce créneau » alors
que la seconde découle de la première.

La question à laquelle personne ne peut répondre aujourd'hui n'est pas
« pourquoi cette séance ? » — chaque moteur sait le dire. C'est :

> **Quelle information a produit quelle décision, et laquelle de ces
> informations était un fait mesuré plutôt qu'une convention produit ?**

Un utilisateur à qui l'on répond « ton volume épaules est à 8 séries » mérite de
savoir si ce 8 vient de ce qu'il a **déclaré**, de ce qu'on a **mesuré**, d'une
**politique produit**, ou d'une **estimation de récupération**. Ces quatre
réponses ont des statuts épistémiques différents et une seule phrase de
justification les aplatit toutes.

---

## 2. Audit — ce qui existe déjà, et ce qui manque

### 2.1 Les décisions livrées et leur versionnement

Le dépôt versionne **quinze constantes réparties sur douze modules de
décision**. C'est une force : la matière d'une trace existe déjà.

| Module | Constante(s) de version | Décision produite |
|---|---|---|
| `weekly_volume_budget` | `POLICY_VERSION = "weekly-volume-v1"` | bande de volume par zone |
| `weekly_planner` | `PLANNER_VERSION = 2` | plan hebdomadaire, empreinte |
| `weekly_capacity_allocator` | `CAPACITY_ALLOCATOR_VERSION = "capacity-allocator-v1"` · `SESSION_SHAPE_CONVENTION_VERSION = "session-shape-v1"` | placement des occurrences · plafonds souples de séance |
| `weekly_set_allocation` | `ALLOCATION_POLICY_VERSION = "set-allocation-v1"` | séries et fourchette de reps |
| `set_contribution` | `SET_CONTRIBUTION_POLICY_VERSION = "set-contribution-v1"` | crédit direct / indirect |
| `weekly_plan_materialization` | `MATERIALIZATION_VERSION = 1` | brouillon de programme |
| `adaptive_replan` | `REPLAN_VERSION = 1` | delta de replanification |
| `training_state` | `TRAINING_STATE_AGGREGATOR_VERSION = 1` | état d'entraînement agrégé |
| `zone_recovery` | `RECOVERY_POLICY_VERSION = 1` | récupération par zone |
| `recovery_contract` | `RECOVERY_CONTRACT_VERSION = 1` · `CARDIO_ADAPTER_VERSION = 1` | contrat de disponibilité · adaptation cardio |
| `morphology_profile` | `MORPHOLOGY_PROFILE_ENGINE_VERSION = 1` | descripteurs morphologiques |
| `morphology_runtime` | `MORPHOLOGY_RUNTIME_VERSION = 1` · `LATERAL_REDUCTION_CONVENTION_VERSION = "lateral-mean-v1"` | assemblage des faits · réduction latérale |

### 2.2 Les quatre manques

**(a) Aucune identité de décision.** Une décision n'a pas d'identifiant. On ne
peut donc ni la citer, ni la comparer à celle de la semaine dernière, ni
constater qu'elle a changé sans que l'utilisateur n'ait rien changé.

**(b) Le lien amont/aval n'est pas matérialisé.** L'empreinte de plan
(`WeeklyPlan.fingerprint`) prouve qu'un plan est le même ou différent — elle ne
dit pas **quelle entrée** a bougé. Le budget alimente l'allocateur, qui alimente
la matérialisation ; ces arêtes existent dans le code, pas dans les données.

**(c) Les alternatives rejetées sont perdues.** L'allocateur classe les zones
(`_rank_zone`) et le générateur classe les candidats : un choix implique des
non-choix, et seuls les choix survivent. « Pourquoi pas le développé incliné ? »
est aujourd'hui sans réponse, alors que le classement l'a su.

**(d) Les sources sont déjà distinctes dans le code, et confondues à la
sortie.** C'est le manque le plus coûteux, et le plus facile à mal réparer.

### 2.3 La distinction que le dépôt défend déjà — et qu'il ne faut pas perdre

Plusieurs tranches livrées ont **payé pour** séparer des choses qu'une trace
naïve ré-aplatirait :

- `Sb_TRAINING_PREFERENCES_01` — « non déclaré » est un état de premier ordre,
  distinct de toute valeur par défaut ;
- `Sb_MORPHO_PROFILE_RUNTIME_01` — priorité **déclarée** ≠ candidat **inféré** ;
  les deux ne se rencontrent jamais dans `MorphologyFacts` ;
- `Sb_SET_CONTRIBUTION_POLICY_01` — le 0,5 est un **coefficient comptable**, pas
  une fraction d'activation ;
- `Sb_MORPHO_PROFILE_RUNTIME_01` — la réduction latérale est une **convention
  d'agrégation**, pas une physiologie ;
- chaîne P0.4 — un fait manquant **réduit la confiance**, il n'est jamais comblé.

Une trace qui produirait un champ `reason: str` unique détruirait ces cinq
distinctions en une ligne. **C'est le principal risque de ce système**, et la
raison pour laquelle la taxonomie de sources du §4 est normative.

---

## 3. `DecisionTrace` — la forme

Un enregistrement par décision observée.

| Champ | Rôle |
|---|---|
| `decision_id` | identité stable et citable |
| `decision_type` | `VOLUME_BAND` · `ZONE_ALLOCATION` · `SLOT_SELECTION` · `SET_PRESCRIPTION` · `CONTRIBUTION_CREDIT` · `REPLAN_DELTA` · `MATERIALIZATION` · `RECOVERY_ASSESSMENT` · `MORPHOLOGY_DESCRIPTOR` |
| `policy_version` | la constante versionnée du moteur émetteur (§2.1) |
| `input_refs` | références aux faits consommés, **par source** (§4) |
| `selected_output` | ce qui a été retenu |
| `rejected_alternatives` | ce qui a été écarté **quand le moteur l'a su** — jamais reconstruit après coup |
| `basis` | la justification déjà produite par le moteur, reprise **telle quelle** |
| `confidence` | catégorie, jamais un pourcentage |
| `plan_fingerprint` | rattachement au plan concerné |
| `program_identity` | programme + version, quand la décision s'y matérialise |
| `created_at` | horodatage d'observation |

`input_refs` est décomposé par nature de source et **jamais** en une liste plate :
`constraint_sources`, `preference_sources`, `morphology_sources`,
`recovery_sources`.

---

## 4. Taxonomie des sources — normative

Sept natures, jamais fusionnées :

| Source | Ce que c'est | Exemple vivant |
|---|---|---|
| `USER_DECLARED` | l'utilisateur l'a dit | `focus_priorities`, `sessions_per_week` |
| `MEASURED_FACT` | mesuré, daté, propriétaire connu | `wingspan_cm`, `waist_cm`, séries réalisées |
| `DERIVED_FACT` | calcul déterministe de faits mesurés | ape index (`wingspan − height`), moyenne latérale |
| `PRODUCT_POLICY` | convention du produit, pas de la physiologie | bande de volume, coefficient 0,5, plafonds de séance |
| `MORPHOLOGY_INFERENCE` | lecture bornée du moteur morphologique | descripteur `INFERENCE`, confiance réduite |
| `RECOVERY_ESTIMATE` | estimation temporelle, pas une mesure | récupération de zone, disponibilité |
| `CATALOG_CONSTRAINT` | contrainte du référentiel | matériel, zone canonique, substitution |

**Règle dure.** Une trace qui ne sait pas classer une entrée ne l'invente pas :
elle la marque non classée et la décision reste lisible. Aucune fusion en un
champ « raison IA » n'est autorisée, quelle que soit la commodité d'affichage.

**Corollaire, appris de la chaîne P0.4 :** une source absente reste absente. Un
`RECOVERY_ESTIMATE` manquant ne devient pas un `MEASURED_FACT` neutre, et
l'absence ne remonte jamais la confiance.

---

## 5. Non-pouvoirs — ce que l'observabilité n'a pas le droit de faire

Ce système **observe**. Il ne décide pas. Sont interdits, sans dérogation :

- choisir ou réordonner un exercice ;
- modifier une bande de volume, une allocation, une prescription ;
- modifier un replan ou un brouillon de programme ;
- **augmenter une confiance** parce que la trace est riche — la quantité de
  justification n'est pas une preuve ;
- réécrire un `basis` produit par un moteur ; la trace **cite**, elle ne
  reformule pas ;
- introduire une taxonomie anatomique concurrente de `BodyZone` ;
- exiger un LLM. La trace est structurée et déterministe ; une génération de
  texte par-dessus serait un consommateur, jamais une dépendance.

**Test d'acceptation central du futur runtime** : retirer entièrement l'écriture
des traces doit laisser **toute sortie produit rigoureusement identique** —
mêmes empreintes de plan, mêmes brouillons, mêmes descripteurs. Si une sortie
bouge, le système est devenu un moteur de décision et doit être rejeté.

---

## 6. Ce qu'une trace devra coûter

L'écriture est un **effet de bord observable** sur des chemins aujourd'hui purs :
`build_weekly_plan` ne prend ni `db` ni `user_id`, et `build_morphology_profile`
est une fonction pure. Cette pureté est un actif — c'est elle qui rend
l'isolation du planificateur démontrable.

**Décision : la trace ne s'écrit pas depuis les moteurs.** Ils continuent de
**retourner** leur justification ; un collecteur en aval assemble et persiste.
Un moteur pur qui se met à écrire en base cesse d'être testable comme il l'est
aujourd'hui, et la démonstration d'isolation morphologique du train en cours
deviendrait impossible à refaire.

---

## 7. Questions ouvertes

| # | Question | Pourquoi elle n'est pas tranchée ici |
|---|---|---|
| OQ-1 | Rétention : combien de temps garde-t-on une trace ? | Dépend d'un usage produit qui n'existe pas encore ; sur-spécifier coûterait une migration. |
| OQ-2 | Les `rejected_alternatives` sont-elles exposées à l'utilisateur ? | Montrer les non-choix peut éclairer ou inquiéter — décision produit. |
| OQ-3 | Une trace est-elle un fait historique immuable ou recalculable ? | Touche l'invariance historique, contrainte #1 du dépôt : mérite sa propre décision. |
| OQ-4 | Granularité : une trace par occurrence, ou par zone et par semaine ? | Le volume de données diffère d'un ordre de grandeur. |

---

## 8. Non-goals

Ce document **n'autorise pas** et le runtime associé **ne livrera pas** :

- de modification d'un moteur de décision existant ;
- d'influence de la morphologie sur la planification (gelée jusqu'au dogfood) ;
- de génération de texte, de LLM, de « coach explique » ;
- de pourcentage de confiance ;
- de champ de justification unique et aplati ;
- de migration ou de modèle dans cette tranche.

---

## Verdict

**Spec livrable, runtime non ouvert.**

L'audit a donné un résultat plus favorable qu'attendu : les douze modules de
décision sont **déjà versionnés** (quinze constantes) et chaque moteur produit
**déjà** sa justification. La matière d'une trace existe ; ce qui manque est une
identité, les arêtes entre décisions, les alternatives écartées, et surtout une
**discipline de source**.

La limite la plus honnête de ce document : la valeur réelle du système dépend
d'`rejected_alternatives`, et c'est le champ le plus difficile à remplir
sincèrement. Un moteur qui n'a jamais classé d'alternative ne peut pas en
inventer une après coup — mieux vaut un champ vide qu'une reconstruction
plausible.
