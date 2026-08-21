# `UX4_03A_BEHAVIORAL_SIGNAL_SEMANTICS` — OPERATOR REVIEW

**Audit sémantique des signaux comportementaux avant toute exposition.**
Aucun commit du rendu `UX4_03` actuel. Aucun calcul nouveau écrit.

---

## 0. Verdict en une phrase

Vos trois blocages sont confirmés par la mesure, et **le dépôt avait déjà
écrit la règle que ma tranche a violée** — dans `recovery_contract.py`, en
toutes lettres, depuis `Sb_FATIGUE_SCALE_FIX_01`.

---

## 1. Ce que le dépôt avait déjà tranché

Votre §6 demande un contrat épistémique. **Il existe déjà**, il est versionné,
et il interdit précisément ce que `UX4_03` a rendu.

### 1.1 — La phrase qui condamne le `45/100`

`app/services/recovery_contract.py:196-199`, dans `normalize_session_feedback` :

> Both inputs ``None`` → ``None``: ``compute_session_fatigue`` would happily
> return its 50/40 defaults, but **"the user told us nothing" is not a
> measurement and must not be dressed up as a neutral reading.**

C'est votre formulation — *« une donnée manquante doit rester manquante »* —
déjà présente dans le code, écrite par une tranche antérieure. Ma tranche a
contourné ce normaliseur en lisant `behavioral.fatigue_score` brut.

### 1.2 — L'agrégat est interdit par construction

`recovery_contract.py:796-807`, `FatigueSignal` :

> There is deliberately **no aggregate**. Someone fatigued by an hour of
> cycling and someone fatigued by heavy squats are not in the same situation,
> and collapsing them into one number destroys exactly the information an
> explanation surface needs. Weighting the three components would also require
> **coefficients no evidence in this repository supports.**

`FatigueSignal` garde trois composantes séparées
(`strength_component` · `cardio_component` · `subjective_component`) plus
`sufficiency`, `confidence` et `basis`. Mon `45/100` est exactement le scalaire
que ce contrat refuse de produire.

`recovery_contract.py:1032` le redit au niveau `TrainingState` :
« no ``readiness_score``, no ``recovery_percentage``, **no opaque composite** ».

### 1.3 — Réponse à votre question d'audit

> *« Auditer si `TrainingState` / `FatigueSignal` est désormais le consommateur
> canonique approprié. »*

**Oui, sans réserve.** Il porte déjà le vocabulaire que vous demandez :

| Votre demande §6 | Ce qui existe déjà |
|---|---|
| classer FACT / DERIVED / ESTIMATE / UNKNOWN | `Sufficiency` = `SUFFICIENT` · `PARTIAL` · `INSUFFICIENT` · `STALE` |
| dire la fiabilité | `Confidence` = `HIGH` · `MEDIUM` · `LOW` · `NONE` |
| ne pas inventer une bande | `RecoveryBand.UNKNOWN` |
| dire d'où ça vient | `FatigueSignal.basis: tuple[str, ...]` |
| refuser la valeur inutilisable | `normalize_fatigue_score()` → `None` |

La bonne tranche n'est donc pas « corriger les libellés de `UX4_03` ». C'est
**brancher la surface sur `TrainingState`** au lieu de `BehavioralState`.

---

## 2. Les quatre signaux — les huit champs exigés

### 2.1 — `fatigue_score` → affiché « Charge ressentie 45/100 »

