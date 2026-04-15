# SPIGNOS Exercise Substitution Graph — Strategic Refinements (Sx_03.1)

**Sprint:** Sx_03_1_exercise_substitution_graph_refinements
**Date:** 2026-04-14
**Status:** Spec strategique — aucun build associe
**Relation:** Raffinement strategique de `SPIGNOS_EXERCISE_SUBSTITUTION_GRAPH_SPEC.md` (Sx_03 — deja built sous Sb_03)
**Nature:** Reconciliation + analyse comparative Option 1 vs Option 2 + preparation Sx_04

---

## 1. Contexte

Le spec `SPIGNOS_EXERCISE_SUBSTITUTION_GRAPH_SPEC.md` (235 lignes) existe et est marque "Spec approved, pending build". Audit du repo reel montre que **le build est deja fait** : modele, service, router, UI, seed, tests, QA script. Option 1 (enrichissement minimal du modele) est en production.

Ce document ne refait pas le spec. Il :

1. Reconcilie le spec avec la realite buildee (tableau spec vs built)
2. Fait rigoureusement la comparaison Option 1 vs Option 2 que le prompt Sx_03 avait demandee mais qui n'a pas ete executee dans le spec original
3. Analyse les 3 gaps observables dans l'implementation actuelle
4. Definit les triggers concrets qui feraient basculer vers Option 2
5. Produit une recommandation nette pour Sx_04

Aucun build associe a ce document. C'est une spec strategique de preparation pour Sx_04 et pour les decisions futures de gouvernance catalogue.

---

## 2. Livrable 1 — Tableau spec Sx_03 vs code built

| Spec item (Sx_03) | Etat reel | Reference code | Statut |
|-------------------|-----------|----------------|--------|
| `substitutes` field in `reference_split.json` | 9 exercices ont des substitutes | `data/reference_split.json` (v6, grep "substitutes" = 9 matches) | **Built** |
| `TemplateExercise.substitutes_json` (TEXT nullable) | Colonne presente, populee par seed | `app/models/catalog.py:81` | **Built** |
| `SessionExercise.substituted_name` (VARCHAR 255 nullable) | Colonne presente | `app/models/session.py:162` | **Built** |
| `actual_exercise_name()` helper | Implemente | `app/services/substitution.py:12` | **Built** |
| `get_substitutes()` helper | Implemente | `app/services/substitution.py:17` | **Built** |
| `can_substitute()` helper | Implemente | `app/services/substitution.py:31` | **Built** |
| Seed lit `substitutes` du JSON vers `substitutes_json` | Oui | `app/services/seed.py` | **Built** |
| Parsing `substituted_name` dans router | Oui | `app/routers/sessions.py:394-398` | **Built** |
| Lock apres premier set complete | Via `can_substitute()` cote template | `session_detail.html:100-117` + helper | **Built** |
| UI substitution picker | Rendu conditionnel | `session_detail.html:98-123` | **Built** |
| `muscle_scoring` utilise `actual_exercise_name` | Oui | `muscle_scoring.py:89` | **Built** |
| Export inclut `substituted_name` | Oui | `export_builder.py:61, 139, 195` | **Built** |
| Session recap prend en compte substitution | Oui | `session_recap.py:63, 79` | **Built** |
| Sharing prend en compte substitution | Oui | `sharing.py:117` | **Built** |
| QA script valide classifiability des substitutes | Oui | `catalog_qa.py:256-268` | **Built** |
| Tests unit + integration | 11 tests | `tests/test_substitution.py` | **Built** |
| Migration Alembic (2 colonnes) | Integree dans migration existante | `migrations/versions/...` | **Built** |
| Canonical `Exercise` entity | Explicitement "DO NOT BUILD" | — | **Not built (par design)** |
| Bidirectional graph | "DO NOT BUILD" | — | **Not built (par design)** |
| Substitution cross-template | "DO NOT BUILD" | — | **Not built (par design)** |
| Comparative analysis Option 1 vs Option 2 | **Manquant dans le spec** | — | **Spec gap** |

