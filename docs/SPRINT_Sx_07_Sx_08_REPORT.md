# Sprint Sx_07 + Sx_08 Report — Parallel Specs

**Date:** 2026-04-15
**Type:** SPEC ONLY — aucun build
**Prerequisite:** Sx_05 + Sx_06 valides
**Parallelisation:** Sx_07 (Machine Atlas) et Sx_08 (Session Review) produits simultanement — domaines disjoints, zero conflit
**Suivi par:** Sx_09 (consolidation transverse) puis phase build

---

## Objectif

Produire en parallele les 2 specs qui restaient a cadrer dans la phase spec du cycle post-v10 :

- **Sx_07** : Machine Knowledge + Substitution UX Surface
- **Sx_08** : Session Review Intelligence (synthese + anomalies + hints + confidence)

---

## Justification de la parallelisation

Les 2 specs touchent des domaines disjoints du produit :

| Sx_07 | Sx_08 |
|-------|-------|
| Atlas machine JSON | Regles anomalies deterministes |
| Lien exercice → machine | Synthese post-seance enrichie |
| UX panneau `i` + drawer substitution | Hints contextuels carte active |
| Page `/science/atlas` | Score de confiance logging |
| Bloc 6 du body carte exercice | Extension `/done` (Sb_R3) |

Aucun conflit detecte :
- Sx_07 n'introduit pas de nouveau signal feedback
- Sx_08 n'introduit pas de nouvelle source de donnees machine
- Les 2 peuvent **enrichir** `/done` independamment (zones_touched peut reference `machine_family` si atlas deploye, mais degrade gracefully sinon)

---

## Decisions prises Sx_07

### D7.1 Atlas in-memory plutot que DB

`app/services/machine_atlas.py` charge `data/machine_atlas.json` au demarrage. Pas de seed en DB, pas de FK.

**Justification :** atlas = reference editoriale stable, pas de ecriture user. Charge legere (~10 KB). Gouvernance git-based.

### D7.2 30 machines V1, 8 familles

Couvre 100% des exercices core v10. Iteration incrementale possible.

### D7.3 Liens exercice optionnels

`machine_slug` et `machine_family` **nullable** sur TemplateExercise. Carte sans lien = pas d'icone `i` (degradation gracieuse).

**Migration :** additive, 2 colonnes VARCHAR(64) nullable sur `template_exercises`. Aucun impact sur SessionExercise snapshots.

### D7.4 Panneau `i` = `<details>` natif dans le body

Bloc 6 de l'ordre vertical fige Sx_02. Respect des 6 garde-fous Sx_02 (position picker, lock, fallback, parsing, structure data, zero JS).

### D7.5 Drawer substitution affine sans refacto

Wording plus explicite ("Machine occupee ?"), count alternatives, style distinctif. Mecanisme interne (radio `substituted_name`, `can_substitute`) **inchange**.

### D7.6 Page `/science/atlas` navigable

Navigation par ancres (`#machine-{slug}`). Pas de search V1 (YAGNI).

---

## Decisions prises Sx_08

### D8.1 Deterministe, pas predictif

Aucune ML/LLM. Regles basees sur seuils chiffres + comparaisons.

### D8.2 5 regles anomalies V1 max

1. Set marque fait sans donnees
2. Charge et reps croissent simultanement en fin d'exercice
3. Delta weight extreme (>30%)
4. Exercice warmup only sans work set
5. Success score haut + reps sous cible (coherence)

Severite unique "info" V1. Ton neutre garanti.

### D8.3 2 hints V1 max sur carte active

A. Charge augmentee > 10% vs derniere fois
B. Reps reduites sur set N vs meme set prior

Suggestions passives, pas de bouton "Appliquer".

### D8.4 Confidence score 0-100

5 composants : work sets renseignes (40) + flag completed coherent (15) + feedback session (20) + anomalies faibles (15) + bodyweight bonus (10).

Niveaux eleve / moyen / faible affiches en badge dans `/done`.

### D8.5 Reduction notes inline

Note exercice → `<details>` optionnel collapsed. Note session → reste dans feedback session (usage terrain OK).

### D8.6 Synthese finale devient point de reflexion principal

`/done` enrichi : top progression + zones sollicitees + anomalies (conditionnel) + confidence badge.

Pas de narration auto-generee V1 (explicitement defere).

---

## Audit repo effectue

| Fichier | Role audite |
|---------|-------------|
| `app/services/session_recap.py` | Structure actuelle recap → extension planifiee |
| `app/services/substitution.py` | 3 fonctions `actual_exercise_name`/`get_substitutes`/`can_substitute` → preserver |
| `app/services/delta.py` | Fournit les deltas deja consumables par top_progression |
| `app/services/muscle_scoring.py` | `classify_exercise` + `ZONE_LABELS` utilisables pour zones_touched |
| `app/templates/session_detail.html` | Structure actuelle bloc 4 (substitute picker) → affinement |
| `app/templates/session_done.html` | Bloc summary extensible pour nouveaux elements |
| `data/reference_split.json` | v10 — ajout de machine_slug / machine_family prevu v11 |

