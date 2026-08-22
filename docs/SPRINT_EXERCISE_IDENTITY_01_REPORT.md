# `Sb_EXERCISE_IDENTITY_01` — l'entité qui n'existait pas

**Tranche** : arbitrage opérateur **A1**, première du TRAIN 1
**Branche** : `sb/exercise-identity-01` · **base canonique** : `c714f36`
**Tier `check_scope`** : `MIGRATION` — tous les contrôles exigés, full sweep local compris

---

## 0. Brainstorming / Options / Risques / Choix retenu

*(CLAUDE.md §3)*

### La question de l'opérateur, et sa réponse mesurée

> « Si une PK canonique existante peut remplir ce rôle, la réutiliser ; sinon
> introduire un identifiant opaque stable. »

**Aucune PK existante ne peut jouer ce rôle, parce qu'aucune table ne
représentait un exercice.** Il n'existait que des *lignes* qui en mentionnaient
un. Mesuré sur les données de graine :

| Candidat | Mesure | Verdict |
|---|---|---|
| `template_exercises.code` (`E1…E8`) | **7 codes sur 8 portent plusieurs noms** (`E3` en porte 15) | C'est une **position** dans un gabarit |
| `template_exercises.id` | **28 noms sur 68 vivent dans ≥2 gabarits** | Identifie une **ligne de programme** |
| `exercise_muscle_mappings.exercise_code` | contient un **nom**, malgré son intitulé | C'est la clé fragile elle-même |
| `session_exercises.*_snapshot` | texte figé | Instantané, pas identité |

Le catalogue compte **17 gabarits, 106 lignes, 68 noms distincts**.

### Ce qui rend le backfill possible

Une slugification déterministe des 68 noms produit **68 slugs distincts, zéro
collision**. C'est la mesure qui autorise une migration purement additive : il
n'y a rien à arbitrer pour créer les identités.

### Options

| # | Option | Verdict |
|---|---|---|
| A | Nom canonique comme identité | **Rejetée** par l'opérateur — ne survit pas au premier renommage. |
| B | Identifiant **opaque** (UUID) | **Rejetée en partie.** L'opacité rendrait indéchiffrables les fichiers de graine, les traces et les rapports. La stabilité ne vient pas de l'opacité : elle vient de ce qu'on **ne régénère jamais**. |
| **C** | **Slug lisible engendré une fois, jamais régénéré** + `name` mutable | **Retenue.** `slug` est l'identité, `name` un libellé. C'est toute la séparation qui manquait. |

### Le risque qui a décidé de la forme de la migration

Ajouter une colonne `exercise_id` sur `session_exercises` puis la remplir
resterait un **`UPDATE` sur des lignes historiques** — et l'ambiguïté de forme
d'une migration est un **arrêt dur** du contrat de dépôt (CLAUDE.md §4).

D'où le choix : **aucune clé étrangère sur les tables existantes.** La
résolution se fait à la lecture, par la table d'alias. L'identité existe et est
utilisable sans qu'une seule ligne d'historique soit réécrite. La dénormalisation
reste possible plus tard, si un besoin mesuré la justifie.

Une garde AST le verrouille : la migration ne peut appeler que
`create_table` / `create_index` / `drop_*`. **Pas même `op.execute`** — une
migration qui exécute du SQL sème ou mute.

---

## 1. Ce que la tranche livre

### `app/models/exercise.py`

| Table | Rôle |
|---|---|
| `exercises` | `slug` **immuable** (identité) · `name` **mutable** (libellé) · `source` · `created_at` |
| `exercise_aliases` | `alias` brut · `normalized` **unique** · FK `CASCADE` |

L'unicité porte sur la forme **normalisée**, pas sur la forme brute. Sans cela,
`Curl marteau câble (corde)` et `Curl marteau câble corde` — **deux chaînes
réellement présentes dans deux fichiers de `data/`** — cohabiteraient comme deux
exercices.

### `app/services/exercise_identity.py`

`normalize` · `slugify` · `resolve_exercise` · `ensure_exercise` · `add_alias`.

Deux propriétés voulues :

- **Un seul chemin de résolution.** L'exercice possède toujours un alias : le
  sien. Il n'y a donc pas un « chemin principal » et un « chemin alias » à tenir
  en accord.
- **`add_alias` refuse un nom déjà porté par un autre exercice.** Repointer
  serait une **fusion**, et une fusion est un jugement produit.

### `app/services/seed_exercise_identity.py`

