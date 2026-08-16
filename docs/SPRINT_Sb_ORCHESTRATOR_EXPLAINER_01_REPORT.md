# SPRINT Sb_ORCHESTRATOR_EXPLAINER_01 — « Pourquoi ce plan ? » (RAPPORT)

**Train :** `AUREN_DECISION_OBSERVABILITY_01`, tranche 2/2 ·
**Base canonique :** `2b0f1d9` · **Branche :** `sb/orchestrator-explainer-01`

Ouverte **après** le gate de reprise produit : `Sb_OPS_CI_SCALE_02` mergée,
canonique verte, nettoyée, et **tous les shards ≥ 6 Go**.

---

## 1. Brainstorming / Options / Risques / Choix retenu

Le risque de cette tranche n'est pas technique, il est **épistémique**. Une page
« Pourquoi ce plan ? » peut détruire en une phrase ce que quatre tranches ont
payé pour construire : la distinction entre *ce que l'utilisateur a déclaré*,
*ce que le produit conventionne*, *ce qui a été mesuré* et *ce qui a été estimé*.

**Options de formulation.** (a) une prose unique « voici pourquoi » — rejetée,
c'est précisément l'aplatissement que la spec de traces interdit ; (b) exposer
les jetons de source — rejetée, `USER_DECLARED` n'est pas une phrase française ;
(c) *(retenue)* **un dictionnaire fermé d'étiquettes**, une par nature, rendu à
côté de chaque explication.

**Risque de fausse promesse morphologique.** Le profil affiche des descripteurs
morphologiques depuis `Sb_MORPHO_PROFILE_READMODEL_01`. Les faire apparaître
ici affirmerait que le planificateur les consomme — **c'est faux**. Exclusion
explicite, testée, et plantée.

**Risque d'explication fabriquée.** Sans trace, la tentation est de reconstruire
une justification depuis le plan lui-même. Refusé : la surface dit qu'elle n'a
rien à montrer.

---

## 2. Ce qui est livré

Carte « Pourquoi ce plan ? » sur `/programs`, **sous** la proposition
hebdomadaire. Lecture seule : aucun `db.add`, `db.commit`, `db.delete` ni
`db.merge` dans le module (vérifié par test).

Au plus **5** explications, dans l'ordre de valeur causale : cadence déclarée →
priorités déclarées → convention produit → contrainte de catalogue réellement
rencontrée → récupération **si elle a pesé**.

Sortie réelle sur la fixture cadence 4 / priorité `arms` :

| Nature | Explication rendue |
|---|---|
| Selon tes préférences | « Tu as demandé 4 séances par semaine. » |
| Selon tes préférences | « Tu as placé biceps parmi tes priorités. » |
| Selon tes préférences | « Tu as placé triceps parmi tes priorités. » |
| Convention de planification | « Auren planifie chaque zone dans une fourchette de volume hebdomadaire… » |
| Contrainte du catalogue | « La zone « pecs » n'a pas pu être servie complètement avec le matériel déclaré. » |

La récupération **n'apparaît pas** : aucun replan n'a tourné, donc aucune source
de récupération n'existe — et aucune n'est inventée.

---

## 3. La plantation qui a demandé trois essais

**Essai 1 — morphologie ajoutée en fin de liste : 26 tests verts.**

Deux défauts se cachaient l'un derrière l'autre :

1. `EXCLUDED_FROM_PLAN_REASONS` comparait `item.source_label` — une chaîne
   française — à `{"MORPHOLOGY_INFERENCE"}`, un jeton. **Le filtre ne filtrait
   rien.** C'était du code mort qui avait l'air d'un garde-fou.
2. La troncature à 5 éléments s'appliquait **après**, donc l'élément planté,
   ajouté en dernier, tombait hors plafond. Il était invisible **pour la
   mauvaise raison**.

**Correction** : `ExplanationItem` porte désormais `source_kind` (le jeton,
jamais rendu) **et** `source_label` (le français, seul rendu) ; le filtre
s'applique sur la **nature**, et **avant** la troncature.

**Essai 2 — morphologie en tête de liste : toujours vert.** Correct cette fois :
le filtre corrigé la retirait. Une plantation que le code neutralise
**n'est pas** un défaut observable.

