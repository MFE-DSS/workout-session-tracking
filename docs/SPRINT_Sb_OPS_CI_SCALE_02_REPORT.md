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
