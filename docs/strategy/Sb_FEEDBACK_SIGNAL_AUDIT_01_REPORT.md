# Sb_FEEDBACK_SIGNAL_AUDIT_01 — audit du signal de feedback (RAPPORT)

**Base canonique :** `8c2cdf8` · **Sprint d'AUDIT — aucun code applicatif modifié.**

Contexte : `Sb_SESSION_SET_ACTION_01` a fait de la série une action utilisateur
réelle (`nav=stay`). Avant d'ajouter des garde-fous techniques ou la
substitution au cockpit, il faut savoir ce qui est **primaire**, ce qui est
**dérivé**, et ce qui est **redondant**.

---

## 0. Le résultat le plus important de cet audit

**Trois des sept champs de signal de `SetLog` ne sont jamais écrits.**

`session_builder.instantiate_session()` crée chaque ligne avec exactement
`kind`, `set_index`, `completed=False`. La boucle de persistance de
`update_exercise_card` n'écrit ensuite que `weight_kg`, `reps`, `completed`.
Aucune route, aucun service, aucun gabarit ne produit :

| champ | état réel |
|---|---|
| `SetLog.technique` | **NULL partout** — seul `restore.py` peut l'importer |
| `SetLog.execution_quality` | **NULL partout** — idem |
| `SetLog.reps_target` | **NULL partout** — idem |

Conséquences vérifiées, pas supposées :

* **L'export émet trois colonnes toujours vides.** `export_builder.py` les
  liste dans l'en-tête CSV et le JSON pour **chaque série de chaque séance**.
* **Il existe du rendu mort.** `exercise_card.html` contient
  `{% if sl.technique %}<span class="tag">{{ sl.technique }}</span>{% endif %}`
  dans la macro de ligne — cette branche n'a jamais pu s'exécuter.
* Le seul producteur possible est l'import (`restore.py`), donc des données
  externes pourraient les remplir alors que le produit ne le peut pas.

Ce n'est pas un détail de propreté : cela signifie que **la qualité technique
n'est mesurée nulle part**, alors que trois colonnes donnent l'impression du
contraire.

---

## 1. A1 — Inventaire complet

Niveau : `S` = série, `E` = exercice, `W` = séance.
Source : `U` = saisi par l'utilisateur, `D` = dérivé, `P` = prescription.

| Champ | Niv. | Src | Sémantique actuelle | Consommateurs | Doublon ? | Décision proposée |
|---|---|---|---|---|---|---|
| `weight_kg` | S | U | charge telle qu'affichée sur l'équipement | overload, progression, export, history, KPI | non | **GARDER** — signal primaire |
| `reps` | S | U | répétitions réalisées | overload, `success_score`, progression, export | non | **GARDER** — signal primaire |
| `completed` | S | D | **dérivé** de la présence de weight/reps (Sx_24 §E) | `success_score`, KPI, `can_substitute`, cockpit | non | **GARDER** — ne jamais rendre saisissable |
| `kind` | S | P | `warmup` / `work` | partout | non | **GARDER** — structurel |
| `set_index` | S | P | rang de la série | ancrage, `success_score`, rep targets | non | **GARDER** — structurel |
| `technique` | S | P (jamais écrit) | méthode prescrite (drop-set…) | export, rendu **mort** | — | **STATUER** — OQ-1 |
| `execution_quality` | S | U (jamais écrit) | qualité d'exécution | export uniquement | **non** — rien ne la dérive | **CANDIDAT #1** — voir §3 |
| `reps_target` | S | U (jamais écrit) | atteinte de la cible par série | export uniquement | **OUI, total** — voir §3 | **NE PAS COLLECTER** |
| `success_score` | E | D | 100/80/50 : reps vs cible × ratio d'achèvement | recap, KPI, stats, delta, anomalies, quality, sharing, history, export | non | **GARDER** — dérivé, jamais demandé |
| `muscle_sensation` | E | U | ressenti musculaire `strong/partial/weak` | briefing, profile_metrics, stats, history, sharing, export | non | **GARDER** |
| `SessionExercise.free_note` | E | U | note libre (140) | export, sharing | non | **GARDER** — non structuré assumé |
| `substituted_name` | E | U | exercice réellement fait | substitution, export | non | **GARDER** |
| `implicit_label` | E | D | étiquette dérivée | briefing | non | **GARDER** |
| snapshots (`exercise_code/name`) | E | P | invariance historique | tout | non | **GARDER** — intangible |
| `concentration` | W | U | `high/medium/low` — « Focalisé / Correct / Distrait » | recovery, confidence, behavioral, training_state, quality, recap, explainer, export | non | **GARDER** |
| `global_state` | W | U | `good/flat/fatigued` — « En forme / Moyen / Fatigué » | **overload_inputs**, recovery, confidence, behavioral, training_state, quality, recap, explainer, export | non | **GARDER — porteur** |
| `bodyweight_kg` | W | U | poids de corps | profile_metrics, export | non | **GARDER** — optionnel |
| `WorkoutSession.free_note` | W | U | note libre (280) | export, recap | partiel avec la note d'exercice | **GARDER** — granularités distinctes |
| cardio (`4 champs`) | W | U | hors périmètre séance de force | export | — | hors périmètre |

