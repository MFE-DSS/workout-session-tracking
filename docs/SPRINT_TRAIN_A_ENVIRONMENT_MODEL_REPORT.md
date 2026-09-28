# `TRAIN A` — Le modèle d'environnement : objets, capacités, exigences

**Statut** : `MERGÉ` · PR #260 · merge `dfcd3bf`
**Branche** : `sb/train-a-environment-model` sur canonique `456519c`
**Tier `check_scope`** : `MIGRATION` — full sweep exécuté
**Migration** : une colonne additive nullable, **zéro backfill**
**Filtre dur** : **ÉTEINT**. Aucun module de décision n'importe le modèle, et
une garde AST le vérifie.

---

## 1. Ce que la tranche livre

Un modèle à **trois couches**, tel qu'arbitré au `§0` :

```
OBJET D'ÉQUIPEMENT   →   CAPACITÉ INTERNE   →   EXIGENCE D'EXERCICE
« un banc inclinable »   « dossier inclinable »   incline_bench_support
```

L'utilisateur déclare des **choses**. Le moteur consomme des **affordances**.
Les deux vocabulaires sont distincts, et un seul module les relie.

---

## 2. Brainstorming / Options / Risques / Choix (`CLAUDE.md §3`)

| option | ce qu'elle aurait coûté | verdict |
|---|---|---|
| `cable = true` global | un tirage vertical assis et une poulie réglable deviennent interchangeables — faux | **écartée** (`§4`) |
| une case par slug d'exercice | l'utilisateur déclarerait des mouvements, pas du matériel ; et `machine_slug` porterait une sémantique que le dépôt lui refuse | **écartée** (`§0`) |
| **objet → capacité → exigence** | un niveau d'indirection de plus | **retenue** |

Le risque principal du choix retenu est qu'un objet **sur-accorde** : lui
prêter une affordance qu'il n'a pas rend faisable ce qui ne l'est pas. Deux
gardes l'épinglent nommément — une station de tirage vertical n'accorde
**pas** d'ancrage haut libre, et une poulie simple n'accorde **pas** deux
colonnes indépendantes.

---

## 3. La question câble, tranchée sur preuve constructeur

`§4` demandait de ne choisir ni le global ni le per-mouvement. La
documentation le justifie :

* le **Dual Adjustable Pulley** de Life Fitness porte **22 réglages de
  hauteur** et **deux colonnes de 390 lb indépendantes**, avec corde, barre
  et poignées fournies ;
* sur le **MJ4 Multi-Jungle** du même constructeur, le « Dual Pulley Lat
  Pulldown » et le « Single Pulley Low Row » sont **deux stations
  sélectorisées distinctes**, chacune avec sa propre colonne de 260 lb.

Trois objets, donc, et non un. « Du câble » ne dit pas lequel — c'est
exactement pourquoi `available_equipment` ne peut pas alimenter
`available_equipment_items`.

---

## 4. Le compte réel, et un écart avec la directive

La directive annonçait **32 connus** et **35 restants**. Mesuré sur les
fichiers de données :

| | |
|---|---|
| exercices prescrits par les 17 gabarits servis | **68** |
| `ATLAS_APPARATUS` bruts (modalité `machine` · `cable` · `smith`) | 35 |
| implément d'atlas sans support structuré (`haltere`) | 4 |
| sans entrée d'atlas | 29 |

`68 − 32 = 36`, pas 35. Le « 32 » de la directive vient de mon propre
déclassement, dans `E1A`, des **trois** exercices Smith dont la prose de
variantes mentionnait un banc. Ce déclassement était le bon réflexe, et le
`§5` le tranche mieux que moi — voir le point suivant.

Le compte final n'est donc ni 32 ni 35 :

| verdict | nombre |
|---|---|
| **exigences établies** | **53** |
| **INCONNU déclaré** | **15** |

---

## 5. Nécessaire, optionnel, alternatif — la distinction fait son travail

Le `§5` nomme un cas : *« si le hip thrust Smith est documenté possible au sol
OU sur banc, le banc n'est PAS obligatoire »*.

