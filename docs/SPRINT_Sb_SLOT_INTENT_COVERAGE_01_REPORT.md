# SPRINT Sb_SLOT_INTENT_COVERAGE_01 — couverture primaire des 11 zones (RAPPORT)

**Train :** `AUREN_WEEKLY_PLAN_PRODUCTIZATION_01`, tranche 1/4 ·
**Base canonique :** `53425ab` · **Branche :** `sb/slot-intent-coverage-01` ·
**Tier `check_scope` :** **SHARED_CODE**

Le planificateur livré en `Sb_WEEKLY_PLANNER_01` savait dire qu'il ne savait pas
programmer `lats`, `core`, `biceps` et `triceps`. Ce sprint ferme ce qui peut
l'être **honnêtement**, et nomme précisément ce qui ne le peut pas.

---

## 1. Brainstorming / Options / Risques / Choix retenu

### La question qui décide de tout

Le brief pose une garde dure : **ne pas ajouter d'intentions bras si la couche
de scoring ne sait pas distinguer un biceps d'un triceps**. Le préflight y a
répondu par la mesure, pas par l'intuition.

`exercise_properties.json` — le pool de candidats du générateur — contient
**17 exercices de bras**, et les 17 partagent le **même triplet** :

```
zone_primary = "arms" · pattern_motor = "isolation_upper" · chain = "isolation"
muscle_group = null   (pour les 17, sans exception)
```

« Curl EZ-bar debout » et « Triceps pushdown corde » sont donc **littéralement
indiscernables** dans la source que le générateur consulte. Une intention biceps
naïve aurait scoré un pushdown exactement comme un curl. **La garde dure du
brief était fondée** : l'implémentation naïve est refusée.

### Options examinées

| # | Option | Verdict |
|---|---|---|
| A | Écrire `muscle_group: biceps/triceps` sur les 17 entrées du pool | **REFUSÉE — par la preuve** |
| B | Discriminer par l'identité de zone détaillée **canonique** | **RETENUE** |
| C | Un second matcher de noms dans le générateur | Refusée d'office (interdit par le brief, et c'est la bonne interdiction) |
| D | Renoncer aux bras, ne livrer que `lats` | Refusée : la discrimination est possible, y renoncer serait un faux constat d'impossibilité |

**Pourquoi A est refusée, et c'est le point le plus important du sprint.**
L'option A suit pourtant le motif architectural existant (`_REGION_ZONE_MUSCLE_GROUP`
sépare déjà `lower` et `shoulders` par `muscle_group`). Elle est refusée parce
que `substitution._classify_suggestion` **conditionne l'éligibilité N1 à
l'égalité de `muscle_group`** :

> « si l'origine a un `muscle_group` renseigné, le candidat doit avoir le même
> pour être éligible à N1 »

Écrire ce champ aurait donc **changé les suggestions du tiroir de substitution
en production** — un changement de comportement runtime dans un moteur fermé,
obtenu par un fichier de données, sans que rien dans le diff ne le laisse voir.
Le brief exige `substitution behavior unchanged` ; A l'aurait violé
silencieusement.

**Option B, retenue.** La discrimination délègue à
`body_zone_source.resolve_exercise_zones` — le **contrat canonique unique** de
lecture des zones du dépôt (corrections revues → ligne formelle
`ExerciseMuscleMapping` → classifieur historique). Aucun matcher nouveau, aucun
champ inventé, **aucune écriture dans le pool**, et le runtime N1/N2/N3 reste
identique au bit près.

### Risques assumés

- **Le chemin pur passe par le classifieur historique.** `db=None` est
  explicitement supporté par le contrat, et `resolution_path` le dit. La même
  attribution est materialisée en base dans `ExerciseMuscleMapping` : c'est la
  *même* donnée, pas une seconde source.
- **Discrimination limitée à `arms`.** Mesurée, pas supposée : c'est la seule
  région macro qui regroupe plusieurs zones détaillées **et** dont le pool est
  entièrement dépourvu de `muscle_group`.

