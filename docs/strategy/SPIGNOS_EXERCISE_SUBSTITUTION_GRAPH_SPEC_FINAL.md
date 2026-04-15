# SPIGNOS Exercise Substitution Graph — Final Spec

**Sprint:** Sx_03_exercise_substitution_graph_spec (FINAL)
**Date:** 2026-04-14
**Status:** Final, aligne avec Sx_01 FINAL + Sx_02 FINAL + realite Sb_03 built
**Relation:** Consolide `SPIGNOS_EXERCISE_SUBSTITUTION_GRAPH_SPEC.md` (v1, built sous Sb_03) + `SPIGNOS_EXERCISE_SUBSTITUTION_GRAPH_REFINEMENTS.md` (Sx_03.1 — 6 triggers + 3 gaps) + contrats composant Sx_02 FINAL.

---

## 0. Contexte et ancrages

Ce spec FINAL s'appuie sur des decisions **deja verrouillees** :

- **Sx_01 FINAL** : signal exercice minimal (weight/reps/completed/muscle_sensation/success_score derive)
- **Sx_02 FINAL** : composant bloc exercice fige, contrat UI SSR-friendly
- **Sb_03 en production** : catalogue JSON-based, `SessionExercise.substituted_name`, `TemplateExercise.substitutes_json`, service `actual_exercise_name`, picker UI, QA script
- **Sx_03.1** : 6 triggers documentes pour migration Option 2 (entite canonique) — aucun atteint

Il **n'y a rien a re-batir structurellement**. Ce spec formalise la vision cible complete (modele conceptuel, taxonomie, gouvernance, analytics) en s'appuyant sur ce qui tourne, pour servir de contrat long-terme et de socle aux enrichissements incrementaux futurs.

---

## 1. Audit du catalogue et des structures reelles

### 1.1 Catalogue actuel

`data/reference_split.json` v6 :
- 15 templates (6 core, 2 utility, 3 specialization, 4 archived)
- 97 exercices
- 9 relations de substitution (sous le champ `substitutes: [...]`)

Structure par exercice dans le catalogue :
```json
{
  "position": 2,
  "code": "E2",
  "name": "Chest Press machine",
  "set_scheme": "3x 8-12",
  "notes": "...",
  "rep_targets": [...],
  "substitutes": ["Developpe couche halteres", "Dips pectoraux"]  // optionnel
}
```

### 1.2 Modele DB

| Table | Champ substitution | Type | Role |
|-------|--------------------|------|------|
| `template_exercises` | `substitutes_json` | TEXT nullable | Liste JSON des substituts du slot |
| `session_exercises` | `substituted_name` | VARCHAR(255) nullable | Nom de l'exercice reellement effectue (NULL = prescrit) |
| `session_exercises` | `exercise_code_snapshot` | VARCHAR(16) NOT NULL | Slot prescrit (immutable) |
| `session_exercises` | `exercise_name_snapshot` | VARCHAR(255) NOT NULL | Nom prescrit au moment de la creation (immutable) |

### 1.3 Service

`app/services/substitution.py` (36 lignes, 3 fonctions) :
- `actual_exercise_name(se)` → `substituted_name or exercise_name_snapshot`
- `get_substitutes(te)` → parse le JSON en liste de strings
- `can_substitute(se)` → True si aucun work set complete

### 1.4 Consumers deja cables

- `muscle_scoring.py:89` — `classify_exercise(actual_exercise_name(se))` pour zone analytics
- `sharing.py:117` — sharecards utilisent `actual_exercise_name`
- `session_recap.py:63, 68, 79` — `/done` affiche `substituted_name or exercise_name_snapshot`, compte les substitutions
- `export_builder.py:61, 139, 195` — JSON et CSV incluent `substituted_name`
- Template `session_detail.html:59, 98-123` — picker conditionnel + badge + rendu nom
- `scripts/catalog_qa.py:256-268` — valide que chaque substitute name est classifiable

### 1.5 Etat des lieux

- **Option 1 (JSON-based)** integralement buildee
- **Option 2 (canonical Exercise entity)** deferee avec 6 triggers (aucun atteint)
- **9 relations de substitution** dans le catalogue, scope volontairement limite aux machines frequemment occupees
- **Taxonomie de mouvement formelle** : inexistante (classification implicite via pattern matching dans `muscle_mapping.py`)

---

## 2. Modele conceptuel — prevu / realise / substitution

### 2.1 Distinction a 5 niveaux