| Champ | Constat |
|---|---|
| **Producteur** | `behavioral.compute_session_fatigue()` puis `compute_weighted_fatigue()` (`behavioral.py:34-58`) |
| **Entrées brutes** | `session.global_state` et `session.concentration` — **deux déclarations verbales** de fin de séance, mappées par table (`fatigued`/`flat`/`good` → 80/50/20 ; `low`/`medium`/`high` → 70/40/10). **Aucun tonnage, aucune série, aucun volume.** |
| **Sémantique du manque** | ⚠ **aucune.** Mesuré : sans déclaration → **45,0** · sans historique → **50,0**. Le manque produit un nombre au milieu de l'échelle, indiscernable d'une mesure. |
| **Fenêtre** | 3 dernières séances terminées, pondérées 0,5 / 0,3 / 0,2. **Pas de filtre `kind`** — une séance de cardio y entre (`training_state.py:31-34`). Pas de borne temporelle : trois séances d'il y a six mois pèsent autant. |
| **Consommateurs réels** | `recommendation.py:402` (seuil de filtrage de templates) · `training_state._subjective_component()` via `normalize_legacy_fatigue` · `recommendation_explainer:227` · **`progress.html:41` (ma tranche, non mergée)** |
| **Libellé actuel** | « Charge ressentie **45**/100 » + jauge |
| **Libellé que le calcul justifie** | « Ressenti déclaré en fin de séance », **sans échelle numérique** — la pondération 0,5/0,3/0,2 n'a aucune justification documentée, et le contrat interdit l'agrégat scalaire |
| **L1 proposé** | `Charge perçue · modérée` — ou **`· inconnue`** dès que `_has_recent_declaration()` est faux |

### 2.2 — `consistency_score` → affiché « Régularité 0/100 »

| Champ | Constat |
|---|---|
| **Producteur** | `behavioral.compute_consistency()` (`behavioral.py:60-61`) |
| **Entrées brutes** | un entier : `sessions_14d`. Formule complète : `min(100, sessions_14d / 14 × 100)` |
| **Sémantique du manque** | 0 séance → **0,0**. Indiscernable d'un « mesuré à zéro ». Aucun état inconnu possible. |
| **Fenêtre** | 14 jours glissants |
| **Consommateurs réels** | voir §3 — **la readiness en fait partie, vous aviez raison** |
| **Libellé actuel** | « Régularité **0**/100 » + jauge |
| **Libellé que le calcul justifie** | **aucun** sur une échelle /100. Le dénominateur 14 pose *une séance par jour* comme le 100 % — soit une norme que ni le produit ni la littérature ne soutiennent. Mesuré : 3 séances / 14 j → **21/100**, ce qui affiche un rythme sain comme un quasi-échec. |
| **L1 proposé** | `3 séances · 14 j` — un **comptage**, sans dénominateur, sans jauge, sans /100 |

> ⚠ Je ne propose **aucune formule de remplacement**. Vous l'avez interdit, et
> définir la régularité est une décision produit, pas un choix de gabarit.

### 2.3 — `trend_direction` → affiché « Continuité stable »

| Champ | Constat |
|---|---|
| **Producteur** | `behavioral.compute_trend(last_7, prev_7)` (`behavioral.py:70-75`) |
| **Entrées brutes** | deux **comptages de séances**. Trois branches : `>` → `up`, `<` → `down`, sinon `stable`. |
| **Sémantique du manque** | ⚠ **le défaut le plus grave de la tranche.** Mesuré : `compute_trend(0, 0)` → **`"stable"`**. Un utilisateur qui n'a **jamais** rien fait lit « Continuité **stable** ». |
| **Fenêtre** | 7 jours vs les 7 précédents |
| **Consommateurs réels** | `behavioral.compute_recommendation:86` · **`progress.html:78` (ma tranche)** |
| **Libellé actuel** | « **Continuité** — stable » |
| **Libellé que le calcul justifie** | « Cadence 7 j » — c'est une **comparaison de deux comptages**, pas une continuité. « Continuité » promet une propriété du temps ; le calcul ne connaît que deux nombres. |
| **L1 proposé** | `Cadence 7 j · 4 → 2 séances`. Et pour `0 → 0` : **`aucune séance sur 14 j`**, jamais « stable » |

**Ce défaut était visible sur ma propre capture** : « Continuité stable » et
« 0 session cette semaine » figuraient sur le même écran, à trois blocs
d'écart. Je l'ai regardée et je ne l'ai pas vu.

