# `Sb_OPS_CI_LINT_TIMEOUT_01` — le budget n'était pas le problème

**Tier `ci_infra`.** Hors queue UI. Quatre annulations du job lint, dont une
sur la CI canonique.

> **J'ai porté un diagnostic faux pendant quatre occurrences.**
> Je l'ai écrit « cache froid » dans trois rapports de sprint et un closeout.
> La mesure l'a réfuté en une commande.

---

## 1. Brainstorming / Options / Risques / Choix retenu (`CLAUDE.md §3`)

| Option | Ce qu'elle donne | Risque | Retenue |
|---|---|---|---|
| **A** — `timeout-minutes: 5 → 10` | le job survit à l'incident | **traite un symptôme mal diagnostiqué** ; un step qui pend prendrait juste deux fois plus de temps à le prouver | **non** |
| **B** — mesurer la distribution, puis en déduire un budget | budget défendable | ne dit rien si la cause n'est pas la durée | partiellement — la mesure était nécessaire, la conclusion est ailleurs |
| **C** — supprimer la dépendance réseau du job | supprime la cause | exige de prouver que l'outil reste disponible | **OUI** |

**Choix : C, arrivé par B.** La distribution devait être mesurée pour choisir un
budget ; c'est elle qui a montré qu'aucun budget n'était en cause.

---

## 2. La mesure qui a réfuté mon diagnostic

40 exécutions du job lint relevées sur l'API GitHub.

| | |
|---|---:|
| succès | **39** |
| minimum | 36 s |
| **médiane** | **51 s** |
| p90 | 77 s |
| maximum | 109 s |
| annulations | **1** — à **319 s**, soit le plafond |

**Toutes les exécutions réussies tournent 21 steps. L'annulation en a exécuté
15.** Un job annulé n'est pas un job permissif : il est **muet**.

### Le détail qui tranche

Sur l'annulation (`run 32226738467`) :

| Steps | Durée |
|---|---:|
| 1 à 9 — dont `Install linters` | **22 s au total** (`Install linters` : **6 s**) |
| **10 — `shellcheck`** | **290 s, jamais terminé** |
| 11 à 15 — `pip-audit`, `gitleaks`, `spec protocol`, `auth scope`, drift | **sautés** |

`Install linters` prend 6 s dans l'annulation, contre 4 à 11 s dans les 39
autres. **Le cache n'était pas froid.** Ce sont les neuf premiers steps qui
prennent 22 s, exactement comme d'habitude, puis un seul step qui pend.

---

## 3. La cause

```yaml
- name: shellcheck (required — Sb_26.1)
  run: |
    sudo apt-get update -qq        # ← interroge un miroir Ubuntu
    sudo apt-get install -y shellcheck
    shellcheck -S warning $(find scripts …)
```

`sudo apt-get update` contacte un miroir Ubuntu **au moment du job**. C'était
la **seule dépendance réseau du job lint**, dans un step dont le travail réel
dure une seconde. Un miroir lent bloque, et le job meurt au plafond en
emportant les six steps suivants.

**Augmenter `timeout-minutes` aurait fait durer le blocage plus longtemps.**

---

## 4. La correction

Les deux lignes `apt-get` sont **retirées**. `shellcheck` est **préinstallé sur
l'image du runner** — `shellcheck 0.9.0-1`, section « Installed apt packages »
de `Ubuntu2404-Readme.md` (`actions/runner-images`, vérifié le 2026-08-20).

**Aucun gate n'est affaibli** : la même commande s'exécute sur les mêmes
fichiers. Deux ajouts :

- **`shellcheck --version`** — un outil préinstallé peut changer de version
  avec l'image. Le journaliser rend le changement lisible dans le log plutôt
  que dans un écart de résultat inexpliqué.
- **`timeout-minutes: 1` au niveau du STEP** — ceinture. Un step d'une seconde
  qui dépasse la minute pend à nouveau, et l'échec doit **nommer le step** au
  lieu de consommer le budget du job.