---

## 2. A2 — Taxonomie cible

Chaque signal dans **une seule** catégorie :

| Catégorie | Signaux |
|---|---|
| **Performance mécanique** | `weight_kg`, `reps` |
| **Qualité technique** | `execution_quality` *(inexistant en pratique)* |
| **Atteinte cible** | `success_score` *(dérivé)* — et `reps_target` qui ferait doublon |
| **Ressenti musculaire** | `muscle_sensation` |
| **État global** | `concentration`, `global_state` |
| **Note libre** | `free_note` (E et W) |
| **Dérivé** | `completed`, `success_score`, `implicit_label` |
| **Prescription** *(catégorie ajoutée)* | `kind`, `set_index`, `technique` |

> **Le brief proposait sept catégories ; il en manquait une.** `technique` et
> `kind` ne sont pas du feedback : ce sont des **prescriptions** venues du
> programme (`RepTarget`), recopiées dans la séance. Les ranger dans
> « qualité technique » aurait fait croire à un signal utilisateur là où il
> n'y en a jamais eu. Cette distinction change la décision les concernant.

---

## 3. A3 — Redondance, explicitée

**`reps_target` × `success_score` : redondance TOTALE, par construction.**

`compute_success_score()` fait exactement ceci, par série complétée :

```
reps >= max_reps  → 100
reps >= min_reps  →  80
sinon             →  50
puis moyenne × (séries complétées / séries prescrites), calé sur 100|80|50
```

C'est **la définition même** de « la cible a-t-elle été atteinte ». Demander
`reps_target` à l'utilisateur reviendrait à lui faire saisir une information
que le système **calcule déjà, à partir d'un chiffre qu'il vient de saisir**.
Pire : les deux pourraient diverger, et il n'existe aucune règle d'arbitrage.

→ **Décision : ne jamais collecter `reps_target`.** Priorité 2 du brief
(« ne pas demander deux fois le même signal ») s'applique littéralement.

**`execution_quality` × `success_score` : ORTHOGONAUX.**

`success_score` ne sait rien de la qualité du mouvement : 8 répétitions
propres et 8 répétitions en triche donnent **exactement** le même score. Rien,
nulle part, ne dérive la qualité technique.

→ **C'est le seul vrai manque de signal du produit.**

**`execution_quality` × `muscle_sensation` : ORTHOGONAUX.**

« Le mouvement était-il propre » (observable, technique) et « ai-je senti le
muscle » (ressenti, subjectif) sont deux questions différentes. Un pratiquant
peut exécuter proprement sans rien sentir, et inversement. Les fusionner
détruirait les deux.

**`muscle_sensation` × `global_state` : ORTHOGONAUX**, granularités
différentes (exercice vs séance).

