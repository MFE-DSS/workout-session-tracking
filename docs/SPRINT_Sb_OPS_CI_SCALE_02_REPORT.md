# SPRINT Sb_OPS_CI_SCALE_02 — 2 → 3 shards, et le compte cesse de dériver (RAPPORT)

**Base canonique :** `dc6cdd0` · **Branche :** `sb/ops-ci-scale-02`

---

## 1. Brainstorming / Options / Risques / Choix retenu

Le déclencheur est une mesure, pas une intuition : le shard B est passé à
**3 701 Mo** de MemAvailable, sous le plancher `HEALTHY` de 4 Go, après une
pente régulière sur quatre tranches (5 065 → 4 772 → 4 380 → 3 701) qui suit la
croissance du nombre de tests (4 314 → 4 453).

**Le goulet est la mémoire par machine**, pas la correction ni la couverture.
Le sharder accepte déjà un `shard_count` arbitraire : la marche suivante la plus
petite est **3 × 2 workers**, qui réduit les tests par machine sans toucher au
modèle d'isolation.

### Le vrai travail n'était pas le « 3 »

Changer `2` en `3` prend une ligne. Le risque était ailleurs : **le nombre
vivait à trois endroits que rien ne comparait**.

| Emplacement | Avant |
|---|---|
| Matrice du workflow | `shard: [1, 2]` |
| `ci_test_shards.DEFAULT_SHARDS` | `2` |
| Assertion de couverture | `if [ "${found}" -ne 2 ]` |

Une seule copie pouvait bouger et **la CI serait restée verte en publiant la
couverture de deux shards sur trois** — une couverture partielle présentée comme
complète.

**Options.** (a) trois constantes et de la discipline — rejetée, c'est l'état
actuel ; (b) une variable de dépôt GitHub — **rejetée par le brief** et à raison,
le nombre doit être versionné avec le code ; (c) *(retenue)* **une source unique
versionnée + dérivation + vérification machine**.

**Choix retenu :**

- `DEFAULT_SHARDS = 3` est la **seule** valeur à changer ;
- l'agrégateur de couverture **dérive** le nombre (`--shard-count`) — la
  troisième copie **n'existe plus** ;
- la matrice YAML, que GitHub Actions ne peut pas calculer, reste en dur mais
  est **comparée à la constante par un test**.

Il reste donc une valeur, une copie, et une machine qui refuse la divergence.

---

## 2. Ce qui n'a pas bougé

