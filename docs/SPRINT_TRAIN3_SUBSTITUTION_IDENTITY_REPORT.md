# TRAIN 3 / `A2` étape B — la substitution se compare par **identité**

`OPERATOR_DECISION` A2 · branche `sb/train3-substitution-identity` · base `51c837d`

---

## 1. Le défaut, prouvé avant d'être corrigé

Deux endroits du produit décident si deux séances portent sur le **même
mouvement**, et tous deux le faisaient par **égalité de chaîne exacte** :

* `overload_inputs._matches_substitution_policy` — l'historique de charges ;
* `stats._matches_current_substitution` — la « dernière fois », qui alimente
  cinq surfaces (`Sx_DOGFOOD_01`).

`Curl marteau câble (corde)` et `Curl marteau câble corde` sont **toutes deux
présentes dans les données du dépôt** — le catalogue écrit la première, l'EKB
la seconde. `Sb_EKB_ORTHOGRAPHIC_ALIAS_01` avait déjà tranché qu'il s'agit d'un
**défaut de construction**, pas d'un désaccord de données : c'est le même
mouvement.

Appelée avec ces deux écritures, la politique rendait `False` :

```
normalize(A) == normalize(B) : True
A == B                       : False

passé A, courant A     → historique consommé : True
passé B, courant B     → historique consommé : True
passé A, courant B     → historique consommé : False   ← le défaut
passé B, courant A     → historique consommé : False   ← le défaut
```

**Le même mouvement ne partageait pas son historique de charges, et rien ne le
disait.** L'utilisateur lisait « aucune référence » là où il avait soulevé la
semaine précédente. C'est le pire genre de défaut du dépôt : celui qui rend une
absence indiscernable d'une vérité.

Le tableau ci-dessus n'est pas une lecture du code — c'est la sortie de la
fonction réelle appelée avec les deux orthographes.

---

## 2. Brainstorming / Options / Risques / Choix retenu (`CLAUDE.md §3`)

### Ce qui a été mesuré avant de concevoir

| Mesure | Résultat |
|---|---|
| Identités `exercises` en base | **102** |
| Noms que le sélecteur de substitution peut proposer | **83** |
| … résolus par le référentiel d'identités | **83 / 83**, zéro trou |
| Écritures distinctes pour une même forme normalisée | **1 paire** — celle ci-dessus |
| Substitutions déjà écrites dans la base de mesure | 0 |

La deuxième ligne décide tout : **le produit peut résoudre 100 % de ce qu'il
propose**. La correction ne demande donc aucune heuristique, aucun
rapprochement flou, aucune donnée nouvelle — seulement de comparer ce que
`Sb_EXERCISE_IDENTITY_01` a déjà rendu comparable.

### Options examinées

**Option A — une clé de comparaison d'identité, partagée par les deux sites.**
*(retenue)* `identity_key(db, name)` rend `None` (prescrit), `id:<slug>` (nom
reconnu) ou `raw:<forme normalisée>` (nom inconnu). Les deux sites comparent
des clés.
· *Pour* : **une seule règle** pour deux surfaces qui devaient déjà s'accorder
et pouvaient diverger en silence. L'élargissement se limite aux écritures d'un
même mouvement.
· *Contre* : une lecture de plus par nom distinct — mesurée, voir §5.

**Option B — normaliser les deux chaînes et comparer.**
· *Pour* : deux lignes, aucune requête.
· *Contre* : recrée un **vocabulaire concurrent** à côté du référentiel
d'identités qu'`A1` vient d'établir. Une fusion curatée (deux noms différents
décidés comme un même mouvement) ne serait pas vue. Rejetée : le dépôt a déjà
payé les vocabulaires parallèles.

**Option C — écrire l'identité en base au moment de la substitution.**
· *Pour* : coût de lecture nul ensuite.
· *Contre* : demande une colonne et un **backfill des lignes historiques** —
ce que l'invariance historique interdit (`CLAUDE.md §2`, additive-only).
Écrire l'identité des futures substitutions **sans** corriger les passées
créerait deux régimes. Différée : c'est un candidat pour l'étape C, pas pour
celle-ci.

### Risques identifiés avant d'écrire, et ce qui les couvre