### 2.4 — `streak_days` → non rendu par `UX4_03`… mais rendu ailleurs

| Champ | Constat |
|---|---|
| **Producteur** | ⚠ **il y en a deux, aux règles différentes** |
| ① `behavioral.py:190-193` | jours calendaires consécutifs, **rupture stricte à aujourd'hui**, pas de jour de grâce |
| ② `profile_metrics.streak_days()` (`profile_metrics.py:62-93`) | jour de grâce (aujourd'hui **ou** hier, pour l'UTC), filtre `status == completed`, filtre `excluded_from_stats` |
| **Sémantique du manque** | 0 — indiscernable d'une série rompue |
| **Consommateurs réels** | ① `compute_recommendation:82,92` · ② `coach_report.py:165` → **`coach_report.html:62`, rendu à l'écran sous le libellé « Streak »** |
| **Libellé actuel** | `UX4_03` : aucun. **`coach_report.html` : « Streak »** |
| **L1 proposé** | aucun — voir §4 |

---

## 3. Registre demandé — tous les consommateurs de `consistency_score`

**Vous aviez raison sur la readiness, et mon premier relevé l'avait manquée.**
Un `grep consistency_score` ne la trouve pas : `compute_readiness` reçoit la
valeur comme **paramètre local nu**, sans le suffixe.

| # | Consommateur | Lecture | Statut sémantique |
|---|---|---|---|
| 1 | `behavioral.compute_readiness()` `behavioral.py:64-68` | `0,5 × (100 − fatigue) + 0,3 × consistency + 0,2 × performance` | ⚠ **composite opaque** — voir §3.1 |
| 2 | `behavioral.compute_recommendation()` `behavioral.py:84` | `< 30` → « La régularité est la clé. » | seuil non justifié : 4 séances / 14 j déclenchent le message |
| 3 | `progress.html:63,66` | **ma tranche, non mergée** | à retirer |

**Il n'y a pas d'autre consommateur dans `app/`.**
`app/services/readiness.py` et le modèle `readiness_entries` sont **une autre
chose** : un questionnaire quotidien déclaré par l'utilisateur, sans aucun lien
de calcul avec `consistency`.

### 3.1 — La readiness dérivée est déjà condamnée par le dépôt

`recovery_contract.py:171-182` :

> **No field of `TrainingState` consumes it (OQ-1).**
> `behavioral.readiness_score` is **the duplicate the audit found**: it shares
> the word "readiness" with the user's declared questionnaire while measuring
> something else entirely. It stays a legacy producer with its current UI, and
> it is **a candidate for visible deprecation** once the new surface exists.

**Mesure de bout en bout, utilisateur qui n'a jamais rien fait :**

```
fatigue     = 50,0   ← défaut « aucun historique »
consistency =  0,0
performance =  0,0
readiness   = 25,0   ← 0,5 × (100 − 50) + 0,3 × 0 + 0,2 × 0
```

**La totalité des 25 points vient du défaut de fatigue.** La readiness d'un
utilisateur sans données est intégralement fabriquée — et elle est déjà
affichée comme « disponibilité » (`home_training_state.py:41`, KPI **hérité**).

---

## 4. Streak — la décision et la contradiction déjà en production

Votre décision : `streak_days → OPERATOR_DECISION / DO_NOT_SURFACE`.

**Elle est déjà violée par une surface livrée**, et l'enregistrer sans le dire
laisserait le registre faux :

| Occurrence | État |
|---|---|
| `coach_report.html:62` — `<span>Streak</span>` | ⚠ **rendu en production**, producteur ② |
| `compute_recommendation:92` — « **Série en cours**, garde le rythme ! » | ⚠ **rendu en prose**, producteur ① |
| `compute_recommendation:82` — « **Belle série !** Mais pense à récupérer » | ⚠ rendu en prose |

