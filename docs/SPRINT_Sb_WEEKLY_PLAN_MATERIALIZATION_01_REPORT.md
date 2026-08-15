# SPRINT Sb_WEEKLY_PLAN_MATERIALIZATION_01 — du plan au programme (RAPPORT)

**Train :** `AUREN_WEEKLY_PLAN_PRODUCTIZATION_01`, tranche 4/4 — **clôture** ·
**Base canonique :** `4740926` · **Branche :** `sb/weekly-plan-materialization-01` ·
**Tier `check_scope` :** **SHARED_CODE**

Le pont qui manquait depuis `Sb_WEEKLY_PLANNER_01` : jusqu'ici `WeeklyPlan`
était une **proposition** que rien ne pouvait exécuter.

---

## 1. Brainstorming / Options / Risques / Choix retenu

### Aucun cycle de vie parallèle — la contrainte structurante

Le brouillon est créé par les services **existants** : `create_draft` →
`replace_draft_tree` → `validate_draft` → `compute_quality_preview`. Pas de
nouvelle machine à états, pas de table, pas de chemin de publication concurrent.
Publier reste `user_program_publish`, sur action explicite, et **une version
publiée n'est jamais mutée** — une replanification produira un nouveau
brouillon, comme n'importe quelle autre modification.

### Ce qui est repris du mapper morpho, et ce qui ne l'est pas

**Repris** : forme de l'arbre, enrichissement EKB (correspondance de nom
canonique **exacte**, `{}` sinon), convention `source_reason`, refus de
fabriquer, limites Custom Program.

