# SPIGNOS Catalog Benchmark Review v1

**Date:** 2026-04-15
**Status:** Spec strategique — pas de build associe directement
**Origine:** benchmark scientifique + documentation bodybuilding produit hors repo, audit catalogue v2026-04-14.v8 effectue
**Suivi par:** Sb_catalog_substitution_v1 (matrice puis build) + Sb_catalog_balance_v1

---

## 1. Verdict global

Le catalogue SPIGNOS v2026-04-14.v8 est **scientifiquement coherent** avec la litterature hypertrophie moderne mais **operationnellement fragile** sur deux dimensions critiques :

- **Robustesse en salle** (substitution insuffisante pour un systeme machine-centric)
- **Cadrage methode** (regle de repos generique pour des compounds lourds)

Et **structurellement desequilibre** sur une dimension secondaire :

- **Volume Push A vs Pull A** (25 vs 15 work sets — ecart de 67%)

Ces 3 points sont a corriger **avant** tout enrichissement de la palette d'exercices ou de la couverture musculaire. Le ROI immediat n'est pas dans la variete mais dans la robustesse d'execution.

---

## 2. Ce que le benchmark valide deja

### 2.1 Cadre hypertrophie

Le noyau du systeme exercice SPIGNOS est compatible avec :
- **Relation dose-reponse volume / hypertrophie** (Schoenfeld et al., metaanalyses 2017-2023)
- **Charges legeres vs lourdes equivalentes** pour l'hypertrophie si proche de l'echec
- **Charges lourdes** specifiquement avantageuses pour la force maximale
- **Cadres ACSM / NSCA** : mix mono- + polyarticulaires, bilateraux + unilateraux, progression
- **Comparaison machines vs charges libres** : differences faibles a nulles sur l'hypertrophie
- **Travail proche de l'echec suffit** : aller a l'echec absolu n'est pas requis pour la croissance

### 2.2 Choix produit defendables

- **Biais machines/halteres** : justifie scientifiquement, coherent avec une salle equipee
- **Refus du discours pseudo-cardio** : aligne avec les cadres ACSM
- **Range de reps large** (6-20) : couvre la majorite des stimuli hypertrophiques
- **Templates `liss-only` + `liss-abs`** : entrainement concurrent gere correctement (volume / ordre / modalite distincts)
- **Mention "calories machine indicatives"** : honnete sur la fiabilite des estimations

**Verdict :** rien dans la litterature recente n'oblige a ajouter squat libre, deadlift libre, ou des patterns fortement techniques. Le catalogue est defendable tel quel sur le fond.

---

## 3. Ce que le benchmark identifie comme trous de couverture

### 3.1 Couverture par grande famille (vs documentation bodybuilding)

| Famille | Etat SPIGNOS | Trous identifies |
|---------|--------------|------------------|
| Pectoraux | Forte (incline, plat, butterfly, dips) | Couloir dips/decline plus complet possible |
| Dos | Forte (pulldown, rowings varies) | Pull-up assiste, T-bar/high row, back extension |
| Epaules | Tres complete (triptyque press + lateral + posterieur) | OK |
| Bras biceps | Bonne (incline, EZ, marteau) | Preacher-type peu present |
| Bras triceps | Bonne (pushdown, overhead, skull) | Dip triceps en machine assistee |
| Quadriceps | Bonne (hack, leg press, extension) | **Aucun pattern unilateral** (lunge, split squat, Bulgarian) |
| Posterieur | Correcte (RDL, hip thrust, leg curl) | Back extension absente |
| Mollets | Correcte | OK |
| Core | Lab base via legs + liss-abs | OK pour V2 |

### 3.2 Inference matrice machines minimale

Le core SPIGNOS est executable dans une salle commerciale possedant : Smith, banc reglable + halteres, double poulie, chest press, shoulder press, lat pulldown, rowing assis ou chest-supported, hack/leg press, leg extension, leg curl, machine mollets.

**Equipements qui augmenteraient la couverture si ajoutes au catalogue :**
1. Machine assistance dips/pull-ups
2. Station preacher ou curl machine
3. Banc back extension
4. Poste hip abduction

