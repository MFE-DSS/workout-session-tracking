# Sprint Sx_03 FINAL Report — Exercise Substitution Graph (Final Spec)

**Date:** 2026-04-14
**Type:** Spec only — aucun build
**Prerequisite:** Sx_01 FINAL + Sx_02 FINAL (composant exercice fige)
**Suivi par :** enrichissements catalogue incrementaux (P2) ou Sb_03.1 leger (P3) selon trigger

---

## Objectif

Produire le spec FINAL du graphe de substitution, consolidant Sb_03 deja build + Sx_03.1 strategique + contrats Sx_02, et fixant la vision long-terme (taxonomie de mouvement, niveaux d'equivalence, modele conceptuel a 5 niveaux) sans engager de rework.

---

## Travail effectue

### 1. Audit catalogue et structures

- `data/reference_split.json` v6 : 15 templates, 97 exercices, 9 relations de substitution
- Modele DB : `template_exercises.substitutes_json` (TEXT) + `session_exercises.substituted_name` (VARCHAR) + snapshots immutables
- Service : `app/services/substitution.py` (36 lignes, 3 fonctions — actual_exercise_name / get_substitutes / can_substitute)
- 6 consumers cables (muscle_scoring, sharing, session_recap, export_builder, template, QA script)

### 2. Modele conceptuel 5 niveaux

- Exercice canonique (implicite via nom, explicite si Option 2)
- Exercice prevu par le template (TemplateExercise)
- Exercice reellement execute (SessionExercise + snapshots + substituted_name)
- Relation de substitution (substitutes_json aujourd'hui, table dediee si Option 2)
- Niveau d'equivalence (non modelise actuellement)

### 3. Taxonomie de mouvement minimale viable

9 dimensions analysees. Recommande 6 dimensions V1 canonique :
- primary_zone, secondary_zones (deja utilises)
- motor_pattern, compound_isolation, laterality, equipment (nouveaux)

Les 3 dernieres (plane, stability, resistance_type) en reserve.

### 4. Taxonomie de proximite substitutive

4 niveaux d'equivalence :
- exact (quasi interchangeables, delta lisible)
- approx (meme zone, biomecanique differente, delta partiel)
- fallback (debloque la seance, signal degrade)
- out_of_scope (rejete par QA script)

### 5. UX substitution — integration Sx_02

Portee locale a l'exercice actif. Emplacement precis : bloc 4 sur 12 dans le body `<details>` (apres done-summary, avant last-time). Comportement avant/apres choix. Picker `<details>` natif, radio group, zero JS. Conservation visible du lien prescrit via badge.

### 6. Garde-fous Sx_02 (tableau 6 items)

Position picker / mecanisme lock / fallback summary / parsing server / structure data / zero JS. Sx_03 peut enrichir sans toucher ces elements.

### 7. Plus petit modele de persistance viable

Stockage per table (prevu / realise / relation). Snapshots immutables. Evolutions additives possibles (raison, niveau). Zero migration destructive.

### 8. Historique — 3 lectures distinctes

- Lecture 1 (execution stricte via actual_exercise_name) : muscle_scoring, physique, sharing
- Lecture 2 (slot-based via snapshots) : last_time, delta, progression_hint, exercise_history, kpis
- Lecture 3 (pattern / canonical, futur) : necessite taxonomie §3

### 9. Impacts analytics

7 surfaces cartographiees : last_time (neutre), delta (biais possible), progression_hint (neutre), dashboards (correct), compare mode (non-trivial), score qualite (acceptable), pattern futur (non faisable sans §3).

### 10. Gouvernance catalogue

- Graphe vit dans le JSON versione
- Enrichissement 2-3 relations par trimestre via revue humaine
- Regles pragmatiques (max 3 substituts, asymetriques OK, pas cross-zone)
- Priorite : P1 machines compound occupees (fait), P2 smith, P3 isolation
- Migration Option 2 seulement si 2+ triggers Sx_03.1 atteints

### 11. Wireframes textuels (6)

- Exercice actif non substituable
- Exercice actif substituable (picker ferme + deplie)
- Exercice actif substitue (summary realise + badge prescrit)
- Exercice done avec rappel
- Historique avec prefixe → pour les substitutions
- Page /done avec count substitutions

### 12. Matrice impacts (13 surfaces)

Du last_time au compare mode futur, chaque consumer cartographie (lecture, comportement, impact). Tableau en §12 du spec.

### 13. Preparation future build

- Migrations probables (Scenario A Option A vs Scenario B Option 2)
- Services a creer ou refactorer (get_substitutes etendu, helper level, exercise_catalog futur)
- 7 tests critiques identifies
- 4 consumers a ajuster plus tard (delta, exercise_history, compare mode, dashboard patterns)

---

## Livrables produits

| Fichier | Type | Contenu |
|---------|------|---------|
| `docs/strategy/SPIGNOS_EXERCISE_SUBSTITUTION_GRAPH_SPEC_FINAL.md` | New | Spec FINAL 16 sections — audit, modele 5 niveaux, taxonomie mouvement, niveaux equivalence, UX Sx_02-compatible, garde-fous, persistance, 3 lectures historique, impacts analytics, gouvernance, wireframes, matrice, build future, recommandations P1-P6, DoD |
| `docs/SPRINT_Sx_03_FINAL_REPORT.md` | New | Ce rapport |

**Aucun fichier code modifie.** Spec only.

---

## Taxonomie minimale viable du graphe

### Dimensions de mouvement (6 V1)

1. primary_zone (11 valeurs : pecs, delt_lat, delt_post, lats, upper_back, biceps, triceps, quads, posterior, calves, core)
2. secondary_zones (liste 0-3)
3. motor_pattern (push_horizontal, push_vertical, pull_horizontal, pull_vertical, squat, hinge, carry, rotation, anti_rotation, isolation)
4. compound_isolation (compound / isolation)
5. laterality (bilateral / unilateral)
6. equipment (machine / barre / haltere / cable / body / smith / kettlebell)

### Niveaux d'equivalence substitutive (4)

1. exact
2. approx
3. fallback
4. out_of_scope (rejete par QA)

---

## Modele conceptuel prevu / realise / substitution

```
[Exercice canonique]         ← abstrait, implicit today
        |
        | reference (futur Option 2)
        v
[TemplateExercise]            ← le prevu
  ├── substitutes_json        ← relations de substitution declarees catalogue
  └── rep_targets             ← prescription
        |
        | instancie en
        v
[SessionExercise]             ← le realise
  ├── exercise_name_snapshot  ← immutable, fige le prevu au moment de la creation
  ├── substituted_name        ← NULL si execute tel quel, sinon nom reel
  ├── success_score           ← derive (Sx_01)
  └── set_logs                ← execution objective
```

---

## Matrice impacts historique + analytics (extraits)

| Surface | Lecture | Comportement | Impact |
|---------|---------|--------------|--------|
| last_time | Slot | Ignore substitution | Neutre |
| delta | Slot | Biais possible | Accepte |
| muscle_scoring | Realise | Classifie selon fait | Correct |
| exercise_history | Slot | Affiche realise avec prefixe → | Lisible |
| /done | Realise + count | Affiche realise + compte substitutions | Correct |
| compare mode (S4) | Les deux cote a cote | A designer | Non-trivial |

---

## Recommandations ordonnees pour le futur build

| Priorite | Action | Cout | Quand |
|----------|--------|------|-------|
| **P1** | Rien a faire. Option 1 buildee est le bon choix | 0 | Immediat |
| P2 | Enrichissement catalogue 2-3 relations / trimestre | 10min par relation | Besoin terrain |
| P3 | Sb_03.1 leger : ajouter substitution_reason enum | 1-2h | A arbitrer, non urgent |
| P4 | Enrichissement JSON avec niveaux d'equivalence (Option A) | 2-3h + revue | Si remontee "delta bizarre" |
| P5 | Migration Option 2 canonical entity | Sprint dedie 8-12h | SI 2+ triggers Sx_03.1 atteints |
| P6 | Taxonomie mouvement complete (§3) | Revue 97 exercices | Apres Option 2 ou feature dedie |

---

## Definition of Done

| Critere | Statut |
|---------|--------|
| Prevu vs realise formalise | ✓ (§2 modele 5 niveaux) |
| Graphe avec niveaux d'equivalence utilisables | ✓ (§4 + regles impact) |
| UX locale substitution exercice actif claire | ✓ (§5 position exacte dans l'ordre 12 blocs) |
| Compatibilite Sx_02 demontree | ✓ (§6 tableau 6 garde-fous) |
| Impacts historiques documentes | ✓ (§8 trois lectures) |
| Impacts analytics documentes | ✓ (§9 + §12 matrice 13 surfaces) |
| Gouvernance catalogue realiste | ✓ (§10 regles + priorites enrichissement) |
| Zero rework composant exercice implicite | ✓ (§6 + §13.2 extensions natives) |

**Spec FINAL approuve. Pret pour enrichissements incrementaux ou Sb_03.1 sur arbitrage.**

---

## Bloqueurs pour prochain sprint

**Aucun.**

Le spec Sx_03 FINAL est un contrat long-terme stable. Les evolutions possibles sont cartographiees par priorite et declenchees par triggers explicites, pas par intention abstraite.

Le systeme exercice SPIGNOS (Sx_01 + Sx_02 + Sx_03) est **en etat de maturite documentaire complete**.

---

## Synthese executive (5 lignes)

- Substitution SPIGNOS V2 : Option 1 JSON-based integralement buildee, stable, correctement nourrit analytics
- 5 niveaux conceptuels distingues, 4 niveaux d'equivalence proposes, 6 dimensions taxonomie cible
- 3 lectures historiques coexistantes (execution stricte, slot-based, pattern futur)
- Zero rework composant exercice — les 6 garde-fous Sx_02 sont respectes par design
- Prochains enrichissements priorises (P2-P6), tous declenches par triggers explicites Sx_03.1