| Niveau | Role | Actuellement represente par |
|--------|------|----------------------------|
| **Exercice canonique** | Identite abstraite transverse ("Chest Press machine" comme concept universel) | **Pas d'entite dediee** — implicite via nom de chaine dans le catalogue |
| **Exercice prevu par le template** | Slot prescrit a une position dans un template (`push-a` / E2 / "Chest Press machine") | `TemplateExercise` (slug+code+name+set_scheme+rep_targets+substitutes_json) |
| **Exercice reellement execute** | Ce qui a ete fait pendant une seance reelle | `SessionExercise` avec `exercise_name_snapshot` (prevu) + `substituted_name` (realise si different) |
| **Relation de substitution** | Lien "A peut etre substitue par B" declare dans le catalogue | `TemplateExercise.substitutes_json` = liste de strings |
| **Niveau d'equivalence** | Qualite semantique de la substitution (exact / approx / fallback) | **Pas encore modelise** — tous les substitutes sont traites au meme niveau |

### 2.2 Doctrine canonique (vision long-terme sans engagement de build)

**Exercice canonique** : un concept porteur d'identite stable (slug + nom + taxonomie de mouvement). Actuellement represente par son **nom de chaine seul** (risque de typos, pas d'alias). Option 2 de Sx_03.1 introduirait une table `exercises` qui porte cette identite.

**Exercice prevu** : instance d'un canonique a une position dans un template. `TemplateExercise` actuel joue ce role avec une resolution implicite via `TemplateExercise.name`.

**Exercice realise** : le `SessionExercise` avec ses `snapshots` (immutables, immuables apres creation) et son `substituted_name` optionnel.

**Relation de substitution** : aujourd'hui un tableau dans le catalogue. Une evolution Option 2 la modeliserait comme table `exercise_substitutions` avec niveau d'equivalence et raison prescriptive.

### 2.3 Raison de substitution

Axe explicitement non modelise aujourd'hui. Gap 2 de Sx_03.1 propose une extension minimale (`session_exercises.substitution_reason` enum nullable). Peut etre build en Sb_03.1 leger (1-2h). Pas de trigger obligatoire.

Enum propose (si jamais build) :
- `machine_busy` : equipement occupe
- `equipment_unavailable` : equipement absent
- `injury` : blessure / douleur
- `preference` : choix personnel
- `other` : autre raison

---

## 3. Taxonomie de mouvement minimale viable

**Statut : cible long-terme, non implementee aujourd'hui.** Documentee ici pour guider les futurs enrichissements catalogue sans exploser en ontologie infinie.

### 3.1 Dimensions minimales viables

| Dimension | Valeurs possibles | Role |
|-----------|------------------|------|
| `primary_zone` | 11 zones existantes (pecs, delt_lat, delt_post, lats, upper_back, biceps, triceps, quads, posterior, calves, core) | **Deja utilise** via `classify_exercise()` |
| `secondary_zones` | Liste de 0 a 3 zones | **Deja utilise** (ex: pecs → [triceps]) |
| `motor_pattern` | push_horizontal, push_vertical, pull_horizontal, pull_vertical, squat, hinge, carry, rotation, anti_rotation, isolation | **Non implementee** — a ajouter si Option 2 |
| `compound_isolation` | compound / isolation | Non implementee |
| `laterality` | bilateral / unilateral | Non implementee |
| `equipment` | machine / barre / haltere / cable / body / smith / kettlebell | Non implementee |
| `plane` | sagittal / frontal / transverse | Optionnel, rarement decisif pour la substitution |
| `stability` | high / medium / low (fonction de la base et de la charge libre) | Optionnel, affecte la substituabilite |
| `resistance_type` | constant / variable (cable) / gravitational / accommodating | Optionnel, utile pour rattachement zone mais secondaire |

### 3.2 Regle de minimalite

**Ne pas depasser 6 dimensions dans une V1 canonique.** Les 9 ci-dessus sont une reserve. Demarrer avec :

1. `primary_zone` (deja fait)
2. `secondary_zones` (deja fait)
3. `motor_pattern` (nouveau)
4. `compound_isolation` (nouveau)
5. `laterality` (nouveau)
6. `equipment` (nouveau)

Les 3 dernieres (`plane`, `stability`, `resistance_type`) n'ajoutent pas de signal decisif pour la substitution V1. A introduire uniquement si un consumer produit en demande.

### 3.3 Gouvernance de la taxonomie

- Valeurs strictement **enumerees** — aucune chaine libre
- Documentees dans un fichier dedie (ex: `docs/strategy/SPIGNOS_MOVEMENT_TAXONOMY.md`) a creer si Option 2 est triggeree
- QA script verifie que chaque exercice canonique a toutes les dimensions renseignees
- Une nouvelle valeur = un changement de catalogue avec version bump

---

## 4. Taxonomie de proximite substitutive

**Niveaux d'equivalence** pour qualifier une relation `A → B` :