**L'atlas du dépôt porte déjà la réponse.** `hip-thrust-smith` déclare
`variants: ["dos banc", "sol"]`. Le banc est une **alternative documentée**,
donc il n'entre pas dans une exigence conjonctive. Exigence : `smith_rack`
seul.

Le cas symétrique tombe dans l'autre sens. `incline-smith-press` déclare
`variants: ["banc 30°", "banc 45°"]` et sa consigne impose un angle de banc :
**aucune exécution sans banc n'est documentée**. Exigence : `smith_rack` +
`incline_bench_support`.

Une garde vérifie que ces deux verdicts **diffèrent**. S'ils rendaient la
même chose, la distinction serait racontée et non implémentée.

Même mécanique sur le face pull : `corde` et `barre en V` sont deux
alternatives, donc **aucun accessoire n'est obligatoire**.

---

## 6. Deux divergences de données, traitées en sens opposé

C'est le point où j'ai d'abord conclu à l'envers, et où la mesure m'a corrigé.

### 6.1 — « Pullover câble » : le nom contre deux champs concordants

J'avais classé `Pullover câble (bras tendus)` en conflit bloquant, au motif
que le nom dit « câble » alors que le slug d'atlas est `pullover-machine`.

C'était faire gagner le nom. En mesurant, `equipment_family` vaut **aussi**
`machine`. **Deux champs structurés concordent, seul le texte libre diverge**
— et trancher pour le texte libre est précisément l'inférence par le nom que
le `§12` interdit. Les deux lignes sont donc résolues en `machine_pullover`,
avec la divergence de **nommage** consignée comme telle.

### 6.2 — « Relevés mollets debout » : deux champs qui se contredisent

Ici `equipment_family = bodyweight` et `machine_slug = standing-calf-raise`
(modalité `machine`). Deux déclarations structurées se contredisent : c'est
un vrai conflit, et la ligne part en **INCONNU**.

J'ai cherché la **classe** et non l'instance : sur les 39 exercices servis
porteurs d'un slug, c'est le **seul** désaccord famille/modalité. Sa sœur
« Relevés mollets debout machine » porte le même slug avec
`family = machine` et reste résolue.

---

## 7. Ce qui reste INCONNU, et pourquoi

15 lignes. Trois causes, pas une.

| cause | nombre | ce qu'il faudrait |
|---|---|---|
| hauteur d'ancrage de poulie non écrite et non sourcée | 8 | une référence autoritaire par mouvement |
| défaut de dépôt : `machine_slug` absent là où une sœur en porte un | 3 | un arbitrage de correspondance d'identité |
| conflit de champs ou d'identité | 4 | un arbitrage opérateur |

ACE s'est révélé **inutilisable pour le câble** : sa bibliothèque range les
poulies et les élastiques dans une même catégorie « Resistance
Bands/Cables », donc elle n'établit aucune hauteur d'ancrage. C'est un fait
mesuré sur la source, pas une impression.

Les trois défauts de dépôt sont concrets et corrigibles :
`Leg Press (pieds hauts, écartés)` n'a **ni** famille **ni** slug alors que
`Leg Press (pieds bas)` porte `leg-press` ; `Reverse fly machine` et
`Rowing chest-supported` ont une famille `machine` et un slug `NULL` alors
que leurs quasi-homonymes en portent un. Les rattacher serait de
l'assimilation par ressemblance de noms — ce que le `§7` interdit
explicitement. Ils attendent donc un arbitrage, pas une devinette.

---

## 8. Le troisième niveau de preuve, isolé pour être refusable

13 lignes ne viennent ni de l'atlas ni d'une source externe, mais de
**l'identité canonique AUREN elle-même** : « Curl **poulie basse** »,
« Élévations latérales haltères **assis** », « Roulette abdominale »,
« Relevé de jambes **suspendu** ».

Ce n'est pas de l'inférence par ressemblance de noms — il n'y a aucun autre
nom en face. C'est la lecture d'une déclaration que le dépôt porte déjà,
et elle est **toujours** recoupée avec `equipment_family`.