---

## 2. Préflight — discrimination des candidats, par la mesure

| Question du brief | Réponse | Preuve |
|---|---|---|
| `lats` vs `upper_back` ? | **OUI, deux fois** | Régions macro **distinctes** dans le pool (`back_width` 8 exos / `back_thickness` 7) **et** motifs distincts (`pull_vertical` / `pull_horizontal`) |
| `biceps` vs `triceps` ? | **NON dans le pool** → OUI par le contrat canonique | 17 exos indiscernables ; le référentiel canonique les partitionne en **12 biceps / 5 triceps** |
| `core` vs toute isolation ? | **OUI pour l'identité, mais zéro candidat** | 8 exercices `core` au référentiel, **aucun** dans `exercise_properties.json` ; EKB `coverage_status: gap`, `movement_pattern`/`equipment_family` à `null` |

**`lats` ne demandait aucun mécanisme** : la région `back_width` existait déjà,
7 exercices `pull_vertical` l'attendaient. La lacune était purement un **trou de
registre**.

---

## 3. Ce qui a été livré

**Quatre intentions**, sur du vocabulaire strictement existant :

| `intent_id` | Zone | Motif | Interdits |
|---|---|---|---|
| `lats_width_vertical_pull` | `lats` | `pull_vertical` | `pull_horizontal` |
| `elbow_flexor_direct` | `biceps` | `isolation_upper` | `pull_vertical`, `pull_horizontal` |
| `elbow_extensor_direct` | `triceps` | `isolation_upper` | `push_vertical`, `push_horizontal` |
| `trunk_core_direct` | `core` | **`core`** (PatternMotor déjà valide) | `isolation_upper`, `isolation_lower` |

**Aucun axe radar fabriqué.** `core` n'en a toujours pas et reste
**indéclarable** comme priorité macro. Sa région vient de l'EKB, dont
`_zone_macro_vocab` porte `core` et dont chaque entrée `zone_primary: core` porte
`zone_macro: core`. Un test vérifie que cette dérivation **concorde avec
`RADAR_AXES` sur les dix zones qui ont un axe** — les deux sources ne peuvent pas
diverger en silence.

**Garde scientifique versionnée dans le code** (`slot_intent.SCIENTIFIC_GUARD`),
pas seulement dans ce rapport. Un test interdit `EMG`, `activation`, `%`,
`obligatoire`, `supérieur`, `prouvé` dans le rationale des nouvelles intentions.
Un créneau bras direct est un **choix de comptabilité de volume**, pas la thèse
que les bras ne progresseraient que par l'isolation.

---

## 4. Le défaut que ce sprint met au jour — et corrige

Avec `core` enfin doté d'une intention, le planificateur a répondu :

```
core   planned_slots=1   unmet_reason=None      exercise_name=None
```