**Statut :** ces ajouts sont **non urgents**. L'absence n'est pas une faille scientifique — c'est une ouverture potentielle V3.

---

## 4. Trois chantiers correctifs prioritaires

### Chantier 1 — Couverture fonctionnelle du graphe de substitution (P0)

**Constat :** 9 relations sur 45 slots core = **80% des slots sans fallback**. Dans un systeme machine-centric, c'est le risque produit numero 1. Chaque machine occupee casse l'experience plus qu'elle ne devrait.

**Cible :** passer de 9 a ~25-30 relations couvrant 100% des slots primaires en core.

**Standard minimal de substitution :**

Hierarchie de fallback par ordre de priorite :
1. Meme famille de machine si dispo
2. Version cable
3. Version haltere/barre
4. Variante poids du corps / regression

**Regle non negociable :** un substitut doit preserver la **zone primaire** ET la **famille de mouvement**. Pas de "vaguement proche".

**Slots prioritaires (P0 = critique, P3 = optionnel) :**

| Priorite | Slot | Substituts recommandes (premier = preferre) |
|----------|------|---------------------------------------------|
| **P0** | Leg extensions assises (legs-a/E3, legs-b/E5) | Sissy squat machine, Reverse Nordic, Knee extension cable unilateral |
| **P0** | Machine shoulder press (short-upper/E3, catch-up-shoulders/E1) | Shoulder press halteres assis, Smith shoulder press, Arnold press |
| **P0** | Leg curls assis (legs-a/E4) | Leg curls allonge, Sliding leg curl, Nordic curl regression |
| **P0** | Leg curls allonge (legs-b/E2) | Leg curls assis, Sliding leg curl |
| P1 | Face pull cable (push-b/E6, pull-a/E5, short-upper/E7) | Reverse fly machine, Y-raise haltere |
| P1 | Tirage poulie haute prise neutre (pull-a/E1, short-upper/E2, catch-up-back-width/E1) | Pull-up assiste machine, Lat pulldown prise large, Tirage vertical unilateral cable |
| P1 | Romanian Deadlift halteres (legs-b/E1) | RDL barre, Back extension 45° bias ischios, Good morning halteres |
| P1 | Shrugs halteres (pull-b/E4) | Shrugs barre, Shrugs cable |
| P1 | Crunch cable a genoux (legs-b/E7, liss-abs/E2) | Machine crunch, Hanging knee raise, Decline crunch |
| P2 | Triceps pushdown barre (push-b/E7, catch-up-arms/E6) | Pushdown corde, Extension overhead cable corde |
| P2 | Curl incline halteres (banc 45°) (pull-b/E5, catch-up-arms/E1) | Curl debout halteres, Preacher curl, Curl cable basse |
| P2 | Tirage front cable prise large (push-b/E5, catch-up-shoulders/E4) | Élévations laterales seules, Upright row haltere |
| P2 | Élévations laterales cable (short-upper/E4) | Élévations laterales halteres, Élévations laterales machine |
| P2 | Élévations laterales halteres assis (push-b/E4, catch-up-shoulders/E3) | Élévations laterales cable, Élévations laterales machine |
| P3 | Hip thrust Smith (legs-b/E4) | Hip thrust halteres (deja), Glute bridge charge |
| P3 | Pullover cable (pull-a/E3, catch-up-back-width/E4) | Straight-arm pulldown, Pullover machine |
| P3 | Tirage vertical unilateral cable (pull-a/E2, catch-up-back-width/E3) | Lat pulldown prise neutre, Pull-up assiste unilateral |
| P3 | Rowing cable assis prise neutre (pull-b/E2) | Rowing chest-supported, Rowing haltere un bras |
| P3 | Curl marteau halteres (pull-b/E7) | Curl marteau cable corde, Curl prise neutre cable |
| P3 | Skull crushers EZ-bar (catch-up-arms/E5) | Extension overhead cable, Pushdown corde |
| P3 | Mollets assis machine (legs-b/E6) | Mollets debout machine, Calf press leg press |

**Total cible : ~21 nouvelles relations** ajoutees a 9 existantes = ~30 relations actives.

