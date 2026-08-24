# `Sb_OPS_LOCAL_SWEEP_MEMORY_01` — le garde-fou qui faisait tomber la machine

**Branche** : `sb/ops-local-sweep-memory-01` · **base** : `b22098d`
**Tier `check_scope`** : `CI_INFRA` — validation CI réelle impérative
**Origine** : constat opérateur, 2026-08-24

---

## 0. Le défaut

`bash scripts/run_ci_pytest.sh`, prescrit par `CLAUDE.md §1` comme **la**
commande de full sweep « CI comme local », a fait tomber la machine de
l'opérateur **à répétition** : VS Code tué, sweep jamais terminé.

Le coût n'est pas seulement le sweep perdu. Un garde-fou qui n'aboutit jamais
ne rend **aucune information**, et il emporte le travail en cours à côté. Trois
fois dans cette session seule, un sweep local a dû être abandonné.

## 1. La cause, mesurée

Le script plafonne déjà les workers sur la RAM, à ~5 Go par worker. Sur une
machine de 16 Go cela autorise 2 workers — et c'est exactement ce qui sature.

**La formule était juste ; son hypothèse était fausse.** Elle raisonne sur la
RAM **installée**, en supposant la machine dédiée au sweep.

| Mesuré le 2026-08-24 | |
|---|---|
| RAM installée | **16 Go** → 2 workers autorisés |
| RAM **disponible** | **5 365 Mo** |
| occupant le reste | éditeur, serveurs de langage, navigateur |

S'y ajoute une croissance **monotone** : un interpréteur qui enchaîne 5 200
tests cumule graphe applicatif importé, métadonnées SQLAlchemy, fixtures et
traceur de couverture. Le pic n'est pas le coût d'un test, c'est le cumul de
tous.

Deux interpréteurs faisant cela en parallèle, sur 5,3 Go réellement libres,
n'ont pas d'issue.

---

## 2. Ce qui est livré

### `scripts/run_local_sweep.sh` — le sweep local, borné par construction

| Décision | Pourquoi |
|---|---|
| **Lots de fichiers, un processus neuf par lot** | le pic redevient celui d'UN lot ; la RSS repart de zéro entre les lots |
| **Pas de couverture par défaut** | `--cov` change le profil mémoire et la durée ; la couverture sert à Sonar, donc à la CI. `--with-coverage` la réactive |
| **Chien de garde mémoire** | la RSS de l'arbre pytest est échantillonnée ; au-delà du budget le sweep **s'arrête lui-même** plutôt que de laisser l'OS choisir quel programme tuer |
| **Budget lu sur la mémoire DISPONIBLE** | c'est toute l'erreur du plafond précédent |
| **Moitié du disponible, plafonnée à 4 Go** | laisser de la marge à l'éditeur n'est pas une politesse : c'est ce qui évite que l'OS arbitre |

### Mesures

Premier essai, lots de **12** fichiers :

```
pics par lot : 724 … 2 896 Mo
lot 20 → ARRÊT du chien de garde (2 896 Mo > 2 842 Mo de budget)
```

Le chien de garde a fonctionné — mais un défaut par lot n'est pas une façon de
travailler. Le coût dépend des **fichiers** autant que de leur nombre : certains
montent un client HTTP et une base par test.

Défaut ramené à **6** fichiers :

```
276 fichiers · 46 lots · budget 2 290 Mo
pics observés : 131 · 146 · 280 · 302 · … · 1 524 · 1 793 Mo
aucun déclenchement du chien de garde
```

**Pic divisé par ~1,6, et la marge n'est plus nulle mais constante.**

### `scripts/run_ci_pytest.sh` — refus mécanique hors CI

```
$ bash scripts/run_ci_pytest.sh
[ci-pytest] REFUS : hors CI, ce script sature un poste de developpement.
[ci-pytest] Sur un poste :  bash scripts/run_local_sweep.sh
[ci-pytest] Diagnostic delibere : ALLOW_LOCAL_CI_SWEEP=1 bash scripts/run_ci_pytest.sh
```

**Le refus est mécanique parce que la prose a déjà échoué.** La version
précédente de ce fichier expliquait longuement le risque, en commentaire ET
dans `CLAUDE.md` — et le script a quand même été lancé en local, plusieurs
fois, par l'agent, dans cette session. Une règle qu'on peut enfreindre sans
rien casser n'est pas une règle.