Le deuxième point mérite d'être dit franchement : ma garde `A4`
(`test_the_daily_streak_is_never_rendered`) bannit la chaîne `"série en cours"`
du corps de `/progress`, **pendant que le même dépôt l'émet depuis
`behavioral.py`**. La garde protège une page ; elle ne protège pas la décision.

`DO_NOT_SURFACE` demande donc une portée explicite de votre part :
la nouvelle surface seulement, ou aussi le retrait des trois occurrences
existantes ? Le retrait de « Streak » du rapport coach serait une
**soustraction** — `CLAUDE.md §5.3` exige qu'elle parte avec son remplacement.

---

## 5. Classification épistémique des quatre signaux

Selon le vocabulaire **déjà versionné** dans `recovery_contract` :

| Signal | Classe | `Sufficiency` réelle | `Confidence` réelle |
|---|---|---|---|
| `fatigue_score` | **ESTIMATE-SUBJECTIVE**, dégradant en **UNKNOWN** | `INSUFFICIENT` sans déclaration ; **jamais** `SUFFICIENT` (aucune composante de charge) | `LOW` au mieux, `NONE` sans déclaration |
| `consistency_score` | **DERIVED** d'un FACT (comptage) — mais le **/100 est un ESTIMATE** (le dénominateur 14 est une norme non fondée) | `SUFFICIENT` pour le comptage | `HIGH` pour « N séances », `NONE` pour « /100 » |
| `trend_direction` | **DERIVED** de deux FACTs | ⚠ **`INSUFFICIENT` quand les deux fenêtres valent 0** — état actuellement absent du calcul | `HIGH` si ≥ 1 séance, sinon `NONE` |
| `streak_days` | **DERIVED** d'un FACT, **deux définitions concurrentes** | `SUFFICIENT` | ⚠ `LOW` — deux producteurs peuvent afficher deux valeurs différentes le même jour |

**Aucun des quatre n'est un FACT présentable tel quel.** Trois des quatre
manquent d'un état `UNKNOWN` que le calcul ne sait pas produire aujourd'hui.

---

## 6. Instrument compact proposé — `SIGNAUX D'ENTRAÎNEMENT`

Votre §5 interdit les ~77 mots supplémentaires. Proposition **L1 seul**, une
ligne par signal, un seul dépliant L2 partagé :

```
SIGNAUX D'ENTRAÎNEMENT

  Charge perçue      modérée · 3 dernières séances
  Séances            3 · 14 derniers jours
  Cadence 7 j        2 → 1 séance

  › Comment AUREN calcule ces signaux
```

Et l'état vide, qui n'existe pas aujourd'hui :

```
  Charge perçue      inconnue · aucun ressenti déclaré
  Séances            aucune · 14 derniers jours
  Cadence 7 j        —
```

| Règle | Raison |
|---|---|
| aucun `/100`, aucune jauge | le contrat interdit l'agrégat scalaire (§1.2) |
| le contexte temporel **dans** la ligne | supprime les trois `signal__note` (−77 mots) |
| une seule divulgation L2 | trois provenances → une explication partagée |
| `—` plutôt que « stable » sur `0 → 0` | corrige le défaut §2.3 |
| bandes de « charge perçue » | ⚠ **décision opérateur requise** — je n'invente aucun seuil |

Pour les bandes, une piste **déjà versionnée** plutôt qu'un vocabulaire neuf :
`RecoveryBand` (`LIKELY_AVAILABLE` · `PARTIALLY_RECOVERED` · `LIKELY_FATIGUED` ·
`UNKNOWN`). Elle porte déjà le « likely » qui dit l'incertitude.

---

## 7. Ce que je n'ai pas fait, et pourquoi

- **Aucun commit.** `PR #138` reste ouverte, verte (8 checks, gate `OK`,
  0 issue, `MERGEABLE/CLEAN`, tête `e32576e`) et **ne doit pas être mergée en
  l'état**. Le rendu actuel est celui que vous refusez.