**PAS repris** : `_INTENT_PRESCRIPTION` comme source de volume. Le nombre de
séries vient du **plan**, qui le tient du budget. Le réutiliser réintroduirait
la seconde vérité de volume que la tranche 2 s'est employée à supprimer. Deux
tests le garantissent : un **structurel** (la table n'est pas importée) et un
**comportemental** (au moins un exercice diffère du chiffre du mapper — sans
quoi la garde structurelle pourrait passer tout en laissant les valeurs
coïncider par accident).

### Le piège trouvé en lisant `validate_draft` avant d'écrire

`validate_draft` refuse une séance sans exercice. Or le plan contient un créneau
`core` **sans exercice** : le laisser entrer dans l'arbre aurait rendu **tout le
brouillon invalidable**, pour une lacune que le plan signale déjà par ailleurs.

Les créneaux vides sont donc écartés, et une séance qui n'en contiendrait que de
tels créneaux l'est aussi. Les positions sont **recalculées en 1..N** :
`replace_draft_tree` exige des positions contiguës, et conserver l'index
d'origine y laisserait des trous. Le manque, lui, ne disparaît pas — il reste
dans le plan et dans le statut.

### Où mettre l'action — et pourquoi pas la Home

Le brief dit « smallest viable **Home/program** consumer ». J'ai choisi la page
**`/programs`**, pas la Home, pour une raison de risque : la Home porte la
parité de recommandation, prouvée octet pour octet sur trois sprints. Y ajouter
une action de création de programme mettrait un geste mutatif sur la surface la
plus gardée du dépôt, alors que « créer un programme » a déjà sa page. La Home
reste **totalement inchangée** par cette tranche.

---

## 2. Le statut dit la vérité, y compris quand elle est partielle

| Statut | Quand | Matérialisable ? |
|---|---|---|
| `READY` | aucune lacune | oui |
| `PARTIAL` | manque de volume structurel | **oui** — exécutable, pas complet |
| `CONSTRAINT_UNMET` | une priorité **déclarée** n'est pas servable | **oui**, mais jamais présenté comme prêt |
| `BLOCKED` | pas de cadence, ou rien de prescrit | **non** — il n'y a rien à écrire |

`CONSTRAINT_UNMET` **prime** sur `PARTIAL` : une promesse faite à l'utilisateur
et non tenue compte davantage qu'un chiffre en deçà.

Un booléen aurait forcé à choisir entre « prêt » et « refusé » là où la réponse
honnête est le plus souvent « exécutable, mais voici ce qui manque ».

---

## 3. La surface

Sur `/programs`, un bloc affiche **avant toute action** : séances/semaine,
exercices, séries planifiées, priorités déclarées, contraintes non résolues et
statut de couverture. Puis **« Créer le programme proposé »**.

Rien n'est automatique : le bloc informe, le bouton agit, et la page suivante
est l'éditeur de brouillon habituel. La page dit explicitement qu'un
**brouillon** est créé et que rien n'est publié ni lancé.

**Confinement** : toute panne de la chaîne de planification laisse la
bibliothèque strictement intacte — la proposition disparaît, la page reste
servie. Proposer un programme est un plus ; ce n'est jamais une raison de casser
l'existant.

---

## 4. Bout en bout, prouvé sur la base

`TrainingPreferences` → `WeeklyVolumeBudget` → `WeeklyPlan` **avec séries** →
brouillon Custom Program → `compute_quality_preview` → `validate_draft`.

Un second test vérifie que **le nombre de `rep_targets` persistés égale le total
de séries du plan** — la dose traverse la frontière sans se perdre.

Le moteur de qualité existant note le brouillon **sans modification** : il
agrégeait déjà `sets_by_zone` depuis `working_sets`, il lit donc les vrais
chiffres sans qu'une ligne y soit touchée.

**Publication, lancement et exécution de séance : aucun changement.** Le test
qui compte est celui qui vérifie qu'après l'action, **tous** les programmes de
l'utilisateur sont en statut `draft`.

---

## 5. Tests — 23 dédiés

Verdict (bloqué sans cadence · partiel sur manque de volume · `CONSTRAINT_UNMET`
prioritaire · jamais `READY` à tort · compte seulement le travail exécutable) ·
arbre (créneaux vides écartés · aucune séance vide · positions contiguës · une
cible de répétitions par série · traçabilité `source_reason` · volume **pas**
issu du mapper, garde structurelle **et** comportementale · déterminisme) ·
bout en bout (chaîne complète validable · séries persistées conformes · refus
d'un plan sans rien d'exécutable) · surface (absente sans cadence · présente
avec · dit « brouillon » · dit « partielle » · crée bien un brouillon · **ne
publie jamais** · confinement de panne).

`S9073` / `S5863` / `S3415` **pré-scannés avant push** : 0, 0, et 6 comparaisons
toutes « actual first ».

> **Note honnête sur un test écarté.** J'avais écrit un test de confinement qui
> remplaçait `_weekly_plan_proposal` elle-même par une fonction qui lève —
> c'est-à-dire **en dehors** du `try/except` qu'il prétendait vérifier. Il ne
> prouvait rien et échouait pour la mauvaise raison. Supprimé ; le test qui fait
> réellement le travail plante la panne **à l'intérieur** de la chaîne.

---

## 6. Non-régressions

Aucune migration, aucune table · Home **non touchée** · `recommendation.py` /
`behavioral.py` / `substitution.py` non touchés · `user_program_publish` /
`user_program_launch` / `session_builder` non touchés · aucun programme publié
muté · `_INTENT_PRESCRIPTION` ni importé ni modifié.

**Échecs locaux hors périmètre** : 3 tests de `test_v1_acceptance.py` sur
`.vscode/launch.json`, absent d'un worktree. Ce fichier n'est pas versionné et
le module est **structurellement exclu de la CI** (`EXCLUDED` dans
`ci_test_shards.py`, `--ignore` dans `run_ci_pytest.sh`). Pré-existant, sans
rapport avec cette tranche.

## Verdict

Le plan devient un **programme exécutable** par le cycle de vie existant, sans
en ouvrir un second, et sans qu'aucune étape se déclenche toute seule :
l'utilisateur voit ce qu'il obtiendra, décide, et récupère un brouillon
modifiable.

Le train se termine sur une chaîne complète et vérifiée de bout en bout —
préférences déclarées, budget en séries, plan, dose, programme — dont chaque
maillon dit ce qu'il ne sait pas faire.

**Ce que le train ne résout pas, et qu'il faut décider** : le programme produit
délivre **44 séries pour 126 en borne basse**. Il est utilisable, honnêtement
étiqueté `PARTIAL`, mais il ne remplit pas le budget. La suite est
`Sb_WEEKLY_PLAN_SLOT_EXPANSION_01` — et c'est une décision sur la forme des
séances, donc une décision produit.
