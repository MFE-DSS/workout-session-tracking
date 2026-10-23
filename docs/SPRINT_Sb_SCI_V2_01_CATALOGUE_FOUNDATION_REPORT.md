# SPRINT Sb_SCI_V2_01 — Fondation statique du catalogue scientifique

**Spec :** `docs/strategy/Sx_SCI_V2_CATALOGUE_INTEGRATION_01_SPEC.md` (v2, rulings §19) ·
**Base :** `0c9e14b` · **Date :** 2026-10-23 · **Branche :** `sb/sci-v2-01-catalogue-foundation`

## 1. Objet

Faire entrer dans le dépôt, comme **donnée versionnée**, le catalogue scientifique clos des 107
exercices, ainsi que :
- son schéma ;
- son registre de preuves ;
- sa politique de crédit d'exposition ;
- un chargeur ;
- un validateur ;
- un rapport de validation régénéré par l'outil.

Tous ces artefacts sont produits par un chemin de génération **reproductible à l'octet**. Rien
n'est consommé par le produit : aucun résolveur d'historique, aucun registre d'exposition, aucun
changement de TRAIN A, de `equipment_model`, de V3, de l'UI, de la base ou du laboratoire N0.

## 2. Brainstorming / Options / Risques / Choix retenu

### 2.1 Où s'arrête la « source » ?

La chaîne d'origine est la suivante :
1. le document arbitré (hors dépôt) ;
2. `build_inputs.py` ;
3. la curation par des agents ;
4. la revue indépendante ;
5. l'assemblage ;
6. la clôture par rulings ;
7. la validation.

| Option | Pour | Contre |
|---|---|---|
| (a) Versionner tout depuis le document arbitré | provenance complète | le document n'est pas dans le dépôt ; la curation et la revue sont des jugements, pas des calculs |
| (b) La source commence aux **faits curés et revus** ; le dépôt rejoue la clôture | rejouable à l'octet ; chaque ruling opérateur est du code relisible | l'amont (extraction, curation) reste une provenance documentée, pas un calcul rejoué |

**Choix : (b).**
- **Sources versionnées** sous `data/sci/sources/` :
  - fiches revues ;
  - patch d'équipement ;
  - carte d'identité ;
  - proposition de delta TRAIN A ;
  - fixtures de régression ;
  - schéma arbitré.
- **`data/sci/evidence_registry.json`** est une autorité source, et non un produit.
- **Le générateur** applique les rulings et produit les quatre fichiers de `data/sci/` plus la
  proposition de delta amendée.
- **Le validateur** produit le rapport.
- Les identifiants source viennent de l'EKB du dépôt, sans copie.

### 2.2 Moteur de validation du schéma

`jsonschema` **n'est pas** une dépendance du dépôt : ni dans `requirements.txt` ni dans le lock,
et la CI installe le lock (`Sb_DEPENDENCY_LOCK_AUTHORITY_01`).

| Option | Pour | Contre |
|---|---|---|
| (a) Ajouter `jsonschema` au runtime et au lock | implémentation de référence | dépendance d'exécution (VPS) pour un outil de validation ; quatre paquets transitifs dont un binaire Rust ; décision de dépendance qui revient à l'opérateur |
| (b) L'ajouter seulement à la ligne pytest de la CI | pas d'impact sur le runtime | dépendance **non verrouillée**, contraire à l'esprit du lock ; modifie `ci.yml` |
| (c) Un validateur **interne** du sous-ensemble 2020-12 effectivement employé, avec liste blanche de mots-clés | aucune dépendance ; un mot-clé non géré **échoue** au lieu d'être ignoré | c'est du code à garder exact |

**Choix : (c).**
- **Une garde de liste blanche** fait échouer tout mot-clé du schéma que le validateur ne sait
  pas appliquer.
- **Une garde de concordance avec `jsonschema`** s'exécute quand la bibliothèque est importable,
  ce qui est le cas sur le poste de développement. Elle compare les deux moteurs sur toutes les
  fiches et tous les défauts plantés. Elle est sautée en CI, et c'est dit, pas caché.

### 2.3 Où vivent les rulings, et ce qui les garde ?

- Les rulings opérateur (fusions, exigences, affichages) sont du **code de génération**.
- Les invariants qu'ils fixent sont **réécrits indépendamment** dans les tests, depuis le texte
  de l'opérateur, et non lus dans le générateur. Une garde qui relirait les constantes du
  générateur ne garderait rien.
- Le validateur reste **générique** (schéma, références, capacités, identités, fixtures).

### 2.4 Rapport et reproductibilité

- **Horodatage.** L'horodatage `generated_at` des prototypes interdisait la reproduction à
  l'octet. Il est remplacé par `sources_digest`, le condensat des sources.
- **Rapport séparé.** Le rapport de validation est un fichier distinct
  (`exercise_catalogue.validation_report.json`) : le catalogue est l'autorité, le rapport une vue
  dérivée.
- **Mode `--check`.** Le générateur et le validateur ont un mode qui compare l'octet sans rien
  écrire. Les tests l'exercent.

### 2.5 Risques

| Risque | Parade |
|---|---|
| Le validateur interne diverge de la norme | liste blanche ; concordance avec `jsonschema` en local ; défauts plantés |
| Une garde de défaut planté « verte » qui ne mord pas | chaque défaut planté doit **échouer** pour une raison nommée, pas seulement par un code de sortie |
| Tier : `scripts/**` est `ci_infra` | full sweep local par lots (`run_local_sweep.sh`), puis CI réelle |
| Fichiers neufs sous `app/` repérés par des gardes de registre (lecteurs, modules) | sweep ciblé, puis sweep complet |
| Taille des fichiers de données | **mesurée** : catalogue 404 Ko, sources revues 356 Ko, rapport 44 Ko ; c'est **six fois** l'EKB (68 Ko), surtout à cause des notes de curation, qui sont la provenance. JSON indenté pour rester diffable ; aucun chargement au démarrage du produit |

