# Sb_OPS_DEPLOY_FAILURE_HONESTY_01 — un rapport d'échec qui ne ment pas sur la production

**Tier `check_scope`** : `CI_INFRA` — full sweep local + validation sur CI réelle impérative.
**Fichiers** : `.github/workflows/deploy-production.yml` · `tests/test_deploy_safety.py`

---

## 1. Le défaut, tel qu'il s'est produit

Le 2026-09-06 à 09:47, un dispatch de « Deploy production » a échoué. Le SHA passé
en entrée était **court** (`91fe01d`) là où l'entrée exige explicitement
40 caractères — `actions/checkout` n'a pas su le résoudre et l'étape de checkout
a échoué.

Les étapes suivantes — `Configure SSH`, le poussage, le smoke test — ont toutes
été **`skipped`**. Aucun octet n'a quitté le runner. La production n'a pas été
contactée.

Le rapport a pourtant annoncé, mot pour mot :

```
X SHA  — VPS left in partial state, investigate via SSH.
```

**Deux affirmations fausses dans une seule ligne.**

1. Il déclarait un **état partiel de la production**, qu'il n'avait aucun moyen
   de connaître : l'étape ne lit rien, elle se déclenche sur `failure()` et
   récite une phrase unique quelle que soit la cause.
2. Il imprimait un **SHA vide**, parce que `steps.sha` n'avait jamais tourné et
   que `steps.sha.outputs.full` rend une chaîne vide. D'où le `SHA  —` avec son
   double espace.

### Pourquoi ce n'est pas cosmétique

Un rapport d'échec est lu **au moment où la confiance est déjà entamée**. Celui-ci
prescrit une action — ouvrir une session SSH sur la production — pour enquêter sur
une panne qui n'existe pas. Dans le meilleur cas il fait perdre du temps ; dans le
pire, il pousse à « réparer » une machine saine pendant qu'on croit une livraison
à moitié posée.

C'est la onzième forme relevée dans ce dépôt d'une **garde qui ne garde rien** :
non pas une garde muette, mais une garde qui **parle sans savoir**. Elle produit
une alarme dont la véracité ne dépend pas de ce qu'elle observe.

---

## 2. Brainstorming / Options / Risques / Choix retenu

### Option A — retirer la phrase

Remplacer `« VPS left in partial state »` par un texte neutre : *« le déploiement
a échoué »*.

* ✅ Une ligne, zéro risque.
* ❌ **Supprime aussi l'information vraie.** Quand le poussage échoue réellement
  *en cours*, l'état partiel est le fait le plus important à dire. On échangerait
  un faux positif contre un faux négatif — et le faux négatif est pire : il tait
  un danger réel.
* ❌ Contraire à `CLAUDE.md §5.3` dans son esprit : une soustraction seule laisse
  le produit plus pauvre.

### Option B — lire l'issue des étapes et distinguer les cas *(retenu)*

Donner un `id` aux deux étapes SSH, puis brancher le message sur
`steps.push_to_vps.outcome` et `steps.smoke.outcome`.

* ✅ Chaque phrase devient **adossée à une observation**, jamais à une hypothèse.
* ✅ Le cas réellement dangereux — poussage réussi + smoke rouge — cesse d'être
  noyé dans la même phrase que les autres, et reçoit son propre `Rollback URGENT`.
* ✅ Le SHA vide est réparé au passage par un repli sur la réf demandée.
* ⚠ Ajoute de la logique shell dans un workflow — donc quelque chose qui peut
  diverger de sa propre prose. **Mitigé par les gardes du §4**, qui exécutent le
  script embarqué et non une copie.

### Option C — interroger le VPS pour connaître son état

Ajouter une étape qui SSH sur la machine et lit l'état réel du déploiement.

* ✅ La réponse la plus exacte possible.
* ❌ **Ouvre une connexion SSH sur la production dans le chemin d'échec**, c'est-à-dire
  au moment le moins sûr. Un échec de checkout n'a aucune raison de contacter la prod.
* ❌ Ne fonctionne pas quand l'échec est justement « SSH indisponible ».
* ❌ Coût et surface d'attaque sans rapport avec le bénéfice.

### Choix retenu — **B**

Elle est la seule qui **ajoute de la vérité sans ajouter d'accès**. Le workflow
possède déjà l'information (l'issue de chaque étape) ; il ne s'en servait pas.
C'est, une fois de plus, *le produit a la décision, pas le moyen de l'appliquer* —
sauf qu'ici le moyen était à portée d'une expression.

### Risques et leur traitement

| Risque | Traitement |
|---|---|
| La logique `case` diverge de la prose du workflow | 5 gardes exécutent **le bloc `run` extrait du YAML**, pas une copie |
| Une expression `${{ }}` glisse dans le bloc `run` et n'est jamais évaluée en test | Une assertion refuse tout `${{` dans le script extrait |
| Un `id` d'étape est renommé et le rapport redevient aveugle | `test_les_etapes_ssh_sont_identifiables_par_le_rapport` épingle les deux `id` |
| Le correctif passe sans jamais avoir vu le défaut | Le rapport d'origine a été **replanté en entier** : 5 gardes sur 5 rougissent |

---

## 3. Ce que le rapport dit désormais

