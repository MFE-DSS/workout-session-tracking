# Sprint Sx_21.1 Amendments Report — Micro-passe de cadrage avant Sb_22a

**Date :** 2026-05-09
**Type :** SPEC AMENDMENTS ONLY — durcissement contrats avant ouverture build.
**Prérequis :** Sx_21 livré (5 docs).
**Successeur :** Sb_22a (décision conclusion §C).

---

## A. Pourquoi cette micro-passe

Les specs Sx_21 v1 sont structurées mais permettent encore des dérives au build :
- une logique de proximité fondée uniquement sur la zone musculaire (substitution trop locale)
- une absence de hiérarchie dure entre niveaux dans Profile Synthesis (risque de duplication ascendante)
- un étiquetage flou dans Coach Report autorisant des appréciations esthétiques
- pas de matrice avant/après obligatoire pour mesurer le ROI de Sb_22a

Amendement = uniquement ajouts/durcissements, aucun rewrite, aucun code.

## B. Deltas par spec

### B.1 — `SPIGNOS_SUBSTITUTION_GAP_PACK_SPEC_v1.md`

| § | Delta | Effet |
|---|---|---|
| §C.1 | **Terminologie verrouillée** : N1 = `Équivalence stricte`, N2 = `Fallback très proche`, N3 = `Fallback zone-only`. Badges UI canoniques (`Équivalent`/`Proche`/`Élargi`). | Interdit silencieusement une suggestion "zone-only" en N1/N2. |
| §C.1 | **Règle stricte v1.1** : une suggestion zone-only est **toujours** N3 et **toujours** étiquetée `Élargi`. | Verrou contre la dérive "le radar est rouge sur les jambes → on suggère n'importe quoi de jambes". |
| §C.2 | Le champ `pattern_motor` pointe vers le nouvel enum §C.2bis. | Source unique de vérité. |
| **§C.2bis (NEW)** | **Enum `pattern_motor` verrouillé** : 11 valeurs exhaustives (push_horizontal, push_vertical, pull_horizontal, pull_vertical, squat, hinge, lunge, isolation_upper, isolation_lower, core, cardio). Script QA `catalog_pattern_qa.py` obligatoire. | Pas d'invention de pattern au fil de l'eau. CI refuse l'invalide. |
| §C.3 seuils | **Garde-fou v1.1** : `pattern_motor identique` est **obligatoire** pour N1 et N2. Pattern différent → N3 imposé, peu importe le score. `compute_n2_suggestions()` lève `ValueError` si on viole. | Élimine le faux positif "même zone donc OK". |
| **§C.4bis (NEW)** | Sous-lot MVP haute valeur : 7 familles fonctionnelles à traiter **avant** les templates synthèse (adduction, rowing/tirage vertical, shoulder press, leg extension/curl, triceps, curl, chest press/incline). | Livre la valeur user en premier, pas la complétude technique. |
| **§C.4ter (NEW)** | **Matrice avant/après obligatoire** dans le sprint report. ≥ 80 % familles couvertes = condition de merge. | Sb_22a n'est plus mergeable sans preuve quantifiée. |
| **§D.bis (NEW)** | Contrat prévu/réalisé : (1) catalogue enrichi mais `template_exercises` jamais modifié rétroactivement, (2) `session_exercises.substituted_name` et `exercise_name_snapshot` intacts, (3) aucune réécriture historique. | Sacralise la séparation prévu/réalisé déjà en place. |
| §E acceptance | 10 critères bloquants (vs 5 v1), tous testables. Inclut l'enum, le garde-fou pattern, la matrice §C.4ter, l'invariant Alembic (pas d'`ALTER` sur `substitutes_json`). | Aucun build ne peut "passer" avec un de ces critères ouvert. |

### B.2 — `SPIGNOS_PROFILE_SYNTHESIS_SPEC_v2.md`

| § | Delta | Effet |
|---|---|---|
| **§A.bis (NEW)** | **Hiérarchie 3 niveaux verrouillée (contrat dur)** : tableau L1/L2/L3 avec ce qui vit à chaque niveau et nulle part en double. Score numérique : L1 + L3 uniquement, jamais L2 (le badge grade suffit), jamais au centre du radar. Radar : L2 et L3, toujours silhouette. Métadonnées : L3 uniquement. Activité agrégée : L3 uniquement. | Verrouille l'anti-pattern "score dupliqué" (B3 dogfood) et l'anti-pattern "preview qui copie la page". |

### B.3 — `SPIGNOS_COACH_REPORT_SPEC_v1.md`

| § | Delta | Effet |
|---|---|---|
| **§B.bis (NEW)** | Étiquetage obligatoire **Mesuré / Inféré / Non déductible**. Tag visible par bloc et par ligne. Vocabulaire fermé — aucun autre toléré. | Tout bloc du rapport déclare sa nature de signal. |
| §B.bis interdits | 4 interdits stricts : aucune appréciation esthétique, aucun pronostic morphologique, aucun verdict performance maximale, aucune comparaison vs autres users (V1). | Coupe court à toute dérive interprétative non fondée. |
| §B.bis obligations | Tag en en-tête de bloc + sur-étiquetage ligne par ligne si nécessaire. Blocs 7-9 systématiquement `Inféré`, mot "probable" obligatoire dans le phrasé. | Discipline d'étiquetage testable au build. |
| §C.x tags | Renommage global `Constaté` → `Mesuré`, `Calculé` → `Inféré`, `Hypothèse` → `Inféré`. | Alignement vocabulaire avec §B.bis. |

### B.4 — `SPIGNOS_DOGFOODING_GENERALIZATION_SPEC_v1.md`

| § | Delta | Effet |
|---|---|---|
| §F garde-fous | Reformulation alignée sur le triptyque verrouillé : `Mesuré` / `Inféré` / `Non déductible`. Le tag `Non déductible` devient obligatoire dès qu'une donnée attendue par le user ne peut pas être produite (VO2max, masse maigre, qualité d'exécution biomécanique). | Cohérence vocabulaire toute la stack Sx_21+. |

