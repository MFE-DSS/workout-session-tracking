# TRAIN 0 — closeout, et le mode d'exécution qui change

**Date** : 2026-08-22
**Canonique finale** : `5fce92b`
**Base d'entrée** : `a29a104`

---

## 0. Ce qui a changé de nature ce jour-là

L'opérateur a **tranché quinze arbitrages en batch** et remplacé le registre de
questions par une **file d'ordres**. Le contrat d'exécution devient :

> L'agent exécute jusqu'à `PR GREEN` sans revenir demander d'arbitrage
> intermédiaire. Il s'arrête **uniquement** si une mesure contredit une
> décision, si l'implémentation exige d'inventer une règle produit ou
> scientifique, ou si une migration destructive/non déterministe est requise.

Les garde-fous des §1–§3 de `CLAUDE.md` restent intégralement en vigueur : ce
protocole les **orchestre**, il ne les remplace pas. Merge, suppression de
branche et de worktree demeurent des arrêts durs.

---

## 1. Ce qui est livré

| PR | Arbitrage | Merge | Méthode |
|---|---|---|---|
| #136 | A12 | `c714f36` | `--merge`, tête `dfec4117` |
| #141 | **A13 + A14** | `079fff6` | `--merge`, tête `da4a3ac` |
| #140 | **A3** | `36f6fd7` | `--merge`, tête `8e30288` |
| #142 | **A1** | `5fce92b` | `--merge`, tête `7d9b64c` |

**Aucun squash, aucun `--admin`, aucun force.** Tête épinglée à chaque merge.

Hors PR : **PR #7 (bcrypt 5) fermée** avec sa preuve technique.

### CI canonique — source de vérité

**Run [`32570620277`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/32570620277)
sur `5fce92b` : `success`, 6/6 jobs verts** (lint · 3 shards pytest · QA
scripts · SonarCloud). Elle couvre les trois merges cumulativement.

**Une run annulée, et ce n'est pas un échec.** Le run sur `079fff6` apparaît
`cancelled` : le groupe de concurrence l'a supersédé au push suivant sur la même
branche. `CLAUDE.md` §2 demande explicitement de distinguer un échec de test
d'une annulation d'infrastructure — c'est le second cas, et le run sur la tête
finale rend le premier caduc.

### Ordre de merge, et pourquoi

`#141 → #140 → #142`. #141 portait le risque ops, #140 ne touchait que des
services, #142 portait la migration et gagnait à partir en dernier sur une base
stabilisée. Les trois éditaient `SPEC_REGISTRY.md` — **la ligne d'A1 avait été
délibérément retirée de sa propre PR** et différée à ce closeout, pour ne pas
fabriquer un conflit à trois dont la résolution aurait exigé des opérations git
sous confirmation. Le report était écrit dans le rapport d'A1, pas subi.

---

## 2. Quatre défauts trouvés en construisant

Aucun n'était cherché. Tous ont été trouvés parce qu'une garde a rougi.

### 2.1 — L'EKB contredisait sa propre cartographie

`103` entrées, **`102` exercices**. Une garde a rougi sur ce `-1` :

| Champ | `Curl marteau câble (corde)` | `Curl marteau câble corde` |
|---|---|---|
| `zone_primary` | `biceps` | `None` |
| `zone_macro` | `arms` | `None` |
| `confidence` | `measured` | `derived` |

**Le même mouvement était cartographié ou non selon l'orthographe rencontrée**,
dans la base de connaissance dite canonique. Non corrigée : ce serait un
jugement, hors périmètre A1. Une garde fixe désormais laquelle des deux survit.

### 2.2 — `check_alembic_drift` mesurait le mauvais arbre

Lancé depuis un worktree, il a rendu **`DRIFT DETECTED`** en réclamant la
suppression des deux tables neuves. Il migrait les migrations **du worktree**
tout en chargeant les modèles **de la canonique** : le script n'insère pas son
`repo_root` dans `sys.path`. Avec `PYTHONPATH` : `OK (no diff)`.

**Troisième occurrence de cette famille de piège** dans ce dépôt. Le
durcissement du script est un sujet `ci_infra` ouvert, signalé et non traité.

### 2.3 — Une garde passait pour la mauvaise raison

Celle vérifiant que le plafond bcrypt porte sa justification cherchait
« passlib » n'importe où au-dessus du pin — et **passait**, satisfaite par la
ligne de dépendance `passlib[bcrypt]>=1.7`. Elle mesurait la présence d'un
paquet, pas celle d'une explication. Resserrée sur un **commentaire**.