---

## Livrables produits

| Fichier | Lignes | Role |
|---------|--------|------|
| `docs/strategy/SPIGNOS_MACHINE_KNOWLEDGE_AND_SUBSTITUTION_SURFACE_SPEC_v1.md` | ~500 | Spec Sx_07 |
| `docs/strategy/SPIGNOS_SESSION_REVIEW_INTELLIGENCE_SPEC_v1.md` | ~600 | Spec Sx_08 |
| `docs/SPRINT_Sx_07_Sx_08_REPORT.md` | ~250 | Ce rapport conjoint |

**Zero fichier code modifie.**

---

## Effort estime phase build

| Sprint | Duree estimee |
|--------|---------------|
| Sb_07 Machine Knowledge + Substitution | 6-8h |
| Sb_08 Session Review + Anomaly Hints | 4-6h |
| **Total** | **10-14h** |

---

## Contradictions ou incertitudes restantes

### Q1 (Sx_07) — Synonymes machine et matching exercices

Si un exercice du catalogue nomme "Machine presse épaule" doit-il match `shoulder-press-machine` ? Le champ `aliases` dans l'atlas permet la resolution souple, mais le mapping explicite via `machine_slug` dans le catalogue evite l'ambiguite.

**Decision V1 :** privileger `machine_slug` explicite dans le catalogue exercices. Aliases restent informative pour la page atlas.

### Q2 (Sx_07) — Evolution de l'atlas et impact history

Si on bump l'atlas (retirer/renommer une machine), les SessionExercise historiques qui pointent (indirect via `template_exercise` non detache) peuvent perdre leur lien.

**Mitigation :** atlas = additif uniquement V1. Pas de rename, pas de suppression. Si besoin de renommer, garder l'ancien slug comme alias.

### Q3 (Sx_08) — Hint "charge augmentee" + convention de charge canonique

Si un user saisit "10" pour un cable unilateral (par cote) et "20" la fois suivante (confusion convention), le hint va dire "+100%" a tort.

**Mitigation :** accepter ce faux positif V1 (rare). Le helper text C05 (Sb_06) reduit cette confusion. Si recurrent, raffiner en regardant `load_semantics` (V2).

### Q4 (Sx_08) — Confidence score affiche au user

Risque psychologique : un user avec confidence faible se sent "puni". Mitigation wording : "Confiance du logging" (pas "de la seance"), et explication dans `/science`.

**A trancher a Sb_08 build si feedback terrain negatif.**

### Q5 (Sx_08) — Regles anomalies sur cardio

Les 5 regles sont toutes strength-oriented (reps, rep_targets, weight). Pour une seance cardio, `compute_anomalies` retournera liste vide par design.

**Acceptable V1.** Des regles cardio dediees peuvent etre ajoutees V2 (ex: "duration_min declare sans bpm_avg").

---

## Dependances entre Sx_07 et Sx_08

### Couplage mineur identifie

`Sx_08 zones_touched` peut enrichir l'affichage avec `machine_family` (cf Sx_07).

**Resolution :** Sb_07 livre les liens machine_slug/family AVANT Sb_08, donc Sb_08 peut consommer `get_for_exercise()` du machine_atlas service. Si build ordre differe, Sb_08 ignore l'info machine et affiche juste zones primaires.

### Independances strictes

- Sb_07 peut etre livre sans Sb_08 (atlas + icone `i` fonctionnent seuls)
- Sb_08 peut etre livre sans Sb_07 (zones_touched affiche via `classify_exercise` uniquement, deja present)

**Ordre recommande :** Sb_07 avant Sb_08 (enrichissement cumulatif).

---

## Prochaine action

**Apres validation humaine Sx_07 + Sx_08 :**

Option A (recommandee) : produire **Sx_09** (Consolidation transverse) pour reconciler Sx_05 → Sx_08, identifier eventuels conflits entre specs, produire la build queue definitive avec estimations d'effort.

Option B : lancer directement **Sb_07** (ou Sb_05) en saut de Sx_09. Acceptable mais reduit la discipline "spec avant build" verrouillee en Sx_05.

**Ma recommandation : Option A.** Sx_09 prend 1-2h et garantit qu'aucune contradiction ne remonte en phase build.

---

## Synthese executive (5 lignes)

- 2 specs produits en parallele (domaines disjoints, 0 conflit)
- Sx_07 = atlas machine JSON + 2 liens exercice optionnels + panneau `i` + drawer affine + page dediee
- Sx_08 = synthese /done enrichie (top progression, zones, anomalies) + 5 regles anomalies + 2 hints + score confiance
- Wording neutre garanti Sx_08 ; garde-fous Sx_02 respectes Sx_07
- Prochaine action : Sx_09 consolidation (1-2h) puis phase build Sb_07 → Sb_08 (10-14h)