## C. Conclusion : Sb_22a prêt ou différer ?

**Verdict : Sb_22a PRÊT.**

Justification :
- Les 4 specs ont chacune au moins un contrat dur supplémentaire qui empêche le build de dériver.
- Le sous-lot haute valeur §C.4bis donne au build un point d'entrée à faible risque et fort signal user.
- La matrice avant/après §C.4ter rend le succès mesurable (≥ 80 % familles couvertes).
- Le contrat prévu/réalisé §D.bis protège l'historique — l'enjeu critique du produit.
- L'enum `pattern_motor` §C.2bis + le garde-fou pattern §C.3 ferment la classe de problème "substitution zone-only" identifiée dans le dogfooding.

Conditions de réussite Sb_22a :
1. Commencer par §C.4bis (sous-lot haute valeur, ~4 h) avant les templates synthèse.
2. Lever `ValueError` dans `compute_n2_suggestions()` si pattern différent — test unitaire obligatoire.
3. Produire la matrice §C.4ter en sortie de build avant de toucher au sprint report.
4. Aucun `ALTER TABLE template_exercises` ni migration touchant `session_exercises`.

## D. Fichiers modifiés

| Fichier | Type | Nature delta |
|---|---|---|
| `docs/strategy/SPIGNOS_SUBSTITUTION_GAP_PACK_SPEC_v1.md` | Edit | §C.1, §C.2, §C.2bis (NEW), §C.3, §C.4bis (NEW), §C.4ter (NEW), §D.bis (NEW), §E |
| `docs/strategy/SPIGNOS_PROFILE_SYNTHESIS_SPEC_v2.md` | Edit | §A.bis (NEW) |
| `docs/strategy/SPIGNOS_COACH_REPORT_SPEC_v1.md` | Edit | §B.bis (NEW) + remplacement vocabulaire `Constaté/Calculé/Hypothèse` → `Mesuré/Inféré/Non déductible` |
| `docs/strategy/SPIGNOS_DOGFOODING_GENERALIZATION_SPEC_v1.md` | Edit | §F garde-fous |
| `docs/SPRINT_Sx_21_1_amendments_REPORT.md` | New | Ce rapport |

**0 ligne code applicatif touchée.** 5 fichiers documentation, 4 specs durcies, 1 mini-report.

## E. Synthèse

Les 4 specs Sx_21 v1 sont maintenant **v1.1 cohérentes**. Les contrats durs ajoutés ferment les risques identifiés en revue :
- pas de proximité zone-only (substitution)
- pas de score dupliqué entre niveaux (profile)
- pas d'appréciation esthétique non fondée (coach)
- triptyque vocabulaire homogène `Mesuré/Inféré/Non déductible`

**Décision : Sb_22a peut être ouvert immédiatement.**
