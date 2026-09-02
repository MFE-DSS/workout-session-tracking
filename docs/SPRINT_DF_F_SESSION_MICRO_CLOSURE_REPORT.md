# `DF-F` — micro-clôture de l'écran de séance

`OPERATOR_ARBITRATION` — registre du 2026-08-29, décisions `D1`, `D2`, `D3` ·
branche `sb/df-f-session-micro-closure` · base `5fbdd8f`

Trois décisions tranchées par l'opérateur sur des rendus mesurés. Elles ne
partagent pas un mécanisme : elles partagent le fait d'avoir été **soumises
puis tranchées**, et c'est pourquoi elles voyagent ensemble.

---

## 1. `D1 = variante D` — l'historique cesse d'être répété

Le lien « Voir historique E{n} → » était rendu sur **chacune des six cartes
repliées**, pour un accès que la carte active porte déjà à son niveau L3.

**Ce n'est pas une soustraction** (`§5.3`) : l'accès n'est pas supprimé, il
cesse d'être dupliqué. Et depuis `DF-E`, atteindre l'historique d'un autre
exercice se fait en touchant sa carte — ce qui l'active, donc rend son
`Historique` disponible. Deux gardes vérifient les deux chemins.

**Ce qui reste, sur décision explicite** : les valeurs de la performance
précédente et la puce `schéma · date`. Ce sont des **données** qu'on lit d'un
coup d'œil ; le lien était une **action** qu'on déclenche une fois.

| Mesuré à 390 px | avant `D1` | après |
|---|---|---|
| densité | 4,15 écr | **3,78** |
| hauteur de carte repliée | 203 px | **151 px** |

---

## 2. `D2 = a` — la puce cesse d'énoncer quelque chose de faux

`_last_time_chip()` renvoyait `"première fois"` dans **trois** situations
distinctes : aucune séance antérieure · une séance antérieure sans première
série · une première série sans charge ni répétitions. Les deux dernières ne
sont pas des premières fois — **l'utilisateur est déjà venu**, il n'a rien noté.

Trois états, trois libellés :

| Situation | Libellé |
|---|---|
| aucune occurrence antérieure | `première fois` |
| occurrence sans valeurs exploitables | **`sans données`** |
| occurrence avec valeurs | `dernière fois 60 kg × 10` |

### Comment ce défaut a été trouvé

**Par un rendu fabriqué pour un arbitrage, pas par un test.** Le comparatif de
densité de `DF-E` a posé la puce et le bloc « Dernière fois » **côte à côte** ;
on lisait alors `première fois` et `aujourd'hui · aucune donnée saisie` sur la
même carte, à propos de la même donnée. `DF-E` n'a pas créé le défaut — il l'a
rendu visible en le posant à côté de la vérité.

### La garde qui exigeait le défaut

`test_briefing_service.py::test_last_time_chip_falls_back_to_premiere_fois`
**imposait** `première fois` dans les quatre cas, y compris les deux faux. Une
garde peut donc épingler un défaut aussi solidement qu'une propriété — et
celle-ci l'a fait pendant tout le temps où la contradiction n'était pas
visible à l'écran.

Elle est scindée en deux, l'une par état, et elles disent maintenant la règle
tranchée.

---

## 3. `D3 = B` — le bouton nomme ce que l'écran montre

`DF-C` avait retiré les codes `É`/`S` des lignes de série ; la commande
dominante continuait de les employer. Plus rien à l'écran ne portait le nom
qu'elle annonçait.

| | avant | après |
|---|---|---|
| échauffement | `VALIDER É1` | **`VALIDER ÉCHAUFFEMENT 1`** |
| série de travail | `VALIDER S1` | **`VALIDER SÉRIE 1`** |

Aucun vocabulaire n'est inventé : ce sont les mots que le **nom accessible**
emploie déjà. Mesuré au rendu : tient sur une ligne à 360 px, hauteur de
bouton inchangée.