**`concentration` × `global_state` : partiellement corrélés, non redondants.**
« Distrait mais en forme » et « focalisé mais fatigué » sont des états réels
et distincts. `global_state` est en outre **porteur** : il alimente
`overload_inputs`, donc la progression de charge. Y toucher aurait un effet
sur le moteur — hors périmètre de tout sprint de présentation.

---

## 4. A4 — Contrat cockpit V1

Contrainte du brief : **+5 secondes de logging maximum**.

**Par SÉRIE — rien de nouveau.** `weight_kg` et `reps` restent les deux seules
saisies. Ajouter un troisième contrôle par série multiplierait le coût par le
nombre de séries (typiquement 15 à 21 par séance) : le budget serait explosé
dès le premier exercice.

**Par EXERCICE — un seul ajout candidat**, `execution_quality`, sur le même
patron que `muscle_sensation` (segmented à trois valeurs, replié, optionnel) :

```
Qualité d'exécution : Propre · Correcte · Dégradée
```

Coût : **un tap, optionnel, une fois par exercice** — soit ~1 s × 6-7
exercices. Dans le budget. C'est le seul signal manquant qui ne soit pas
dérivable.

**Par SÉANCE — rien de nouveau.** `concentration`, `global_state`,
`bodyweight_kg`, note libre existent déjà et sont consommés.

**À NE PAS afficher dans le cockpit actif** : `success_score` (dérivé, sa
place est la revue), les notes libres (déjà repliées), le cardio.

> **Réserve honnête.** `execution_quality` reste un **candidat**, pas une
> recommandation ferme : le produit n'a aujourd'hui **aucun consommateur** qui
> saurait quoi en faire. Le collecter avant d'avoir un lecteur créerait une
> quatrième colonne toujours vide — exactement le défaut décrit au §0. Voir
> **OQ-2**.

---

## 5. A5 — Où vivront les garde-fous techniques

**Ils ont déjà un domicile, et il est peuplé.** `data/machine_atlas.json` —
version `2026-04-15.v1`, **8 familles, 29 machines** — porte par machine :

```
aliases · common_mistakes · equipment · execution_cues ·
laterality · load_semantics · name · slug · variants
```

Correspondance avec les quatre notions demandées :

| Notion visée | Emplacement |
|---|---|
| `technical_cues` | **existe** → `machines[].execution_cues` |
| `common_errors` | **existe** → `machines[].common_mistakes` |
| `setup_checklist` | **manque** → nouvelle clé de machine |
| `correction_hint` | **manque** → à indexer **par erreur**, pas par machine |

**Conséquences pour la conception :**

1. **Aucun changement de modèle, aucune migration.** L'atlas est un fichier de
   données ; l'enrichir n'affecte pas la base.
2. **La surface de rendu existe** : `.machine-panel`, déjà déplacé sous la
   console par `Sb_UIV2_SESSION_FOCUS_02`, en grammaire `.disclosure`, fermé
   par défaut. Le contrat exact `class="machine-panel"` est épinglé par
   `test_machine_atlas_surface` — à ne pas casser.
3. **`correction_hint` ne doit pas être une clé de machine** : une correction
   répond à une **erreur** (« dos rond » → « rentre les côtes »), pas à un
   appareil. L'indexer par machine dupliquerait le même conseil sur 29
   entrées. Elle appartient à côté de chaque `common_mistakes`.
4. **Couplage avec `execution_quality`** : si la qualité dégradée est un jour
   collectée (§4), le lecteur naturel est précisément ce corpus — c'est le
   consommateur qui manque aujourd'hui.

---

## 6. A6 — Non-régression historique

**Priorité 1 du brief : ne perdre aucun historique.** La stratégie tient en
quatre règles.

1. **Aucun rétro-remplissage, jamais.** Les trois champs morts sont NULL sur
   toutes les séances passées. Inventer une valeur — même « inconnu » —
   réécrirait l'histoire. `CLAUDE.md §2` (additive-only) l'interdit déjà.
2. **`NULL` doit rester lisible comme « non mesuré »**, pas comme « mauvais ».
   Toute lecture future doit distinguer *absence* et *valeur basse* — le même
   piège que `NULL ≠ []` traité dans le sprint préférences.