### Chantier 2 — Regle de repos differenciee (P0)

**Constat :** une seule regle "90-150s" dans `global_notes` du JSON. Trop generique pour des compounds lourds (hack squat, RDL, presses inclines, rowings lourds).

**Cible :** trois regimes explicites documentes dans `global_notes` :

```
Repos differencies selon l'effort :
- Mouvements lourds multiarticulaires (hack, leg press, RDL, presses inclines, rowings lourds, shoulder press) : 2-3 minutes minimum
- Isolation et accessoires (curls, extensions, lateral raises, calf raises) : 60-90 secondes
- Series tres pres de l'echec, RP ou DS : 90-120 secondes
```

**Implementation :** mise a jour de `data/reference_split.json` `global_notes` (zero migration, zero code). Page `/science` deja en place pour exposer la regle si besoin.

**Pas de timer par set dans l'UI** — surcharge inutile.

### Chantier 3 — Equilibrage volume Push A vs Pull A (P1)

**Constat :**
- Push A : 8 exercices, 25 work sets
- Pull A : 5 exercices, 15 work sets
- Ecart : 67% — Push A devient long en pratique gym (~75 min), Pull A est sous-dimensionne meme pour un focus etroit (largeur)

**Decision recommandee :** **Option B — enrichir Pull A**.

Ajouter 1-2 exercices a Pull A pour atteindre ~7 ex / ~20 work sets, alignant avec la densite des autres core.

**Candidats d'ajout pour Pull A** (a arbitrer en B) :
- Pullover machine (renforce largeur, complement E3 cable)
- Tirage horizontal cable poitrine basse (chest-supported style assis cable)
- Shrugs avec mention "leger volume" (transition delts post → upper back)

**Justification :** Pull A focus "Dos largeur + Delts posterieurs" reste valide, mais 5 exercices c'est sous le seuil de stimulation pour les zones cibles. L'absence d'isolation biceps reste **assumee** (focus largeur explicite).

**Pas d'allegement de Push A** : 25 sets sur 8 exercices reste pratiquable. Si la duree devient un probleme, c'est l'utilisateur qui peut tronquer (le flow `Enregistrer et terminer` permet de partir tot).

---

## 5. Ce que le benchmark identifie comme NON URGENT

A documenter mais **ne pas faire dans Sb_catalog_*_v1** :

| Item | Raison du defer |
|------|-----------------|
| Ajout pattern unilateral genou-dominant (lunge, split squat, Bulgarian) | Complement de couverture, pas de gap critique. Defer V3. |
| Ajout back extension / hyperextension | Optionnel. Si trigger besoin posterieur explicite. |
| Ajout preacher-type curl | Couvert par incline curl en partie. P3 enrichissement. |
| Ajout dips assistes / pull-up assistes machines | Si feature "machine matrix" prioritaire. Sinon P3. |
| Ajout T-bar row / high row | Nice to have. Pas critique. |
| Ressuscitation des templates archives (`upper-pecs-delts`, etc.) | **Non recommande**. Hors V2 par decision design. |
| Tempo prescrit par exercice | Litterature ne soutient pas. Pas dans le scope. |
| Deroulement chronologie / minutage par seance | Hors scope, deborde de l'objet du catalogue. |

---

## 6. Sprints proposes et ordre

### Sb_catalog_substitution_v1 (priorite **haute**)

**Objectif :** appliquer le standard minimal de substitution + regle de repos differenciee.

**Perimetre :**
- `data/reference_split.json` : ajouter ~21 relations de substitution selon matrice §4 chantier 1
- `data/reference_split.json` : mettre a jour `global_notes` avec regle de repos differenciee (chantier 2)
- Bumper version → v9
- Run `scripts/catalog_qa.py` → verifier classifiability de chaque substitute name
- `tests/test_catalog_integrity.py` : run full suite, doit passer

**Pas de code Python a modifier.** Pas de migration. Pas de service.

**Cout estime :** 1-2h (revue + edition JSON + verification).