| Risque | Couverture |
|---|---|
| **L'appariement s'élargit trop** — deux mouvements différents partagent un historique. *Pire que le défaut corrigé : une charge fausse plutôt qu'absente.* | garde dédiée · les formes normalisées distinctes donnent des identités distinctes |
| Un nom **inconnu** devient comparable à tout | `raw:` — il se compare à son égal, jamais à `None` ni à un autre |
| Une clé d'identité **collisionne** avec une clé brute | préfixes distincts, garde dédiée |
| La frontière **prescrit / substitué** bouge | quatre gardes, dont les deux sens |
| Un **N+1** apparaît dans une boucle qui grandit avec l'usage | mémoïsation par appel, **mesurée** (§5) |
| La comparaison **redevient orthographique** ailleurs | garde structurelle sur les deux modules |

### Choix retenu

**Option A.** L'étape C (`exercice custom structuré`) reste devant nous : elle
traite le cas où le nom substitué n'existe dans aucun référentiel. Cette
tranche lui prépare le terrain — `raw:` est exactement la population qu'elle
aura à structurer.

---

## 3. Ce qui a changé

| Fichier | Nature |
|---|---|
| `app/services/exercise_identity.py` | `identity_key()` + les deux préfixes de clé |
| `app/services/overload_inputs.py` | comparaison par clé · mémoïsation · extraction de `_comparable_exercise` |
| `app/services/stats.py` | `_normalize_sub` rend une clé d'identité · mémoïsation |
| `tests/test_train3_substitution_identity.py` | **neuf** — 14 gardes |

**Aucune migration, aucune colonne, aucune écriture.** Le `substituted_name`
reste le contrat de **stockage** ; seule la **comparaison** change. Les lignes
historiques ne sont pas touchées — elles sont simplement mieux lues.

---

## 4. Gardes plantées

**7 défauts plantés, 7 gardes rouges.**

| Défaut planté | Garde | Verdict |
|---|---|---|
| `stats` revient à la comparaison de chaînes | les deux orthographes partagent l'historique | 🔴 |
| `overload` revient à la comparaison de chaînes | l'overload suit la même règle | 🔴 |
| un nom inconnu devient le cas prescrit | un inconnu garde une clé propre | 🔴 |
| l'identité cesse d'être consultée | les deux orthographes | 🔴 |
| un substitué sans clé consomme tout | la garde du cas conservateur | 🔴 |
| les deux familles de clés se confondent | préfixes distincts | 🔴 |

**Une mutation a d'abord survécu**, et elle a révélé un trou de couverture réel :
`current_is_substituted=True` **avec une clé courante nulle** — le cas
conservateur, quand le nom substitué est vide. Aucune de mes gardes ne
l'exerçait ; passer ce branchement à `return True` laissait tout vert, alors
qu'un créneau substitué aurait emprunté n'importe quel historique, prescrit
compris. Garde ajoutée, mutation rejouée : rouge.

---

## 5. Coût, mesuré

La résolution interroge la table d'alias. Les deux boucles appelantes
parcourent un ensemble qui **grandit avec l'usage** — d'où la mesure plutôt que
l'espoir.

Banc : 40 séances × 7 créneaux = **280 lignes passées**, substitutions
alternées.

| | Requêtes de résolution |
|---|---|
| Sans mémoïsation | 7 |
| **Avec mémoïsation par appel** | **2** |

Et le cas défavorable — une substitution courante qui **ne correspond à rien**,
donc aucun court-circuit de boucle :

| Historique | Requêtes de résolution |
|---|---|
| 140 lignes | 3 |
| 560 lignes | **3** |

**Le coût ne dépend pas de la taille de l'historique** mais du nombre de noms
distincts comparés. Le cache ne survit pas à l'appel : il ne peut donc pas
devenir périmé quand le référentiel change.

⚠ **Correction d'une affirmation que j'avais faite trop vite.** J'ai d'abord
écrit que la boucle de `stats` produisait un N+1 croissant. Mesuré : elle
court-circuite dès qu'un créneau trouve sa correspondance, donc le coût est
borné par le nombre de créneaux, pas par l'historique. La mémoïsation reste
justifiée — elle divise par 3,5 sur le banc et rend le cas défavorable plat —
mais pas pour la raison que j'avançais.

---

## 6. Vérifications (`CLAUDE.md §1`)

| Vérification | Résultat |
|---|---|
| `check_scope.py` | **`SHARED_CODE`** |
| Sweep ciblé, 12 fichiers consommateurs | **225 passés, 0 échec** |
| **Full sweep local** — non exigé au tier, lancé sur doute (`stats` alimente cinq surfaces) | **285/285 fichiers, 84 lots, tous verts** · pic 1516 Mo pour 1980 de budget · **1 adaptation automatique**, aucun fichier sauté |
| `tests/test_train3_substitution_identity.py` | **14 passés** |
| Tests historiques de la politique de substitution | **64 passés** — 0 affaibli, 0 supprimé |
| ruff (rapport CI reproduit) | **276 avant / 276 après** |
| Pré-scan AST S9073 / S5863 / S1192 | 1 littéral hissé en constante, 0 restant |
| `python:S3776` | `_history_signals_for_code` était à **16 pour 15 permises** → extraction de `_comparable_exercise`, **0 comportement changé** |