3. **Ne rien supprimer, ne rien renommer.** Même morts, ces champs sont dans
   le contrat d'export et dans `restore.py`. Les retirer casserait la
   restauration d'archives déjà produites. Le brief l'interdit et l'audit
   confirme que c'est justifié.
4. **Les colonnes d'export restent en place et dans le même ordre.** Des
   consommateurs externes peuvent parser positionnellement.

**Sur le rendu mort de `technique`** : le supprimer ne perdrait aucune donnée
(la branche n'a jamais pu s'exécuter), mais rendrait invisible une valeur
importée par `restore.py`. → **le garder** ; il coûte une ligne et couvre
l'import.

---

## 7. Decision proposal

| # | Décision | Confiance |
|---|---|---|
| D1 | **Ne jamais collecter `reps_target`.** Redondance totale avec `success_score`, par construction. | **Élevée** |
| D2 | **Conserver les trois champs morts** (colonne, export, restore). Ne pas supprimer, ne pas renommer, ne pas rétro-remplir. | **Élevée** |
| D3 | **Documenter les trois champs comme « importables, non produits »** — pour que le prochain lecteur ne les prenne pas pour du signal disponible. | **Élevée** |
| D4 | **N'ajouter aucun contrôle au niveau SÉRIE.** Le coût se multiplie par 15-21. | **Élevée** |
| D5 | **`execution_quality` au niveau EXERCICE = seul candidat**, sur le patron `muscle_sensation`. **À ne pas construire tant qu'aucun consommateur n'existe.** | **Moyenne** — voir OQ-2 |
| D6 | **Garde-fous techniques dans l'atlas**, pas en base. `setup_checklist` par machine ; `correction_hint` par **erreur**. | **Élevée** |
| D7 | **Ne pas toucher `concentration` / `global_state`.** `global_state` alimente `overload_inputs` : c'est du moteur. | **Élevée** |

---

## 8. Build queue recommended

Ordre proposé, du moins risqué au plus engageant :

1. **`Sb_ATLAS_TECHNICAL_GUARDS_01`** — enrichir l'atlas (`setup_checklist`,
   `correction_hint` indexé par erreur) et le rendre dans la disclosure
   machine existante. **Aucun modèle, aucune migration, aucun signal
   nouveau.** Le plus sûr, et il rend la valeur la plus visible.
2. **`Sb_SUBSTITUTION_COCKPIT_01`** — la substitution existe déjà
   (`can_substitute`, N1/N2/N3, parité testée) ; il s'agit de la rendre
   fluide en séance. Aucun signal nouveau requis.
3. **`Sb_SESSION_REVIEW_SIGNAL_01`** — rationaliser la **restitution** :
   `success_score` et `muscle_sensation` sont déjà collectés et peu exposés.
   Améliorer la lecture avant d'ajouter de la collecte.
4. **`Sb_EXECUTION_QUALITY_01`** — *seulement si* OQ-2 est tranché en faveur
   d'un consommateur réel. Collecter d'abord, lire ensuite serait reproduire
   exactement le défaut du §0.
5. **`Sb_REST_EVENT_TRACE_01`** — indépendant, hérité du sprint précédent,
   exige une migration.

> **Note de séquencement.** L'ordre place délibérément la **restitution**
> (3) avant la **collecte** (4). Le produit a montré qu'il sait ajouter des
> colonnes que personne ne remplit ; il n'a pas encore montré qu'il sait
> exploiter ce qu'il collecte déjà.

---

## 9. Questions ouvertes — arbitrage humain requis

**OQ-1 — `technique` : prescription ou signal ?**
Le champ existe sur `SetLog` mais provient du programme (`RepTarget`), et
n'est jamais recopié à l'instanciation. Trois lectures possibles : (a) bug
d'omission dans `session_builder`, la prescription devrait être copiée ;
(b) champ obsolète conservé pour l'import ; (c) emplacement futur d'une
technique *réellement appliquée* (différente de celle prescrite). **Les trois
mènent à des sprints différents.** Je ne tranche pas : rien dans le code ne
dit laquelle était l'intention.

