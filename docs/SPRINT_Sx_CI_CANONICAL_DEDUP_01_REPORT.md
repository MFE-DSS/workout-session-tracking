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

## 4. Phase 2 — UNE PREUVE FAUSSE, ET CE QUI LA REMPLACE

### ⛔ Ce que j'avais écrit, et pourquoi c'était faux

La première version raisonnait ainsi :

> Si `tree(M) == tree(H)`, alors fusionner `B` dans `H` n'a rien apporté : `B`
> est la base de branchement. Donc toute base antérieure `B′` est un ancêtre de
> `H`, et l'arbre testé valait `tree(H)`.

**L'étape du milieu est un saut.** `tree(M) == tree(H)` dit seulement que la
contribution **nette** de la base est nulle — ce qui vaut aussi après un
aller-retour. J'ai présenté comme une démonstration un raisonnement qui n'en
était pas un, et l'opérateur l'a arrêté avant merge.

### Le contre-exemple, reproduit mécaniquement

```
1. la base reçoit X
2. la CI de PR teste merge(base+X, H)  →  H + X
3. la base ANNULE X (revert) → son arbre redevient celui de la base
4. le merge final donne tree(M) == tree(H)

tree(M)          : 467910335a29
tree(H)          : 467910335a29   ← l'ancienne règle disait REUSE
tree TESTÉ en PR : 4a8143d2f455   ← contenait x.py
```

**Faux `REUSE`** : la CI n'a jamais vu le contenu devenu canonique. C'est
exactement ce que l'ordre interdit sans exception.

Deux gardes le figent : l'une **conserve le contre-exemple** pour qu'on ne
puisse plus réintroduire l'ancien raisonnement en croyant l'avoir démontré,
l'autre vérifie que la règle actuelle le refuse.

### On ne déduit plus — on capture

Pendant le run `pull_request`, là où GitHub a fait le checkout de
`refs/pull/N/merge`, le job **enregistre ce qui est réellement testé** :

```
tested_merge_sha · tested_tree_sha · head_sha · base_sha · run_id
        → artefact `pr-attestation`, rétention 7 jours
```

Au push canonique, `REUSE` exige que `tree(M)` soit **exactement** égal au
`tested_tree_sha` attesté par un run de PR dont les contrôles requis sont
verts. Six façons d'échouer, six gardes plantées :

| Cas | Verdict |
|---|---|
| artefact **absent** | FULL |
| artefact **expiré** | FULL |
| jeu d'artefacts **ambigu** | FULL |
| artefact **illisible** | FULL |
| artefact attestant une **autre tête** | FULL |
| artefact se réclamant d'un **autre run** | FULL |

---

## 4bis. L'obstacle qui avait motivé la déduction

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

## 7ter. Le second défaut : un mécanisme qui n'aurait **rien mesuré**

Trouvé le 2026-09-02, après une CI de PR **verte 9/9**, en téléchargeant à la
main l'artefact que le run venait de déposer.

```
HTTP Error 401: Server failed to authenticate the request.
```

`urllib` **recopie les en-têtes de la requête initiale sur une redirection**.
L'URL de téléchargement d'un artefact répond `302` vers un stockage dont l'URL
porte **déjà sa propre signature** ; il reçoit alors un
`Authorization: Bearer <jeton GitHub>` qu'il ne reconnaît pas, et refuse.

### Pourquoi c'est grave alors que l'échec est fermé

Ce défaut **ne produit aucun faux `REUSE`** : `attested_payload` lève, le
verdict reste `FULL`. Il est pourtant plus pernicieux que le précédent.

Le mécanisme aurait rendu `FULL` **à chaque merge, indéfiniment**. Le shadow
mode aurait journalisé « aucune réutilisation » pendant des semaines, la
comparaison demandée par la Phase 5 aurait été *parfaite* — zéro faux `REUSE`,
puisque zéro `REUSE` — et la conclusion honnête aurait été « le gain mesuré est
nul, la tranche ne sert à rien ». **La cause réelle — un en-tête de trop sur une
redirection — n'apparaissait dans aucun journal.**

