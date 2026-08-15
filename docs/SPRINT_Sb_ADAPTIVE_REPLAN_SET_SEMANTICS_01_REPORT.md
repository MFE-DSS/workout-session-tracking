# SPRINT Sb_ADAPTIVE_REPLAN_SET_SEMANTICS_01 — replanification en séries (RAPPORT)

**Train :** `AUREN_WEEKLY_PLAN_PRODUCTIZATION_01`, tranche 3/4 ·
**Base canonique :** `d66a74f` · **Branche :** `sb/adaptive-replan-set-semantics-01` ·
**Tier `check_scope` :** **ISOLATED** — vérifié, pas supposé : `adaptive_replan`
n'a **aucun consommateur** dans `app/`, c'est un service feuille non encore
branché à une surface.

---

## 1. Brainstorming / Options / Risques / Choix retenu

### Le problème posé par la tranche précédente

`PlanDelta` ne portait que `slots_before` / `slots_after`. Depuis que la tranche
2 alloue des **séries**, un créneau peut en contenir deux comme quatre : « un
créneau retiré » ne dit plus **combien de travail bouge**. Le delta était devenu
une unité sans dose.

### Option écartée : remplacer les créneaux par les séries

Tentant, plus simple. Écartée parce que **les deux mesurent des choses
différentes** : les créneaux décrivent la **forme** de la semaine (quels
exercices sortent), les séries en décrivent la **charge**. Un consommateur qui
veut savoir « quel exercice disparaît de mardi » n'a que faire d'un total de
séries. Le brief le dit d'ailleurs : *« Slot movement may remain separately
observable. »*

**Retenu** : les deux axes, exposés côte à côte, et `is_reduction` qui exige une
réduction **sur les deux**. Un créneau en moins peut cacher des séries en plus —
la garde couvre ce cas, et deux tests le prouvent sur des deltas fabriqués
exprès.

### La limite que je refuse de contourner

Le brief demande que, si une preuve de séries **réellement effectuées** existe,
seules les séries **non effectuées** soient reconsidérées.

**Cette preuve n'existe pas.** Rien ne persiste l'identité **plan ↔ séance** :
aucune donnée ne dit quelle séance enregistrée réalise quel créneau planifié, ni
combien de séries d'un exercice ont été faites. Le brief prévoit ce cas —
*« retain the limitation explicitly and do not pretend exact performed-set
matching »* — et c'est exactement ce qui est fait.

**Conséquence tenue** : une séance écourtée **est** une divergence (elle peut
déclencher une redistribution) mais **ne retire aucune série**. Réduire ici
reviendrait à deviner ce qui a été fait, et à prescrire moins à quelqu'un qui a
peut-être tout terminé en avance.

La limite est écrite **dans le code** (`PERFORMED_SET_IDENTITY_LIMITATION`), pas
seulement dans ce rapport, et une **garde structurelle** vérifie qu'aucun
appariement séance↔créneau n'a été tenté en douce.

---

## 2. Ce qui a été livré

`PlanDelta` porte `sets_before` / `sets_after` à côté de `slots_before` /
`slots_after`, plus `sets_removed`. `ReplanResult` expose `sets_removed_total`.

`is_reduction` exige une non-augmentation **sur les deux axes**.

Le `basis` dit combien de séries sortent de la semaine, et — quand une séance a
été écourtée — pourquoi **aucune** n'est retirée par déduction.

**Rien d'autre n'a bougé** : la détection de divergence est inchangée, les
déclencheurs admis sont les mêmes, la source de récupération reste P0.4 seule.

---

## 3. L'asymétrie, désormais en séries

| Preuve | Effet autorisé |
|---|---|
| Récupération estimée limitante (**avec** confiance) | reporter, redistribuer, **retirer des séries** |
| Bonne readiness déclarée | **rien** — aucune replanification |
| Zone estimée récupérée | **aucun delta** |
| `Confidence.NONE` sur une bande limitante | **aucune contrainte fabriquée** |
| Séance écourtée | divergence, mais **zéro série retirée** |

**Aucun delta ne peut augmenter une série, jamais.** C'est la propriété qui rend
une replanification automatique acceptable : sans elle, le système prescrirait
progressivement davantage à qui se déclare en forme — c'est-à-dire à qui se
plaint le moins.

---