**Une zone sans le moindre exercice se déclarait couverte.** Le générateur émet
un créneau pour toute intention retenue, y compris quand rien ne peut le
remplir ; le planificateur comptait ces créneaux. Le défaut était **latent** —
invisible tant que les quatre zones concernées n'avaient aucune intention — et
c'est exactement le fail-open que le brief de la tranche 2 demande d'attraper
(« planned_slots=1 n'est pas automatiquement couvert »).

Trois corrections :

1. `planned_slots` ne compte que les créneaux **remplis** ;
2. la raison vient d'un `gap_kind` **nommé par le générateur**
   (`coverage` / `availability` / `distinctness`), plus jamais déduite de la
   simple présence d'une déclaration de matériel ;
3. **un axe partiellement servi n'est pas servi** — `arms` n'est satisfait que si
   `biceps` **et** `triceps` le sont.

Le point 3 mord immédiatement : les **cinq** candidats triceps du référentiel
sont **tous à la poulie**. Sans câble déclaré, « Bras » ressort non servi, en
nommant `Triceps`.

---

## 5. Résultat

| Zone | Avant | Après |
|---|---|---|
| `lats` | aucune intention | **servie** — Lat pulldown prise large |
| `biceps` | secondaire seulement | **servie** — Curl EZ-bar debout |
| `triceps` | secondaire seulement | **servie** — Extension overhead câble |
| `core` | aucune intention | **intention réelle, `UNMET_NO_CANDIDATE`** |
| 7 autres | servies | inchangées |

**Couverture d'intention : 11/11.** **Couverture programmable : 10/11.**

L'exception restante est **de données, pas de registre**, et la distinction est
portée par deux constantes différentes (`UNMET_NO_CANDIDATE` vs
`UNMET_NO_INTENT`) pour qu'un consommateur sache à quel mur il est. Donner des
propriétés aux huit exercices de tronc exigerait d'inventer leur
`movement_pattern` et leur `equipment_family` : aucune source du dépôt ne les
porte. **C'est une décision produit, pas un travail d'implémentation** — elle
appartient à l'opérateur, et le sprint la lui remonte plutôt que de la
fabriquer.

### Les six axes déclarables

| Axe | Zones | Servable |
|---|---|---|
| `pecs`, `shoulders`, `back_thickness`, `lower` | — | oui (inchangé) |
| **`back_width`** | `lats` | **oui** (nouveau) |
| **`arms`** | `biceps` + `triceps` | **oui**, si le matériel couvre les deux |

---

## 6. Tests — 28 nouveaux, dont un plant vérifié

Le test qui porte la preuve n'est pas « biceps sélectionne un curl » : c'est
**`test_the_pool_genuinely_cannot_tell_a_curl_from_a_pushdown`**, qui épingle
que la source ne sépare *pas*. Sans lui, la discrimination pourrait devenir
redondante sans que personne s'en aperçoive.

**Le plant** (`test_the_discrimination_guard_bites_when_removed`) retire `arms`
de l'ensemble discriminé et vérifie que les deux intentions retombent bien sur
le **même** jeu de candidats. Il assert explicitement que le plant n'est pas
inerte — une garde non prouvée est une garde supposée.

Couverture : audit 11 zones · lats ne prend que du lats · un rowing ne peut
jamais satisfaire lats · biceps ⊥ triceps (exhaustif sur tous les candidats
qualifiants, pas un exemple) · core ne prend aucune isolation haute · créneau
vide ≠ couverture · restriction matériel nommée comme telle · axe à moitié servi
refusé · `exercise_properties.json` intact · générateur inchangé hors nouvelles
intentions · aucun matcher de noms · déterminisme.

### Tests existants mis à jour — et pourquoi ce n'est pas un affaiblissement

Neuf tests épinglaient **la limitation que ce sprint ferme**. Le plus parlant :

```python
- assert zones_servable_as_primary() < set(ZONE_VOLUME_TARGET)   # sous-ensemble strict
+ assert zones_servable_as_primary() == set(ZONE_VOLUME_TARGET)  # égalité
```

L'assertion est passée d'une contrainte **faible** à une contrainte **forte**.
Aucun test n'a été supprimé, rendu optionnel, ni relâché. Le témoin de
`test_a_structural_gap_survives_the_replan` passe de `lats` à `core` : la
propriété testée — replanifier ne comble pas un manque structurel — est
identique, seule la zone témoin encore lacunaire a changé.

---

## 7. Non-régressions vérifiées

`substitution.py` non modifié · `exercise_properties.json` non modifié (test
dédié) · `recommendation.py` / `behavioral.py` non touchés · aucune migration,
aucune écriture, aucun changement de cycle de vie · `RADAR_AXES` inchangé ·
générateur déterministe hors nouvelles intentions.

## 8. Limites assumées

- **`core` reste non programmable** faute de propriétés candidates. Remontée,
  pas comblée.
- **Une divergence de données préexistante détectée hors périmètre** :
  « Calf press leg press » est `calves` selon l'EKB et `quads` selon le
  classifieur canonique (le groupe `quads` contient « leg press » et gagne). Ce
  sprint **ne la corrige pas** — elle n'entre pas dans son périmètre et le
  contrat exige qu'une divergence inexpliquée soit un arrêt, pas une entrée
  ajoutée en passant à la liste des corrections revues. Elle est signalée pour
  arbitrage.
- La discrimination canonique s'applique à `arms` uniquement, sur constat
  mesuré ; toute nouvelle région surchargée devra être examinée de la même
  façon.

## Verdict

**Couverture d'intention 11/11, couverture programmable 10/11.** Les deux axes
déclarables qui n'étaient pas servables — `back_width` et `arms` — le sont
désormais, et la discrimination bras est **prouvée** plutôt qu'affirmée : le
test qui compte épingle que la source de données ne sépare *pas*, et le plant
vérifie que la garde retirée fait bien retomber les deux intentions sur le même
jeu de candidats.

L'implémentation naïve interdite par le brief a bien été refusée, et pour une
raison qui n'était pas prévisible depuis le brief : écrire `muscle_group` sur
les 17 exercices de bras aurait **changé les suggestions de substitution en
production** via une simple édition de fichier de données.

Un fail-open a été trouvé et corrigé au passage : une zone sans aucun exercice
se déclarait couverte. Il était latent, et le devient d'autant moins que la
tranche 2 va compter des séries plutôt que des créneaux.

Reste `core` : intention réelle, aucun candidat programmable. **Décision produit
remontée à l'opérateur**, pas comblée par fabrication.

---

## Closeout (post-merge)

| | |
|---|---|
| PR | **#93** — `--merge --match-head-commit`, **sans** squash / `--admin` / force |
| Build | `46e50de` + correctif Sonar `e134c8e` |
| Merge | **`e80e4c5`** |
| CI canonique | **`31887837362` — 5/5 GREEN** |
| Gate Sonar | **`OK`** — couverture du neuf **98,1 %**, 0 smell, 0 bug, 0 vulnérabilité |
| Threads / Gitar | **0 / 0** |
| Tests | 4093 (shard 1 : 1978 · shard 2 : 2115) — identique au full sweep local |
| Manifeste | 231 fichiers ⇒ 116 + 115, nouveau fichier absorbé automatiquement |

### Capacité CI — **HEALTHY**

| | Shard A | Shard B |
|---|---|---|
| min MemAvailable | **5 777 Mo** | **4 769 Mo** |
| min SwapFree | 3 071 Mo — **jamais entamé** | 3 071 Mo — **jamais entamé** |
| Durée | 8 min 06 | 9 min 28 |

Les deux shards tiennent la cible ≥ 4 Go. **Tendance à surveiller** : le shard B
passe de ~5 200 Mo (tranches précédentes) à **4 769 Mo**. Marge réelle mais en
érosion — cohérent avec le modèle de coût établi (la mémoire suit les tests
utilisant le fixture `client`, et cette tranche en ajoute peu).

### Incident Sonar résolu dans le périmètre

**1 finding réel** : `python:S8997` ×2 — le plant de discrimination échangeait un
`frozenset` de module à la main avec restauration en `finally`. Sonar a raison,
`monkeypatch` fait la même chose avec un démontage garanti. Les deux
`cache_clear()` sont partis avec : `_canonical_detailed_zone` indexe des noms
d'exercices et ne lit jamais l'ensemble patché — les vider suggérait un couplage
inexistant.

**Piège de diagnostic évité** : après le correctif, l'API du gate renvoyait
**encore** `ERROR 15` alors que le job SonarCloud tournait toujours. Lire ce
chiffre comme un échec aurait déclenché une seconde correction inutile sur du
code déjà bon. Attendre l'analyse réelle a donné `OK` — application directe de
la règle « ne jamais changer de code sur le seul agrégat ».
