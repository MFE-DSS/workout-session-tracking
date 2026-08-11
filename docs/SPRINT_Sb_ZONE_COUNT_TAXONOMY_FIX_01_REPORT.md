# SPRINT Sb_ZONE_COUNT_TAXONOMY_FIX_01 — Projection zone détaillée → axe radar (RAPPORT)

**Base canonique :** `9f8323f` · **Branche :** `sb/zone-count-taxonomy-fix-01` · **Tier :**
**SHARED_CODE** (`check_scope`), traité **avec full sweep local** — voir §5.
**Autorité de spec :** `docs/strategy/Sx_AUREN_ORCHESTRATOR_01_GAP_CONSOLIDATION_SPEC.md` **§P0.1**
(et §C.0-A pour le constat d'audit). **P0.1 du train `AUREN_P0_CORRECTNESS`.**
**0 migration · 0 écriture DB · 0 changement de taxonomie publique · 0 refonte UI.**

## 1. Brainstorming / Options / Risques / Choix retenu (`CLAUDE.md §3`)

### Le défaut, vérifié dans le code actif (pas dans un vieux rapport)

`profile_metrics._zone_session_counts` initialisait son accumulateur sur les **6 axes macro**
(`RADAR_AXIS_ORDER`) puis y insérait la **zone détaillée** rendue par `classify_exercise`
(`delt_lat`, `lats`, `upper_back`, `quads`, `posterior`, `calves`, …), derrière un garde
`if z in counts`.

Les deux niveaux taxonomiques ne partagent **qu'un seul libellé** : `pecs`. Conséquence
mécanique : `pecs` était le **seul axe pouvant jamais s'incrémenter**. `shoulders`,
`back_width`, `back_thickness`, `arms`, `lower` étaient **structurellement figés à 0**, quelle
que soit la réalité de l'entraînement. Le garde `if z in counts` rendait la perte **silencieuse**.

Ce n'est pas une imprécision de classement : c'est une lecture **fausse par construction** de
« zone travaillée / peu travaillée » sur la page profil, dans le coach report, dans l'inférence
coach (texte visible) et dans l'entrée radar Body Intelligence.

### Un second exemplaire du défaut, découvert au préflight

`body_intelligence_inputs._radar_zone_counts` portait **sa propre table** zone détaillée → axe,
écrite à la main, documentée comme « heuristique V1 ». Trois problèmes cumulés :

1. **C'était un doublon** de `RADAR_AXES`, la relation macro/détaillée déjà canonique.
2. **Il divergeait déjà** : il déclarait une zone `glutes` **absente** des 11 zones détaillées
   (`ZONE_LABELS`) — preuve concrète qu'une table dupliquée dérive.
3. Sa docstring annonçait « réagrège les 11 zones », alors que son entrée était **déjà** macro.
   Elle ne retenait donc que `pecs` (seul libellé commun) et **jetait tout le reste**.

Corriger uniquement l'amont aurait laissé BI cassé : la table locale aurait refiltré les axes
corrigés et tout remis à 0 sauf `pecs`. La spec exige explicitement « Body Intelligence input
receives corrected values » — les deux points devaient donc bouger ensemble.

### Options considérées

| # | Option | Verdict |
|---|---|---|
| A | Écrire une table `DETAILED_TO_AXIS` à la main dans `profile_metrics` | **Rejetée.** Ce serait la *sixième* table concurrente, exactement ce que la spec interdit. La table BI prouve empiriquement qu'une copie manuelle dérive. |
| B | Changer `classify_exercise` pour qu'il rende directement un axe macro | **Rejetée.** La spec l'interdit, et ce serait faux : `muscle_scoring` a besoin du niveau détaillé (11 zones scorées, puis agrégées). On perdrait de l'information. |
| C | Faire porter la projection à chaque consommateur | **Rejetée.** C'est la maladie actuelle (deux implémentations divergentes). Multiplie les frontières au lieu de les réduire. |
| D | **Dériver l'inverse de `RADAR_AXES`, projeter à UNE frontière, supprimer le doublon** | **Retenue.** |

### Pourquoi `RADAR_AXES` est la table canonique — justification explicite

La spec demande : « Reuse an existing canonical mapping if one already exists. If multiple
mappings exist: select the one already designated as canonical by current architecture, and
explicitly document why. » Deux candidates existaient. `RADAR_AXES` l'emporte parce que
l'architecture actuelle la traite **déjà** comme la relation officielle :

- `muscle_scoring.py:331-333` agrège les scores de zone sur les axes **en itérant
  `RADAR_AXES[axis]["zones"]`** — c'est le sens direct de la même relation ;
- `coach_report._zones` **libelle** ses clés via `RADAR_AXES.get(key)["label"]` ;
- `tests/test_auren_body_zone_contract.py` **la pinne** comme contrat ;
- elle vit dans `muscle_mapping.py`, à côté de `ZONE_LABELS` / `ZONE_VOLUME_TARGET` /
  `RADAR_AXIS_ORDER`, c'est-à-dire dans le module de taxonomie lui-même.

La table BI, à l'inverse, était locale, non testée, auto-qualifiée d'« heuristique V1 » et déjà
divergente. Le choix n'est pas arbitraire.

**Le point décisif : l'inverse est *dérivé*, pas recopié.**

```python
ZONE_TO_RADAR_AXIS = {
    zone: axis_key
    for axis_key in RADAR_AXIS_ORDER
    for zone in RADAR_AXES[axis_key]["zones"]
}
```

Aucun nouveau vocabulaire n'est introduit et les deux sens **ne peuvent pas diverger** : modifier
`RADAR_AXES` déplace automatiquement la projection. C'est la différence entre réutiliser la
table canonique et en fabriquer une sixième.

### Risques identifiés et traitement

| Risque | Traitement |
|---|---|
| Des valeurs affichées changent (5 axes passent de 0 à leur vraie valeur) | **C'est l'objectif du sprint**, pas un effet de bord. Le contrat de clé (`RADAR_AXIS_ORDER`) est inchangé : aucun consommateur ne casse. |
| `core` n'a **pas** d'axe radar | Projette sur `None` et est **abandonné**, jamais forcé sur un axe. `test_auren_bodymap_master` pinne déjà « `core` ∈ macros canoniques, ∉ `RADAR_AXIS_ORDER` ». Fabriquer un axe aurait inventé de la taxonomie. |
| Double comptage en agrégeant (une séance `delt_lat` + `delt_post` = 2 épaules ?) | La projection est faite **à l'intérieur** de l'ensemble par séance → une séance compte **au plus une fois par axe**. Deux tests dédiés. |
| Régression silencieuse chez un consommateur lointain | Tier remonté d'un cran : **full sweep local** en plus du broad sweep obligatoire. |
| Réintroduction future d'une table locale | Test qui échoue si `body_intelligence_inputs` redéfinit une table zone→axe. |

**Aucune taxonomie publique n'a dû être modifiée** → la condition de STOP de la spec
(« STOP only if fixing this requires changing the PUBLIC zone taxonomy ») **n'a pas été
atteinte**. `ZONE_LABELS`, `RADAR_AXES`, `RADAR_AXIS_ORDER`, `classify_exercise` : **inchangés**.

## 2. Ce qui est livré

### 2.1 `app/services/muscle_mapping.py` — la frontière de projection (unique)

Ajout de `ZONE_TO_RADAR_AXIS` (dérivée) et de `radar_axis_for_zone(zone) -> str | None`.
`None` signifie « cette zone n'a légitimement pas d'axe » (`core`) ou « ce n'est pas une zone
détaillée connue » (`unknown`, ou une clé déjà macro passée par erreur). Les appelants
**abandonnent** ces cas au lieu de leur inventer un axe.

Rien d'autre n'est touché dans ce module : ni les patterns, ni `classify_exercise`, ni le
chemin DB `Sb_32.2`.

### 2.2 `app/services/profile_metrics.py::_zone_session_counts` — le correctif

La zone détaillée est projetée **avant** comptage, à l'intérieur de l'ensemble par séance :

```python
axis = radar_axis_for_zone(primary) if primary else None
if axis is not None:
    axes_in_session.add(axis)
```

Le garde `if z in counts` disparaît : il ne masque plus rien, puisque toute valeur non-`None`
issue de la projection **est** un axe valide. La docstring énonce désormais le contrat de clé
(6 axes macro) et la sémantique « une séance compte au plus une fois par axe ».

**Préservés à l'identique** : filtre `status == "completed"`, filtre `excluded_from_stats`,
fenêtre temporelle, précédence de `substituted_name` sur `exercise_name_snapshot`, tie-break
déterministe de `top_zone` / `neglected_zone` par `RADAR_AXIS_ORDER`.

### 2.3 `app/services/body_intelligence_inputs.py` — suppression du doublon

La table locale de 11 entrées est supprimée. La fonction ne fait plus qu'une **normalisation de
forme** (garantir les 6 axes, y compris à 0, pour que le composeur puisse détecter
`undertrained_zone`). Le commentaire explique pourquoi elle n'a plus le droit de re-projeter.

Retiré au passage le `_ = classify_exercise` (« anti unused import ») et son import : c'était un
échafaudage réservé à un raffinement zone→axe par nom d'exercice — précisément ce que la
projection canonique rend caduc. Conserver un import mort au nom d'un plan annulé n'a pas de sens.

## 3. Sémantique avant / après

Jeu de données : une séance épaules (`Élévation latérale`), une séance dos-largeur
(`Traction`), deux séances jambes (`Hack squat`).

| Axe | Avant | Après |
|---|---|---|
| `pecs` | 0 | 0 |
| `shoulders` | **0** (perdu) | **1** |
| `back_width` | **0** (perdu) | **1** |
| `back_thickness` | 0 | 0 |
| `arms` | 0 | 0 |
| `lower` | **0** (perdu) | **2** |

`top_zone` : avant, **impossible** hors `pecs` (max de six zéros → `None`, ou `pecs`). Après :
`lower` (2 séances). `neglected_zone`, coach report, inférence coach et radar BI héritent
directement de la correction.

## 4. Tests — `tests/test_zone_count_taxonomy.py`, 24 tests

**Preuve que les tests mordent réellement.** Avant de les considérer comme acquis, j'ai
**temporairement restauré les lignes défectueuses** et relancé le fichier :
**13 échecs / 11 passés**. Les 11 survivants sont les tests purs de projection, qui portent sur
la table dérivée et sont par construction insensibles au bug amont. Le correctif rétabli :
**24/24**. Les tests ne sont donc pas décoratifs.

Couverture :

- **Projection (pur, sans DB)** — égalité stricte avec l'inverse de `RADAR_AXES` ; tout axe
  projeté est un vrai axe ; les 11 zones détaillées **moins `core`** couvrent exactement les
  6 axes ; `core` → `None` ; `unknown` / `""` / clés macro → `None` ; `pecs` → `pecs`.
- **Fixtures verrouillées** — la classification détaillée de chaque nom d'exercice utilisé est
  pinnée, pour que les tests de comptage ne mentent pas si un pattern substring bouge.
- **Les 4 familles exigées par la spec** — poitrine → `pecs`, épaule/deltoïde → `shoulders`,
  dos → `back_width` / `back_thickness`, bas du corps → `lower` (via `quads`, `posterior`,
  `calves`).
- **≥ 2 axes non nuls dans le même jeu de données** — `{pecs, arms, lower}`.
- **Une séance compte une fois par axe** — `delt_lat` + `delt_post` → `shoulders == 1` ;
  `quads` + `posterior` + `calves` → `lower == 1` ; trois séances épaules distinctes → 3.
- **Régression explicite du vieux bug** — une zone détaillée non-`pecs` (`delt_lat`) qui
  disparaissait compte désormais.
- **`core` seul** → aucun axe. **Exercice non classifiable** → aucun axe.
- **`substituted_name` prioritaire** — snapshot pectoraux, substitution élévation latérale →
  `shoulders == 1`, `pecs == 0`.
- **Filtres préservés** — `in_progress`, `excluded_from_stats`, hors fenêtre : non comptés.
- **Déterminisme** — lectures répétées identiques ; tie-break vérifié (`pecs` pour `top_zone`,
  `back_width` pour `neglected_zone`). Conforme à la mémoire Sonar S5863 : `first`/`second` sont
  liés à des variables distinctes, jamais `assert f(x) == f(x)`.
- **Consommateurs nommés par la spec** — coach report (clés macro correctement libellées),
  **inférence coach** (`strong_points` cite désormais « Épaules », branche inatteignable avant),
  **entrée BI** (`back_width == 1`, `lower == 2`), composeur BI (`_undertrained_zones` peut
  enfin être piloté par un axe non-`pecs`).
- **Anti-retour** — test échouant si `body_intelligence_inputs` réintroduit une table zone→axe.
  Pinné sur la source, car la régression visée (« quelqu'un rajoute un dict local ») se comporte
  correctement isolément et ne casse que l'invariant « une seule frontière de projection ».

## 5. Vérifications locales

`check_scope` : **SHARED_CODE** (broad sweep ciblé obligatoire ; full sweep « recommandé si
doute »). **Doute assumé et full sweep exécuté** : le changement touche `muscle_mapping`, module
de taxonomie fondateur, et modifie la **valeur** rendue par un service consommé par le coach, la
page profil et Body Intelligence. `CLAUDE.md §1` demande de remonter d'un cran en cas de doute ;
l'over-check a déjà attrapé de vraies régressions trois fois sur ce repo.

| Contrôle | Résultat |
|---|---|
| Broad sweep ciblé (zone, profil, BI, coach, contrats taxonomie, scoring) | **204 passés** |
| Full sweep parallélisé | voir §7 |
| Nouveaux tests ciblés | **24 passés** |
| ruff (fichiers touchés + neuf) | **clean** |
| Budget ruff | **543 ≤ 548** — strictement **neutre** vs la canonique |
| `check_spec_protocol` | **PASS** |

## 6. Non-régressions et interdits tenus

**Interdits de la spec, tous tenus** : `classify_exercise` non réécrit · taxonomie publique
`BodyZone` non redéfinie · radar non reconstruit · Body Intelligence non reconstruit · aucune
heuristique floue ni substring ajoutée · aucun vocabulaire de zone inventé · **0 changement de
schéma** · **0 migration** · **0 refonte UI** · **aucune sixième table concurrente** (le nombre
de tables zone→axe passe de **2 à 1**).

**Interdits du train, tous tenus** : pas de force-push, pas de rebase, pas de squash, pas de
merge `--admin`, `AGENTS.md` non touché, aucun flag Body Intelligence modifié, aucun déploiement.

### 6bis. Deux gardes d'isolation à signaler honnêtement

Le full sweep a fait échouer `test_worked_area_descriptor::test_muscle_mapping_untouched` et
`test_exercise_muscle_mapping::test_no_consumer_service_file_changed`. Ces deux gardes s'appuient
sur `git diff --name-only HEAD`, c'est-à-dire sur l'**arbre de travail** : elles interdisent des
modifications **non committées** de `muscle_mapping.py` et des services consommateurs, et
redeviennent vertes **au commit**. C'est un mode de faux échec déjà connu sur ce repo.

Deux choses méritent d'être dites plutôt que tues :

1. **Elles ne sont pas affaiblies ni supprimées** (garde-fou du train). Elles restent telles quelles.
2. **Leur portée réelle est faible** : mesurer `git diff HEAD` ne protège que le WIP. Elles
   étaient écrites pour prouver l'isolation de *leur* sprint (`Sb_32.2`, UI worked-area) et n'ont
   pas de valeur d'invariant permanent. La spec canonique **autorise explicitement** l'impact P0.1
   sur `profile_metrics` et `body_intelligence_inputs`, et `classify_exercise` n'est pas modifié.
   Renforcer ces gardes serait un travail légitime — **hors périmètre de ce sprint**, donc non fait.

## Verdict

**Livré.** La projection zone détaillée → axe radar existe désormais à **une seule frontière**,
**dérivée** de la table canonique et donc incapable de diverger. Les 6 axes du radar sont
atteignables ; « zone travaillée / peu travaillée », le coach report, l'inférence coach et
l'entrée Body Intelligence reflètent les séances réelles au lieu du recouvrement accidentel de
deux niveaux de taxonomie. Le nombre de tables zone→axe concurrentes passe de **2 à 1**.

**Critère d'acceptation de la spec — atteint** : « zone travaillée / peu travaillée must reflect
actual sessions rather than the accidental overlap between detailed and macro labels. »

**Preuve exécutée, pas affirmée** : les lignes défectueuses restaurées font échouer **13** des
24 tests ; rétablies, **24/24**.

| Vérification | Résultat |
|---|---|
| Tests ciblés neufs | **24 passés** |
| Broad sweep ciblé (zone/profil/BI/coach/taxonomie/scoring) | **204 passés** |
| Full sweep parallélisé | **3059 passés** + 2 gardes d'arbre de travail (§6bis), vertes au commit |
| ruff (fichiers touchés + neuf) | clean |
| Budget ruff | 543 ≤ 548 (neutre) |
| `check_spec_protocol` | PASS |

Statut : `Sb_ZONE_COUNT_TAXONOMY_FIX_01 PR GREEN / MERGE PENDING` — puis merge permanent
autorisé par le `GO TRAIN`.