**Risques :**
- Substitute name non classifiable par `muscle_mapping.classify_exercise()` → QA script bloque. Mitigation : ajouter le pattern dans `muscle_mapping._EXERCISE_PATTERNS` si exercice nouveau, ou ajuster le wording pour matcher un pattern existant.
- Re-seed declenche par bump version pourrait potentiellement casser des tests dependants des templates names (deja vu dans S0). Mitigation : tourner full suite et fixer les divergences au fur et a mesure.

**Criteres d'acceptation :**
- [ ] ~30 relations de substitution actives (vs 9 actuellement)
- [ ] Tous les slots P0 et P1 ont au moins 1 substitut declare
- [ ] `global_notes` contient la regle de repos differenciee
- [ ] Version bumpee a `2026-04-15.v9`
- [ ] `python scripts/catalog_qa.py` retourne exit code 0
- [ ] `pytest tests/test_catalog_integrity.py -v` passe
- [ ] Full suite green hors deploy_artifacts/v1_acceptance

### Sb_catalog_balance_v1 (priorite moyenne, **post-substitution**)

**Objectif :** equilibrer la densite Push A vs Pull A.

**Perimetre :**
- `data/reference_split.json` : ajouter 1-2 exercices a Pull A
- Documenter l'arbitrage dans `docs/strategy/SPIGNOS_CATALOG_GOVERNANCE.md`
- Bumper version → v10
- Re-run QA + tests

**Cout estime :** 30 minutes.

**Risques :** faibles. Ajout incremental.

**Criteres d'acceptation :**
- [ ] Pull A contient 7 exercices (vs 5)
- [ ] Pull A contient 18-22 work sets (vs 15)
- [ ] Aucune regression sur les autres templates
- [ ] QA script passe
- [ ] Full suite green

### Builds explicitement deferes

Aucun nouveau build dans cette revue ne touche :
- Modele DB
- Migrations
- Services Python
- UX du composant exercice
- Substitution graph Option 2 (canonical entity — triggers Sx_03.1)
- Taxonomie de mouvement complete (deferree)

---

## 7. Decoupage operationnel C → B → A

| Etape | Livrable | Statut |
|-------|----------|--------|
| **C** | Ce document — `SPIGNOS_CATALOG_BENCHMARK_REVIEW_v1.md` | **En cours** (a valider par l'utilisateur) |
| **B** | Matrice complete des substitutions sous forme exploitable (table CSV ou MD avec slot → substituts → niveau d'equivalence si pertinent) | Pending |
| **A** | Implementation Sb_catalog_substitution_v1 + tests + commit | Pending |

L'etape B sert a **valider la liste exacte des substitutions** avant de toucher le JSON. L'etape A est mecanique une fois B verrouille.

---

## 8. Definition of Done — spec C

| Critere | Statut |
|---------|--------|
| Verdict global du benchmark synthetise | ✓ §1 |
| Ce qui est valide scientifiquement documente | ✓ §2 |
| Trous de couverture identifies | ✓ §3 |
| 3 chantiers correctifs prioritaires definis | ✓ §4 |
| Standard minimal de substitution etabli | ✓ §4 chantier 1 (hierarchie + regle non negociable) |
| Regle de repos differenciee redigee | ✓ §4 chantier 2 |
| Decision Push A vs Pull A arbitree | ✓ §4 chantier 3 (option B) |
| NON URGENT explicitement documente | ✓ §5 (8 items defers) |
| Sprints suivants cadres | ✓ §6 (Sb_catalog_substitution_v1 + Sb_catalog_balance_v1) |
| Decoupage C → B → A clair | ✓ §7 |
| Pas de build engage par ce document | ✓ |

---

## 9. Synthese executive

- Catalogue SPIGNOS v8 : **scientifiquement coherent, operationnellement fragile**
- 3 chantiers correctifs prioritaires : **substitution gym-proof** (P0) + **repos differencie** (P0) + **equilibre Push A/Pull A** (P1)
- Cible substitutions : passer de 9 a ~30 relations, couverture 100% des slots primaires core
- Aucun chantier ne touche le code Python, modele DB, ou UX composant exercice
- Ordre execution recommande : **C (ce spec) → B (matrice validee) → A (build JSON v9)**

Pret pour l'etape B des validation utilisateur de ce document.