**Verdict :** Sx_03 Option 1 est buildee integralement. Le seul gap est l'absence d'analyse comparative rigoureuse que le prompt initial exigeait.

**Statut recommande pour le spec historique :**

> **BUILT (Sb_03).**
> **Comparative analysis + refinements : voir SPIGNOS_EXERCISE_SUBSTITUTION_GRAPH_REFINEMENTS.md (Sx_03.1).**

---

## 3. Livrable 2 — Comparaison rigoureuse Option 1 vs Option 2

### Option 1 — Enrichissement minimal (current)

Modele :
- Substituts stockes comme liste de **strings** dans `template_exercises.substitutes_json`
- `session_exercises.substituted_name` comme string libre
- Catalogue JSON (`reference_split.json`) source de verite
- Pas d'identite transverse de l'exercice

Ce qui marche deja :
- Le user peut substituer en 1 clic
- `muscle_scoring` classifie correctement via `actual_exercise_name`
- Historique preserve (snapshots immutables)
- Zero migration pour evoluer (juste editer le JSON et bumper la version)

### Option 2 — Entite canonique `Exercise`

Modele hypothetique :

```
exercises
├── id               INTEGER PK
├── slug             VARCHAR(64) UNIQUE (ex: "chest-press-machine")
├── name             VARCHAR(255) (nom d'affichage fr)
├── muscle_zone      VARCHAR(32) (primary zone — resolved from mapping)
├── equipment        VARCHAR(64) (machine, haltere, barre, cable, body, ...)
├── pattern          VARCHAR(32) (push, pull, squat, hinge, carry, ...)
├── laterality       VARCHAR(16) (bilateral, unilateral, ...)
├── created_at       DATETIME
└── INDEX(slug)

exercise_aliases   -- si besoin de noms alternatifs
├── exercise_id     FK exercises.id
├── alias           VARCHAR(255)
└── UNIQUE(alias)

exercise_substitutions
├── from_exercise_id  FK exercises.id
├── to_exercise_id    FK exercises.id
├── equivalence_level VARCHAR(16) (exact, approx, fallback)
├── reason_hint       VARCHAR(128) (machine_busy, injury, equipment_unavailable)
└── UNIQUE(from_exercise_id, to_exercise_id)

template_exercises
├── ... (existant) ...
└── exercise_id       FK exercises.id (NEW, nullable pendant migration)

session_exercises
├── ... (existant) ...
├── prescribed_exercise_id  FK exercises.id (NEW)
└── actual_exercise_id      FK exercises.id nullable (NEW, = prescribed si pas substitue)
```

### Comparaison dimension par dimension

| Dimension | Option 1 (built) | Option 2 (canonical) | Gagnant |
|-----------|------------------|---------------------|---------|
| **Cout de migration** | Nul (fait) | Lourd : ~97 exercices a canoniser + 2 tables + 2 FK + backfill des snapshots historiques | **Option 1** |
| **Proprete analytique** | Classification par pattern matching sur string. Fragile aux typos. Muscle zone derivee au runtime via `classify_exercise()`. | Classification authoritative en dur sur l'entite. Zero typo possible. Zones, equipment, pattern queryables. | **Option 2** (nettement) |
| **Compatibilite historique** | Snapshots immutables preservent la lisibilite. Classification retro peut deriver si les patterns changent. | Backfill necessaire : mapper les snapshots historiques vers `exercise_id`. Ambiguites (typo historique) doivent etre tranchees. | **Option 1** |
| **Facilite d'integration flow session** | Aucun changement necessaire, l'UX existe | L'UX existante continue de fonctionner si la FK est correctement populee. Pas de changement UX visible. | **Egalite** |
| **Gouvernance catalogue** | Editer le JSON suffit. Version bumpee → reseed. Seed fait tout. | Edition JSON + maintenance du pool canonique. Nouveau exercice = nouvelle ligne dans `exercises`. Risque de divergence si plusieurs devs/editeurs. | **Option 1** |
| **Evolutivite** | Ajouter un champ (ex: equipment) necessite extension du JSON + migration de colonne + derivation runtime | Ajouter un champ = 1 colonne dans `exercises` + data migration. Queries SQL natives. | **Option 2** (si besoin de queries riches) |
| **Integrite referentielle** | Aucune. Un typo dans un substitute n'est pas detecte a l'ecriture. QA script en garde-fou (warning). | Forte. FK garantit l'existence. Tout substitute pointe vers un exercice reel. | **Option 2** (de loin) |
| **Requetes cross-cutting** | Difficile : "tous les exercices pecs avec machine" necessite de re-classifier tous les noms. | Trivial : `SELECT ... WHERE muscle_zone='pecs' AND equipment='machine'`. | **Option 2** |
| **Bidirectional substitution** | Doit etre ecrite explicitement dans les 2 sens dans le JSON | `exercise_substitutions` peut etre modelee symetriquement a la DB ou derivee | **Option 2** |
| **Custom exercises user** | Non supporte (catalogue fige) | Extensible (table ouverte) | **Option 2** (si V3+) |
| **Taille du schema** | 0 nouvelle table | +2 tables, +2-3 colonnes | **Option 1** |
| **Complexite code** | 37 lignes de service, suffisant | Minimum 150+ lignes pour CRUD, graph queries, backfill | **Option 1** |
| **Robustesse typo** | Faible (QA warning seulement) | Forte (FK constraint) | **Option 2** |