| Niveau | Nom | Semantique | Exemple |
|--------|-----|-----------|---------|
| **1** | `exact` | Meme pattern moteur + meme groupe musculaire + meme charge probable + meme laterality. Quasi interchangeables pour l'analytics. | Hack Squat ↔ Leg Press pieds bas serres |
| **2** | `approx` | Meme zone principale + pattern similaire mais charge ou biomecanique differente. Equivalent pour la zone mais deltas moins fiables. | Chest Press machine ↔ Developpe couche halteres |
| **3** | `fallback` | Meme zone principale mais charge tres differente ou complement fonctionnel. Utile pour debloquer la seance, signal degrade. | Hip Thrust Smith ↔ Hip Thrust halteres, Chest Press machine ↔ Dips pectoraux |
| **4** | `out_of_scope` | Trop eloigne. Ne doit pas etre propose automatiquement. | Squat ↔ Curl (hors perimetre) |

**Regle :** seuls les niveaux 1 a 3 sont acceptables dans le catalogue. Niveau 4 sert de garde-fou pour le QA script (rejeter une relation `exact` entre un squat et un curl).

### 4.1 Impact du niveau sur le signal analytique

| Niveau | Delta progression lisible ? | Last-time pertinent ? | Score qualite comparable ? |
|--------|---------------------------|----------------------|---------------------------|
| exact | Oui | Oui | Oui |
| approx | Partiel (weight non directement comparable) | Oui | Oui, avec marge |
| fallback | Non (charge echelles differentes) | Utile comme reference temporelle | Oui mais a interpreter |
| out_of_scope | N/A | N/A | N/A |

**Exploitable en V2 futur** : le dashboard pourrait afficher un badge "comparabilite degradee" quand un fallback a ete utilise, sans bloquer le user.

### 4.2 Modelisation proposee (cible long-terme)

Trois options de modelisation :

**Option A — Inline dans le JSON** (extension minimale du catalogue actuel) :
```json
"substitutes": [
  {"name": "Developpe couche halteres", "level": "approx"},
  {"name": "Dips pectoraux", "level": "fallback"}
]
```

**Option B — Table dediee** (si Option 2 trigger atteinte) :
```
exercise_substitutions
├── from_exercise_id  FK
├── to_exercise_id    FK
├── equivalence_level VARCHAR(16) (exact / approx / fallback)
├── direction         VARCHAR(16) (unidirectional / bidirectional)
└── UNIQUE(from, to)
```

**Option C — Pas de niveau** (statu quo) : tous les substituts sont traites au meme niveau. Simple mais perd le signal.

**Recommandation :** Option A a l'occasion d'un enrichissement catalogue (sans migration DB — `substitutes_json` stocke deja du JSON libre). Option B seulement si triggers Sx_03.1 atteints.

---

## 5. Comportement UX de la substitution dans le flow Sx_02 (sans rework)

### 5.1 Portee

**Substitution locale a l'exercice actif uniquement.** Jamais cross-template, jamais via un menu global.

### 5.2 Emplacement exact du picker

Dans le body du `<details>` exercice, a la **position 4** de l'ordre vertical fige de Sx_02 FINAL §4.2 :

1. Lien historique discret
2. Set scheme
3. Done-summary (si completed)
4. **Substitute picker** (si `can_substitute` et substitutes disponibles) ou **Substitute badge** (si deja substitue)
5. Last-time
6. Delta
7. Hint
8. Set list warmup
9. Set list work
10. Muscle sensation
11. Free note
12. Footer CTA

### 5.3 Comportement avant choix

- Le picker est un `<details class="substitute-picker">` ferme par defaut
- Summary : "Machine indisponible ? Substituer →"
- Contenu au deplie : radio group avec option prescrite (value="") + options substitutes
- Zero JS, tout natif

### 5.4 Comportement apres choix

- User selectionne une radio autre que la prescrite
- Save exercise card → POST include `substituted_name`
- Server parse et verifie `can_substitute(se)` encore valide (pas de set complete entre temps)
- Le SessionExercise est ecrit avec `substituted_name`
- Au re-render, le picker disparait (lock via `can_substitute` == False apres 1er set ou apres choix)
- Un badge discret `.substitute-badge` remplace : `Substitue : **Developpe couche halteres** (prescrit : Chest Press machine)`

### 5.5 Conservation visible du lien avec l'exercice prevu

- Summary de la carte utilise `substituted_name or exercise_name_snapshot` → affiche le **realise**
- Badge rend explicite le **prescrit** entre parentheses
- Historique et exports preservent les deux colonnes
- `/done` affiche `→ {substituted_name}` a cote du code du slot pour rendre la substitution visible

### 5.6 Compatibilite mobile une main

- Picker = `<details>` standard, tap sur summary pour deplier
- Radio buttons avec target > 44x44px (herite du design system existant)
- Pas de drag, pas de swipe, pas de modal
- Le label de chaque radio est tronque a 30 caracteres (tronque cote template via `truncate(30)`) pour eviter wrap agressif

---

## 6. Garde-fous figes par Sx_02 (inchangeables par Sx_03)

