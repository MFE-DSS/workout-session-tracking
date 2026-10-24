# SPRINT Sb_SCI_V2_03 — Exigences `any_of` dans le moteur d'équipement (backend seul)

**Spec :** `docs/strategy/Sx_SCI_V2_CATALOGUE_INTEGRATION_01_SPEC.md` (v4 : §8.1, §8.2, §12) ·
**Base :** `8f9e3df` · **Date :** 2026-10-24 · **Branche :** `sb/sci-v2-03-train-a-delta`

## 1. Objet

`equipment_model` apprend la grammaire V1 des exigences du catalogue scientifique :
- une **conjonction** de capacités atomiques et de groupes `any_of` (au moins deux capacités
  atomiques, sans imbrication) ;
- une capacité **absente du vocabulaire servi** rend `UNKNOWN`, jamais `FEASIBLE`.

Le verdict reste celui de TRAIN A pour toute exigence de l'EKB. Ni le registre servi ni le web ne
changent.

## 2. Brainstorming / Options / Risques / Choix retenu

### 2.1 Le périmètre a changé en cours de tranche

La v3 de la spec mettait dans `Sb_SCI_V2_03` l'application du delta TRAIN A **et** la
déclaration des nouveaux objets. Le premier rendu, 13 cases neuves sur la page web *Mon plan*, a
été préparé, puis arrêté avant toute exposition. L'opérateur a tranché le 2026-10-24 : **tout
nouvel écran vise l'app mobile**. Ces cases n'auraient eu aucun effet pour l'utilisateur, puisque
V3 ne lit pas ces capacités.

| Option | Pour | Contre |
|---|---|---|
| (a) Appliquer le delta quand même et laisser le web afficher les cases | « fait » au sens de la v3 | travail visible sur la surface quittée, sans valeur ; exigerait un §5.1 web |
| (b) Appliquer le delta et cacher les cases sur le web | registre complet | un drapeau d'affichage de plus, et un registre qui ment sur ce qui est déclarable |
| (c) **Backend seul** : `any_of` et `UNKNOWN` hors vocabulaire ; delta et écran dans la piste mobile | aucune surface touchée ; le moteur est prêt pour le jour où l'app déclarera le matériel | le registre servi reste à 29 objets |

**Choix : (c)**, sur arbitrage opérateur. La spec passe en v4 (§8.2, §12) ; la modification du
registre préparée dans le worktree a été **annulée**, jamais commitée.

### 2.2 Où et comment évaluer un groupe `any_of`

- **Dans `equipment_model.py`**, sa seule maison. Il y a une seule notion de faisabilité, et aucun
  second résolveur.
- **Le groupe est un objet** (`AnyOf`), validé à la construction : au moins deux options, toutes
  atomiques. Une imbrication est donc impossible à représenter.
- **Le JSON du catalogue** se lit par `parse_requirements`, strict : tout membre qui n'est ni une
  chaîne ni `{"any_of": [...]}` est refusé.

### 2.3 Capacité inconnue du registre servi

La spec §8.1 l'exige : une capacité citée mais absente du vocabulaire rend `UNKNOWN`. Composition
des verdicts :
- un membre **connu et manquant** suffit à rendre `NOT_FEASIBLE` ;
- sinon, un membre indécidable rend `UNKNOWN` (atome inconnu, ou groupe dont aucune option connue
  n'est possédée mais dont une option est inconnue) ;
- sinon, `FEASIBLE`.

Pour toute exigence EKB, dont toutes les capacités sont connues (garde existante), cette règle se
réduit **exactement** à l'inclusion d'ensembles d'avant.

### 2.4 Risques

| Risque | Parade |
|---|---|
| Changer un verdict servi par mégarde | garde de **parité exhaustive** : chaque exercice de l'EKB, contre une palette d'environnements, comparé à la formule d'avant recopiée dans le test |
| Une entrée EKB se met à porter un `any_of` | garde : l'EKB n'en porte aucun |
| Un groupe vide, à une seule option ou imbriqué | `AnyOf` les refuse à la construction ; contre-preuve plantée |
| L'inconnu promu en faisable | garde : capacité hors vocabulaire ⇒ `UNKNOWN`, même dans l'environnement le plus riche |

## 3. Réalisé

### 3.1 Code

`app/services/equipment_model.py` :
- **`AnyOf`** (au moins deux options atomiques, sans imbrication) ;
- **`parse_requirements`**, lecteur strict du JSON du catalogue ;
- **`feasibility` / `missing_capabilities`**, composés membre à membre. Un groupe non satisfait
  est nommé `any_of(a|b)`.

Aucun autre fichier de code, aucun appelant modifié. `environment_resolution` et
`environment_activation` passent toujours des exigences EKB atomiques.

### 3.2 Gardes (`tests/test_sci_v2_03_any_of.py`, 24 tests)

| Garde | Ce qu'elle établit |
|---|---|
| **Parité exhaustive** | Les 107 exercices de l'EKB × 61 environnements : non déclaré, vide, complet, chaque objet seul, et tout sauf chaque objet. Verdict **et** liste des manques sont identiques à la formule d'avant, recopiée dans le test. |
| L'EKB sans `any_of` | Le chemin servi ne voit que des capacités atomiques. |
| Grammaire V1 | Groupe vide, à une option ou imbriqué : refusé. Six formes JSON hors grammaire : refusées. |
| Catalogue scientifique | Les 107 exigences se lisent, et au moins un groupe existe (le pullover). |
| Verdicts de groupe | Le pullover câble est faisable avec la poulie double, ou avec une poulie simple plus une corde ou une barre. Il ne l'est pas sans accessoire, ni sans ancrage haut. Le verdict est `UNKNOWN` si rien n'est déclaré. |
| Inconnu | Une capacité hors du vocabulaire servi est `UNKNOWN` même dans la salle la plus riche. Un manque connu refuse quand même. Un groupe avec une option inconnue reste `UNKNOWN` tant qu'aucune option connue n'est possédée. |

**Contre-preuves : 7/7 mutations en mémoire détectées** :
- inconnu lu comme manquant ;
- inconnu lu comme possédé ;
- `any_of` évalué comme un ET ;
- groupe à une option admis ;
- l'inconnu qui l'emporte sur un manque connu ;
- environnement vide traité comme non déclaré ;
- groupe omis de la liste des manques.

### 3.3 Vérifications

| Contrôle | Résultat |
|---|---|
| `check_scope.py` | **SHARED_CODE** (`equipment_model` est importé par TRAIN A) |
| Suites TRAIN A existantes et nouvelle garde | 173 passés, **sans aucun amendement de garde existante** |
| Full sweep local (`run_local_sweep.sh`, 366 fichiers, lancé parce que `equipment_model` porte tout TRAIN A) | **6 980 passés, 0 échec**, 1 sauté préexistant |
| Budget ruff | 264, valeur du canonique |
| Pré-scan Sonar | deux constructions corrigées avant push (S9073, S5778), plus un nom de variable qui déclenchait S3415 |
| `check_spec_protocol` | OK |

### 3.4 Périmètre interdit respecté

Ni `data/equipment_registry.json` ni le web ne sont modifiés : la modification préparée a été
annulée sur arbitrage opérateur (§2.1). V3, la mémoire de conseil, la base, l'UI et le N0 sont
intacts.

**Verdict :** `Sb_SCI_V2_03` (v4, backend seul) est construite et vérifiée en local. Le statut
final dépend de la CI réelle.
