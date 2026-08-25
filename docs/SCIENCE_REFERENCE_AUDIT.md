# Audit de la page Science — `POST_CONVERGENCE_INTEGRITY_01` / B

Science est désormais le **document de provenance canonique** du produit :
`/progress` et le Coach Report y pointent par liens profonds, et ses sept
règles portent des identifiants stables. Une affirmation périmée n'y est plus
une imprécision de documentation — c'est une **provenance fausse**.

Chaque section visible a donc été confrontée au code, ligne à ligne.

---

## Verdict

| Section | Classement | Preuve |
|---|---|---|
| Pourquoi noter change la progression | `CURRENT` | prose de méthode, aucune affirmation vérifiable sur le produit |
| Méthode d'entraînement (7 règles) | `CURRENT` | `data/method_rules.json`, versionné ; slugs épinglés par une garde |
| Place du cardio | `CURRENT` | `Auren capture : durée, BPM, machine` — exact ; « calories indicatives » exact |
| **Scoring cardio vs musculation** | `CURRENT` **reformulé** | voir ci-dessous |
| Convention de saisie des charges | `CURRENT` | inchangée |
| Programmes et séances · Exercices et séries | `CURRENT` | inchangées |
| **Score dérivé** | `CURRENT` | `feedback.compute_success_score` : reps vs plage prescrite + séries complétées. Exact. |
| Historique | `CURRENT` | comparaison et deltas par exercice : livrés par `TRAIN1-B` |
| **Synthèse et physique** | **`STALE_PRODUCT_MODEL`** | remplacé — voir ci-dessous |
| Ce qui reste privé | `CURRENT` | vérifié contre le partage squad |
| Atlas des machines · Muscle Focus | `CURRENT` | voir §D |
| **Diagramme d'architecture** | **`STALE_PRODUCT_MODEL`** | remplacé — voir ci-dessous |

**Aucune section n'est classée `UNSUPPORTED_CLAIM`.** La page ne contient
aucune affirmation scientifique que le dépôt ne puisse pas soutenir — les
affirmations qu'elle porte sont *opératoires* (comment AUREN compte), pas
physiologiques.

---

## Ce que l'audit a contredit, et il faut le dire

L'ordre listait six éléments comme périmés. **Cinq sur six décrivaient
fidèlement du code vivant**, vérifiés nombre par nombre :

| Élément signalé | Réalité mesurée |
|---|---|
| « Scoring cardio vs musculation » | mécanisme vivant — `compute_session_quality` dispatche par type, les deux branches existent |
| « cible 20 min LISS » | `_cardio_duration_component` : `if duration_min >= 20: return 50.0` |
| « 115–135 bpm » | `_cardio_intensity_component` : `if 115 <= bpm_avg <= 135: return 20.0` |
| « > 85 / 100 » | arithmétique : 50 (durée) + 20 (intensité) + 20 (complétion par défaut) = **90**, avant tout point subjectif |
| « Score dérivé » | `compute_success_score` : reps vs plage + séries complétées |
| « Synthèse et physique » | **périmé, confirmé** |

Je ne les ai donc pas supprimés. Les supprimer aurait retiré de la provenance
**exacte** d'un document dont c'est la fonction.

**Mais l'intuition derrière le signalement était juste, et le défaut réel est
ailleurs : le vocabulaire.** « Cible 20 min » présente un palier de barème
comme un objectif d'entraînement, sur la page de référence d'un produit qui
vient de retirer le langage d'objectif de tous ses instruments — « % de cible »
de l'exposition musculaire, « cible OMS » du rapport coach.

Ce n'est pas de la staleness, c'est une **collision de doctrine**. Le bloc est
donc reformulé :

- **aucun nombre n'a bougé** — 20 min, 115-135 bpm, 85/100 sont conservés ;
- **aucune règle nouvelle n'est inventée** ;
- le texte dit ce que le barème **fait** plutôt que ce que l'utilisateur
  **devrait viser**, et il nomme la distinction en toutes lettres :
  *« Ce sont des paliers de barème, pas des objectifs d'entraînement. »*

---

## Les deux blocs réellement périmés

### « Synthèse et physique »

Il décrivait **deux surfaces qui n'existent plus** :

- « La page **Synthèse** calcule 5 axes (régularité, progression, évolution
  corporelle, récupération, équilibre musculaire) » — c'est le modèle du
  tableau de bord, qu'aucune route ne rend depuis `Sb_27.6` ;
- « La page **Physique** montre l'équilibre de développement par zone » —
  retirée par `TRAIN1-C`.

Remplacé par une description de **Progression**, la seule surface d'analyse.
Aucune règle scientifique n'a été inventée : ce bloc n'en contenait pas, il
décrivait des surfaces.

Une phrase a été **sauvée** : « tu ne vois jamais un score qu'on ne peut pas
calculer honnêtement ». Elle était une promesse quand elle a été écrite ; elle
est devenue littéralement vraie avec `TRAIN1-C`, où une mesure sans
dénominateur cesse de rendre un tiret et disparaît en nommant sa cause.

### Le diagramme d'architecture

**Trouvé parce que l'ordre disait « chaque section visible », pas « chaque
section du gabarit ».** Le SVG `_partials/science_diagram.svg` rendait trois
surfaces de sortie : `Synthese`, `Physique`, `Classement`. Deux sur trois
n'existent plus, et la **description accessible** (`<desc>`) les nommait aussi
— un lecteur d'écran recevait donc l'architecture de 2026-04.

Un `grep` sur le gabarit seul ne l'aurait jamais vu : le contenu vit dans un
partiel SVG inclus.

Corrigé : deux sorties (`Progression`, `Classement`), flèches et description
accessible alignées.

---

## D — Atlas

**`SCIENCE_ATLAS = REFERENCE_SECONDARY`.**

Sa longueur totale — 15,3 écrans, 2 074 mots, 32 blocs — **n'est pas un
défaut** : c'est un référentiel machine par machine, consulté par entrée
ponctuelle, pas lu de bout en bout. Le sommaire par famille et les ancres
machine stables suffisent en l'état.

**Condition de réouverture, et une seule :** que `TRAIN 3` démontre une entrée
dans l'atlas **sans contexte machine connu**. Tant que l'entrée se fait depuis
un exercice identifié, la navigation par ancre répond à la question posée.

Aucune refonte, aucune mesure de densité à corriger.
