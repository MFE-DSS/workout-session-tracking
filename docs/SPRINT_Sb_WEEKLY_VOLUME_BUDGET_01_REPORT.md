# SPRINT Sb_WEEKLY_VOLUME_BUDGET_01 — Bandes de planification (RAPPORT)

**Base canonique :** `2af6c68` · **Branche :** `sb/weekly-volume-budget-01` · **Tier :**
**ISOLATED** (`check_scope`). **Tranche 1/3 du train `AUREN_CORE_ORCHESTRATION_01`.**
**Premier consommateur réel des préférences persistées.**
**0 table · 0 migration · 0 écriture · 0 modif `recommendation.py`/`behavioral.py` ·
0 morphologie · 0 modèle de récupération · 0 déploiement.**

## 1. Architecture — fonction pure, assumée

Un budget est **dérivé**, pas déclaré. Le persister figerait un calcul en fait utilisateur,
exactement ce que `Sb_TRAINING_PREFERENCES_01` s'est employé à rendre impossible. Seule une
préférence *déclarée* est stockée, et elle l'est déjà. Des tests interdisent `db.add`,
`db.commit` et `__tablename__` dans le module.

## 2. La politique de bande

```
policy_version     = "weekly-volume-v1"
planning_low_sets  = max(0, baseline - PLANNING_TOLERANCE_SETS)
baseline_sets      = ZONE_VOLUME_TARGET hérité / BodyZone.volume_target
planning_high_sets = baseline + PLANNING_TOLERANCE_SETS
```

Épinglé tel qu'exigé : **10 → [8, 10, 12]**, **18 → [16, 18, 20]**, testés comme **sorties
de politique produit**, jamais comme affirmations scientifiques.

**±2 est une tolérance de planification.** Ni volume minimal efficace, ni maximum
récupérable, ni plage optimale, ni capacité de récupération mesurée, ni seuil biologique.
**Aucune littérature n'est invoquée** — un test échoue si `acsm`, `et al`, `étude` ou
`meta-analys` apparaît dans le module. Les noms de champs portent la même discipline :
`minimum_sets`, `maximum_sets`, `MEV` et `MRV` sont chacun interdits par test paramétré.

Chaque zone transporte `policy_version`, `basis` et `source` — ce dernier nommant
explicitement la **baseline héritée**, pour qu'aucun consommateur n'ait à deviner si un
chiffre vient de l'utilisateur ou du système.

## 3. Les priorités sont consommées et **ne créent pas de volume**

Les axes radar déclarés sont projetés vers les zones par la relation canonique
`RADAR_AXES` — **aucune correspondance nouvelle** — et les zones concernées sont
**annotées** : `priority_rank`, `priority_source = USER_DECLARED`,
`preferred_direction = HIGHER_WITHIN_BAND`.

**Aucune borne ne bouge.** Aucune arithmétique de bonus n'existe (`rank1`, `+= 2`, `+= 1`,
`rank_bonus` interdits par test). Choisir le point exact dans la bande appartient au
planificateur, seul à connaître cadence, équipement et faisabilité des créneaux : résoudre
une allocation globale ici produirait un chiffre que le planificateur devrait ensuite
contredire.

`core` n'appartient à aucun axe radar et ne peut donc pas être priorisé — la même limite que
le roll-up macro de P0.4, énoncée plutôt que contournée.

## 4. La cadence est un contexte, pas une dose

`sessions_per_week` est transporté ; **1, 3, 6 et non déclarée produisent des bandes
identiques** (test paramétré). Aucun multiplicateur de fréquence n'existe dans le module.

## 5. Comptage des séries inchangé

Introduire un poids fractionnaire pour les séries indirectes changerait l'unité de comptage
de `muscle_scoring`, de la qualité de programme et des séances enregistrées — une migration
sémantique exigeant un audit des consommateurs. Consigné comme `SET_CONTRIBUTION_CANDIDATE`,
**délibérément non construit**.

## 6. Invariants prouvés par plantation

- faire monter la base avec le rang de priorité ⇒ **2 tests échouent** ;
- multiplier la base par la cadence ⇒ **2 tests échouent**.

**Note de méthode** : la première plantation de cadence était **inerte** — un multiplicateur
calculé mais jamais appliqué. La garde n'était donc pas prouvée et aurait été rapportée
comme telle. Ré-armée correctement avant toute affirmation.

## 7. Tests

**58 dédiés**, écrits en **classes d'équivalence et invariants** plutôt qu'une permutation
par cas : la croissance de la suite coûte désormais de la mémoire CI mesurable. Régression
ciblée sur préférences, recommandation, home, `TrainingState` et `muscle_scoring` :
**271 passés**.

Ajout de `tests.helpers.module_code_only` : le piège du scan de docstring — une garde qui
échoue sur sa propre documentation — est apparu dans **trois** fichiers de tests successifs ;
l'extracteur AST est désormais partagé plutôt que réécrit une quatrième fois.

## Verdict

**Livré, mergé.** Le budget existe, il est traçable jusqu'à sa politique et sa source, et il
ne prétend rien qu'il ne mesure.

**Limite structurante, volontaire** : ce budget ne choisit **aucun** point dans ses bandes.
C'est le planificateur qui le fera, et c'est la seule conception qui évite qu'une allocation
décidée ici soit contredite ensuite par la cadence ou l'équipement.

---

## 8. Closeout post-merge

| | |
|---|---|
| PR | **#90** — `MERGED` |
| Build → merge | `d1b195a` → **`92216be`** |
| Gate | `CLEAN` · **8/8** · Sonar **`OK`**, couverture du neuf **98,6 %**, 0 issue |
| Threads | **0 non résolu** · Gitar **0 finding** |
| Shards | 8 min 05 / 8 min 16 |
| Capacité | **HEALTHY** — min MemAvailable **5 620 / 5 137 Mo**, **swap intact** |
| Manifeste | 228 fichiers ⇒ **114 + 114**, absorption automatique |

**Tendance de capacité affinée.** Le coût mémoire suit les tests utilisant le fixture
`client`, pas le nombre de tests : +97 tests majoritairement HTTP (#86) ont coûté 400–950 Mo
de marge, alors que +58 tests majoritairement purs (cette tranche) n'en ont coûté
quasiment aucun — une marge a même augmenté. Les tranches 2 et 3, riches en intégration,
se comporteront plutôt comme #86.
