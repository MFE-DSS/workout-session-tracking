# SPIGNOS Recommendation V2 — Antagonist & Recovery Logic Spec v1

**Sprint ID :** Sx_18_reco_v2_antagonist_spec
**Date :** 2026-04-21
**Statut :** SPEC ONLY — base scientifique + arbitrage produit, aucune ligne de code
**Origine :** dogfooding J+0 §F2 (« il faudrait faire séance logique pour qu'on fasse le choix chronologique de groupes musculaires antagonistes ou suc qui est le plus efficace selon la science »)
**Successeur :** Sb_18_reco_v2_antagonist_build

---

## A. Statut

Spec d'arbitrage produit + design moteur V2. Le moteur V1 (Sb_12) trie les templates par `staleness_by_zone` agrégée sur 7 j ; il ne connaît ni les antagonismes, ni le timing fin de récupération par groupe. Cette spec pose la base scientifique, propose une heuristique déterministe, et cadre le scope du build Sb_18.

## B. Contexte produit

### B.1 Le moteur Sb_12 actuel

`recommend_next_session` score les templates non-archived selon 4 composants :

```
score = 40·staleness  +  20·alternation_kind  −5·redundancy_48h  +  catalog_affinity
```

Avec :
- `staleness_by_zone[z] = 1 - hard_sets_7d[z] / 8` (clamp 0..1).
- Pas de notion d'antagonisme ; pas de notion de timing par zone.
- Filtres : archived exclu, fatigue > 70 → short/LISS only, redundancy > 8 hard sets / 48h → exclu.

Limite produit observée en dogfooding J+0 : si l'utilisateur a fait deux séances Push successives, le moteur va proposer Pull ou Legs **par défaut** parce que la staleness des zones push est faible. Mais il ne dit **pas** *pourquoi* c'est physiologiquement cohérent, et il ne distingue pas les cas suivants :

- Push hier 18h → Pull aujourd'hui 18h (24 h de récup pour les pecs / triceps — minimal) : **OK** scientifiquement (groupes différents).
- Push hier 18h → Push aujourd'hui 18h (24h de récup pour les **mêmes** groupes) : **PAS OK** — le moteur Sb_12 le rejette via redundancy mais sans wording explicite.
- Push hier 18h → Legs aujourd'hui 18h : **idéal** — antagoniste haut/bas, récupération maximale.
- Push samedi → Pull lundi → Legs mercredi → Push vendredi : pattern hebdomadaire classique PPL, déjà optimal.

L'utilisateur veut que le moteur **comprenne et explique** ces dimensions.

### B.2 Demande utilisateur intégrale (notes dogfooding)

> « la séance qui pourrait suggérer, ça serait sur un muscle qui serait en tout logique pas travaillé, ou du moins être encore en récupération, donc peut-être une séance jambes je sais pas, du moins il faudrait faire séance logique pour qu'on fasse le choix chronologique de faire des groupes musculaires antagonistes ou suc qui est le plus efficace selon la science en réalité, et c'est-à-dire peut-être faire une autre séance sur un autre muscle ou peut-être en réalité sur le même. C'est à toi de faire les recherches scientifiques pour constater ce qui est le mieux dans en fait le cercle vertueux ou plutôt l'enchaînement, de quel type de séance pour quel muscle doit se faire l'une derrière l'autre. »

Décodage : (1) prendre en compte le délai de récupération réel par groupe musculaire, (2) intégrer une logique d'antagonisme push/pull/legs ou agoniste/antagoniste, (3) baser tout ça sur la littérature scientifique récente, pas une intuition.

## C. Base scientifique

### C.1 Récupération musculaire par groupe — état de la littérature

Synthèse des consensus récents (méta-analyses 2018–2024 sur EMG, force, hypertrophie, DOMS) :

| Groupe musculaire | Temps de récupération typique post-séance haute intensité |
|-------------------|-----------------------------------------------------------|
| Quadriceps | **48–72 h** (volume élevé, fibres lentes/rapides mixtes, DOMS plus longs) |
| Ischios / fessiers (chaîne postérieure) | **48–72 h** |
| Pectoraux | **48 h** |
| Dorsaux (lats) / dos d'épaisseur | **48 h** |
| Deltoïdes (postérieurs / latéraux / antérieurs) | **24–48 h** (utilisé indirectement sur push **et** pull, donc fragmenté) |
| Triceps | **24–48 h** (souvent indirectement sollicité) |
| Biceps | **24–48 h** |
| Mollets | **24–48 h** (haute densité, récupération rapide) |
| Core | **24 h** (sauf travail dynamique lourd) |

**Sources clés :** Schoenfeld (2017–2023) sur la fréquence d'entraînement ; Helms & Aragon sur la récupération volume-dépendante ; Heaselgrave et al. 2019 sur l'optimum 12–20 sets/semaine par groupe ; Krieger 2010 (méta-analyse séries multiples vs uniques).

**Implications produit :**

- La fenêtre de 48 h utilisée par le filtre `redundancy` de Sb_12 est **scientifiquement fondée** pour les zones « rapides » (delts, biceps, triceps, mollets, core).
- Pour les **gros groupes** (quads, posterior, pecs, lats), une fenêtre **72 h** serait plus précise. Le moteur V1 sous-estime le besoin de récupération sur ces zones.

### C.2 Antagonismes et synergies

L'antagonisme musculaire se décline en 3 niveaux pertinents pour SPIGNOS :

#### Niveau 1 — Push / Pull (haut du corps)

- **Push** : pectoraux, deltoïdes (antérieur/latéral), triceps.
- **Pull** : grand dorsal, dos d'épaisseur, biceps, deltoïde postérieur.

Ces deux groupes sont **antagonistes fonctionnels** : ils s'opposent sur les mouvements de bras (extension vs flexion d'épaule). Une séance Push n'épuise pas les muscles de la séance Pull, et vice-versa. Donc enchaîner **Push J → Pull J+1** est physiologiquement défendable.