Une garde énonce la **propriété** plutôt que les deux cas : aucun libellé de
commande, dans aucun état, ne doit réintroduire un code alphabétique.

---

## 4. `D9` et `D10` — ce que cette tranche ne devait pas défaire

L'ordre est explicite : « Preserve D9 and D10 exactly ». Deux gardes le
verrouillent, et toutes deux ont été **plantées** :

* **`D9`** — aucune validation à la frappe ni au `blur`. Le script n'écoute que
  `keydown`. Planter `blur` ou `input` fait rougir.
* **`D10`** — le dock du repos ne porte que `−15 s` / `+15 s`. Y ajouter une
  sortie d'exercice fait rougir.

Ces deux propriétés ont coûté une tranche chacune ; elles pouvaient être
défaites par mégarde en « améliorant » le dock.

---

## 5. Exposition `§5.1`

Rendu réel, Chromium, 360 / 390 / 430 px, sur un **processus Python neuf**.

| | mesure |
|---|---|
| densité | **4 / 3,8 / 3,3 écr** (contre 4,4 / 4,1 / 3,6) |
| débordement horizontal | **aucun** |
| cibles < 44 px | **aucune** |
| cible d'activation, la plus petite | 109 px |
| liens d'historique rendus | **1** (contre 7) |

> ⚠ **Le serveur de lab ne recharge pas Python.** Ma première capture montrait
> encore `VALIDER É1` et `première fois` : le gabarit s'était rechargé, pas
> `console_state.py` ni `briefing.py`. C'est le piège documenté en `DF-B`,
> rattrapé cette fois **avant** d'exposer la capture.

---

## 6. Fautes de l'agent

1. **Un sweep ciblé, encore, insuffisant.** Il couvrait huit fichiers et était
   vert ; le sweep complet a trouvé `test_briefing_service.py`, absent de ma
   liste. C'est la deuxième tranche consécutive où c'est le sweep complet qui
   trouve — la leçon de `DF-E` s'applique telle quelle.
2. **Une capture périmée, arrêtée à temps.** Voir §5.
3. **Deux `I001`** dans le fichier neuf — la famille qui a coûté un cycle CI
   sur la PR #152. Attrapés par ruff avant le push. Le troisième, dans
   `briefing.py`, **préexiste** : vérifié en passant ruff sur la version
   canonique, il est hors périmètre.

---

## 7. Vérifications

| | |
|---|---|
| `tests/test_df_f_session_micro_closure.py` | **11 gardes** · **9 défauts plantés, 9 rouges** |
| Broad sweep ciblé (console de séance) | 125 passés — **et insuffisant**, voir §6 |
| **Full sweep local** | **291/291 fichiers verts**, pic 1956 Mo / 2184 |
| ruff (fichiers touchés) | **propre** |
| `check_ruff_budget.py` | **275 / 548** |
| Pré-scan AST | **0** après hoisting d'un littéral |

---

## 8. Ce que cette tranche a découvert, et qui la dépasse

En préparant `D4` — compléter le champ `chain` pour les 38 exercices non
couverts —, une vérification a montré que **l'instruction et le code se
contredisent**.

`exercise_properties.json` a un **contrat implicite** : une entrée porte ses
cinq champs. Les 48 entrées existantes le respectent, et c'est pourquoi le
défaut suivant ne s'est jamais déclenché.

Deux mécanismes s'additionnent :

1. `compute_suggestions()` court-circuite N2 et N3 quand `origin_props is
   None` — un exercice **absent** ne reçoit donc que les suggestions curées.
   Une entrée **partielle** lève ce garde-fou ;
2. le scoring compare les champs avec `.get()`, donc **`None == None` compte
   comme une correspondance**.

**Mesuré**, avec exactement les entrées que `D4` demande :

```
N2 proposés pour « Leg press » (entrée ne portant que `chain`) :
   85  Skull crushers EZ-bar
   85  Lateral raise machine
```