Granularité **fichier** · round-robin alphabétique déterministe **inchangé**
(le brief interdit de toucher à l'algorithme avant mesure) · `-n auto` toujours
interdit · **2 workers par shard** · exclusion `test_v1_acceptance` inchangée ·
une seule `coverage.xml` combinée en aval · artefact de shard manquant =
**échec dur** · nom du check requis `pytest + QA scripts` · gating `docs/**`
inchangé · **aucun code produit touché**.

Partition à 3 : **244 fichiers → 82 / 81 / 81**. Le fichier de test neuf de ce
sprint y est entré **tout seul** — c'est la propriété du manifeste généré.

---

## 3. Plantations — deux ont révélé des trous réels

| # | Plantation | Résultat |
|---|---|---|
| 1 | retirer un shard de la matrice | **mord** |
| 2 | dupliquer un index de shard | **mord** (2 gardes) |
| 3 | recoder le compte de couverture en dur | **mord** |
| 4 | omettre un fichier de test | **passait au vert** → corrigé |
| 5 | restaurer `-n auto` | plantation **mal visée** → rejouée, mord |

### (4) La garde de partition était **circulaire**

`canonical_test_files()` est *défini* comme le répertoire `tests/` moins
`EXCLUDED`, et toutes mes assertions de partition comparaient les shards à cette
même fonction. Ajouter un fichier à `EXCLUDED` rétrécissait **les deux côtés à
la fois** : la partition restait « exacte », les 90 tests restaient verts, et le
fichier cessait silencieusement de tourner.

C'est **exactement** le mode d'échec que la docstring du sharder dit exister
pour rendre impossible — et rien ne le vérifiait.

Deux gardes ajoutées : `EXCLUDED` est épinglé **par valeur** (une décision
singulière et délibérée), et l'ensemble canonique est ancré sur le **système de
fichiers** plutôt que sur la définition du module.

### (5) Une plantation mal visée ne prouve rien

Ma première version remplaçait `-n "${CI_PYTEST_WORKERS}"` **dans le workflow**
— où cette chaîne n'existe pas : elle vit dans `scripts/run_ci_pytest.sh:51`. Le
fichier n'était pas modifié, donc « aucun test ne tombe » ne disait rien du tout.
Rejouée contre le script, la garde tombe.

> Note honnête : mes deux premières gardes anti-`-n auto` échouaient sur les
> **commentaires** qui expliquent pourquoi `-n auto` est proscrit. L'invariant
> porte sur ce qui est exécuté : les lignes de commentaire sont retirées avant
> le scan.

---

## 4. Preuves locales

| Preuve | Résultat |
|---|---|
| Tests de topologie + stabilité CI | **93** |
| Partition exacte à 1, 2, 3, 4, 5 et 8 shards | vérifiée |
| Budget ruff | 536 ≤ 548 |
| `check_spec_protocol` | OK |
| Full sweep local | *(voir closeout)* |

**La CI réelle est la preuve obligatoire de ce sprint** (`CLAUDE.md` §1 :
`ci_infra` ⇒ « valider IMPÉRATIVEMENT sur la CI réelle »). Les mesures de
capacité sont reportées au closeout — elles n'existent pas avant l'exécution.

---

## 5. Dépendance externe signalée

Le workflow lit `CI_PYTEST_WORKERS: ${{ vars.CI_PYTEST_WORKERS }}`, une
**variable de dépôt**. `run_ci_pytest.sh` retombe sur `2` si elle est absente,
donc la valeur versionnée gouverne par défaut — mais une modification de cette
variable dans les réglages GitHub changerait le nombre de workers **sans aucun
commit**. Hors périmètre de ce sprint ; consigné parce que c'est précisément le
genre de source unique externe que le brief refuse pour le nombre de shards.

## Verdict

Le passage à 3 shards est la partie facile. La partie utile est que le nombre
de shards a cessé d'exister en trois exemplaires non comparés — et que la
tentative de le faire diverger fait désormais tomber un test.

Au passage, la plantation a montré que la garde censée empêcher un fichier de
test de disparaître **se comparait à elle-même**. Elle regarde maintenant le
disque.

---

## Closeout (post-merge)

| | |
|---|---|
| PR | **#107** — `--merge --match-head-commit`, **sans** squash / `--admin` / force |
| Build | `bac2b8a` — **vert au premier passage**, aucun correctif |
| Merge | **`541900f`** |
| CI de validation (PR) | run **`31946573499`** — 6/6 |
| CI canonique | run **`31947072072`** — **6/6** |
| Gate Sonar | **`OK`** — 0 smell, 0 bug, 0 vulnérabilité |
| Threads / Gitar | **0 / 0** |
| Full sweep local | **4 481** |

### Acceptance de capacité — **CIBLE ATTEINTE**

Cible : `min MemAvailable >= 6 Go` sur **chaque** shard.

| Shard | Fichiers | Tests | min MemAvailable (PR) | min MemAvailable (canonique) | min SwapFree | Runtime |
|---|---|---|---|---|---|---|
| 1 | 82 | 1 532 | 6 261 Mo | **6 241 Mo** | 3 071 — intact | 7 min 22 |
| 2 | 81 | 1 474 | 8 274 Mo | **8 289 Mo** | 3 071 — intact | 5 min 28 |
| 3 | 81 | 1 475 | 8 528 Mo | **8 507 Mo** | 3 071 — intact | 5 min 42 |

Les deux exécutions concordent à ~20 Mo près : la mesure est stable, pas un
coup de chance d'ordonnancement.

### Avant / après

| | 2 shards | 3 shards |
|---|---|---|
| Pire shard | **3 701 Mo** (`WATCH`) | **6 241 Mo** (`HEALTHY`) |
| Swap | intact | intact |
| Runtime shard | 8 min 37 / 8 min 55 | 7 min 22 / 5 min 28 / 5 min 42 |
| Tests | 2 143 + 2 310 = 4 453 | 1 532 + 1 474 + 1 475 = **4 481** |
| Couverture combinée | 10 340 / 707 / **93,16 %** | 10 340 / 707 / **93,16 %** |
| Workers | 2 | 2 |

**Parité de couverture exacte**, aux trois nombres près. Le +28 de tests est
exactement le fichier de topologie ajouté par ce sprint.

L'agrégateur a journalisé `[coverage] expected 3 shard data files, found 3` :
la dérivation fonctionne en production, pas seulement dans un test.

### Déséquilibre constaté — **signalé, non corrigé**

Le shard 1 est un vrai point aberrant : **6 241 Mo contre 8 289 / 8 507**, soit
~2,2 Go d'écart, et **7 min 22 contre ~5 min 35** — pour **un seul fichier de
plus**. Le déséquilibre vient donc du **contenu** des fichiers, pas de leur
nombre : le round-robin alphabétique équilibre les fichiers, pas leur coût.

Le brief est explicite : tous les shards ≥ 6 Go ⇒ **arrêter**, et ne pas
implémenter de partition pondérée **préventivement**. Le constat est donc
**consigné comme évidence** pour une décision future, et rien n'est optimisé.

> Note honnête : ma première mesure d'acceptance a imprimé « 3 SHARDS SUFFICE »
> à partir de **zéro échantillon** — le run était encore en cours, les logs
> n'étaient pas téléchargeables, la boucle ne s'est jamais exécutée et le
> drapeau `ok` est resté vrai par défaut. Exactement le mode d'échec des gardes
> vacantes, cette fois dans mon propre outillage. Le script **sort en erreur**
> si le nombre d'échantillons est nul ou si le nombre de shards mesurés ne
> correspond pas à celui attendu.
