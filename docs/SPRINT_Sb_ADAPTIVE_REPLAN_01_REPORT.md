# SPRINT Sb_ADAPTIVE_REPLAN_01 — Replanification adaptative (RAPPORT)

**Base canonique :** `5c7d0e0` · **Branche :** `sb/adaptive-replan-01` · **Tier :**
**ISOLATED**. **Tranche 3/3 — clôture du train `AUREN_CORE_ORCHESTRATION_01`.**
**0 persistance · 0 mutation de programme publié · 0 second modèle de récupération ·
0 LLM · 0 déploiement.**

## 1. Une divergence réelle, sinon rien

Sans écart constaté entre le plan et ce qui s'est passé, le service renvoie
**explicitement** « aucune replanification ». Une churn quotidienne spéculative donnerait
l'illusion d'un système attentif tout en rendant le plan imprévisible.

Déclencheurs admis, et eux seuls : séance manquée · séance écourtée · séance matériellement
incomplète · changement de contrainte déclarée · récupération estimée incompatible avec le
travail prévu.

## 2. L'asymétrie est la tranche

| Preuve | Peut | Ne peut jamais |
|---|---|---|
| **Limitante** | reporter, redistribuer, réduire, laisser un manque explicite | — |
| **Optimiste** | — | dépasser le budget, ajouter des séries, monter la charge, créer une séance, outrepasser la cadence |

Une bonne readiness déclarée ne produit **aucune** replanification ; une zone récupérée
**aucun** delta ; et aucun delta ne peut augmenter un nombre de créneaux.

Ce n'est pas une prudence de façade. Un signal optimiste est presque toujours moins fiable
qu'un signal limitant — un utilisateur qui *se sent* frais peut se tromper, une séance non
faite est un fait — et un système qui monte la dose sur du déclaratif finirait par prescrire
davantage à ceux qui se plaignent le moins.

## 3. Discipline de preuve

`Confidence.NONE` **ne fabrique aucune contrainte** : une absence de preuve n'est pas une
preuve de contrainte, règle P0.4 appliquée telle quelle. **Seule P0.4 est lue** — un second
modèle de fatigue finirait par diverger du premier.

Les manques **structurels survivent** à la replanification : redistribuer ne comble pas un
trou que le planificateur n'a jamais su servir, donc `lats` et `core` restent dans
`unmet_budget_after`.

## 4. Versionnement

Rien de publié n'est muté sur place. Une replanification produit une **nouvelle version**
portant l'empreinte d'origine, la divergence, le delta déterministe et sa raison —
l'historique reste lisible et l'on peut toujours dire *pourquoi* la semaine a changé. Le
travail est **reporté, pas déclaré inutile**.

## 5. La plantation a trouvé un trou dans mes propres tests

Trois violations plantées ont bien fait échouer les gardes d'asymétrie. **Une quatrième a
révélé mieux** : retirer le filtre `Confidence.NONE` ne cassait **rien**, parce que le
contrôle de bande couvrait à lui seul tous les cas que j'avais écrits. La garde n'était pas
porteuse.

Le cas manquant — **bande limitante AVEC confiance nulle** — est désormais testé, et une
re-plantation prouve qu'il mord. C'est exactement la combinaison où cette garde gagne sa
place.

## 6. Corrigé avant le push

`python:S5863` (`assert f(x) == f(x)` — le motif pourtant déjà consigné en mémoire, que j'ai
réécrit malgré tout) · un littéral répété 14 fois · et une décomposition **préventive** de
`detect_divergences` : `S3776` avait mordu la tranche 2 sur exactement cette forme, le
pré-scan inclut désormais un contrôle de complexité.

## Verdict

**Livré, mergé. Train complet.**

Ce que la tranche garantit vraiment : le système peut **réduire** ce qu'il propose sur
preuve, et ne peut **pas** l'augmenter sur optimisme. C'est la propriété qui rend une
replanification automatique acceptable — sans elle, un planificateur adaptatif dérive vers
« toujours plus » à chaque bonne journée déclarée.

**Limite assumée** : `completed_sessions` est un **compte**, pas un rapprochement
plan↔séance. Rapprocher une séance enregistrée d'un créneau planifié exigerait une identité
que rien ne persiste encore ; la deviner produirait des divergences fantômes. C'est aussi
pourquoi « réalisé / restant » n'est toujours pas affiché sur la Home.

---

## 7. Closeout post-merge

| | |
|---|---|
| PR | **#92** — `MERGED` |
| Build → merge | `3ffd367` → **`7bda441`** |
| Gate | `CLEAN` · **8/8** · Sonar **`OK`**, couverture du neuf **100 %**, **0 smell** |
| Threads | **0** · Gitar **0 finding** |
| Capacité | **HEALTHY** — **5 306 / 5 220 Mo**, swap intact |
| Manifeste | 230 fichiers ⇒ **115 + 115** |

**36 tests dédiés**, **436** en régression ciblée sur la chaîne P0.4 + planification.