### Synthese

**Option 1 est le bon choix tant que :**
- Le catalogue reste en dessous de ~150 exercices
- Les substitutions restent simples et peu nombreuses (< 30 relations)
- Aucune analytique cross-cutting complexe n'est requise ("tous les exercices bilateraux cable push" — hors roadmap)
- L'equipe n'a pas besoin de support "custom exercises"
- La gouvernance du catalogue reste mono-editeur (le fondateur)

**Option 2 devient necessaire si :**
- Le catalogue depasse ~150 exercices (risque typos, perte de gouvernance)
- Plusieurs contributeurs editent le catalogue
- Un besoin analytique par `equipment`, `pattern`, `laterality` emerge (ex: "detecte si le user est sur-sollicite en machine vs poids libres")
- Un feature "custom exercises user-defined" est planifiee
- Le besoin de bidirectional substitution apparait (graphe de substitution reel, pas liste unidirectionnelle)
- La maintenance de typos/aliases devient un probleme recurrent

---

## 4. Livrable 3 — Analyse des 3 gaps observables

### Gap 1 — Identite fragile par chaine de caracteres

**Constat :** Les substituts sont des noms stringifies. Rien dans le schema ne garantit que "Chest Press machine" ecrit dans un substitute corresponde bien a un exercice reel. Un typo ("Chess Press") est silencieux au save, la substitution persiste, mais la classification `classify_exercise()` peut echouer ou mal zoner. Le QA script catch certains cas (pattern unknown) mais pas les typos proches ("Chest press machine" avec une casse differente).

**Impact actuel :** Faible — le catalogue est petit (~97 exercices), un seul editeur (le fondateur). Le QA script limite les degats.

**Impact futur :** Moyen — si le catalogue croit ou si la gouvernance s'ouvre, les typos deviennent un risque de perte de signal analytique.

**Solutions possibles :**

