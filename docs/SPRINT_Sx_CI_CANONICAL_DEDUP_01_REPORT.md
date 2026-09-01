# `Sx_CI_CANONICAL_DEDUP_01` — ne pas recalculer le même verdict

`OPERATOR_DECISION` — audit `Sx_CI_INTELLIGENT_IMPACT_01` accepté, arbitrages
`C1`–`C5` rendus · branche `sb/ci-canonical-dedup-01` · base `5fbdd8f`

**Livré en SHADOW MODE.** Rien n'est court-circuité tant que l'opérateur n'a pas
armé la variable. C'est la Phase 5 de l'ordre, et c'est le défaut du mécanisme.

---

## 1. Ce que l'audit a établi, et ce que cette tranche en fait

Mesuré sur 60 runs (2026-08-23 → 08-31), au job et au step :

| | |
|---|---|
| Run canonique après merge | **490 runner-minutes — 39 % du total** |
| Merges dont l'arbre est identique à la tête de PR | **19 / 20** |
| Part du runner-time qui est du pytest | **90 %** |
| Ce que viserait une architecture impact-aware (classifier, QA, scans) | **18 secondes** |

Une exécution sur un arbre identique ne peut pas, **par construction**, produire
une information susceptible de changer le verdict. C'est le seul poste dont
l'ordre de grandeur justifie une tranche.

---

## 2. Phase 0 — la protection de branche, et pourquoi elle ne prouve rien

Lue mécaniquement le 2026-09-01 :

```
required_status_checks
    strict: false          ← « require branch up to date » DÉSACTIVÉ
    contexts: ["pytest + QA scripts", "SonarCloud"]
enforce_admins:        false   ← un admin peut passer outre
required_pull_request_reviews: absent
allow_force_pushes:    false
allow_deletions:       false
restrictions:          absentes ← le push direct est POSSIBLE
```

**`strict: false` est le fait décisif.** La propriété recherchée — *« au moment
du merge, le merge candidate testé contient bien la dernière base canonique »* —
**n'est pas garantie par la plateforme**. Le taux de 19/20 est une conséquence
de l'usage séquentiel, pas un invariant appliqué.

L'ordre interdisait explicitement de l'inférer de l'historique. Conséquence
directe sur le design : **la vérification d'arbre ne peut jamais être sautée,
elle EST le garde-fou.**

### Une alternative écartée, chiffrée

Activer `strict: true` imposerait l'invariant — mais chaque PR devrait être
remise à jour avant merge, ce qui **relance la CI à chaque mise à jour**. Le
coût augmenterait au lieu de baisser.

---

## 3. Phase 1 — ce qui diffère malgré un arbre identique

| Différence | Classe | Conséquence |
|---|---|---|
| **SonarCloud** : analyse *de PR* vs analyse *de branche* | **ANALYSIS_ONLY** | **Sonar continue de tourner sur push** — c'est lui qui met à jour le gate projet et la référence de code neuf |
| `BASE_SHA` / `HEAD_SHA` du classifier | ANALYSIS_ONLY | ensembles de fichiers équivalents |
| `concurrency.group` | NONE | — |
| `paths-ignore` sur push seulement | NONE | — |
| secrets · permissions · `vars.*` | NONE | identiques hors PR de fork |

**Et le résultat qui porte tout le reste** : aucun test n'exécute git contre
l'état du dépôt. Les occurrences de `git` dans `tests/` sont des assertions
**textuelles** sur le source de `deploy_prod.sh`. Le verdict pytest est donc
**une fonction pure de l'arbre**.

---

## 4. Phase 2 — la preuve, et l'obstacle qu'elle a dû contourner

`refs/pull/N/merge` **est supprimé après merge** — vérifié, `git fetch` échoue.
L'API ne conserve pas non plus la base du run : `pull_requests` revient vide.
**On ne peut donc pas récupérer a posteriori l'arbre que la PR a testé.**

La propriété s'établit alors par démonstration plutôt que par relevé :

> Soit `M` le commit de merge, de parents `(B, H)`.
> La CI de PR a testé `merge(B′, H)`, où `B′` est la tête canonique **au moment
> du run** — donc un ancêtre de `B`, la canonique n'avançant que dans un sens.
>
> Si `tree(M) == tree(H)`, fusionner `B` dans `H` n'a rien apporté : `B` est la
> base de branchement. `B′ ≤ B` est donc lui aussi un ancêtre de `H`, et
> fusionner un ancêtre dans `H` ne change rien.
>
> **⇒ l'arbre testé valait `tree(H)` = `tree(M)`, quelle que soit `B′`.**