| Garde-fou | Reference Sx_02 FINAL | Impact si casse |
|-----------|----------------------|----------------|
| Position picker (top body, apres done-summary, avant last-time) | §4.2 ordre vertical fige bloc 4 | Re-design complet du body obligatoire |
| Mecanisme `can_substitute(se)` (False si 1 work set completed) | §5.5 transitions + §11 contraintes | Casse le principe "lock apres execution", regressions historique |
| Fallback summary `substituted_name or exercise_name_snapshot` | §4.1 header + template line 59 | Casse display dans jump bar, summary card, recap |
| Parsing serveur `form.get("substituted_name")` avec check `can_substitute` | Sb_03 deja buildee | Casse la route POST, tests d'integration |
| Structure data `substitution_data[id] = {substitutes, can_substitute}` | §2.2 context template | Casse le template Jinja, necessite re-ecriture context |
| Zero JS | Sx_02 §8 regles densite | Sort de la grammaire SSR, effet SPA |

**Sx_03 peut enrichir SANS toucher ces elements.** Extensions natives documentees en Sx_02 FINAL §11.4 :
- Ajout d'attributs `data-equivalence` sur les options du picker
- Badge `.substitute-badge` enrichi avec raison ou niveau
- Nouveau `<details>` optionnel pour `substitution_reason`
- Metadata visuelles discretes sur les options du picker

---

## 7. Plus petit modele de persistance viable

### 7.1 Stockage sur le PREVU (`template_exercises`)

| Champ | Type | Statut | Role |
|-------|------|--------|------|
| `name` | VARCHAR(255) | Existe | Nom prescrit du slot |
| `substitutes_json` | TEXT nullable | Existe | Liste JSON de noms substituts |
| (futur) `motor_pattern` | VARCHAR(32) | Optionnel Option 2 | Taxonomie |
| (futur) `equipment` | VARCHAR(32) | Optionnel Option 2 | Taxonomie |

### 7.2 Stockage sur le REALISE (`session_exercises`)

| Champ | Type | Statut | Role |
|-------|------|--------|------|
| `exercise_code_snapshot` | VARCHAR(16) | Existe, immutable | Slot prescrit (E1, E2...) |
| `exercise_name_snapshot` | VARCHAR(255) | Existe, immutable | Nom prescrit fige |
| `substituted_name` | VARCHAR(255) nullable | Existe | Nom reellement execute si substitue |
| (optionnel) `substitution_reason` | VARCHAR(32) nullable | Gap 2 de Sx_03.1 | Raison de substitution |
| (optionnel) `substitution_level` | VARCHAR(16) nullable | Si Option A adopte | Niveau d'equivalence au moment du choix |

### 7.3 Stockage sur la RELATION (catalogue)

Aujourd'hui : simple liste dans `substitutes_json`. 

Evolution possible Option A (sans migration) :
```json
"substitutes": [
  {"name": "X", "level": "approx"},
  {"name": "Y", "level": "fallback"}
]
```

Evolution Option B (avec migration, si triggers atteints) : table `exercise_substitutions` dediee.

### 7.4 Snapshot vs canonique

**Regle inviolable :** les `snapshots` (`exercise_code_snapshot`, `exercise_name_snapshot`, `template_slug_snapshot`, `template_name_snapshot`) sont **immutables** apres creation. Le catalogue peut evoluer (reseed, version bump) sans affecter l'historique.

**Canonique** (si jamais introduit en Option 2) serait reference via FK optionnelle (`prescribed_exercise_id`, `actual_exercise_id` nullable), pas via remplacement des snapshots.

### 7.5 Strategie de compatibilite historique

- **Zero migration destructive** — toutes les evolutions possibles (raison, niveau, canonique) sont **additives**
- Les valeurs legacy (null) ne bloquent rien — tous les consumers tolerent
- Les exports preservent les anciennes colonnes
- QA script peut valider les nouvelles valeurs sans toucher aux anciennes

---

## 8. Impacts historique — 3 lectures distinctes

### 8.1 Lecture 1 — Historique strict d'execution

**Question repondue :** "Qu'est-ce que j'ai REELLEMENT fait au cours du temps ?"

**Source :** `actual_exercise_name(se)` (realise).

**Consumers :**
- `muscle_scoring.py` — classifie le muscle zone selon ce qui a ete fait
- `physique dashboard` — zones reflètent l'execution reelle
- `sharing.py` — les sharecards montrent le realise
- Future correlation zone ↔ mesures corporelles

**Comportement attendu :** si le user substitue systematiquement Chest Press par Developpe couche halteres, le muscle_scoring voit du pecs (zone commune) mais avec secondary zones potentiellement differentes (triceps vs stabilisateurs scapulaires). Pas de perte de signal.

### 8.2 Lecture 2 — Lecture orientee template (slot)

**Question repondue :** "Comment j'ai progresse sur le SLOT E2 de Push A au cours du temps ?"