`ALLOW_LOCAL_CI_SWEEP=1` laisse le diagnostic délibéré possible : **nommé**,
donc jamais accidentel.

Le chemin CI est **intact** — vérifié : avec `CI=true`, le script produit les
mêmes drapeaux canoniques qu'avant.

### `CLAUDE.md §1` — la règle change dans le contrat versionné

La clause prescrivait « UNE SEULE » commande, « CI comme local, même source de
vérité ». C'est cette ligne qui a été exécutée. Elle en prescrit désormais
**deux, une par contexte**, avec la mesure qui l'a produite.

---

## 3. Gardes

**12 gardes neuves**, toutes sur le COMPORTEMENT et non sur un commentaire.

| Garde | Ce qu'elle empêche |
|---|---|
| `test_the_ci_script_refuses_to_run_outside_ci` | le retour du script qui tue la machine — et le refus doit **nommer** l'alternative |
| `test_the_local_sweep_refuses_to_run_on_ci` | la réciproque : deux chemins qui prétendent être « le sweep » |
| `test_the_budget_reads_available_memory_not_installed` | interdit `hw.memsize` : c'est l'erreur d'origine |
| `test_the_batch_default_carries_its_measurement` | le chiffre 6 doit voyager avec le pic de 2 896 Mo qui l'a produit |
| `test_the_watchdog_names_the_files_of_the_offending_batch` | « réduire SWEEP_BATCH » sans dire lesquels laisse chercher à l'aveugle |
| `test_coverage_is_off_by_default_locally` | le retour du profil mémoire de la CI en local |
| `test_the_repo_contract_points_at_the_local_script` | la clause `CLAUDE.md` ne peut plus rediverger |
| `test_the_local_script_passes_shellcheck` | le script neuf entre dans le même gate que les autres |

### Deux gardes existantes réparées, dont une qui passait pour la mauvaise raison

`test_a_non_numeric_worker_count_is_refused` assertait `"REFUS" in stderr`. Mon
nouveau refus local dit **aussi** « REFUS » : la garde aurait continué à passer
sans jamais éprouver le refus qu'elle vise. Elle asserte désormais le message
propre à la valeur non entière, et pose `ALLOW_LOCAL_CI_SWEEP` pour atteindre
le code qu'elle teste.

`test_the_local_worker_count_is_capped_by_physical_ram` idem : elle retirait
`CI` de l'environnement et n'atteignait plus le plafond qu'elle éprouve.

---

## 4. Vérifications

| Contrôle | Résultat |
|---|---|
| `check_scope` | `CI_INFRA` |
| `bash -n` + `shellcheck` sur le script neuf | propre |
| `check_ruff_budget` | 281 ≤ 548 |
| `check_spec_protocol` | PASS |
| `test_ci_runner_stability.py` | 75 → **87 passed** |
| Chemin CI inchangé | vérifié avec `CI=true` : mêmes drapeaux canoniques |
| **Sweep local par lots** | 46 lots, pics 131–1 793 Mo, aucun déclenchement |

⚠ **Une réserve honnête.** Le sweep par lots ci-dessus a démarré **avant** la
réparation des deux gardes existantes : son lot 11 a donc échoué sur une
version périmée du fichier. Relancé isolément après correction : **87/87**.
La CI réelle porte la vérification finale, comme l'exige le tier `CI_INFRA`.

---

## 5. Non-régressions

- **0 gate retiré** — aucun drapeau canonique changé, aucun step de workflow
  touché.
- **Le chemin CI est identique**, conditionné sur `CI` comme avant.
- **0 test affaibli** : 2 réparés pour atteindre le code qu'ils visent,
  12 ajoutés.
- Le refus reste **contournable délibérément**, jamais par distraction.

---

## 6. Ce que ce sprint ne prétend pas

Il ne rend pas le sweep local **rapide** : 46 lots séquentiels prennent plus
longtemps qu'un run parallèle. Il le rend **terminable**, ce qui n'était plus
le cas. Un sweep qui aboutit en trente minutes vaut infiniment mieux qu'un
sweep qui tue l'éditeur au bout de vingt.