Appliquée aux 20 derniers merges par le script lui-même :

```
REUSE 19   FULL 1     ← 5499c34 (PR #159), rattrapé par « l'arbre diffère »
```

**Vingt-et-unième cas, observé pendant la tranche** : le merge de `DF-F`
(`9094d72`) a un arbre identique à la tête de PR #178. Le run canonique
correspondant a consommé ~27 runner-minutes pour rejouer un contenu déjà
validé — la donnée n'a demandé aucun run supplémentaire.

---

## 5. Phase 3 — architecture

```
push canonique
   │
   ├─ canonical-attestation        stdlib seule · ≤ 5 min · contents+actions: read
   │      │
   │      ├─ skip_shards=true ──► shards NON programmés
   │      │                        lint · QA · migrations · perf : INCHANGÉS
   │      │                        Sonar : INCHANGÉ, couverture importée
   │      │                                du run de PR attesté
   │      │
   │      └─ sinon ─────────────► pipeline actuel, à l'identique
   │
PR │ ────────────────────────────► attestation ignorée, shards toujours
                                    programmés (`always()`)
```

**Seuls les shards pytest sont évités.** Le reste tourne à l'identique — 44 s
au total, une assurance à prix presque nul.

### Pourquoi Sonar n'est pas touché, et reçoit une vraie couverture

L'analyse sur `push` est une analyse **de branche**, distincte de l'analyse de
PR. La sauter aurait échangé du calcul contre une **dégradation de signal**, ce
que l'ordre interdit. Elle reçoit donc la couverture **du run attesté** — même
contenu, donc même couverture, donc entrée rigoureusement identique.

---

## 6. Phase 5 — le shadow mode est le défaut, pas une option

`skip_shards` exige **deux** conditions : un verdict `REUSE` **et** la variable
`CI_CANONICAL_REUSE_ENABLED = true`. Absente, le mécanisme **prédit et
journalise** pendant que la suite complète continue de tourner.

```
[attestation] WOULD_REUSE — arbre identique à la tête 56e12032, run 33274036652
[attestation] SHADOW MODE — CI_CANONICAL_REUSE_ENABLED n'est pas à `true`.
[attestation] La suite complète tourne quand même. Ce verdict est une
              PRÉDICTION, à comparer au résultat réel.
```

Le workflow consomme `skip_shards`, **jamais** `would_reuse` — une garde
l'interdit explicitement. Armer est une décision d'opérateur, réversible en une
variable, sans toucher au code.

---

## 7. Phase 4 — les huit cas, plantés

**43 gardes · 16 défauts plantés · 16 rouges.**

| Cas | Situation | Verdict |
|---|---|---|
| **A** | arbre identique + run vert | **REUSE** (si armé) |
| **B** | base déplacée avant merge — *famille de la PR #159* | FULL |
| **C** | aucun run CI de PR | FULL |
| **D** | run annulé | FULL |
| **E** | run rouge | FULL |
| **F** | le workflow ou le mécanisme de sélection a changé | FULL |
| **G** | push direct sur la canonique | FULL |
| **H** | provenance indéterminable, API muette, exception | FULL |

Le cas **B** est reproduit sur un **vrai dépôt git avec un vrai merge à deux
parents**, la canonique avançant avant la fusion.

### Le piège le plus dangereux, câblé et gardé

Un job qui dépend d'un job **ignoré** est ignoré à son tour. Sur une PR,
`canonical-attestation` est ignoré (`if: push`). **Sans `always()` sur les
shards, plus aucune PR n'aurait été testée — avec une CI verte.** Une garde
dédiée l'épingle, et la planter la fait rougir.

---

## 7bis. Le défaut que seule la CI réelle pouvait montrer

La première version portait `if: github.event_name == 'push'` **sur le job**
d'attestation. Il était donc **ignoré** sur une PR — ce qui semblait correct, et
que ni le YAML ni le sweep local ne pouvaient contredire.

Mesuré sur la CI réelle, run **33534376497** :

```
canonical attestation: skipped
SonarCloud:            skipped   ← CONTRÔLE REQUIS par la protection de branche
```

