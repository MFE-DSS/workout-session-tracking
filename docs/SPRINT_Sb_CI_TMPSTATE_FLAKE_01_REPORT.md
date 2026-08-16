# SPRINT Sb_CI_TMPSTATE_FLAKE_01 — supprimer la course, pas le symptôme (RAPPORT)

**Train :** `AUREN_RELEASE_READINESS_01`, tranche 2/3 ·
**Base canonique :** `3b20ae4` · **Branche :** `sb/ci-tmpstate-flake-01`

---

## 1. Le mécanisme, prouvé avant toute correction

Le test `TestFixtureTempCleanup::test_a_failing_test_still_cleans_up` a fait
rougir la CI sur `AUREN_EFFECTIVE_VOLUME_COMPLETION_01` (`assert 3 <= 2`), sans
rapport avec la tranche en cours.

`_tmp_dir_count()` lisait **`tempfile.gettempdir()`** — le répertoire temporaire
**partagé par toute la machine** :

```
racine partagée : /var/folders/hf/…/T
répertoires workout-test-* déjà présents : 53 945
```

Ces 53 945 répertoires sont les vestiges de la fuite historique corrigée par
`Sb_OPS_CI_RUNNER_STABILITY_01`. Le test comptait donc ~54 000 entrées dont
**aucune ne lui appartenait**, avant puis après un pytest imbriqué.

**Course reproduite déterministement**, sans attendre le hasard :

```python
before = count()                                   # 53 945
tempfile.mkdtemp(prefix="workout-test-")           # « un autre worker xdist »
after  = count()                                   # 53 946
assert after <= before                             # False
```

Il suffit qu'un worker voisin crée son répertoire entre les deux relevés. Le
test échantillonnait un **état global**, sous exécution parallèle.

**Aucun défaut produit** n'a été trouvé : le fixture `client` nettoie
correctement, y compris sur le chemin d'échec. Le défaut est entièrement dans
la mesure.

---

## 2. Le correctif — porter la mesure sur ce que le test possède

Le sous-processus reçoit `TMPDIR` pointant sur une racine dérivée de
`tmp_path`, que pytest alloue **par test et par worker**.
`tempfile.mkdtemp` du fixture `client` honore `TMPDIR`, donc les répertoires
observés sont exactement ceux que ce test a provoqués.

```
avant : glob(tempfile.gettempdir() / "workout-test-*")   ← 54 000 entrées étrangères
après : glob(tmp_path / "owned-tmp" / "workout-test-*")  ← uniquement les siennes
```

**Isolation prouvée** : une création étrangère dans la racine partagée reste
invisible depuis une racine possédée (test dédié qui rejoue la course exacte).

**L'invariant est devenu déterministe.** Rien n'a été masqué : ni suppression de
xdist, ni sérialisation, ni `sleep`, ni retry, ni `flaky`, ni `xfail`, ni
affaiblissement d'assertion. Un test structurel interdit ces six contournements.

### Deux défauts adjacents corrigés au passage

**(a) Une assertion vacante.**
`test_the_directory_exists_while_the_fixture_is_in_use` vérifiait qu'il existe
« au moins un » `workout-test-*` dans la racine partagée. Avec 53 945
répertoires hérités, **elle passait même si le fixture n'avait rien créé**. Elle
interroge désormais le chemin exact publié par le fixture via `DATABASE_URL`.

**(b) Un nom de fichier instable entre processus.**
Le fichier de test imbriqué était nommé d'après `abs(hash(body))`. `hash()` d'une
chaîne est **randomisé par processus** : deux workers ne calculaient pas le même
nom, et rien ne garantissait l'unicité. Remplacé par un digest `sha256` stable,
dérivé du corps **et** de la racine possédée.

---

## 3. Preuves

| Preuve | Résultat |
|---|---|
| Course reproduite avant correction | `after > before` déterministe |
| Racine partagée invisible depuis une racine possédée | vérifié |
| Exécutions répétées sous `-n 4 --dist worksteal` | **3/3 vertes**, 60 tests |
| Nettoyage normal | inchangé |
| Nettoyage sur chemin d'échec | inchangé |
| Sharding canonique | **non modifié** |
| Couverture | inchangée |

**Plantation** : reconnecter la mesure à `gettempdir()` fait tomber **2 tests** —
la garde structurelle *et* la garde comportementale qui rejoue la course.

> Note honnête : ma première version de la garde structurelle scannait tout le
> fichier à la recherche des mots interdits — et tombait sur **sa propre liste**.
> Le corps du test est désormais exclu du scan, comme le font déjà les tests
> voisins pour les docstrings.

---

## 4. Périmètre

**Aucun code produit modifié.** Le sprint est de l'hygiène de test : un seul
fichier de tests touché, aucune modification de l'architecture CI, du manifeste
de shards ni du script canonique.

## Verdict

La course n'est plus masquée, elle **n'existe plus** : la mesure ne peut
physiquement pas observer l'état temporaire d'un autre worker.

Le sprint a aussi révélé que le même défaut de conception — échantillonner un
état global — rendait une assertion voisine **complètement vacante** depuis
l'origine. Elle passait grâce à 53 945 répertoires qui n'avaient rien à voir
avec elle.

---

## Closeout (post-merge)

| | |
|---|---|
| PR | **#102** — `--merge --match-head-commit`, **sans** squash / `--admin` / force |
| Build | `96a2b47` — **vert au premier passage**, aucun correctif |
| Merge | **`5547601`** |
| CI canonique | run `31931126902` — **succès, 3/3 jobs** |
| Gate Sonar | **`OK`** — 0 smell, 0 bug, 0 vulnérabilité (4 conditions à 0) |
| Threads / Gitar | **0 / 0** |
| Périmètre | 1 fichier de tests + 3 docs — **aucun code produit** |

### Capacité CI — **HEALTHY**

| | Shard A | Shard B |
|---|---|---|
| min MemAvailable | **5 195 Mo** | **5 065 Mo** |
| min SwapFree | 3 071 Mo — **jamais entamé** | 3 071 Mo — **jamais entamé** |
| `workers=` | 2 | 2 |

Sixième tranche consécutive au-dessus de 5 Go sur les deux shards. `workers=2`
vérifié dans les deux logs : le manifeste de shards n'a pas été contourné.

**Télémétrie de la fuite** : `tmp_dirs` culmine à **9** (shard A) et **10**
(shard B) sur 79 relevés — à comparer aux 53 945 répertoires hérités de la
racine partagée. Le nettoyage du fixture fonctionne ; la correction de ce sprint
portait bien sur la **mesure**, pas sur un défaut de nettoyage.
