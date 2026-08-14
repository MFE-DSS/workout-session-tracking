# SPRINT Sb_TRAINING_PREFERENCES_01 — Préférences déclarées (RAPPORT)

**Base canonique :** `62ff4bd` (puis fusion de `eb20744`) · **Branche :**
`sb/training-preferences-01` · **Tier :** **SHARED_CODE** (`check_scope`).
**Première source PERSISTÉE de préférences du dépôt.**
**0 modif `recommendation.py`/`behavioral.py` · 0 planificateur · 0 déploiement.**

## 1. Préflight — aucune source autoritative n'existait

Prouvé, pas supposé : `User` ne porte que l'identité et des mesures physiques ; un `grep`
de `sessions_per_week|focus_priorities|available_equipment|training_preferences` sur `app/`
et `migrations/` renvoie **zéro modèle et zéro migration** ; et
`program_quality_engine.UserProfile` — qui déclare pourtant `sessions_per_week` et
`available_equipment` — est une **dataclass pure jamais construite nulle part** dans `app/`.
Un consommateur déclaré que rien n'alimentait. Cette table est ce qui l'alimentera.

## 2. Le HARD STOP, et sa résolution

`morphology_profile.FOCUS_CANDIDATE_VOCAB` a été audité puis **écarté sur preuve** : son
propre commentaire le définit comme « candidats d'orientation admis (**jamais une priorité
appliquée** — build suivant) », ses 4 jetons ne sont **pas** des codes `BodyZone`, et ils ne
permettent de déclarer ni quadriceps, ni biceps, ni dos.

Escaladé à l'opérateur, qui a tranché pour les **axes radar canoniques** : déjà canoniques,
déjà libellés, et projetables vers les zones par `radar_axis_for_zone` — donc consommables
par un futur budget de volume **sans nouvelle table de correspondance**. Un test vérifie que
les deux vocabulaires ne s'intersectent pas.

**Limite assumée** : `core` n'appartient à aucun axe et ne peut donc pas être priorisé —
la même limite que le roll-up macro de P0.4, pas une nouvelle.

## 3. Schéma — révision `q8r3l9m0o11`

```
training_preferences
  id · user_id (FK users, UNIQUE, indexé, ON DELETE CASCADE)
  sessions_per_week    INTEGER NULL
  focus_priorities     TEXT NULL   -- liste JSON ORDONNÉE d'axes
  available_equipment  TEXT NULL   -- liste JSON de familles
  created_at · updated_at
```

**Additive, sans backfill** : la migration ne crée **aucune ligne**, pour personne — un test
vérifie qu'`INSERT` n'y apparaît jamais. Une ligne par utilisateur au maximum est une
**contrainte de base**, prouvée par `IntegrityError`, pas une convention applicative.

## 4. `NULL` n'est jamais `[]`

| État | Signification |
|---|---|
| aucune ligne | rien n'a été déclaré |
| `sessions_per_week = NULL` | cadence non déclarée |
| `focus_priorities = NULL` | priorités non déclarées |
| `focus_priorities = []` | **explicitement** aucune priorité |
| `available_equipment = NULL` | disponibilité inconnue |
| `available_equipment = []` | **explicitement** aucun matériel externe |

Épinglé jusqu'aux octets stockés : `NULL` reste `NULL` SQL, `[]` est stocké `"[]"`.

**Doublons traités différemment, par conception** : un doublon de **priorité** est une
erreur (dans une liste ordonnée le rang est ambigu, et deviner trahirait l'intention) ;
un doublon d'**équipement** est normalisé (sémantique d'ensemble, l'ordre ne porte rien),
avec un ordre de sortie canonique.

## 5. Aucun défaut caché — prouvé par plantation

Planter trois violations — cadence par défaut à 3, `NULL` écrasé en `[]`, équipement inconnu
silencieusement ignoré — fait échouer **9 tests**. Un JSON corrompu en base **remonte** au
lieu d'être remplacé par une liste vide : transformer une donnée perdue en déclaration
explicite « aucune priorité » serait une affirmation que l'utilisateur n'a jamais faite.

## 6. Surface de saisie et propriété

La **page profil existante**, à côté de `/profile/body` et `/profile/measurements`. Aucune
navigation nouvelle, aucun assistant, aucun JS. L'ordre des priorités passe par trois
`<select>` — le plus petit mécanisme déterministe disponible en SSR.

Le propriétaire vient de `CurrentUser` (session) ; le formulaire ne porte **aucun**
`user_id`, donc un identifiant forgé n'a rien à quoi s'accrocher — prouvé deux fois. Un
marqueur caché distingue « section jamais soumise » de « soumise sans rien cocher ».

## 7. Isolation prouvée à l'exécution

- **Parité de recommandation** : déclarer 7 séances + priorités + matériel laisse
  `home["today"]` **identique**.
- **Parité P0.4** : `TrainingState` égal avant et après déclaration d'équipement.
- `TrainingState.equipment` reste `None` — la disponibilité déclarée n'est **pas** une
  disponibilité biologique, et la peupler est délibérément différé.

## 8. Ce que le blocage CI a coûté, et appris

Cette PR a subi **trois arrêts du runner** sans jamais un échec de test. Le diagnostic a
écarté échec, timeout, concurrence et disque, puis mesuré la vraie cause : la suite
demandait **~16,6 Go** pour une machine de **15,99 Go**. Deux sprints d'infrastructure
(`Sb_OPS_CI_RUNNER_STABILITY_01`, absorbé, puis `Sb_OPS_CI_SCALE_01`) ont été nécessaires.

Après sharding : **shard A 5 514 Mo / shard B 5 271 Mo** de mémoire disponible minimale,
**swap jamais entamé**. Les shards passent en 7 min 57 et 8 min 10.

## Verdict

**Livré, mergé, canonique verte.** La première source persistée de préférences existe, et
elle est construite pour que le planificateur à venir puisse toujours distinguer
**« l'utilisateur l'a dit »** de **« le système l'a supposé »** — ce qui était l'objectif,
plus que les trois champs eux-mêmes.

**Limite** : rien ne consomme encore ces préférences. `UserProfile` reste non alimentée ;
le brancher appartient au budget de volume hebdomadaire.

---

## 9. Closeout post-merge

| | |
|---|---|
| PR | **#86** — `MERGED` |
| Build → fusion canonique → merge | `6b5c542` → `ee3bd20` → **`c8c2209`** |
| Gate PR | `CLEAN` · **7/7** · Sonar **`OK`**, couverture du neuf **97,1 %**, 0 issue |
| Threads | **0 non résolu** |
| CI canonique | **`31850832062` — 5/5 GREEN** |
| Capacité | **HEALTHY** — 5 514 / 5 271 Mo, swap intact |
| Migration | `q8r3l9m0o11` · drift, snapshot, patterns, roundtrip : **tous verts en CI** |

**Rafraîchissement sans rebase** : la canonique a été **fusionnée** dans la branche. Un
seul conflit, purement mécanique — les deux branches portaient le **même** correctif d'ancrage
d'horloge du fixture Home, découvert indépendamment de part et d'autre ; seule la
formulation du commentaire différait. Aucun comportement de préférences touché.

**Le manifeste de shards a absorbé le nouveau fichier de test tout seul** : 226 → **227
fichiers, 114 + 113**. C'est précisément pourquoi il est généré et non maintenu à la main.