**Un état « ignoré » se propage dans le graphe.** `SonarCloud` dépend de `test`,
qui dépend désormais de l'attestation ; le contrôle requis a cessé de rendre un
verdict. C'est exactement ce que le critère `A7` de l'ordre interdit — et ce que
la mission avait nommé d'avance : *« aucun required check ne doit rester
Expected/Pending parce qu'un workflow a été filtré avant de démarrer. »*

### La correction, et pourquoi celle-là

Rescaper `sonar` avec `always()` aurait **masqué la cause**. Elle est supprimée :

* **le job ne porte plus aucune condition** — il tourne sur tous les événements ;
* **le filtre vit dans le script**, qui répond `FULL` hors `push`.

Le graphe ne contient donc plus **aucun job ignorable**, et la classe entière de
problème disparaît. Coût mesuré : ≈ 10 s par run de PR.

Deux gardes l'épinglent, et les planter les fait rougir : l'une interdit toute
condition sur le job, l'autre vérifie que l'événement est bien transmis au
script.

**Ce défaut n'était visible ni en local, ni dans le YAML, ni dans les 43 gardes
qui existaient alors.** Seule la CI réelle pouvait le montrer — c'est
littéralement la raison pour laquelle `CLAUDE.md §1` impose une validation sur
CI réelle au tier `ci_infra`.

---

## 8. Fautes de l'agent — trois vagues de gardes creuses, puis un défaut réel

C'est le cœur de ce que cette tranche laisse au dépôt.

**Première vague.** Deux mutations sont passées : désarmer la comparaison
d'arbres, et faire renvoyer `REUSE` par l'attrape-tout. Mes gardes
**n'atteignaient jamais ces lignes** — elles échouaient plus tôt, sur l'absence
de jeton ou de merge. Correction : un **vrai dépôt git** avec un vrai merge à
deux parents et une API simulée.

**Deuxième vague.** Deux autres sont passées **pour la mauvaise raison** :
retirer le rejet d'un run rouge laissait le verdict correct, parce qu'un rejet
*ultérieur* rattrapait derrière. Le verdict était bon, la propriété n'était pas
gardée. Correction : épingler la **raison**, pas seulement le verdict.

**Troisième vague.** Un cas manquait purement — un run **encore en cours**.
Désarmer sa vérification laissait les 32 gardes vertes, parce qu'aucune ne
construisait cet état.

> **Une garde n'existe que pour l'état qu'elle fabrique.**

C'est le même enseignement que `DF-C` et `DF-E`, sous un troisième angle. Il ne
s'apprend apparemment qu'en plantant, à chaque fois.

---

## 9. Vérifications

| | |
|---|---|
| `check_scope.py` | **`CI_INFRA`** — full sweep local obligatoire, **validation sur CI réelle impérative** |
| `tests/test_ci_canonical_attestation.py` | **43 gardes** · 16 défauts plantés, 16 rouges |
| Familles de gardes CI existantes | **253 passés** |
| **Full sweep local** | **292/292 fichiers verts**, pic 1711 Mo / 1920 |
| ruff · budget | **propre** · 275 / 548 |
| Pré-scan AST (`S9073` · `S1192`) | **0** après factorisation |
| Déploiement production | **non touché** — une garde le vérifie |

---

## 10. Ce que cette tranche ne fait pas

* **Aucune sélection de tests** (`C1` différé). Le plafond mesuré — 44 fichiers
  sur 291, ≈ 60 s de wall-clock — ne justifiait ni la complexité ni le risque.
* **Aucune architecture impact-aware lourde** (`C4`). Elle viserait 18 s.
* **Aucun changement du déploiement production** (`C5` séparé).
* **Aucune activation.** Le shadow mode doit d'abord produire ses données.

## 11. Ce qui reste à l'opérateur

1. **Observer le shadow mode** sur plusieurs merges — la CI journalise
   `WOULD_REUSE` / `WOULD_FULL` à chaque push canonique, sans rien changer.
2. **Comparer** : zéro faux `REUSE` autorisé.
3. **Armer**, si et seulement si la comparaison est parfaite :
   `CI_CANONICAL_REUSE_ENABLED = true` en variable de dépôt.
4. **Mesurer le gain réel** après activation — l'hypothèse de l'audit
   (≈ 95 % des merges, ≈ 39 % du runner-time) est une **prévision**, pas un
   critère de réussite.