**Aucune surface visible modifiée** : pas de gabarit, pas de feuille de style.
`CLAUDE.md §5.1` ne s'applique donc pas à cette tranche. Ce qui change à
l'écran est une **valeur** — une référence de charge apparaît là où le produit
disait « aucune référence » — et c'est précisément ce que les gardes de
comportement mesurent bout en bout.

---

## 7. Ce que cette tranche ne fait pas

* **`A2` étape C — l'exercice custom structuré.** Quand un nom substitué
  n'existe dans aucun référentiel, il reste aujourd'hui du texte, et cette
  tranche lui donne une clé `raw:` pour qu'il se compare correctement à
  lui-même. Le **structurer** — lui donner une identité, donc une zone, donc
  une place dans l'analytique — est l'étape suivante.
* Aucune fusion de quasi-doublons. `Sb_EXERCISE_IDENTITY_01` a relevé **17
  paires** dans le seul catalogue et a délibérément laissé la décision ouverte :
  fusionner est un **jugement produit**, pas une dérivation. Cette tranche ne
  fusionne rien — elle rapproche seulement deux écritures dont la forme
  normalisée est **déjà identique**.

---

## 8. Closeout post-merge

| | |
|---|---|
| PR | **#165** |
| Merge | **`d8a3f2a`** — `--merge`, tête épinglée `fa8a831`, **pas de squash, pas de `--admin`, pas de force** |
| CI de PR | 9/9 `pass`, **aucun cycle rouge** |
| CI canonique (`push` sur le merge) | run **32950139170** — **succès** |
| Sonar (gate PR) | **OK** — couverture neuve **96,9 %** · 0 bug · 0 code smell · 0 vulnérabilité · duplication 0,0 % |
| Fils de revue non résolus | 0 |

### Ce que cette tranche laisse au dépôt, au-delà du code

**Un défaut qu'on peut prouver vaut mieux qu'un défaut qu'on peut décrire.**
Le tableau du §1 n'est pas une lecture du code : c'est la sortie de la fonction
réelle appelée avec les deux orthographes. Cela a coûté quinze lignes de script
et a rendu la suite indiscutable — y compris pour décider **quoi ne pas
faire**.

**La correction n'a eu besoin d'aucune heuristique parce que la mesure l'a
montré.** 83 noms proposables sur 83 déjà résolus : il n'y avait rien à
deviner. Sans cette mesure, l'appariement flou aurait paru raisonnable — et
aurait été exactement ce qu'`A2` interdit.

**Deux fautes d'agent, consignées :**

1. **Une mutation a survécu**, et c'est elle qui a trouvé le trou : le cas
   conservateur (`current_is_substituted=True`, clé courante nulle) n'était
   exercé par aucune garde. Sans plantation, ce branchement serait resté non
   couvert et son inversion serait passée inaperçue.
2. **J'ai affirmé un N+1 croissant sans le mesurer.** La boucle court-circuite
   dès qu'un créneau trouve sa correspondance : le coût est borné par le nombre
   de créneaux, pas par l'historique. La mémoïsation reste justifiée — elle
   divise par 3,5 sur le banc et aplatit le cas défavorable — mais la raison
   que j'avançais était fausse, et le §5 porte la correction.

**Le sweep adaptatif a servi pour la première fois en conditions réelles.**
`Sb_OPS_LOCAL_SWEEP_ADAPTIVE_BATCH_01` a été livré sur un banc forcé ; ici, une
dépassement de budget réel a déclenché **une adaptation automatique** et le
sweep a terminé **285/285 fichiers** sans intervention. Sur les quatre tranches
qui ont précédé cet outil, trois s'étaient arrêtées en laissant le travail
inachevé.

### Reste ouvert

* **`A2` étape C — l'exercice custom structuré.** La population `raw:` que
  cette tranche vient de nommer est exactement ce qu'elle aura à traiter.
* Deux arbitrages UI hérités de TRAIN 2, aucun bloquant : **Q5** (« Pourquoi ce
  plan ? » en carte bordée pour un objet de rang 2) et l'**appellation
  « Explore »**.