**`timeout-minutes: 5` du job est conservé.** Avec un p90 à 77 s et un maximum
à 109 s, il n'a jamais été en cause. Le changer aurait été remplacer un chiffre
arbitraire par un autre.

**Si une image future cessait de fournir l'outil**, le step échoue sur
`command not found` — un échec **nommé**, pas une annulation muette.

---

## 5. Gardes

**6 gardes neuves**, `TestLintJobHasNoNetworkDependency`. **4 plantations**,
chacune exigée rouge :

| Défaut replanté | Garde | Verdict |
|---|---|---|
| `apt-get` réintroduit dans le job | `..._installs_nothing_over_the_network` | rougit |
| la vérification elle-même retirée | `..._shellcheck_still_runs_on_the_same_files` | rougit |
| le garde-fou de step supprimé | `..._step_carries_its_own_timeout` | rougit |
| un gate **renommé** pour le neutraliser | `..._removed_or_renamed` | rougit |

### La garde faible que la plantation a démasquée

La première version vérifiait qu'un mot-clé apparaissait dans le job. La
plantation a renommé `gitleaks scan (required — Sb_26.4)` en
`gitleaks scan DISABLED (required — Sb_26.4)` : **la garde est restée verte**.
Neutraliser un gate en le renommant est exactement le geste à attraper — les
gardes vérifient désormais le **début de déclaration exact** de chaque step.

### Et une garde qui a lu sa propre prose, pour la troisième fois

Le workflow **explique** pourquoi `apt-get` a été retiré, donc la chaîne
apparaît dans sa propre justification. La garde rougissait sur l'explication du
correctif. Corrigé par un dépouillement des commentaires YAML.

---

## 6. Vérification

`check_scope` **CI_INFRA** → ruff propre · budget **281 ≤ 548** · spec protocol
OK · full sweep local.

**Validation sur CI réelle obligatoire** (`CLAUDE.md §1`) : un changement de
pipeline doit prouver son effet sur une CI réelle, jamais seulement en local.
La PR est la preuve.

---

## 7. Une erreur de procédure, attrapée par la CI

Le premier push est parti rouge sur `check_spec_protocol` — ce rapport n'avait
pas de section verdict — **et sur `test_spec_protocol`, qui exécute le même
contrôle**. Une seule cause pour deux échecs.

**La cause racine n'est pas l'oubli, c'est l'ordre.** J'ai lancé le contrôle
requis **et** le sweep complet, puis j'ai écrit ce rapport. Les deux étaient
verts sur un arbre qui n'existait plus au moment du commit.

> Une vérification requise se lance **juste avant le commit**, sur l'arbre
> qu'on committe. La cocher tôt puis continuer à écrire, c'est vérifier autre
> chose que ce qu'on livre.

C'est exactement le motif que ce dépôt combat ailleurs — une preuve verte qui
ne porte pas sur l'objet qu'elle prétend couvrir.

---

## Verdict

**`Sb_OPS_CI_LINT_TIMEOUT_01` — cause corrigée, symptôme non traité, et c'est
délibéré.**

Le job lint ne dépend plus d'aucun miroir réseau. `timeout-minutes: 5` du job
est **conservé** : la distribution mesurée — médiane 51 s, p90 77 s, max 109 s
sur 39 exécutions — dit qu'il n'a jamais été en cause. Aucun gate retiré,
aucun step rendu advisory, aucun cache désactivé.

La validation fait autorité **sur la CI réelle**, pas en local
(`CLAUDE.md §1`, tier `ci_infra`).

---

## 9. Ce que la tranche ne fait pas

- **Ne touche à aucun autre job.** `pytest` (45 min), les shards (20 min) et
  l'agrégateur (10 min) sont inchangés.
- **Ne retire aucun gate**, ne rend aucun step advisory, ne désactive aucun
  cache.
- **Ne change pas `timeout-minutes` du job**, parce que la mesure dit qu'il
  n'est pas en cause.