## 3. Réalisé

### 3.1 Fichiers

| Fichier | Nature |
|---|---|
| `data/sci/sources/*` | **sources** : fiches revues, patch d'équipement, carte d'identité (et son rapport), proposition de delta de base, fixtures de régression, schéma arbitré |
| `data/sci/evidence_registry.json` | autorité E0, 96 entrées (source) |
| `data/sci/exposure_credit_policy.json` | autorité `sci-exposure-credit-v1`, rédigée (source) |
| `data/sci/exercise_catalogue.schema.json` | **généré**, vocabulaires fermés |
| `data/sci/exercise_catalogue.json` | **généré**, 107 fiches |
| `data/sci/train_a_delta_proposal.json` | **généré**, delta TRAIN A proposé, non appliqué |
| `data/sci/exercise_catalogue.changes.txt` | **généré**, journal de clôture |
| `data/sci/exercise_catalogue.validation_report.json` | **généré** par le validateur, épingle le condensat du catalogue |
| `scripts/generate_sci_catalogue.py` | générateur, `--check` |
| `scripts/validate_sci_catalogue.py` | validateur et moteur de schéma interne, `--write` / `--check` |
| `app/services/sci_catalogue.py` | chargeur et politique de crédit ; **aucun appelant** |
| `tests/test_sci_catalogue_{loader,validator,generation,rulings}.py` | 123 tests |
| `docs/strategy/Sx_SCI_V2_CATALOGUE_INTEGRATION_01_SPEC.md` (v2), `Sx_AUREN_SCIENTIFIC_ENGINE_V2_SPEC.md`, `SPEC_REGISTRY.md` | autorité versionnée |

### 3.2 Résultat du validateur (régénéré)

| Mesure | Valeur |
|---|---|
| Fiches source | **107/107** |
| Erreurs de format | **0** |
| Publiables | 107 |
| Identités canoniques = candidats du compilateur | **84** |
| Alias historiques | **23** (11 par faits sources, 12 par définition opérateur) |
| UNIQUE / doublon exact / variante légitime / **UNRESOLVED** | 48 / 18 / 18 / **0** |
| Vecteurs d'exposition incomplets | 28 |
| Exigences UNKNOWN | 1 |
| `machine_unspecified` | 29 |
| `any_of` réels | 1 |
| `CONTENT_EXECUTION_MISMATCH` | 2 |
| Fixtures de régression | 4, vertes |

Comparé au prototype de clôture hors dépôt, le catalogue généré dans le dépôt ne diffère que sur
les **quatre** fiches visées par les rulings du GO BUILD : deux `content_alignment` et les
exigences des deux rowings assis. Toutes les autres fiches sont identiques en science, en
opérationnel et en identité.

### 3.3 Vérifications

| Contrôle | Résultat |
|---|---|
| `check_scope.py` | **CI_INFRA** (`scripts/**`) ⇒ full sweep local + CI réelle |
| Tests de la tranche | 123 passés. La concordance avec `jsonschema` a été **exécutée** localement (bibliothèque présente) et sera **sautée** en CI |
| Défauts plantés | **29/29** rejetés, chacun pour **sa** raison nommée (26 sur les fiches, 3 sur le delta) |
| Reproductibilité | `generate_sci_catalogue.py --check` et `validate_sci_catalogue.py --check` : 0 écart ; deux constructions identiques à l'octet |
| ruff, fichiers neufs | propre |
| Budget ruff | 264 ≤ 548 |
| `check_spec_protocol` | OK |
| Full sweep local (`run_local_sweep.sh`, 363 fichiers par lots) | **6 905 passés, 0 échec**, 1 sauté (préexistant) |

### 3.4 Ce que la tranche a attrapé chez moi

1. **Une mutation de test vide.** Le test « changer une source change la construction »
   remplaçait une chaîne absente du fichier. Il ne mutait rien, et il aurait été vert pour cette
   raison si le condensat avait été mal calculé. Il est réécrit : il vérifie que la mutation a lieu,
   puis exige que le **catalogue** généré change, pas seulement le condensat.
2. **Le nom du module servi dans un test.** Écrire le nom du recommandeur V3 en clair aurait fait
   rougir la garde d'import `REC-CP2`. Le test vérifie maintenant une règle plus forte : aucun
   module SCI n'importe quoi que ce soit sous `app.`.
3. **Une exécution inventée.** J'allais donner aux deux rowings assis une exécution canonique
   (« poignée en V ») que l'opérateur n'a pas définie. Il a statué sur l'**accessoire** seulement.
   L'exécution a été retirée.

### 3.5 Périmètre interdit respecté

Aucun résolveur d'historique, aucun registre d'exposition, aucun changement de
`data/equipment_registry.json` ni de `equipment_model.py`, aucune UI, aucun changement de V3 ni de
recommandation, aucun comparateur d'ombre, aucune migration, aucun travail sur le N0, aucune
correction de contenu servi, aucune promotion. `app/services/sci_catalogue.py` n'a aucun appelant.

**Verdict :** `Sb_SCI_V2_01` est construite et vérifiée en local. Le statut final dépend de la CI
réelle, impérative au tier CI_INFRA.