**Caveat :** les **deltoïdes postérieurs** appartiennent au plan « pull », mais ils sont aussi sollicités sur les `face pull`, `rear delt fly`, `reverse fly`. Si tu fais Push avec `face pull` en finisseur, tu pré-fatigues les rear delts qui réapparaîtront en Pull demain. Cette interdépendance est mineure mais réelle.

#### Niveau 2 — Haut / Bas (ou Upper / Lower)

- **Haut du corps** : pecs, dos, épaules, bras.
- **Bas du corps** : quadriceps, postérieur, mollets.

Antagonisme parfait : un haut du corps n'épuise jamais un bas du corps (sauf core qui est sollicité sur les compounds debout). Donc **Haut J → Bas J+1** est l'option la plus sûre pour la récupération, et c'est le pattern Upper/Lower 4×/sem qui est très populaire scientifiquement.

#### Niveau 3 — Push / Pull / Legs (split classique)

Le catalogue SPIGNOS suit ce split : `push-a/b`, `pull-a/b`, `legs-a/b`. Rotation 3 jours :
- Cycle J / J+1 / J+2 / J+3 : Push → Pull → Legs → Push (ou rest).
- Aucune zone primaire n'est re-stimulée < 72 h, ce qui respecte la borne haute des gros groupes.

**Pattern PPL = optimal scientifique pour 3 séances strength/sem** (Schoenfeld 2017 sur fréquence ≥ 2/sem par groupe, 48–72 h récup respectée).

### C.3 Intégration cardio (LISS)

Le cardio LISS faible intensité (zone aérobie 60–70 % FC max) **ne crée pas de fatigue neuromusculaire significative** sur les zones strength. Donc :

- **LISS J → Strength J+1** : aucun risque, récupération non impactée.
- **Strength J → LISS J+1** : LISS sert de récupération active, accélère même la résorption des DOMS sur la zone travaillée la veille (vasodilatation).

Le moteur peut donc **insérer LISS librement** dans le pattern, sans re-démarrer le compteur de récupération des zones strength.

### C.4 Cas limite — zone partiellement re-sollicitée

Si tu fais Push J (pecs + delts + triceps) puis Pull J+1 (lats + biceps + delts post + biceps), les **deltoïdes** sont re-touchés < 24 h. Mais :

- Sur Push, les delts antérieurs / latéraux sont primaires.
- Sur Pull, ce sont les delts postérieurs.
- → **3 sous-zones différentes**, donc impact mineur. Acceptable scientifiquement.

À condition que le volume cumulé hebdo par sous-zone reste dans 12–20 sets / semaine (Schoenfeld 2017).