- **Aucune formule de remplacement** pour la régularité — vous l'avez interdit.
- **Aucun seuil de bande** inventé pour la charge perçue.
- **Aucun retrait** de « Streak » du rapport coach : ce serait une soustraction
  seule (`§5.3`), et sa portée est votre décision.

---

## 8. Décisions opérateur requises pour ouvrir `UX4_03B`

| # | Question | Pourquoi elle vous revient |
|---|---|---|
| **D1** | La surface se branche-t-elle sur **`TrainingState`** plutôt que `BehavioralState` ? | C'est le vrai correctif (§1.3), et c'est un changement de périmètre par rapport au brief `UX4_03` |
| **D2** | Bandes de « charge perçue » : `RecoveryBand` existante, ou vocabulaire neuf ? | Aucun seuil n'est documenté dans le dépôt |
| **D3** | Portée de `DO_NOT_SURFACE` sur le streak : nouvelle surface seule, ou aussi les 3 occurrences livrées ? | Le retrait est une soustraction (§5.3) |
| **D4** | `behavioral.readiness_score` : dépréciation visible, comme `recovery_contract` l'anticipe ? | Le dépôt l'a nommé « candidate for visible deprecation » sans fixer la date |
| **D5** | `compute_consistency` : le `/100` disparaît-il **du calcul** ou seulement de l'écran ? | Deux consommateurs internes lisent encore l'échelle (§3) |

---

---

## 9. `UX4_03B_BEHAVIORAL_CONSUMER_ALIGNMENT` — tranche enregistrée

**Décision opérateur du 2026-08-21.** Les quatre défauts ci-dessous sont
**réels, mesurés, et hors du périmètre du correctif de surface**. Ils sont
consignés ici plutôt que corrigés au passage : élargir un patch de vocabulaire
en refonte de quatre consommateurs est exactement la dérive de périmètre que
`CLAUDE.md §4` érige en arrêt dur.

**Cette tranche doit être terminée AVANT le closeout final d'`UX4_03`.**

| # | Défaut | Preuve | Priorité |
|---|---|---|---|
| **B1** | `readiness_score` consomme le `consistency_score` hérité — `0,5 × (100 − fatigue) + 0,3 × consistency + 0,2 × performance` | mesuré : utilisateur sans données → `readiness = 25,0`, dont **100 % vient du défaut de fatigue** | ⚠ **la plus haute** — désignée par l'opérateur |
| **B2** | « Streak » rendu dans le rapport coach, par un **second** producteur | `coach_report.html:62` ← `profile_metrics.streak_days` (jour de grâce + filtres) ≠ `behavioral.streak_days` (rupture stricte, **aucun filtre `completed` ni `excluded_from_stats`**) | haute — contredit `DO_NOT_SURFACE` |
| **B3** | `compute_recommendation` écrit « **Série en cours**, garde le rythme ! » et « Belle série ! » | `behavioral.py:82,92` — chaîne bannie par la garde `A4` sur `/progress`, émise ailleurs par le même dépôt | haute |
| **B4** | Les trois cartes de `weekly_loop` affichent « pas encore assez de données » en tête de Progression | motif condamné par la doctrine d'augmentation : *un module vide guide ou disparaît* | moyenne |

Contraintes héritées de la décision : **aucune formule nouvelle · aucun modèle
physiologique nouveau · aucune refonte de l'Accueil.** Un retrait de « Streak »
ou d'une carte vide part avec son remplacement (`§5.3`).

`recovery_contract:177` nomme déjà `behavioral.readiness_score` « *the
duplicate the audit found… candidate for visible deprecation* » : **B1 n'ouvre
pas un débat, il exécute une décision déjà écrite** dont la date n'avait jamais
été fixée.

---

**`UX4_03A_BEHAVIORAL_SIGNAL_SEMANTICS` — OPERATOR REVIEW. STOP.**