- **Patch Option 1** : normaliser les noms (slug-style) dans le JSON + comparer par slug ; index de validation par QA script renforce → statistiquement moins de typos mais pas zero.
- **Solution structurelle** : Option 2 (FK force l'existence).

### Gap 2 — Raison de substitution non capturee

**Constat :** Quand le user substitue, on capture le nom du substitut mais pas pourquoi. Signal perdu pour :
- Detection de patterns ("Chest Press est substitue 40% du temps → le parc est sous-dimensionne")
- Adaptation catalogue ("cet exercice devrait etre remplace par son substitut le plus utilise")
- Signal medical ("blessure recurrente sur rowing → proposer alternatives sans tirer dos")

**Impact actuel :** Faible — aucun consumer n'exploite ce signal aujourd'hui.

**Impact futur :** Moyen — pour un feature "catalog health" dans la gouvernance (quand ?) ou "adaptive catalog" (V3+).

**Solutions possibles :**

- **Patch Option 1** : ajouter `substitution_reason` (VARCHAR 32) nullable sur `session_exercises`, enum controle : `machine_busy | injury | preference | equipment_unavailable`. Zero migration lourde.
- **Solution structurelle** : Option 2 inclut un `reason_hint` au niveau de la relation substitution, ce qui est different (prescrit au catalogue, pas capture a la session). Les deux sont complementaires.

### Gap 3 — Niveau d'equivalence non documente

**Constat :** Le JSON catalogue dit "X peut etre substitue par Y" sans preciser la qualite de l'equivalence :
- Equivalence exacte (meme pattern, meme charge probable, meme ciblage) — ex: "Hack Squat" ↔ "Leg Press pieds bas serres"
- Equivalence approximative (meme zone mais biomecanique differente) — ex: "Chest Press machine" ↔ "Dips pectoraux" (zone = pecs mais charge bw vs machine)
- Fallback degrade (solution en dernier recours, signal analytique moins fiable) — ex: "Hip thrust Smith" ↔ "Hip thrust halteres" (meme pattern mais charge tres differente)

**Impact actuel :** Nul — tous les substitutes sont traites au meme niveau. Les deltas et les KPIs ne distinguent pas.

**Impact futur :** Important — pour Sx_04 (consolidation), pour le body engineering dashboard, pour la confiance analytique. Une substitution "approximative" devrait idealement marquer les KPIs comme moins fiables, ou au moins etre loggue pour analyse.

**Solutions possibles :**

- **Patch Option 1** : etendre le JSON catalogue a `{"name": "X", "equivalence": "exact"|"approx"|"fallback"}` au lieu d'une simple liste de strings. Modeler ca dans `substitutes_json`. Zero migration DB.
- **Solution structurelle** : Option 2 avec `equivalence_level` sur la relation.

---

## 5. Livrable 4 — Triggers concrets pour migrer vers Option 2

Option 2 doit etre declenchee **SI au moins un des triggers suivants est atteint**. Pas avant. Pas parce que "c'est plus propre".

### Trigger A — Scaling du catalogue
- Le catalogue depasse **150 exercices distincts**
- Ou : le nombre de relations de substitution depasse **40**
- Raison : au-dela, le risque de typo et de divergence devient ingerable en JSON.

### Trigger B — Gouvernance multi-editeurs
- **Plus d'un contributeur** edite regulierement le catalogue
- Ou : un workflow d'approbation devient necessaire pour chaque changement
- Raison : FK en base > discipline manuelle JSON.

### Trigger C — Requete analytique cross-cutting
- Un besoin produit emerge qui necessite de filtrer les exercices par :
  - `equipment` (machine vs halteres vs cable vs poids du corps)
  - `pattern` (push horizontal vs push vertical vs pull horizontal...)
  - `laterality` (bilateral vs unilateral)
- Raison : difficile a implementer proprement sur strings, trivial en SQL sur FK.

### Trigger D — Feature "custom exercises"
- Le user doit pouvoir creer ses propres exercices
- Raison : necessite une table ouverte, pas un JSON fige.

### Trigger E — Bidirectional substitution graph
- Un besoin emerge de modeler le graphe symetriquement (A↔B automatiquement implique B↔A)
- Ou : de traverser le graphe ("tous les substituts des substituts de X, niveau 2")
- Raison : structure relationnelle > duplication JSON bidirectionnelle.

### Trigger F — Typo/alias devient un probleme
- Le QA script produit regulierement des warnings non resolus
- Ou : des bugs de classification apparaissent en prod a cause de mismatches de casse/accents
- Raison : contrainte referentielle > discipline manuelle.

### Seuil combine

Si **0 trigger atteint** : ne pas migrer. Option 1 est le bon choix.
Si **1 trigger atteint** : analyser en profondeur, peut-etre attendre un 2e.
Si **2+ triggers atteints** : planifier la migration vers Option 2 (ecrire un spec de migration dedie).

---

## 6. Livrable 5 — Recommandation pour Sx_04

### Position dans Sx_04 (consolidation transverse)

**Recommandation nette : NOT YET.**

Motifs :
1. Aucun des 6 triggers n'est aujourd'hui atteint. Le catalogue a ~97 exercices et 9 relations de substitution. Un seul editeur.
2. Option 1 couvre tous les besoins actuels (substitution runtime, scoring correct, historique preserve).
3. Le cout de migration (~97 exercices a canoniser + 2 tables + backfill) est substantiel et le benefice immediat nul.
4. Les 3 gaps observes (identite, raison, equivalence) peuvent tous etre patches sur Option 1 avec des changements incrementaux mineurs.

### Ce que Sx_04 DOIT documenter comme decision transverse

1. **Reaffirmer Option 1 comme modele actuel** et justifier que Option 2 est une capacite future, pas une dette.
2. **Integrer les 6 triggers** comme declencheurs explicites de re-evaluation.
3. **Prioriser les 3 patches Option 1** si besoin :
   - Patch Gap 2 (substitution_reason) — le plus simple, le plus utile a moyen terme. Faible cout.
   - Patch Gap 3 (equivalence_level) — utile pour la confiance analytique du body engineering dashboard. Cout moyen.
   - Patch Gap 1 (identite slug-based) — le plus complexe, le plus structurel. A ne faire que si le QA signale des typos recurrents.
4. **Ne PAS ouvrir Option 2** dans Sx_04. Rediger explicitement "deferred jusqu'a trigger".

### Ce que Sx_04 peut absorber comme decision immediate

- **Patch Gap 2** (capturer la raison de substitution) comme build candidate Sb_04 ou Sb_04.1 — cout minimal, signal utile pour gouvernance catalogue.
- **Sacralisation du slot-based vs exercise-based distinction** comme principe d'analytics (deja documente dans Sx_03 section 6, a re-affirmer dans Sx_04).

### Ce que Sx_04 NE doit PAS faire

- Introduire une table `exercises` "juste au cas ou"
- Obliger un backfill des snapshots historiques (breaking change)
- Modifier la signature de `classify_exercise()` pour esperer une resolution par entite
- Introduire un concept "Exercise" dans les specs V2 sans trigger

---

## 7. Synthese executive

| Question | Reponse |
|----------|---------|
| Sx_03 est-il buildee ? | **Oui, integralement** (Option 1, Sb_03) |
| Le spec historique est-il complet ? | **Non** — il manque la comparaison rigoureuse Option 1 vs Option 2. Ce document la comble. |
| Faut-il canonifier les exercices maintenant ? | **Non** — aucun trigger atteint. |
| Faut-il patcher les 3 gaps ? | **Gap 2 oui** (faible cout, vraie valeur). **Gap 3 oui moyen terme** (important pour analytics). **Gap 1 non** tant que le QA script ne signale pas de recurrence. |
| Sx_04 doit-il reouvrir le debat ? | **Non** — Sx_04 doit integrer les triggers de ce document comme reference, puis proposer eventuellement les patches mineurs sur Option 1. |
| Un build Sb_03.1 est-il necessaire ? | **Optionnel** — uniquement pour Gap 2 (substitution_reason). Cout minimal, valeur de gouvernance future. A arbitrer dans Sx_04. |

---

## 8. Marquage recommande du spec Sx_03 historique

Ajouter en tete de `SPIGNOS_EXERCISE_SUBSTITUTION_GRAPH_SPEC.md` :

```
**Statut : BUILT (Sb_03).**
**Analyse comparative + refinements strategiques : voir SPIGNOS_EXERCISE_SUBSTITUTION_GRAPH_REFINEMENTS.md (Sx_03.1).**
**Canonical Exercise entity : DEFERRED — triggers documentes dans Sx_03.1 §5.**
```

Ne pas ecraser le contenu du spec historique. Il documente la decision originale (Option 1) et reste la reference normative de ce qui tourne en prod.