Une extension triceps proposée comme alternative à une presse à cuisses.

**Ce défaut de scoring existe indépendamment de `DF-D`** : toute entrée
partielle entrant dans ce registre, par quelque chemin que ce soit, produira ce
genre de suggestion. Il mérite sa propre tranche.

Trois voies pour `D4`, soumises à l'opérateur :

* **un fichier dédié** lu uniquement par la suggestion de repos — honore
  l'instruction à la lettre, n'arme aucun défaut, ne touche pas au moteur ;
* **compléter les cinq champs** pour les 38 exercices — exclu par l'ordre, et
  demanderait une validation métier par exercice ;
* **corriger le scoring** pour que deux champs absents ne se comptent jamais
  identiques — un vrai correctif, mais un changement de comportement du moteur
  de substitution, qui mérite ses propres gardes.

---

## 9. Hors périmètre

* **`DF-D`** — suggestion de repos contextuelle : bloquée sur la forme de `D4`.
* **`D11`** — dette de dépendance (passlib / `bcrypt<5`) : PR séparée, sur ordre.
* **Nettoyage CSS** des classes de l'ancienne interface.
* **Déploiement** : la canonique n'est pas en production.


---

## 10. Closeout post-merge

| | |
|---|---|
| PR | **#178** |
| Merge | **`9094d72`** — `--merge`, tête épinglée `56e1203`, **pas de squash, pas de `--admin`, pas de force** |
| CI de PR | **9/9 `pass`**, **aucun cycle rouge** |
| Gate Sonar (PR) | **`OK`** — 0 bug · 0 code smell · 0 vulnérabilité · **couverture du code neuf 100 %** |
| CI canonique (`push` sur le merge) | run **33528541413** — **succès, 6/6 jobs** |
| Full sweep local | **291/291 fichiers verts**, pic 1956 Mo / 2184 |
| Fils de revue non résolus | **0** |

### Ce que cette tranche laisse au dépôt

**Une garde peut exiger le défaut.**
`test_last_time_chip_falls_back_to_premiere_fois` imposait `première fois` dans
quatre situations, dont **deux où l'utilisateur était déjà venu**. Elle a tenu
le défaut en place aussi solidement qu'elle aurait protégé une propriété — et
personne ne l'a vue tant que la contradiction n'était pas **visible côte à côte
à l'écran**.

Ce défaut n'a pas été trouvé par un test mais **par un rendu fabriqué pour un
arbitrage**. C'est le troisième cas de cette session où l'exposition visuelle
trouve ce qu'aucune garde ne regardait — après l'`opacity` de `DF-C` et les
cibles sous 44 px.

**Et, deuxième tranche consécutive, c'est le sweep COMPLET qui a trouvé.** Mon
sweep ciblé couvrait huit fichiers et était vert ; `test_briefing_service.py`
n'y figurait pas.

### Ce que cette tranche a découvert et qui la dépasse

En préparant `D4`, une vérification a montré qu'une entrée ne portant que
`chain` dans `exercise_properties.json` ferait proposer **« Skull crushers
EZ-bar » (score 85) comme alternative N2 à « Leg press »**. Le registre a un
contrat implicite — une entrée porte ses cinq champs — et `None == None` compte
comme une correspondance dans le scoring. **Ce défaut vaut une tranche à part.**

### Reste ouvert

* **`DF-D`** — suggestion de repos contextuelle : la classification des 24
  exercices est prête, la forme de `D4` attend l'arbitrage (fichier dédié
  plutôt qu'entrées partielles dans le registre).
* **Le scoring de substitution** — `None == None` traité comme une
  correspondance. Tranche à part.
* **`D11`** — dette de dépendance (passlib / `bcrypt<5`), PR séparée sur ordre.
* **Déploiement** : `9094d72` **n'est pas en production** — le dernier
  déploiement est `32cf5ee`.