Je l'ai quand même **étiquetée séparément** (`IDENTITE_AUREN`) plutôt que
fondue dans les faits sourcés, pour que l'opérateur puisse la refuser en
bloc sans toucher aux 40 autres. Si elle est refusée, le compte devient
**40 connus / 28 inconnus**.

---

## 9. Sécurité des utilisateurs existants (`§12`)

Après migration, tout utilisateur existant porte
`available_equipment_items = NULL` : **environnement concret non résolu**. Et
un environnement non résolu rend `UNKNOWN`, jamais un refus.

Quatre gardes épinglent les dérivations interdites :

| dérivation | verdict |
|---|---|
| `dumbbells` ⟶ « possède un banc » | refusée |
| une machine ⟶ les treize machines | refusée |
| une poulie ⟶ toute configuration câble | refusée |
| familles grossières ⟶ objets concrets | refusée |

### Un défaut évité, pas découvert après coup

`save_training_preferences` **remplace l'état entier** : passer `None` pour
un champ signifie « non déclaré ». Y ajouter un quatrième paramètre aurait
fait effacer la déclaration d'environnement **à chaque soumission du
formulaire hérité**, par une surface qui ignore jusqu'à l'existence du champ.

C'est une classe de défaut déjà vécue ici, et qui a déjà perdu des données
en production. L'environnement concret a donc son **propre point d'écriture**
(`save_available_equipment_items`), et une garde vérifie qu'écrire les
préférences grossières n'efface pas les objets déclarés.

---

## 10. Les trois verdicts, et les deux lignes qui portent le contrat

| environnement \ exigence | inconnue | aucune | listée |
|---|---|---|---|
| **non déclaré** (`NULL`) | `UNKNOWN` | `FEASIBLE` | `UNKNOWN` |
| **aucun** (`[]`) | `UNKNOWN` | `FEASIBLE` | `NOT_FEASIBLE` |
| **déclaré** | `UNKNOWN` | `FEASIBLE` | couverture |

La colonne « inconnue » ne descend **jamais** en `FEASIBLE`, si riche que
soit la salle. Et « n'exige aucun matériel » reste faisable même sans
déclaration : c'est le seul cas où l'absence ne bloque rien, parce qu'il n'y
a rien à posséder.

Trois chaînes, pas un continuum. Une garde vérifie qu'aucun verdict n'est
convertible en nombre.

---

## 11. Delta de schéma exact

```
training_preferences
  + available_equipment_items  TEXT  NULL        ← additive, nullable, zéro backfill

exercise_knowledge_base.json
  + equipment_requirements     list|absent       ← 53 entrées sur 103
                                                   absence = NULL = inconnu, jamais []

data/equipment_registry.json   NOUVEAU           ← 29 capacités, 26 objets
data/equipment_curation.json   NOUVEAU           ← 68 lignes de provenance
app/services/equipment_model.py NOUVEAU          ← résolveur, non branché
```

Révision Alembic `x5y0s6t7v18`, sur `w4x9r5s6u17`. Idempotente, downgrade
symétrique, aucun `UPDATE`.

---

## 12. Contenu sans matériel (`E4A`, `§9`) — statut

**Identités résolues, intégration NON effectuée.** Ce que la détection de
doublon a rendu, contre les 103 noms canoniques :