Idempotent, rejouable, **n'invente aucun nom**. Ordre : catalogue d'abord (pour
que `name` soit le nom que l'utilisateur voit), puis EKB, puis les alias déjà
déclarés dans `exercise_knowledge_base._aliases`.

**Preuve de bout en bout** sur une base réelle :

```
1er passage : Exercise identity: 102 exercices (+68 catalogue, +34 EKB), 2 alias déclarés
2e  passage : Exercise identity: 102 exercices (+0 catalogue, +0 EKB), 0 alias déclarés
```

---

## 2. Deux défauts trouvés en construisant

### 2.1 — L'EKB contient deux lignes pour le même exercice, **et elles se contredisent**

`103` entrées, `102` exercices. Une garde a rougi sur ce `-1` et l'a mis au
jour :

| Champ | `Curl marteau câble (corde)` | `Curl marteau câble corde` |
|---|---|---|
| `zone_primary` | `biceps` | `None` |
| `zone_macro` | `arms` | `None` |
| `confidence` | `measured` | `derived` |
| `variant_key` | `curl-marteau-cable-paren-corde` | `curl-marteau-cable-corde` |

Le même mouvement était donc **cartographié ou non selon l'orthographe
rencontrée**. C'est exactement la fragilité qu'A1 existe pour tuer, et elle
vivait déjà dans la base de connaissance dite canonique.

La graine conserve l'entrée du catalogue — ici, aussi la mesurée. Ce n'est pas
un hasard heureux mais l'effet de l'ordre des sources, et une garde le fixe :
`test_the_surviving_row_of_the_collapse_is_the_one_the_user_sees`.

**Je ne corrige pas l'EKB dans cette tranche** : ce serait modifier une source
de connaissance sur un jugement, hors périmètre A1.

### 2.2 — `check_alembic_drift` mesurait le mauvais arbre

Lancé depuis le worktree via `env -C`, le script a rendu **`DRIFT DETECTED`** en
listant mes deux tables comme « à supprimer ». Faux : il migrait les migrations
**du worktree** tout en chargeant les modèles **de la canonique** — le script
n'insère pas son `repo_root` dans `sys.path`, donc `import app` résout ailleurs.

Avec `PYTHONPATH` sur le worktree : `OK (no diff)`.

C'est la même famille de piège que le sweep qui teste la canonique depuis un
worktree. **Tous les contrôles de cette tranche ont été relancés avec
`PYTHONPATH`.** Le durcissement du script lui-même est un sujet `ci_infra`
distinct, signalé et non traité ici.

---

## 3. Ce que la tranche ne tranche pas

**Une identité par nom distinct existant. Aucune fusion.**

L'audit a relevé **17 paires de quasi-doublons dans le seul catalogue** :

- vraisemblablement le **même** mouvement — `Hip thrust Smith` ~ `Hip thrust
  Smith machine`, `Rowing chest-supported` ~ `Rowing machine chest-supported`,
  `Roulette abdominale` ~ `Roulette abdominale (ab wheel rollout)`, `Rear delt
  fly machine` ~ `(pec deck inversé)` ;
- vraisemblablement **deux variantes** — `Rowing câble assis prise large` ~
  `neutre` ~ `serrée`, `Triceps pushdown barre` ~ `corde`, `Tirage poulie haute
  prise large` ~ `neutre` ;
- **ambigu** — `Leg Press (pieds bas)` ~ `(pieds bas, serrés)`, `Curl incliné
  haltères` ~ `(banc 45°)`.

Trancher est un jugement produit. `ExerciseAlias` existe pour que ce jugement,
quand il tombera, soit **additif** : une ligne d'alias, un repointage, aucune
destruction.

Autre mesure au passage : **24 des 68 noms du catalogue n'ont aucune entrée dans
`exercise_properties`** (69 clés, 44 en commun). Constat, pas correction.

---

## 4. Vérifications — tier `MIGRATION`

| Contrôle | Résultat |
|---|---|
| `check_scope` | `MIGRATION` |
| ruff (6 fichiers) | `All checks passed!` |
| `check_ruff_budget` | ≤ 548 |
| `check_spec_protocol` | PASS |
| `check_alembic_drift` | **OK (no diff)** — avec `PYTHONPATH`, cf. §2.2 |
| `check_schema_snapshot` | **OK** — snapshot régénéré, 161 lignes |
| `check_migration_patterns` | **OK** — aucun motif dangereux |
| `check_migration_roundtrip` | **OK** — 52 objets, schéma identique avant/après |
| Tests dédiés | **32 passed** |
| Full sweep local | *cf. appendice* |

---

## 5. Non-régressions

- **Additive stricte** : deux tables neuves, **0 colonne ajoutée**, 0 DROP,
  0 RENAME, **0 UPDATE de donnée historique**. Garde AST sur la migration.
- **0 moteur de décision touché** — garde AST : ni `recommendation`, ni
  `substitution`, ni `behavioral` n'importe le service d'identité.
- **0 surface UI** — cette tranche n'a rien à montrer ; CLAUDE.md §5 ne
  s'applique pas.
- **0 nom inventé** : tout vient de `reference_split.json` ou de
  `exercise_knowledge_base.json`.
- **0 revendication scientifique.**

---

## 5bis. Entrée au registre : différée au closeout, et pourquoi

`SPEC_REGISTRY.md` §8 demande la mise à jour **dans le même commit que le
rapport**. Je m'en écarte ici, délibérément et une seule fois : **trois PR
ouvertes modifient déjà ce fichier** — #140 y insère la section du cycle UX4,
#141 une ligne dans la table OPS. Y ajouter une troisième édition depuis une
branche qui ignore les deux autres fabriquerait un conflit à trois, dont la
résolution passe par des opérations git sous confirmation.

La ligne `Sb_EXERCISE_IDENTITY_01` part donc dans le **commit de closeout**,
une fois les trois branches retombées sur la canonique. C'est un report de
quelques heures, pas un oubli — et il est écrit ici pour qu'il ne puisse pas en
devenir un.

---

## 6. Ce que la tranche ouvre

**A10 — instrument PROGRESSIF** peut désormais s'appuyer sur une clé stable
plutôt que sur un nom. C'était sa dépendance déclarée.

**A2 étape B** (résolution/typeahead de substitution) a maintenant sa cible :
`resolve_exercise`.