| Issue de `push_to_vps` | Issue de `smoke` | Message |
|---|---|---|
| jamais atteinte / `skipped` | — | *le VPS n'a JAMAIS été contacté — la production est **INTACTE*** |
| `failure` | — | *le poussage a ÉCHOUÉ EN COURS — la production peut être à moitié posée* |
| `success` | `failure` | *le code **EST** déployé et le smoke a échoué* → **Rollback URGENT** |
| `success` | `success` | *l'échec est postérieur (marquage du tag)* → **aucun rollback requis** |

Et la cible affichée retombe sur la réf demandée quand le SHA n'a pas pu être
résolu ; à défaut de tout, elle dit `<aucune réf résolue>` plutôt qu'un blanc.

---

## 4. Vérifications

| Contrôle | Résultat |
|---|---|
| `check_scope` | `CI_INFRA` |
| `ruff` (fichiers touchés) | `All checks passed!` |
| `check_ruff_budget` | `267 ≤ 548` |
| `check_spec_protocol` | `OK` |
| `actionlint` | aucun signalement |
| `tests/test_deploy_safety.py` | 46 passés (41 avant, +5) |
| **Défaut d'origine replanté** | **5 gardes rougissent, fichier restauré à l'identique** |
| Full sweep local | `bash scripts/run_local_sweep.sh` |
| **CI réelle** | **impérative avant merge — le changement porte sur le pipeline** |

### Non-régressions

* Aucun chemin de succès n'est touché : `Tag successful deploy` est inchangé.
* Aucun secret, aucune permission, aucun déclencheur modifié — les gardes
  existantes `test_workflow_stays_dispatch_only_with_production_approval` et
  `test_workflow_ref_is_still_required` restent vertes.
* L'étape sort toujours en `exit 1` : un échec reste un échec.

### Ce que cette tranche ne fait PAS

* Elle **ne corrige pas** la cause du dispatch raté (un SHA court accepté par
  l'entrée puis rejeté par `checkout`). Le message le rappelle désormais
  — *« l'entrée « ref » attend un SHA COMPLET de 40 caractères »* — mais l'entrée
  ne valide toujours pas sa forme. C'est une tranche distincte, et elle demande
  une décision : rejeter au dispatch, ou continuer d'accepter un nom de branche
  comme le fait la description actuelle.
* Elle ne touche pas `actions/checkout@v4`, dont le runner signale la dépréciation
  Node 20. Une PR dependabot ouverte le couvre.

---

## Verdict

**LIVRÉ.** Le rapport d'échec du déploiement ne prononce plus aucune phrase sur
l'état de la production qu'il n'ait pas lue dans l'issue d'une étape.

Le défaut corrigé n'était pas une imprécision de rédaction : c'était une **alarme
dont la véracité ne dépendait pas de ce qu'elle observait**. Elle prescrivait
d'ouvrir une session SSH sur la production pour enquêter sur une panne inexistante,
au moment précis où on la lit de la manière la moins critique.

Cinq gardes tiennent désormais la distinction, et elles ont vu le défaut d'origine
rougir avant d'être livrées.

Reste ouvert, et nommé : **l'entrée `ref` accepte toujours un SHA court sans le
valider** — la cause du dispatch raté. La corriger demande de trancher si un nom de
branche reste accepté, comme la description de l'entrée le promet aujourd'hui.
C'est une décision, pas un oubli.

---

## Appendice de clôture — post-merge

| | |
|---|---|
| **PR** | [#218](https://github.com/MFE-DSS/workout-session-tracking/pull/218) |
| **Méthode** | `--merge`, `--match-head-commit a3254ca` — pas de squash, pas de `--admin`, pas de force |
| **Commit de merge** | `793be86` |
| **CI de PR** | 7/7 verts (3 shards · QA · lint · attestation · Gitar) |
| **Gate Sonar** | `OK` — 0 bug, 0 code smell, 0 vulnérabilité sur le code neuf |
| **Fils de revue non résolus** | 0 |
| **CI canonique** | [`run 34029186636`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/34029186636) sur `793be86` — **success** |
| **Full sweep local** (exigé par le tier `CI_INFRA`) | **81 lots verts · 324/324 fichiers · pic 2309 Mo sur un budget de 2619** |

### Un incident de parcours, pour mémoire

La PR a d'abord rougi sur `spec protocol check` : la section **Verdict** manquait au
rapport. Cause exacte — j'avais lancé `check_spec_protocol.py` **avant** d'écrire le
rapport, donc sur un dépôt qui n'avait pas encore le fichier. Le contrôle passait sur
une absence.

*Leçon d'ordonnancement : les contrôles se lancent après que TOUS les fichiers de la
tranche sont écrits, jamais entre deux.* Corrigé par `a3254ca`.

### Ce qui reste ouvert

L'entrée `ref` du workflow accepte toujours un **SHA court** sans le valider — c'est
la cause du dispatch raté qui a révélé ce défaut. Le message d'échec le rappelle
désormais, mais la validation au dispatch demande de trancher si un **nom de branche**
reste accepté, comme la description de l'entrée le promet aujourd'hui.

**Branche `sb/deploy-failure-honesty` et worktree `-dep` : NON supprimés.**
`CLAUDE.md §2` réserve la suppression de branche/worktree à une action humaine.
