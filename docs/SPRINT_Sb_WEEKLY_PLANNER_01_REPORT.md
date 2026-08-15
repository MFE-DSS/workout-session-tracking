# SPRINT Sb_WEEKLY_PLANNER_01 — Planificateur hebdomadaire (RAPPORT)

**Base canonique :** `58115a9` · **Branche :** `sb/weekly-planner-01` · **Tier :**
**SHARED_CODE**. **Tranche 2/3 du train `AUREN_CORE_ORCHESTRATION_01`.**
**0 persistance · 0 mutation de programme publié · 0 modif `recommendation.py` · 0 déploiement.**

## 1. Un moteur de proposition, pas la recommandation du jour

Le planificateur répartit un budget sur une semaine **déclarée** ; il ne choisit pas la
séance du jour. Les deux ne se lisent pas l'un l'autre, dans les deux sens, et des tests
l'épinglent.

## 2. Rien n'est reconstruit, aucune correspondance n'est inventée

La sélection d'exercice reste au générateur **fermé** `morpho_program_generator`, qui
possède déjà classement, départages déterministes, filtre d'équipement et distinction
*couverture* / *disponibilité*. Le planificateur fournit des intentions et interprète les
lacunes.

Les zones à servir viennent de la taxonomie `BodyZone` canonique du budget. Les clés de
priorité passées au générateur sont **dérivées** en inversant
`PRIORITY_TO_INTENTS × primary_zone` — si le registre bouge, la dérivation suit. Un test
vérifie qu'aucun jeton de priorité morphologique n'est écrit en dur ici.

## 3. Le résultat d'audit est le vrai livrable

Le registre `SlotIntent` est **fermé** et couvre **7 zones sur 11** en primaire. `biceps` et
`triceps` ne sont atteignables qu'en **secondaire** ; **`lats` et `core` par aucune
intention**.

Projeté sur les axes que `Sb_TRAINING_PREFERENCES_01` propose à l'utilisateur, **deux des
six ne sont pas servables** :

| Axe déclarable | Zones | Servable |
|---|---|---|
| `back_width` — Dos largeur | `lats` | **aucune intention** |
| `arms` — Bras | `biceps`, `triceps` | **secondaire seulement** |

**Un utilisateur peut déclarer une priorité que le planificateur ne sait pas programmer.**
La réponse correcte est de le dire : fabriquer une intention pour `lats` inventerait une
taxonomie d'exercice que personne n'a validée. Chaque zone non servie sort dans
`unmet_budget` avec une raison **nommée** (`no_slot_intent_covers_this_zone`), chaque axe
déclaré non servable sort dans `unmet_constraints` en français.

C'est une **limite produit mise au jour**, pas un défaut introduit — et sans elle, un
utilisateur se demanderait pourquoi son dos n'est jamais travaillé.

## 4. Cadence

La cadence déclarée est respectée exactement. **Non déclarée, aucune séance n'est
fabriquée** : inventer « 3 » transformerait une absence en fait utilisateur. La cadence
**répartit** le travail, elle n'en crée ni n'en retire — un test épingle le total de
créneaux **égal entre 2 et 5 séances**.

## 5. Déterminisme prouvé

Empreinte `sha256` sur la structure triée, stable d'une machine à l'autre là où un `hash()`
Python ne le serait pas. Mêmes entrées ⇒ plan et empreinte identiques ; cadence différente
⇒ empreinte différente. Aucune horloge, aucun aléa, aucune persistance.

## 6. Consommateur Home

Contexte hebdomadaire **à côté** de la décision du jour : séances proposées, prochaine
séance, et **une seule** contrainte non satisfaite — lister tous les manques transformerait
un bloc de contexte en rapport de défauts. **Parité de recommandation prouvée** : tuile
désactivée par panne injectée, `today` identique.

« Réalisé / restant » est **délibérément absent** : cela exige une détection de divergence
plan↔réel, qui appartient à la tranche 3. L'affirmer ici reviendrait à deviner quelle séance
enregistrée réalise quel créneau planifié.

## 7. Matérialisation — non tentée, et pourquoi

Le pont `WeeklyPlan → brouillon Custom Program → validation → publication` est réel mais non
trivial ; l'embarquer mettrait une mutation de cycle de vie dans un sprint de proposition.
Recommandé en suivi étroit (`Sb_WEEKLY_PLAN_MATERIALIZATION_01`). Le planificateur ne mute
rien aujourd'hui : `UserProgram`, `publish` et les écritures de statut sont interdits par
test.

## Verdict

**Livré, mergé, canonique verte.** Le plan existe, il est déterministe, et **il dit ce qu'il
ne sait pas faire**.

**Limite structurante** : deux axes déclarables sur six restent non programmables tant que
le registre d'intentions n'est pas étendu. C'est une décision produit — étendre le registre
exige de valider de nouvelles intentions d'exercice — et elle est désormais visible plutôt
que découverte à l'usage.

---

## 8. Closeout post-merge

| | |
|---|---|
| PR | **#91** — `MERGED` |
| Build → correctif Sonar → merge | `4d89542` → `951e392` → **`1769536`** |
| Gate | `CLEAN` · **8/8** · Sonar **`OK`**, couverture du neuf **99,3 %**, **0 smell** |
| Threads | **0** · Gitar **0 finding** |
| CI canonique | **`31875357294` GREEN** |
| Capacité | **HEALTHY** — **5 215 / 5 385 Mo**, swap intact |
| Manifeste | 229 fichiers ⇒ **115 + 114** |

**Un finding Sonar, réel et corrigé à la cause** : `python:S3776`, complexité cognitive
**20 contre 15**, sur `build_weekly_plan`. Localisé par le **CLI authentifié** (règle,
fichier et ligne en un appel), jamais déduit de l'écart de gate. La fonction faisait six
choses ; elle est décomposée en helpers nommés, comportement inchangé — mêmes 50 tests,
mêmes empreintes.

**50 tests dédiés**, 291 en régression ciblée.