**OQ-2 — `execution_quality` : collecter avant d'avoir un lecteur ?**
C'est le seul manque de signal réel, mais aucun consommateur ne saurait
l'exploiter aujourd'hui. Deux positions défendables : collecter tôt pour
constituer un historique (les données manquantes ne se rattrapent pas), ou
attendre un lecteur pour ne pas créer une quatrième colonne vide. **Le §0 de
cet audit est un argument fort pour attendre** — mais c'est un arbitrage
produit, pas technique.

**OQ-3 — les colonnes d'export toujours vides.**
L'export publie trois colonnes systématiquement nulles. Faut-il (a) les
conserver telles quelles pour la stabilité du format, (b) les documenter
comme réservées, ou (c) prévoir une v2 du format ? **D2 recommande (a) ou
(b)** ; (c) est une décision de compatibilité externe.

**OQ-4 — granularité du ressenti.**
`muscle_sensation` est par exercice. Une séance à 7 exercices demande donc 7
taps. Faut-il un ressenti par **zone** plutôt que par exercice ? Cela
réduirait la saisie et alignerait le signal sur le modèle de zones du
planificateur — mais c'est un changement de sémantique, pas une optimisation.

---

## Verdict

Le produit n'a pas un problème de **manque** de champs de feedback : il en a
**trois qu'il n'écrit jamais**, dont un (`reps_target`) qu'il ne devrait
jamais écrire parce qu'il le calcule déjà, et un (`technique`) dont personne
ne sait plus s'il est une prescription ou un signal.

Le seul vrai manque est la **qualité technique** — et le bon réflexe n'est pas
de se dépêcher de la collecter, mais de construire d'abord de quoi la lire.

---

## Closeout (post-merge)

| | |
|---|---|
| PR | **#116** — `--merge --match-head-commit d10c38c`, **sans** squash / `--admin` / force |
| Merge | **`5af5ff4`** |
| CI canonique | run `32005159366` — **succès 6/6, au premier passage** |
| Gate Sonar | **`OK`** — 0 bug, 0 smell, 0 vulnérabilité, 0 % duplication |
| Threads / Gitar | **0 / 0** |
| CI PR | **9 checks verts au premier passage**, aucun aller-retour |
| Périmètre | **2 fichiers** : le rapport + la garde de véracité |
| Code applicatif | **aucune modification** — `app/` intact |

### Capacité CI — `HEALTHY`, partition parfaitement équilibrée

| Shard | Fichiers | min MemAvailable | min SwapFree |
|---|---|---|---|
| 1 | 84 | 6 810 Mo | 3 071 — intact |
| 2 | 84 | 8 296 Mo | 3 071 — intact |
| 3 | 84 | 6 842 Mo | 3 071 — intact |

`workers=2`, manifeste respecté, jamais `-n auto`. **84/84/84** — partition
parfaitement équilibrée pour la première fois, et le shard le plus bas est à
**6 810 Mo**, très au-dessus du plancher de 4 Go. Le déséquilibre suit bien la
**partition**, pas la machine : trois tranches successives l'ont confirmé.

### Ce que la garde de véracité protège désormais

Le constat central de l'audit est **exécutable** et vit dans la suite
canonique. Si `execution_quality` ou `reps_target` acquiert un producteur
ailleurs que dans le modèle, l'export ou l'import, le test tombe avec un
message explicite : **relire l'audit**, pas corriger une régression.

C'est le point qui distingue ce document d'une note d'analyse : il **périme
tout seul** au lieu de vieillir en silence.

### Suite

Les quatre OQ restent ouvertes et attendent un arbitrage humain. La queue de
build recommandée (§8) place délibérément la **restitution avant la
collecte** — `Sb_ATLAS_TECHNICAL_GUARDS_01` en tête, `Sb_EXECUTION_QUALITY_01`
conditionné à OQ-2.