## 4. Plantations — les deux gardes mordent

Après trois gardes non porteuses sur ce train, chaque invariant est éprouvé.

**(a) Preuve limitante qui AJOUTE des séries** (`sets_after = sets_before + 2`)
⇒ **4 tests tombent**, dont l'asymétrie héritée de la tranche précédente
(`test_postponed_work_is_reduced_never_increased`).

**(b) Filtre `Confidence.NONE` retiré** ⇒ **2 tests tombent**.

Ce second point mérite d'être noté : dans le train précédent, **cette même
plantation ne cassait rien** — le contrôle de bande couvrait à lui seul tous les
cas écrits, et la garde n'était pas porteuse. Le cas manquant avait été ajouté
alors ; **la re-plantation d'aujourd'hui confirme que le correctif tient**.

---

## 5. Tests — 20 dédiés

Delta en séries · total exposé · mouvement de créneaux **séparément
observable** et non déductible de la charge · aucun delta n'ajoute jamais une
série · bonne readiness ⇒ aucune replanification · zone récupérée ⇒ aucun delta
même à côté d'une zone fatiguée · `Confidence.NONE` ne fabrique rien ·
`is_reduction` rejette une hausse de séries **même** si les créneaux baissent,
et l'inverse · séance écourtée : divergence sans retrait · limite énoncée dans
le `basis` **et** dans le code · garde structurelle contre tout appariement
plan↔séance · manques structurels survivants · nouvelle version, jamais une
mutation · déterminisme sur trois cadences.

Les 36 tests existants de `Sb_ADAPTIVE_REPLAN_01` passent **inchangés** —
l'ajout de champs est additif, aucune assertion n'a eu à être relâchée.

---

## 6. Non-régressions

Aucune persistance, aucune migration, aucune surface · `recommendation.py` /
`behavioral.py` / `substitution.py` non touchés · détection de divergence
inchangée · P0.4 reste la source unique · aucun second modèle de fatigue ·
aucun LLM, aucun aléa.

## Verdict

La dose adaptative se compte enfin dans la même unité que le budget et le plan.
L'asymétrie — **réduire sur preuve, ne jamais ajouter sur optimisme** — est
préservée et désormais vérifiée sur les séries, pas sur un proxy.

La demande du brief sur les séries effectuées est **honorée par sa limite** :
sans identité plan↔séance persistée, une séance écourtée diverge sans rien
retirer. Prétendre un appariement exact aurait été la seule vraie faute
possible ici, et la garde structurelle empêche qu'elle se glisse plus tard.

Cette limite se lève naturellement avec la **tranche 4** : matérialiser le plan
lui donne une existence persistée à laquelle une séance peut se rattacher.

---

## Closeout (post-merge)

| | |
|---|---|
| PR | **#95** — `--merge --match-head-commit`, **sans** squash / `--admin` / force |
| Build | `a982a2b` — **vert au premier passage**, aucun correctif |
| Merge | **`b63b954`** |
| Gate Sonar | **`OK`** — couverture du neuf **100 %**, 0 smell, 0 bug, 0 vulnérabilité |
| Threads / Gitar | **0 / 0** |
| Tests | **4 147** (shard 1 : 2 191 · shard 2 : 1 956) |

### Capacité CI — **HEALTHY**

| | Shard A | Shard B |
|---|---|---|
| min MemAvailable | **4 746 Mo** | **5 817 Mo** |
| min SwapFree | 3 071 Mo — **jamais entamé** | 3 071 Mo — **jamais entamé** |

Les deux tiennent la cible ≥ 4 Go. Le shard le plus chargé alterne d'un run à
l'autre selon la répartition en tourniquet ; le **minimum des deux** reste la
grandeur à surveiller, et il tient entre 4,7 et 4,9 Go sur les trois tranches.

### Zéro incident

Première tranche du train verte **au premier passage** : pas de finding Sonar,
pas de conflit, pas de reprise de CI. Le pré-scan `S9073`/`S3415` ajouté après
la tranche 2 a fait son travail en amont plutôt qu'en réaction — 0 assertion
composite, 9 comparaisons toutes « actual first » vérifiées avant la poussée.

L'ordre **closeout de N avant branchement de N+1**, adopté après l'incident de
la tranche 2, a également tenu : la PR est sortie `MERGEABLE` d'emblée.