| candidat ACE | doublon AUREN | verdict |
|---|---|---|
| Push-Up (#41) | aucun | identité **neuve** |
| Bodyweight Squat (#135) | `Hack Squat machine`, `Sissy squat machine`, `Squat Smith machine` — toutes appareillées | identité **neuve** |
| Forward Lunge (#94) | aucun | identité **neuve** |
| Glute Bridge (#49) | `Hip thrust Smith`, `Hip thrust haltères` | **mouvement différent** (épaules surélevées, charge externe) — identité neuve, correspondance à consigner |
| Front Plank (#32) | aucun | identité **neuve** |

Les cinq sont étiquetés « No Equipment » par ACE, donc
`equipment_requirements = []`, ce qui les rend faisables même sans
environnement déclaré.

**Pourquoi l'intégration n'est pas dans cette tranche.** Ajouter un nom
canonique modifie le jeu **épinglé** de 103 noms et la répartition de
couverture 67/36, tous deux gardés par quatre tests distincts, et le `§13`
exige en plus un **gabarit** de force sans matériel vivant dans
`reference_split.json`. C'est une livraison séparable, prête à exécuter, et
la mélanger à une migration aurait fait une tranche que personne ne peut
relire.

`§9` est respecté sur son interdiction : **aucun mouvement de tirage au
poids du corps n'a été inventé**. Un gabarit sans matériel n'aura pas de
tirage, et cela se dira.

---

## 13. Porte du filtre dur (`§13`)

| condition | état |
|---|---|
| toutes les exigences connues sur les candidats servis | ❌ **15 INCONNUS** |
| environnement concret représentable | ✅ livré |
| gabarit de force sans matériel vivant | ❌ identités résolues, non intégrées |
| utilisateurs existants en sécurité | ✅ `NULL`, 4 gardes |
| zéro `UNKNOWN` sur environnement résolu | ❌ |
| état « aucun candidat faisable » implémenté | ❌ non ouvert |
| empreinte d'Advice Memory | ❌ à ne toucher qu'en dernier |

**Le filtre reste éteint.** Une garde AST vérifie qu'aucun module de
décision n'importe `equipment_model` ; le seul importeur admis est la couche
de **déclaration**, et une seconde garde vérifie qu'elle n'y lit que le
**vocabulaire**, jamais un verdict.

⚠ Une condition non listée par le `§13` mérite de l'être : les 68 sont les
exercices **prescrits**. Les gabarits servent aussi **66 substituts**
(103 noms canoniques au total, 31 en recouvrement). Un filtre dur qui
ignorerait les substituts refuserait un candidat dont la substitution était
faisable.

---

## 14. Vérifications

* `check_scope` : `MIGRATION` — les dix contrôles requis exécutés
* `check_alembic_drift` · `check_schema_snapshot` · `check_migration_patterns`
  · `check_migration_roundtrip` · `check_spec_protocol` : tous `OK`
* `ruff` sur **tous les fichiers Python du diff** (et non sur une liste
  choisie à la main — c'est la cause racine qui s'est répétée deux fois) :
  propre. Scan `S9073` par AST : aucun.
* 42 gardes neuves, **trois mutations jouées** : l'ignorance devenue
  permission, le banc fabriqué par les haltères, le banc du hip thrust rendu
  obligatoire — toutes attrapées, dont la liaison provenance ↔ contrat servi
* 237 tests ciblés verts sur les contrats touchés
* **sweep local complet : `tous les lots sont verts.`** — 353 fichiers, aucun
  sauté, pic 1 472 Mo

### Une garde verte qui ne mesurait rien — attrapée par la CI

Le sweep local était vert et la CI a rendu **un** rouge, dans mon propre
fichier neuf : `test_an_item_declaring_an_unknown_capability_is_refused`,
`DID NOT RAISE`.

La cause est un défaut déjà consigné dans ce dépôt, sous une forme nouvelle.
La fixture `client` **purge `sys.modules["app.*"]**`. Les noms importés en
tête d'un fichier de tests sont liés à la **première** génération du module ;
dès qu'un test a utilisé `client`, un
`monkeypatch.setattr("app.services.equipment_model…")` ré-importe et patche
la **seconde**. La garde appelait alors une fonction que personne n'avait
patchée, ne levait rien, et passait.

Pourquoi verte en local : la collecte importe tout, puis les tests s'exécutent
dans l'ordre du fichier, et cette garde y précède tous les tests à `client`.
En CI, le découpage en shards la plaçait après. **Ce n'est pas un aléa de
parallélisme : c'est un ordre, et c'est la CI qui avait raison.**

Corrigé en résolvant **un seul** objet-module dans le test et en ne passant
que par lui. Le défaut d'origine a été **replanté tel quel** dans un fichier
jetable pour vérifier qu'il reproduit le message exact de la CI — il le
reproduit. Et une garde neuve mesure désormais la **prémisse** :
après un test à `client`, le module fraîchement résolu n'est plus celui dont
le fichier a importé les noms.

---

## 15. Livrables du `§14`

| demandé | où |
|---|---|
| table de curation des 68 | [annexe](SPRINT_TRAIN_A_ENVIRONMENT_CURATION_TABLE.md) · `data/equipment_curation.json` |
| résolutions internes | annexe, classe `ATLAS` — 34 lignes |
| résolutions externes des restants | annexe, classes `EXTERNE` (6) et `IDENTITE_AUREN` (13) |
| reliquat non résolu exact | `§7` ci-dessus · annexe, section « lignes INCONNUES » — 15 |
| vocabulaire final des objets | annexe — 26 objets |
| vocabulaire des capacités internes | annexe — 29 capacités |
| matrice objet → capacité | annexe, colonne « capacités dérivées » |
| delta de schéma exact | `§11` ci-dessus |
| statut du contenu sans matériel | `§12` ci-dessus |
| statut de la porte du filtre dur | `§13` ci-dessus |

---

## 16. Ce que cette tranche n'ouvre pas

Aucune surface utilisateur. Le `§0` demande que les deux déclarations ne
soient pas rendues comme deux questionnaires sans rapport — c'est une
décision d'écran, donc soumise au contrat de livraison UI, donc hors d'une
tranche de migration.

La récupération reste **close**. Les substitutions restent gelées.

---

## 17. Closeout

| | |
|---|---|
| **PR** | [#260](https://github.com/MFE-DSS/workout-session-tracking/pull/260) |
| **Merge** | `dfcd3bf66b989036c3e64ac5648318337dd4ed3a` |
| **Méthode** | `--merge` avec `--match-head-commit c86e86a` — pas de squash, pas de `--admin`, pas de force |
| **CI canonique** | run [`36416478850`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/36416478850) — **7/7 verts** |
| **Sonar** | `OK` — 0 bug, 0 code smell, couverture nouveau code **100 %** |
| **Threads de revue** | 0 non résolu |
| **Migration** | `x5y0s6t7v18` — additive, nullable, zéro backfill |

### Déploiement en production

| | |
|---|---|
| **Run** | [`36418056397`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/36418056397) — `success` |
| **SHA déployé** | `dfcd3bf` — **le SHA exact validé par la CI canonique**, closeout docs exclu |
| **Tag** | `deploy/prod/2026-09-28-1150-dfcd3bf` |
| **Sauvegarde préalable** | `var/backups/workout_pre_deploy_20260928_115036.db` |
| **Smoke VPS** | 17 contrôles, **tous `PASS`**, dont `check_alembic_drift returns OK` |
| **Smoke externe** | `spignos.com/healthz` · `/healthz/strict` · `/welcome` → **200** |

**Deux migrations ont été appliquées, pas une.** La production était restée
sur `v3w8q4r5t16` : elle a reçu `w4x9r5s6u17` (`UI-CP8R`, la vérité temporelle
du repos, mergée mais jamais déployée) **puis** `x5y0s6t7v18`. Les deux sont
additives et sans backfill, et la sauvegarde précède les deux.

Le `check_alembic_drift` de la production rend `OK` **après** migration : c'est
la preuve que la colonne existe réellement là-bas et non seulement dans le
modèle.

### Ce qui reste à l'arbitrage de l'opérateur

| question | effet si tranchée |
|---|---|
| le niveau de preuve `IDENTITE_AUREN` (13 lignes) | refusé ⇒ **40 connus / 28 inconnus** |
| les trois défauts de dépôt (`machine_slug` absent) | 3 INCONNUS résolus |
| le conflit `Relevés mollets debout` | 1 INCONNU résolu |
| le périmètre des **66 substituts**, absent du `§13` | élargit la porte du filtre dur |

🤖 Generated with [Claude Code](https://claude.com/claude-code)