## D. Changements proposés au moteur

Trois extensions du moteur Sb_12, **toutes additives, sans casser** la signature actuelle :

### D.1 `staleness_by_zone` granulaire 24h / 48h / 72h

Au lieu d'une seule fenêtre 7 j, calculer un score de **disponibilité** par zone qui tient compte du **temps écoulé** depuis la dernière sollicitation lourde.

```
availability_by_zone[z] = clamp(0, 1, hours_since_last_hard_set[z] / recovery_hours_target[z])
```

Avec :

```python
RECOVERY_HOURS_TARGET = {
    "pecs":      48,
    "lats":      48,
    "upper_back":48,
    "delt_lat":  36,
    "delt_post": 36,
    "biceps":    36,
    "triceps":   36,
    "calves":    36,
    "quads":     72,   # gros volume, DOMS prolongés
    "posterior": 72,
    "core":      24,
}
```

Lecture : quand `hours_since_last >= recovery_hours_target`, la zone est totalement « disponible » (1.0). Avant ça, l'availability croît linéairement.

Cette métrique remplace `staleness_by_zone` dans le scoring strength.

### D.2 Antagonist bonus

Bonus séparé qui récompense les templates dont les zones primaires **n'ont pas été touchées** par la dernière séance strength :

```python
def antagonist_bonus(template_zones, last_session_zones):
    """Returns 0..15. Higher = better antagonism."""
    if not last_session_zones:
        return 0  # cold start, no bonus
    overlap = set(template_zones) & set(last_session_zones)
    if not overlap:
        return 15        # parfait — antagoniste complet
    if len(overlap) <= 1:
        return 8         # partiel — une zone secondaire commune (ex. delts)
    return 0             # gros recouvrement, pas d'antagonisme
```

Composant ajouté au scoring.

### D.3 Scoring V2 final

```
score = 35·mean(availability_by_zone[z] for z in primary_zones)
      + 15·antagonist_bonus_share
      + 20·alternation_kind
      −  5·redundancy_24h_share        # nouveau : 24h, plus strict que 48h
      + catalog_affinity (15/10/20)
      + cardio_absent_bonus (10)
```

Notez le rééquilibrage des poids : staleness passe de 40 à 35 pour faire de la place au bonus antagoniste 15. Total cap inchangé (100).

### D.4 Phrase explicative enrichie

Ajout de slots scientifiquement informés dans `_build_phrase` :

| Slot | Trigger | Wording |
|------|---------|---------|
| `quads_recovery` | last session ≥ legs et < 72 h | « Jambes travaillées il y a {N}h — encore en récupération » |
| `antagonist_perfect` | overlap=0 entre last et candidate | « {Group}/{antagonist group} — pas de chevauchement musculaire » |
| `partial_overlap_delts` | overlap=1, zone delts | « Légère sollicitation delts hier, OK pour {kind} aujourd'hui » |
| `optimal_ppl` | pattern Push→Pull→Legs reconnu | « Pattern Push/Pull/Legs respecté » |

Cap toujours 140 chars.

### D.5 Nouveau signal `last_session_zones`

Ajout dans `Signals` (Sb_12) :

```python
@dataclass
class Signals:
    # ... existing fields ...
    hours_since_last_by_zone: dict[str, float]  # hours, large for "never"
    last_strength_session_zones: list[str]       # primary zones of last strength
    availability_by_zone: dict[str, float]       # 0..1, replaces staleness V1
```

Calculé via une nouvelle requête : la dernière `WorkoutSession` strength complétée du user, ses `session_exercises`, et leurs zones primaires via `classify_exercise(actual_exercise_name(se))`.

## E. Cas particuliers

| Cas | Traitement |
|-----|-----------|
| Cold start (< 3 lifetime sessions) | Comportement Sb_12 inchangé : Push A par défaut |
| Pas de strength récent (uniquement cardio) | `availability` = 1 partout, antagonist_bonus = 0, scoring tombe sur staleness fictive max → premier core par display_order |
| Plusieurs strength dans les dernières 24 h | Empilement : `last_strength_session_zones` = union des zones touchées dans les 24 h |
| Spécialisation (catch-up-back-width par exemple) | Garder la règle Sb_12 §H.1 (ratio < 0.5 sur 14 j) inchangée |
| Bodybuilder qui veut reprendre un même groupe < 48 h | Le moteur le **dégrade** mais ne l'**exclut pas** — l'utilisateur peut toujours bypass via `/library` |