> **Une garde qui ne garde rien a une cousine : un mécanisme qui ne mesure
> rien.** Le premier échoue en laissant passer ; le second échoue en ne passant
> jamais, et se déguise en résultat négatif.

### Ce qui l'a trouvé, et ce qui ne l'aurait jamais trouvé

Les 56 gardes d'alors **injectaient toutes une fausse API**. Aucune n'exerçait
la couche redirection — par construction, puisqu'elles la remplaçaient. Le
sweep local, la CI de PR verte et le gate Sonar étaient tous d'accord.

Ce qui l'a trouvé : **avoir exécuté le vrai téléchargement sur le vrai artefact
du vrai run**. C'est le même geste que le rendu réel exigé par `§5.1` pour l'UI,
transposé à une couche réseau.

### La correction, et les quatre gardes

`_DropAuthOnRedirect` retire `Authorization` quand la redirection **change
d'hôte**, et refuse un `Location` en clair — qui exfiltrerait le jeton. Les
gardes ajoutées, chacune rouge à la plantation correspondante :

| Garde | Ce qu'elle interdit |
|---|---|
| le jeton n'atteint jamais le stockage | le défaut d'origine, en entier |
| le jeton survit à une redirection **même hôte** | une correction qui casserait l'API elle-même |
| une redirection en clair est refusée | l'exfiltration du jeton |
| le téléchargement passe **par cet ouvreur** | un retour silencieux à `urlopen` |

Vérification finale, sur données réelles et non simulées : l'artefact du run
**33604235503** se télécharge, et son `tested_tree_sha` vaut
`8e917b78111ca5a34a691152db665a2b55faf86f`, **exactement** l'arbre de la tête
`362ffcc` — tandis que `tested_merge_sha` (`c9b1a596`) est un **commit
distinct**, l'aperçu de merge que GitHub avait réellement checkout. La capture
décrit donc bien ce qu'elle prétend, et rien n'est reconstruit.

---

## 8. Fautes de l'agent — trois vagues de gardes creuses, une preuve fausse, un mécanisme inerte

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

**Quatrième vague — et c'est la plus instructive.** Une preuve **fausse** :
`tree(M) == tree(H) ⇒ l'arbre testé vaut tree(M)`. Aucune plantation ne pouvait
l'attraper, puisque le défaut n'était pas dans le code mais dans le
**raisonnement que le code implémentait fidèlement**. C'est l'opérateur qui l'a
attrapée, avec un contre-exemple (§4). Première fois dans ce train qu'une faute
survit à des gardes correctes : elles gardaient bien la règle — la règle était
fausse.

Aggravant : ma première reproduction de ce contre-exemple **a échoué en
silence** (`git revert -q`, drapeau inexistant) et m'a rendu un résultat
rassurant. Reprise avec vérification des codes de retour, elle a confirmé le
faux `REUSE`. *Un banc d'essai dont on ne vérifie pas qu'il a réellement tourné
est un troisième instrument faux.*

**Cinquième vague.** Un mécanisme **inerte** plutôt qu'incorrect (§7ter) : le
téléchargement d'artefact échouait toujours, donc le verdict était toujours
`FULL`. Aucune des 56 gardes ne pouvait le voir — **elles remplaçaient toutes la
couche défaillante**. Trouvé en exécutant le vrai téléchargement.

> **Un mécanisme qui ne mesure rien se déguise en résultat négatif.**

---

## 9. Vérifications

| | |
|---|---|
| `check_scope.py` | **`CI_INFRA`** — full sweep local obligatoire, **validation sur CI réelle impérative** |
| `tests/test_ci_canonical_attestation.py` | **60 gardes** · 26 défauts plantés, 26 rouges |
| Téléchargement d'artefact | **exercé sur l'API réelle**, pas simulé (run 33604235503) |
| Familles de gardes CI existantes | **253 passés** |
| **Full sweep local** | **292/292 fichiers verts**, 86 lots, pic 1703 Mo / 1881, 0 fichier sauté |
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