### 2.4 — Le lock ne gouvernait que les machines

`Sb_DEPENDENCY_LOCK_AUTHORITY_01` avait converti la CI et `deploy_prod.sh` et
**oublié l'humain**. **9 directives vivantes** installaient encore les plages
ouvertes — dont l'audit `pip-audit` de `SECURITY_BASELINE`, qui auditait donc
des *plages* et non des versions.

---

## 3. Deux échecs de sweep, aucune régression, aucun test affaibli

- `test_alembic_head_unchanged` — sentinelle délibérée. **Migrée** vers
  `t1u6o2p3r14` et augmentée de la raison de la forme retenue. Jamais
  supprimée.
- `test_no_model_migration_schema_touched` — lit `git diff --name-only HEAD`,
  donc rougit sur tout travail **non commité** et redevient vert au commit.
  **Vérifié plutôt que supposé** : 33/33 après commit.

---

## 4. Vérifications par tranche

| Tranche | Tier | Sweep local | CI PR |
|---|---|---|---|
| `MUSCLE_MAPPING_TRUTH_01` | `SHARED_CODE` | 397 ciblés (23 + 339 + 58) | 8/8 · Sonar OK · 98,6 % |
| `Sb_OPS_INSTALL_AUTHORITY_01` | `CI_INFRA` | **5147** (30:15, `workers=2`) | 8/8 · Sonar OK |
| `Sb_EXERCISE_IDENTITY_01` | `MIGRATION` | **5173** (30:21) + drift/snapshot/patterns/roundtrip | 8/8 · Sonar OK · 97,7 % |

### Réserve de méthode, consignée

Le full sweep d'A1 a tourné sur `7e9ea07`, **avant** le correctif Sonar
`7d9b64c`. Le refactor est couvert par les 32 gardes dédiées et par la CI
complète sur la tête finale — mais le sweep local, lui, ne porte pas sur le
dernier commit. Dit plutôt que tu.

### Incidents Sonar, tous in-scope

- #140 — `python:S3776` 22/15 sur `build_zone_exposure` → extraction de
  `_tally`.
- #142 — `python:S5890` (`= None` sur un `list[str]`) → `default_factory` ;
  `python:S3776` 16/15 → `_create_missing` + `_apply_declared_aliases`.

Aucun n'a été adjugé faux positif. Tous corrigés à la source.

---

## 5. État de la file d'ordres

| Statut | Ordres |
|---|---|
| **Exécutés** | A1 · A3 · A12 · A13 · A14 |
| **À exécuter — TRAIN 1** | A4 → A5 → A10 → A11 → A7 → A6 |
| **À exécuter — TRAIN 2** | A15 |
| **À exécuter — TRAIN 3** | A2 |
| **Différé sous condition** | A9 (instrument PRESCRIPTIF + contrat validé) · A3-c (retrait du matcher hérité) |
| **Clos, aucune action** | A8 |

A1 étant livrée, **A10 (instrument PROGRESSIF) a sa dépendance levée**.

---

## 6. Constaté, délibérément non traité

- **17 paires de quasi-doublons** dans le catalogue — de `Hip thrust Smith` ~
  `Hip thrust Smith machine` (le même mouvement) à `Rowing câble assis prise
  large` ~ `neutre` ~ `serrée` (des variantes). `exercise_aliases` existe pour
  que la fusion, quand elle sera tranchée, soit **additive**.
- **24 des 68 noms du catalogue** n'ont aucune entrée dans
  `exercise_properties` (69 clés, 44 en commun).
- **`weekly_loop.py` couvert à 81,6 %** — le plus bas des services de
  Progression. A11 ordonne son absorption ; vérification au moment d'attaquer
  A11.
- **`check_alembic_drift` à durcir** (`repo_root` dans `sys.path`) — sujet
  `ci_infra`.
- **L'état réel de la production reste NON MESURÉ** : A13 ferme la divergence
  documentaire, pas l'environnement déployé.

---

## 7. Nettoyage

**Non exécuté.** Suppression de branche et de worktree reste un arrêt dur de
`CLAUDE.md` §4. Trois branches et trois worktrees attendent un mot explicite :
`sb/muscle-mapping-truth-01`, `sb/ops-install-authority-01`,
`sb/exercise-identity-01` — plus `work/ops-ci-lint-timeout-01` (#136).