## F. Impacts techniques

| Surface | Modif | Effort |
|---------|-------|--------|
| `app/services/recommendation.py` | Ajout `RECOVERY_HOURS_TARGET`, `availability_by_zone`, `antagonist_bonus`, refacto `_score_template`, slots phrases enrichis, signal `last_strength_session_zones` | 4 h |
| `app/services/recommendation.py` | Nouvelle query : dernière strength session avec ses exercises + zones primaires | 1 h |
| `tests/test_recommendation_service.py` | Étendre fixtures pour valider antagonist_bonus, availability_by_zone, nouveaux slots phrases | 2 h |
| `app/services/quality_score.py` ou util | Helper `is_strength_session(session)` réutilisable | 30 min |
| Spec / phrases | Mise à jour des slots dans `_build_phrase` + tests | 1 h |
| Sprint report | Décisions, tableau récup, exemples de scoring avant/après | 30 min |

**Build Sb_18 estimé : 8–10 h.** Pas de migration, pas de nouveau template, pas de surface UI nouvelle — la phrase explicative reste rendue par le partial existant.

## G. Calibration

Les valeurs `RECOVERY_HOURS_TARGET` ci-dessus sont **issues de la littérature** — elles peuvent être ajustées au sein de `recommendation.py` si le dogfooding montre qu'elles sont mal calibrées sur le profil utilisateur (genre, niveau d'entraînement, sommeil — variables individuelles non capturées).

Sb_13 a déjà mis en place le CLI `reco_calibration_report.py` qui reportera `reco_acceptance_rate` post-V2 ; on pourra mesurer l'impact.

## H. Risques