**Essai 3 — filtre désactivé *et* élément injecté : 3 gardes tombent** —
`test_morphology_never_appears_as_a_plan_reason`,
`test_the_rendered_section_never_mentions_morphology` (page rendue) et
`test_every_rendered_item_carries_an_allowed_nature`.

La leçon vaut d'être écrite : **une plantation doit produire un défaut
observable**. Neutraliser le correctif fait partie de la plantation.

---

## 4. Preuves

| Preuve | Résultat |
|---|---|
| Tests dédiés | **28** |
| Balayage ciblé (explainer, traces, programmes, readmodel, planner) | **197** |
| Budget ruff | 536 ≤ 548 |
| Pré-scan Sonar S9073 / S1192 | **0 / 0** |
| Écriture en base depuis l'explainer | **aucune** |

Garanties tenues : aucun pourcentage rendu · aucun jeton d'énumération rendu ·
aucune formulation « l'IA pense que » · alternatives rejetées **jamais**
visibles · confiance **jamais** inventée pour une préférence déclarée ou une
convention produit · même trace ⇒ sortie identique · aucun LLM (test sur le
source) · `/programs` répond **200** même si l'explainer lève.

---

## 5. Isolation

Aucun des **8 modules gelés** ne mentionne `orchestrator_explainer`. Charger
`/programs` ne déplace pas l'empreinte du plan hebdomadaire. Le module est
importé par la seule route de liste des programmes.

## 6. Limites énoncées

- **La récupération n'est encore jamais causale** : `REPLAN_DELTA` et
  `RECOVERY_ASSESSMENT` ne sont pas écrits par la tranche 1, donc la branche
  correspondante existe mais ne se déclenche pas. Elle est écrite pour le jour
  où le replan sera tracé — pas simulée en attendant.
- **Les traces n'existent qu'après matérialisation** : un utilisateur qui n'a
  jamais créé de brouillon voit l'état « indisponible », ce qui est exact.
- **Alternatives rejetées** : persistées vides, et de toute façon non exposées
  en V1.

## Verdict

La page explique **ce qui a réellement produit le plan**, en gardant visible la
nature de chaque raison — déclarée, conventionnelle, contrainte.

Le vrai piège n'était pas d'écrire les phrases : c'était de croire qu'un filtre
existait parce qu'une constante portait son nom. Il comparait une étiquette
française à un jeton, et la troncature masquait le reste.

---

## Closeout (post-merge)

| | |
|---|---|
| PR | **#108** — `--merge --match-head-commit`, **sans** squash / `--admin` / force |
| Build | `80e21b1` — **vert au premier passage**, aucun correctif |
| Merge | **`c646378`** |
| CI canonique | run `31948768149` — **succès, 6/6** |
| Gate Sonar | **`OK`** — 0 smell, 0 bug, 0 vulnérabilité, couverture new code **89,9 %** |
| Threads / Gitar | **0 / 0** |
| Contrats gelés | diff **vide** (9 modules + `AGENTS.md`) |

### Capacité sous la nouvelle topologie — **HEALTHY**

| Shard | Fichiers | Tests | min MemAvailable | min SwapFree |
|---|---|---|---|---|
| 1 | 82 | 1 507 | **8 040 Mo** | 3 071 — intact |
| 2 | 82 | 1 422 | **6 354 Mo** | 3 071 — intact |
| 3 | 81 | 1 580 | **8 309 Mo** | 3 071 — intact |

Tous les shards restent **au-dessus de 6 Go** avec la tranche ajoutée, donc
très au-dessus du plancher de 4 Go : aucune règle d'arrêt ne se déclenche et
une tranche runtime supplémentaire reste permise.

**Observation sur le déséquilibre.** Le shard bas n'est plus le même : c'était
le 1 (6 241 Mo) sous SCALE_02, c'est le 2 (6 354 Mo) ici. Le déséquilibre
**suit la partition**, pas une machine — le round-robin a redistribué les
fichiers quand celui de cette tranche est arrivé. Cela confirme que le coût est
porté par le **contenu** des fichiers, et qu'un déséquilibre observé une fois
n'incrimine aucun runner en particulier. Toujours consigné, toujours non
corrigé : la pondération reste interdite tant que la capacité tient.