**Source :** `(template_slug_snapshot, exercise_code_snapshot)` (slot identity, ignore substitutions).

**Consumers :**
- `last_time_by_exercise_code` — slot-based (retourne le dernier E2 de Push A peu importe substitutions)
- `delta.py` — compare first completed sets entre occurrences du meme slot
- `progression_hint.py` — hint base sur prior weight/reps du meme slot
- `exercise_history` — historique par (template, code)
- `kpis` per template — agrege par template_slug

**Comportement attendu :** l'historique du slot E2 de Push A mixe les occurrences "Chest Press machine" et "Developpe couche halteres" comme si c'etaient des executions du meme slot (ce qu'elles sont fonctionnellement). Les deltas de weight peuvent etre bizarres entre deux substitutions differentes, mais c'est un cout acceptable pour la perspective programme.

### 8.3 Lecture 3 — Lecture par pattern / groupe musculaire (futur)

**Question repondue :** "Combien de push horizontal est-ce que je fais par semaine ?"

**Source :** taxonomie de mouvement + `actual_exercise_name` → agregation par `motor_pattern` et `primary_zone`.

**Consumers (futurs) :**
- Body engineering dashboard v2 — axe "equilibre patterns" (push vs pull vs squat vs hinge)
- Alertes de desequilibre ("tu fais 80% de push vs 20% pull")
- Recommandations adaptatives

**Pre-requis :** taxonomie de mouvement deployee (voir §3). **Pas faisable aujourd'hui.** Documentee comme vision long-terme, pas comme feature imminente.

---

## 9. Impacts analytics

### 9.1 Dernier fois (`last_time`)

**Comportement actuel :** slot-based. Retourne le dernier E2 de Push A peu importe substitutions. Le `weights_str` et `reps_str` affiches peuvent donc venir d'une substitution differente de celle en cours.

**Impact user :** acceptable. Le user comprend que "la derniere fois sur ce slot" peut etre une machine differente.

**Amelioration future potentielle :** afficher un badge discret "Derniere fois : {actual_exercise_name}" si substituted. Non-bloquant, pure enhancement.

### 9.2 Deltas

**Comportement actuel :** compare first completed work sets du meme slot. Si deux occurrences consecutives ont des substitutes differents, le delta de weight/reps peut etre biaise (ex: "+15 kg" quand on passe d'halteres a machine).

**Mitigation future si Option A adopte :** annoter le delta avec le niveau d'equivalence. Si `approx` ou `fallback`, afficher un `~` ou un tooltip explicatif. **Optionnel, pas bloquant.**

### 9.3 Progression par exercice

**Par slot** (lecture 2) : inchange, fonctionne deja via snapshots.

**Par exercice canonique** (lecture 1, nominal) : possible aujourd'hui via `actual_exercise_name` + agregation par nom. **Mais fragile** (typos, variantes de casse). **Robuste en Option 2** via FK.

### 9.4 Progression par pattern

**Aujourd'hui** : impossible (pas de taxonomie de mouvement). Aucun consumer ne la calcule.

**Futur** : necessite taxonomie §3. Deferee.

### 9.5 Dashboards futurs

- **Physique dashboard** : deja correctement nourri via `actual_exercise_name` → zone classification. Aucun impact negatif.
- **Body engineering dashboard** : meme logique, pas de rework.
- **Dashboard "patterns" futur** : necessite §3 (non implementee).

### 9.6 Compare mode (entre membres d'une squad)

**Question :** "Alice fait E2 Chest Press, Bob substitue par Developpe couche. Comment comparer ?"

**Strategie :** comparer par **slot** (lecture 2) pour l'affichage side-by-side. Les deux font "E2 de Push A". Les weights peuvent etre sur des echelles differentes. Afficher un badge de substitution transparent pour que le context soit clair.

**Ne pas agreger de force les substitutes differents.** Le compare mode affiche ce qui a ete fait cote Alice et cote Bob, honetement.

### 9.7 Score qualite / interpretation future

**Aujourd'hui :** `success_score` derive (Sx_01 FINAL) s'applique au SessionExercise via rep_targets du slot prescrit. La substitution n'affecte pas les rep_targets → le score reste calculable et comparable.

**Cas edge :** si le user substitue un compound 6-10 par un isolation 12-15, les rep_targets ne sont plus adaptes. Le score derive peut etre dur (le user fait 12 reps d'isolation vs target max=10 de compound → score 100 mais semantiquement le context a change).

**Acceptation :** c'est le cout de la substitution. Le user sait ce qu'il a fait. L'alternative (recalculer rep_targets en dynamique) est une complexification non-justifiee en V2.

---

## 10. Gouvernance catalogue

### 10.1 Ou vit le graphe

**Aujourd'hui** : dans `data/reference_split.json`, champ `substitutes` par exercice.

**Versionne** via `version: YYYY-MM-DD.vN` dans le meme fichier.

**Seed** : `app/services/seed.py` repopulate la DB quand la version change.

### 10.2 Enrichissement progressif

**Politique :** **ajouter des relations une par une, via revue humaine**.

Pipeline :
1. Identification d'un besoin (ex: utilisateur signale qu'il substitue souvent E4 de Push A)
2. Ajout d'une relation dans le JSON avec (eventuellement) un niveau d'equivalence
3. Bump de version
4. Run QA script → garantit classifiability
5. Commit + deploy

**Pas de generation automatique** de relations. Risque d'ontologie explosive.

### 10.3 Eviter l'ontologie infinie

Regles pragmatiques :

- **Max 3 substituts par exercice** (viser 2 en pratique)
- **Substituts asymetriques autorises** (A→B ne signifie pas B→A automatiquement) — la question "quel substitut ai-je sous la main ?" depend du slot source
- **Pas de substituts cross-zone** (pas de pecs→dos)
- **Pas de substituts de niveau 4** (out_of_scope) — QA script les rejette si tentative

### 10.4 Comment commencer petit mais utile

**Priorite d'enrichissement catalogue** :

| Priorite | Type d'exercice | Raison |
|----------|----------------|--------|
| **P1** | Machines compound souvent occupees (Chest Press, Hack Squat, Leg Press) | Forte valeur UX immediate |
| P2 | Smith machines (Incline Smith, Smith Squat) | Alternative haltere/barre souvent possible |
| P3 | Machines d'isolation (Leg Extension, Leg Curl) | Alternatives haltere ou cable |
| P4 | Exercices a haut turnover (cables, halteres) | Rarement occupes, P4 |

**Status actuel :** 9 relations couvrent essentiellement P1 et partiellement P2. C'est deja un bon point de depart.

### 10.5 Critere de migration vers Option 2

Si et seulement si **2+ triggers Sx_03.1** sont atteints :
1. Catalogue >150 exercices OU >40 relations
2. >1 editeur
3. Requete analytique cross-cutting emergente
4. Feature custom exercises
5. Bidirectional graph necessaire
6. Typos/aliases probleme recurrent

Alors : rediger un Sb_X dedie avec migration, backfill, et garde-fous tests.

---

## 11. Wireframes textuels SSR / mobile-first

### 11.1 Exercice actif NON substituable (pas de substitutes catalogues)

```
┌────────────────────────────────────────┐
│ ▼ E1 Incline Smith Press    0/3 ●      │  ← active
│                                        │
│    Voir historique E1 →                │
│    3x 6-10                             │
│                                        │
│  [pas de picker affiche]               │
│                                        │
│    Derniere fois · il y a 4j           │
│    70/70/70 kg · 8/8/8 reps            │
│    ...                                 │
└────────────────────────────────────────┘
```

### 11.2 Exercice actif SUBSTITUABLE (substitutes dispo, rien coche)

```
┌────────────────────────────────────────┐
│ ▼ E2 Chest Press machine    0/3 ●      │  ← active
│                                        │
│    Voir historique E2 →                │
│    3x 8-12                             │
│                                        │
│    ▶ Machine indisponible ? Substituer │  ← <details> picker ferme
│                                        │
│    Derniere fois · il y a 4j           │
│    55/55/55 kg · 10/10/10 reps         │
│    ...                                 │
└────────────────────────────────────────┘
```

Au deplie :
```
    ▼ Machine indisponible ? Substituer
    ┌────────────────────────────────────┐
    │ ( ) Chest Press machine            │  ← prescrit, default
    │ ( ) Developpe couche halteres      │
    │ ( ) Dips pectoraux (buste penche)  │
    └────────────────────────────────────┘
```

### 11.3 Exercice actif SUBSTITUE (user a choisi)

```
┌────────────────────────────────────────┐
│ ▼ E2 Developpe couche halteres  0/3 ●  │  ← summary affiche le realise
│                                        │
│    Voir historique E2 →                │
│    3x 8-12                             │
│                                        │
│  ┌─────────────────────────────────┐   │
│  │ Substitue : Developpe couche... │   │  ← badge discret
│  │ (prescrit : Chest Press machine)│   │
│  └─────────────────────────────────┘   │
│                                        │
│    Derniere fois · il y a 4j           │
│    55/55/55 kg · 10/10/10 reps         │
│    ...                                 │
└────────────────────────────────────────┘
```

### 11.4 Exercice done avec rappel du substitut

```
┌────────────────────────────────────────┐
│ ▶ E2 Developpe couche halteres  3/3 ✓  │  ← compact, done (ok)
│    22/22/22 kg · 10/10/10 reps         │
└────────────────────────────────────────┘
```

Au deplie par re-clic :
```
▼ E2 Developpe couche halteres   3/3 ✓
  ┌─────────────────────────────────┐
  │ Substitue : Developpe couche... │
  │ (prescrit : Chest Press machine)│
  └─────────────────────────────────┘
  ... (reste du body inchangee) ...
```

### 11.5 Historique (exercise_history page) — prevu vs realise lisible

```
E2 de Push A — Historique

Lun 14/04 · Push A
  → Developpe couche halteres      22/22/22 kg · 10/10/10 · score 100

Ven 11/04 · Push A
  Chest Press machine              55/55/55 kg · 10/10/10 · score 80

Mar 08/04 · Push A
  → Dips pectoraux (buste penche)  BW · 8/8/6 · score 50

Sam 05/04 · Push A
  Chest Press machine              55/55/50 kg · 10/10/8 · score 80
```

Regle visuelle : prefixe `→` quand substitue (avec nom realise), sans prefixe quand prescrit execute tel quel.

### 11.6 Page `/done` avec substitutions

```
Par exercice
  E1  Incline Smith Press       3/3   100
  E2  → Dev. couche halteres    3/3    80
  E3  Dips pectoraux            3/3   100
  E4  ...
```

Resume section affiche `Substitutions : 1` si au moins une substitution dans la seance.

---

## 12. Matrice impacts historique + analytics

| Surface | Lecture | Comportement substitution | Impact |
|---------|---------|--------------------------|--------|
| `last_time_by_exercise_code` | Slot | Retourne derniere occurrence du slot (ignore substitution) | Neutre |
| `compute_delta` | Slot | Compare first completed sets du slot | Biais possible si substitutes differents |
| `compute_progression_hint` | Slot | Hint base sur prior first set du slot | Neutre |
| `exercise_history` | Slot | Affiche prevu + realise via actual_exercise_name | Lisible avec prefixe → |
| `kpis` per template | Slot (groupe par template_slug) | Agrege par template | Neutre |
| `muscle_scoring` zones | Realise (actual_exercise_name) | Classifie zone selon ce qui a ete fait | Correct |
| `physique dashboard` | Realise | Via muscle_scoring | Correct |
| `body engineering dashboard` | Realise | Via muscle_scoring | Correct |
| `sharing` sharecards | Realise (actual_exercise_name) | Affiche ce qui a ete fait | Correct |
| `export_builder` JSON/CSV | Les deux (snapshots + substituted_name) | Preserve tout | Complet |
| `session_recap` /done | Realise (display) + count | Affiche realise + compte substitutions | Correct |
| `leaderboard` (global et squad) | Via quality_score | Score fonctionne sur SessionExercise snapshots | Neutre |
| Squad compare (S3) | Slot + realise affiches | A designer : montrer prescrit + realise cote a cote | Non-trivial (Sx_04 ou S4) |
| Future analytics pattern (§8.3) | Realise + taxonomie | Agrege par motor_pattern via canonical | Non faisable aujourd'hui |

---

## 13. Preparation future build (sans l'implementer)

### 13.1 Migrations probables

**Scenario A — Enrichissement Option A (raison + niveau inline JSON)** :
- Migration 1 : `ALTER TABLE session_exercises ADD COLUMN substitution_reason VARCHAR(32) NULL;`
- Bump version catalogue JSON avec syntaxe `{"name": "X", "level": "approx"}`
- Script one-shot de normalisation des `substitutes_json` existants : transformer les listes de strings en listes d'objets (niveau = null par defaut)
- Impact : nul sur consumers existants (tolerants)

**Scenario B — Migration Option 2 (canonical entity)** : seulement si 2+ triggers Sx_03.1 atteints.
- Migration : creer table `exercises`, `exercise_substitutions`
- Backfill : mapper les ~97 exercices distincts du catalogue vers des entrees canoniques
- Resolution des ambiguites (typos historiques, casse differente)
- Ajout de FK optionnelles sur `template_exercises.exercise_id` et `session_exercises.prescribed_exercise_id` / `actual_exercise_id`
- Scripts de reconciliation + tests exhaustifs

Les 2 scenarios sont mutuellement exclusifs en pratique (Option 2 absorbe Option A).

### 13.2 Services a creer / refactorer

**Si Option A build (Sb_03.1 enrichi)** :
- Etendre `get_substitutes(te)` pour retourner `list[dict{name, level}]` au lieu de `list[str]`
- Garder compatibilite : si format ancien (liste strings), wrapper chaque element en `{name: X, level: null}`
- Ajouter helper `get_substitute_level(te, name) -> str | None`
- Consumer template : picker affiche le niveau comme attribut discret (badge ou tooltip)

**Si Option 2 build (hypothetique)** :
- Nouveau service `app/services/exercise_catalog.py` avec CRUD canonique
- Refactor `muscle_mapping.classify_exercise` pour resoudre via FK
- Helpers de reconciliation (resolve_by_name_or_alias)

### 13.3 Points de tests critiques

| Test | Objectif |
|------|----------|
| `test_substitution_lock_after_first_completed_set` | Verifier que `can_substitute` bascule a False |
| `test_substituted_name_snapshots_preserved` | Verifier que `substituted_name` persiste a travers reseed |
| `test_actual_exercise_name_classification` | Verifier zone classification correcte en substituant |
| `test_substitution_level_in_delta` (futur) | Verifier badge de delta si niveau approx/fallback |
| `test_catalog_qa_rejects_out_of_scope_substitution` | QA script refuse pecs→squat (futur si levels introduits) |
| `test_historique_affiche_realise_vs_prescrit` | Visuel, verifier prefixe → |
| `test_substitution_reason_optional` (si build) | Reason nullable, pas de blocage |

### 13.4 Consumers a ajuster plus tard

- `delta.py` : optionnellement annoter avec `substitution_mismatch` flag si les 2 cotes ont des substitutes differents
- `exercise_history.py` : ajouter colonne `substitution_level` dans les entries si Option A adopte
- `compare mode` (S4 future) : afficher prescrit + realise side-by-side
- `dashboard / body engineering` : introduire un 6e axe "adherence pattern" si taxonomie §3 deployee

---

## 14. Recommandations ordonnees pour le futur build

Aucun build obligatoire par ce spec. Recommandations priorisees :

### P1 — Rien a faire maintenant

L'etat actuel (Option 1 JSON-based integralement buildee) est le **bon choix** tant que 0 trigger Sx_03.1 n'est atteint.

### P2 — Enrichissement catalogue incremental

Ajouter 2-3 nouvelles relations de substitution par trimestre en fonction des besoins terrain remontes. Rester dans la gouvernance §10.

### P3 — Sb_03.1 leger : ajouter `substitution_reason`

**Cout estime :** 1-2h. **Valeur :** gouvernance moyen terme (detecter patterns de blocage machines).
**Quand :** a arbitrer. Non-urgent. Le user n'en a pas besoin pour utiliser le produit.

### P4 — Enrichissement JSON avec niveaux d'equivalence (Option A)

**Cout estime :** 2-3h + revue catalogue.
**Valeur :** analytics de confiance + badge UX.
**Quand :** si une remontee user demande "pourquoi mon delta est bizarre quand je substitue".

### P5 — Migration Option 2 (canonical entity)

**Cout estime :** sprint dedie, 8-12h + backfill + tests exhaustifs.
**Valeur :** robustesse + extensibilite (custom exercises, cross-cutting queries).
**Quand :** SI et SEULEMENT SI 2+ triggers Sx_03.1 atteints. Pas avant.

### P6 — Taxonomie de mouvement complete (§3)

**Cout estime :** revue de 97 exercices + design de 6 dimensions + QA.
**Valeur :** analytics par pattern, alertes desequilibre.
**Quand :** apres Option 2 si triggers, ou si feature produit dedie emerge.

---

## 15. Definition of Done

| Critere | Statut |
|---------|--------|
| Prevu vs realise formalise sans ambiguite | ✓ (§2 modele conceptuel 5 niveaux) |
| Graphe de substitution defini avec niveaux d'equivalence | ✓ (§4 taxonomie 4 niveaux + regles) |
| UX locale substitution dans exercice actif claire | ✓ (§5 position, comportement avant/apres, mobile une main) |
| Compatibilite Sx_02 demontree | ✓ (§6 tableau 6 garde-fous inchangeables) |
| Impacts historiques documentes | ✓ (§8 trois lectures distinctes) |
| Impacts analytics documentes | ✓ (§9 sept surfaces + §12 matrice complete) |
| Gouvernance catalogue realiste | ✓ (§10 regles + priorites P1-P4 enrichissement) |
| Zero rework composant exercice implicite | ✓ (§6 garde-fous + §13.2 services refactorables sans casser le template) |

---

## 16. Synthese executive

**Substitution SPIGNOS — etat V2 stable :**

- **5 niveaux conceptuels** distingues (canonique / prevu / realise / relation / niveau)
- **4 niveaux d'equivalence** proposes (exact / approx / fallback / out_of_scope)
- **6 dimensions de taxonomie minimale** (zone primary + secondary + pattern + compound + laterality + equipment)
- **3 lectures analytiques** coexistantes (execution stricte / slot-based / pattern futur)
- **Option 1 buildee** (JSON, `substituted_name`, picker UI, consumers cables)
- **Option 2 deferee** jusqu'a triggers explicites (6 triggers Sx_03.1)
- **6 garde-fous** de Sx_02 inchangeables par Sx_03
- **P3 enrichissement `substitution_reason`** identifie comme prochaine amelioration legere optionnelle

Le graphe de substitution est **fonctionnel, analytiquement correct, historiquement resilient, et extensible**. Zero rework composant exercice anticipe.