| Risque | Probabilité | Mitigation |
|--------|-------------|------------|
| Calibration RECOVERY_HOURS mal ajustée pour cet utilisateur | Élevée | Constantes centralisées en tête de fichier, ajustables après dogfooding 7 j (cycle Sx_13.x) |
| Phrase explicative perçue comme « medical advice » | Faible | Wording neutre obligatoire (« encore en récupération » et non « tu es trop fatigué ») |
| Coût compute leaderboard V2 + reco V2 cumul | Faible | Volume utilisateur faible. Cache 5 min envisageable si nécessaire |
| Antagonist_bonus dominant le scoring → lock sur PPL strict | Moyen | Cap 15 pts, plafond préserve la diversité catalogue |
| Conflits entre staleness V1 (7j) et availability V2 (24/48/72 h) | Moyen | V2 **remplace** V1 (n'additionne pas), évite double-comptage |

## I. Acceptance criteria

| Critère | Statut |
|---------|--------|
| Base scientifique citée et résumée (§C) | ✓ |
| Tableau de récupération par groupe documenté | ✓ |
| 3 niveaux d'antagonisme cartographiés | ✓ |
| Heuristique antagonist_bonus chiffrée 0/8/15 | ✓ |
| Scoring V2 final écrit avec poids | ✓ |
| 4 slots phrase explicative ajoutés | ✓ |
| Cas particuliers cold start / cardio-only / spécialisation traités | ✓ |
| Effort build Sb_18 estimé (8–10 h) | ✓ |
| Risques listés + mitigations | ✓ |
| Pas de migration, pas de JS, pas de nouvelle surface UI | ✓ |
| Calibration centralisée et ajustable | ✓ |

## J. Recommandation build suivant

**Sb_18 build** dès que cette spec est validée. Effort 8–10 h. Surface limitée à `recommendation.py` + quelques tests.

**Pré-requis avant Sb_18 :**
- Validation humaine de la spec (poids, table récup, slots phrases).
- Optionnel : passe dogfooding 7 j sur le moteur V1 pour avoir une baseline `reco_calibration_report.py` à comparer post-V2.

**Ouvertures différées (V3+) :**
- Modèle individualisé : ajuster `RECOVERY_HOURS_TARGET` par utilisateur via la readiness daily (sleep, fatigue) — réclame Sx_20 dédié.
- Prise en compte du **volume cumulé hebdo par zone** (cap 12–20 sets/sem Schoenfeld 2017) — peut désactiver des templates qui rechargeraient une zone déjà sur-volumineuse.
- Distinction inter-séances **même zone, intensité variable** : un Push lourd 1RM est plus exigeant qu'un Push 12-15 sub-max. Ne pas l'intégrer V2 — trop de variance individuelle, coûte cher en data.
- Suggestion proactive d'**éviter** une séance plutôt que d'en proposer une (« repos recommandé aujourd'hui ») — V3 si signal observé.

---

## Annexe A — Tableau d'antagonisme par template

Pré-calculé pour les 6 templates core :

| Template | Zones primaires | Antagoniste(s) idéal(aux) |
|----------|-----------------|---------------------------|
| push-a | pecs, delt_lat, triceps | pull-a, pull-b, legs-a, legs-b |
| push-b | pecs, delt_lat, triceps | pull-a, pull-b, legs-a, legs-b |
| pull-a | lats, delt_post | push-a, push-b, legs-a, legs-b |
| pull-b | upper_back, biceps | push-a, push-b, legs-a, legs-b |
| legs-a | quads, posterior, calves | push-a, push-b, pull-a, pull-b |
| legs-b | quads, posterior, calves | push-a, push-b, pull-a, pull-b |

Cardio (`liss-only`, `liss-abs`) : antagoniste de **tout** strength, jamais de chevauchement. Bonus 15 quand alternance kind est aussi déclenchée.

## Annexe B — Exemples de scoring V1 vs V2

**Cas 1 — Hier Push A, aujourd'hui matin.**

V1 :
- staleness pecs=0, delt_lat=0, triceps=0 → score Push A = 40·0 + 15·core = 15
- staleness lats=1, biceps=1, delt_post=0.7 → score Pull A = 40·0.9 + 15 = 51
- staleness quads=1, posterior=1, calves=1 → score Legs A = 40·1 + 15 = 55
- → top-1 Legs A, top-2 Pull A

V2 :
- 14 h depuis Push → availability pecs=14/48=0.29, delt_lat=14/36=0.39, triceps=14/36=0.39
  - score Push A = 35·0.36 + 15·antagonist(0)=0 + … = 12 + 15 catalog = 27
  - antagonist_bonus push-a vs push-a = 0 (overlap total)
- 14 h depuis dernière strength → availability lats=14/48=0.29, …
  - score Pull A = 35·~0.4 + 15·15 (overlap=0 lats vs pecs) + 15 catalog = 14 + 15 + 15 = 44
- score Legs A = 35·1 + 15·15 (no overlap) + 15 = 65
- → top-1 Legs A (more strongly justified), top-2 Pull A

V2 produit le même classement mais avec une **justification scientifique** dans la phrase : « Jambes pas travaillées récemment + antagonisme parfait → Legs A recommandé ».

**Cas 2 — Avant-hier Legs A (40 h), hier Push A (14 h), aujourd'hui matin.**

V1 :
- staleness lats=1, biceps=1, posterior=0.6 → Pull A score = 40·0.9 + 15 = 51
- staleness pecs=0, triceps=0 → Push B score = 40·0 + 15 = 15
- staleness quads=0.6, posterior=0.6 → Legs B score = 40·0.6 + 15 = 39
- → top-1 Pull A

V2 :
- last strength = Push A (14 h ago, zones {pecs, delt_lat, triceps})
- antagonist_bonus(Pull A vs {pecs, delt_lat, triceps}) → overlap=0 → 15
- antagonist_bonus(Legs B vs {pecs, delt_lat, triceps}) → overlap=0 → 15
- availability quads = 40/72 = 0.55 (Legs A il y a 40h)
- availability lats = 14/48 = 0.29 (Pull n'a pas encore été fait, donc never → 1.0 en réalité)
- score Pull A = 35·1 + 15 + 15 = 65 — wording « Pull A — pas de chevauchement avec Push A d'hier »
- score Legs B = 35·0.6 + 15 + 15 = 51 — wording « Jambes encore en récupération à 40h, attendre J+3 idéalement »
- → top-1 Pull A, **mais avec phrase enrichie** qui explique pourquoi pas Legs B aujourd'hui.

V2 produit donc à la fois un meilleur ordre **et** une explication crédible. C'est ce que le user demande dans ses notes.
