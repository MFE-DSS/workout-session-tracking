# SPIGNOS Catalog Substitution Matrix v1 (etape B)

**Date:** 2026-04-15
**Status:** Matrice exploitable, en attente de validation utilisateur avant build (etape A)
**Cible:** version catalogue `2026-04-15.v9`
**Origine:** Sb_catalog_substitution_v1, derive de `SPIGNOS_CATALOG_BENCHMARK_REVIEW_v1.md` §4 chantier 1
**Avant build (A):** valider ce document ; ajustements possibles sur wording, choix de substituts, ou priorites.

---

## 0. Lecture du document

Chaque ligne = une nouvelle relation de substitution a ajouter dans `data/reference_split.json`. Les noms sont **exactement** ceux qui seront ecrits dans le JSON. Les zones sont celles qui seront calculees par `classify_exercise()` une fois les patterns ajoutes (voir §5).

Format des cellules de substitut : `Nom — zone` ou `Nom — [pattern manquant, ajout requis]`.

---

## 1. Statistiques de cible

| Indicateur | Avant (v8) | Apres (v9 cible) | Delta |
|---|---|---|---|
| Total relations declarees | 9 | **34** | +25 |
| Slots core avec >=1 substitut | 7 / 45 (16%) | 26 / 45 (58%) | +19 slots couverts |
| Substituts uniques proposes | 14 | ~40 | +26 |
| Patterns muscle_mapping requis | 0 | 7 (a ajouter) | +7 |

---

## 2. Matrice complete des nouvelles substitutions

### Priorite P0 — Critique (6 nouvelles relations)

Slots dont l'absence de substitut casse le plus l'experience.

| Slot | Exercice prescrit (catalogue) | Substituts proposes |
|------|-------------------------------|---------------------|
| `legs-a` E3 | Leg extensions assises | 1. Sissy squat machine — quads<br>2. Reverse Nordic — quads `[pattern]`<br>3. Leg extension câble unilatéral — quads `[pattern]` |
| `legs-b` E5 | Leg extensions assises | 1. Sissy squat machine — quads<br>2. Reverse Nordic — quads `[pattern]`<br>3. Leg extension câble unilatéral — quads `[pattern]` |
| `short-upper` E3 | Machine shoulder press | 1. Shoulder press haltères assis — delt_lat<br>2. Smith shoulder press — delt_lat<br>3. Arnold press — delt_lat `[pattern]` |
| `catch-up-shoulders` E1 | Machine shoulder press | 1. Shoulder press haltères assis — delt_lat<br>2. Smith shoulder press — delt_lat<br>3. Arnold press — delt_lat `[pattern]` |
| `legs-a` E4 | Leg curls assis | 1. Leg curls allongé — posterior<br>2. Sliding leg curl — posterior |
| `legs-b` E2 | Leg curls allongé | 1. Leg curls assis — posterior<br>2. Sliding leg curl — posterior |

### Priorite P1 — Forte (11 nouvelles relations)

Couverture des exercices reutilises >=2x sans fallback.

| Slot | Exercice prescrit | Substituts proposes |
|------|-------------------|---------------------|
| `push-b` E6 | Face pull câble (corde) | 1. Reverse fly machine — delt_post<br>2. Y-raise haltère — delt_post `[pattern]` |
| `pull-a` E5 | Face pull câble | 1. Reverse fly machine — delt_post<br>2. Y-raise haltère — delt_post `[pattern]` |
| `short-upper` E7 | Face pull câble | 1. Reverse fly machine — delt_post<br>2. Y-raise haltère — delt_post `[pattern]` |
| `catch-up-shoulders` E6 | Face pull câble | 1. Reverse fly machine — delt_post<br>2. Y-raise haltère — delt_post `[pattern]` |
| `pull-a` E1 | Tirage poulie haute prise neutre | 1. Traction assistée machine — lats `[pattern]`<br>2. Lat pulldown prise large — lats |
| `short-upper` E2 | Tirage poulie haute prise neutre | 1. Traction assistée machine — lats `[pattern]`<br>2. Lat pulldown prise large — lats |
| `catch-up-back-width` E1 | Tirage poulie haute prise neutre | 1. Traction assistée machine — lats `[pattern]`<br>2. Lat pulldown prise large — lats |
| `legs-b` E1 | Romanian Deadlift haltères | 1. Romanian Deadlift barre — posterior<br>2. Back extension 45° (bias ischios) — posterior `[pattern]`<br>3. Good morning haltères — posterior |
| `pull-b` E4 | Shrugs haltères | 1. Shrugs barre — upper_back<br>2. Shrugs câble — upper_back |
| `legs-b` E7 | Crunch câble à genoux | 1. Machine crunch — core<br>2. Hanging knee raise — core<br>3. Decline crunch — core |
| `liss-abs` E2 | Crunch câble à genoux | 1. Machine crunch — core<br>2. Hanging knee raise — core<br>3. Decline crunch — core |

### Priorite P2 — Moyenne (9 nouvelles relations)

| Slot | Exercice prescrit | Substituts proposes |
|------|-------------------|---------------------|
| `push-b` E7 | Triceps pushdown barre | 1. Pushdown corde — triceps<br>2. Extension overhead câble (corde) — triceps |
| `catch-up-arms` E6 | Triceps pushdown barre | 1. Pushdown corde — triceps<br>2. Extension overhead câble (corde) — triceps |
| `pull-b` E5 | Curl incliné haltères (banc 45°) | 1. Curl debout haltères — biceps<br>2. Preacher curl — biceps<br>3. Curl câble basse — biceps |
| `catch-up-arms` E1 | Curl incliné haltères (banc 45°) | 1. Curl debout haltères — biceps<br>2. Preacher curl — biceps<br>3. Curl câble basse — biceps |
| `push-b` E5 | Tirage front câble (prise large) | 1. Upright row haltères — delt_lat<br>2. Upright row câble — delt_lat |
| `catch-up-shoulders` E4 | Tirage front câble (prise large) | 1. Upright row haltères — delt_lat<br>2. Upright row câble — delt_lat |
| `short-upper` E4 | Élévations latérales câble | 1. Élévations latérales haltères — delt_lat<br>2. Élévations latérales machine — delt_lat |
| `push-b` E4 | Élévations latérales haltères assis | 1. Élévations latérales câble — delt_lat<br>2. Élévations latérales machine — delt_lat |
| `catch-up-shoulders` E3 | Élévations latérales haltères assis | 1. Élévations latérales câble — delt_lat<br>2. Élévations latérales machine — delt_lat |

### Priorite P3 — Optionnel mais utile (8 nouvelles relations)

| Slot | Exercice prescrit | Substituts proposes |
|------|-------------------|---------------------|
| `pull-a` E3 | Pullover câble (bras tendus, poulie haute) | 1. Pullover machine — lats `[pattern]`<br>2. Straight-arm pulldown câble — lats |
| `catch-up-back-width` E4 | Pullover câble (bras tendus) | 1. Pullover machine — lats `[pattern]`<br>2. Straight-arm pulldown câble — lats |
| `pull-a` E2 | Tirage vertical unilatéral câble | 1. Lat pulldown prise neutre — lats<br>2. Traction assistée unilatérale — lats `[pattern]` |
| `catch-up-back-width` E3 | Tirage vertical unilatéral câble | 1. Lat pulldown prise neutre — lats<br>2. Traction assistée unilatérale — lats `[pattern]` |
| `pull-b` E2 | Rowing câble assis prise neutre | 1. Rowing chest-supported — upper_back<br>2. Rowing haltère un bras — upper_back |
| `pull-b` E7 | Curl marteau haltères | 1. Curl marteau câble corde — biceps<br>2. Curl prise neutre câble — biceps |
| `catch-up-arms` E5 | Skull crushers EZ-bar | 1. Extension overhead câble (corde) — triceps<br>2. Pushdown corde — triceps |
| `legs-b` E6 | Mollets assis machine | 1. Mollets debout machine — calves<br>2. Calf press leg press — calves |

---

## 3. Total cumule (avant + apres)

| Slot | Substituts avant (v8) | Substituts apres (v9) |
|------|----------------------|------------------------|
| `push-a` E1 | Développé incliné haltères 30° | (inchangé) |
| `push-a` E2 | Développé couché haltères, Dips pectoraux (buste penché) | (inchangé) |
| `push-a` E4 | Machine shoulder press | (inchangé) |
| `push-b` E2 | Chest Press machine, Incline Smith Press | (inchangé) |
| `push-b` E4 | — | Élévations latérales câble, Élévations latérales machine |
| `push-b` E5 | — | Upright row haltères, Upright row câble |
| `push-b` E6 | — | Reverse fly machine, Y-raise haltère |
| `push-b` E7 | — | Pushdown corde, Extension overhead câble (corde) |
| `pull-a` E1 | — | Traction assistée machine, Lat pulldown prise large |
| `pull-a` E2 | — | Lat pulldown prise neutre, Traction assistée unilatérale |
| `pull-a` E3 | — | Pullover machine, Straight-arm pulldown câble |
| `pull-a` E4 | Écarté arrière d'épaule câble, Face pull câble | (inchangé) |
| `pull-a` E5 | — | Reverse fly machine, Y-raise haltère |
| `pull-b` E1 | Rowing haltère un bras (banc), Rowing câble assis prise neutre | (inchangé) |
| `pull-b` E2 | — | Rowing chest-supported, Rowing haltère un bras |
| `pull-b` E4 | — | Shrugs barre, Shrugs câble |
| `pull-b` E5 | — | Curl debout haltères, Preacher curl, Curl câble basse |
| `pull-b` E7 | — | Curl marteau câble corde, Curl prise neutre câble |
| `legs-a` E1 | Squat Smith machine (pieds avancés), Leg Press (pieds bas, serrés) | (inchangé) |
| `legs-a` E2 | Hack Squat machine | (inchangé) |
| `legs-a` E3 | — | Sissy squat machine, Reverse Nordic, Leg extension câble unilatéral |
| `legs-a` E4 | — | Leg curls allongé, Sliding leg curl |
| `legs-b` E1 | — | Romanian Deadlift barre, Back extension 45° (bias ischios), Good morning haltères |
| `legs-b` E2 | — | Leg curls assis, Sliding leg curl |
| `legs-b` E4 | Hip thrust haltères | (inchangé) |
| `legs-b` E5 | — | Sissy squat machine, Reverse Nordic, Leg extension câble unilatéral |
| `legs-b` E6 | — | Mollets debout machine, Calf press leg press |
| `legs-b` E7 | — | Machine crunch, Hanging knee raise, Decline crunch |
| `liss-abs` E2 | — | Machine crunch, Hanging knee raise, Decline crunch |
| `short-upper` E2 | — | Traction assistée machine, Lat pulldown prise large |
| `short-upper` E3 | — | Shoulder press haltères assis, Smith shoulder press, Arnold press |
| `short-upper` E4 | — | Élévations latérales haltères, Élévations latérales machine |
| `short-upper` E7 | — | Reverse fly machine, Y-raise haltère |
| `catch-up-shoulders` E1 | — | Shoulder press haltères assis, Smith shoulder press, Arnold press |
| `catch-up-shoulders` E3 | — | Élévations latérales câble, Élévations latérales machine |
| `catch-up-shoulders` E4 | — | Upright row haltères, Upright row câble |
| `catch-up-shoulders` E6 | — | Reverse fly machine, Y-raise haltère |
| `catch-up-arms` E1 | — | Curl debout haltères, Preacher curl, Curl câble basse |
| `catch-up-arms` E5 | — | Extension overhead câble (corde), Pushdown corde |
| `catch-up-arms` E6 | — | Pushdown corde, Extension overhead câble (corde) |
| `catch-up-back-width` E1 | — | Traction assistée machine, Lat pulldown prise large |
| `catch-up-back-width` E3 | — | Lat pulldown prise neutre, Traction assistée unilatérale |
| `catch-up-back-width` E4 | — | Pullover machine, Straight-arm pulldown câble |

**Templates archived (`upper-pecs-delts`, `upper-back-arms`, `lower-quad-bias`, `lower-posterior-bias`) : aucun changement.**

---

## 4. Patterns `muscle_mapping.py` requis

L'ajout de ces 7 patterns garantit que tous les substituts seront classifiables par `classify_exercise()` sans alterer la classification des exercices existants.

| # | Patterns a ajouter | Zone primaire | Zones secondaires | Substituts couverts |
|---|---------------------|---------------|-------------------|---------------------|
| 1 | `["pullover", "pull-over"]` | lats | biceps | Pullover machine |
| 2 | `["traction", "pull-up", "pullup", "pull up"]` | lats | biceps | Traction assistée machine, Traction assistée unilatérale (note : "traction" deja present comme pattern lats) |
| 3 | `["arnold press"]` | delt_lat | triceps | Arnold press |
| 4 | `["y-raise", "y raise"]` | delt_post | upper_back | Y-raise haltère |
| 5 | `["back extension", "hip extension", "hyperextension"]` | posterior | core | Back extension 45° (bias ischios) |
| 6 | `["reverse nordic", "sissy"]` | quads | — | Reverse Nordic, Sissy squat machine |
| 7 | `["knee extension"]` | quads | — | Leg extension câble unilatéral (alias de leg extension) |

**Verification preliminaire :** "Sissy squat machine" est deja matche par le pattern existant `"squat"` (zone quads). "traction" est deja un pattern lats. Les autres sont nouveaux ou explicitement requis.

**Note d'implementation :** ces additions vont dans `_EXERCISE_PATTERNS` dans `app/services/muscle_mapping.py`. Le pattern matching est case-insensitive et substring-based — pas de regression sur les classifications actuelles.

---

## 5. Regle de repos differenciee a inserer dans `global_notes`

Ajouter au champ `global_notes` du JSON v9, en remplaçant la ligne actuelle "Repos inter-séries 90-150s sauf indication contraire" :

```
Repos différencié selon l'effort :
  - Mouvements lourds multiarticulaires (hack squat, leg press, RDL, presses inclinées, rowings lourds, shoulder press) : 2-3 minutes minimum
  - Isolation et accessoires (curls, extensions, élévations latérales, mollets) : 60-90 secondes
  - Séries très près de l'échec, RP ou DS : 90-120 secondes
```

---

## 6. Plan d'execution etape A (Sb_catalog_substitution_v1)

| Etape | Action | Fichier | Test |
|-------|--------|---------|------|
| 1 | Ajouter les 7 patterns dans `_EXERCISE_PATTERNS` | `app/services/muscle_mapping.py` | `pytest tests/test_muscle_mapping.py -v` (pas de regression) |
| 2 | Modifier les 34 slots du catalogue (ajout `substitutes`) | `data/reference_split.json` | — |
| 3 | Mettre a jour `global_notes` avec regle repos differenciee | `data/reference_split.json` | — |
| 4 | Bumper version `2026-04-14.v8` → `2026-04-15.v9` | `data/reference_split.json` | — |
| 5 | Run QA script | — | `python scripts/catalog_qa.py` (exit 0 attendu) |
| 6 | Run full test suite | — | `pytest --ignore=tests/test_deploy_artifacts.py --ignore=tests/test_v1_acceptance.py -q` (519+ pass attendu) |
| 7 | Sprint report | `docs/SPRINT_Sb_catalog_substitution_v1_REPORT.md` | — |
| 8 | Commit | — | — |

**Cout total estime :** 1.5h (incluant verification et debug eventuel sur substitute names).

---

## 7. Decisions ouvertes a valider par l'utilisateur

Avant de passer a l'etape A, voici les points qui meritent un OK explicite :

### D1 — Naming des nouveaux substituts

Tous les noms de substituts sont en **francais avec accents**, conformes a la convention SPIGNOS existante. Exemples : "Reverse Nordic", "Y-raise haltère", "Traction assistée machine".

**Question :** OK avec ces wordings, ou changements souhaites ?

### D2 — Granularite des substituts

Certains slots ont **3 substituts** (legs-a/E3 leg extensions, push-b/E2 curl incliné). Cela peut paraitre genereux.

**Question :** Cible **2 substituts max** par slot ou **3 max** acceptable ?

### D3 — Niveau d'equivalence inline

Le format actuel reste **liste de strings** (`"substitutes": ["X", "Y"]`). Sx_03 FINAL P4 propose Option A (`{"name": "X", "level": "exact"}`) mais c'est differé.

**Question :** Garder format strings (cohérent avec v8) ou profiter de la v9 pour passer au format `{name, level}` ?

Recommandation : **garder strings** — separer l'enrichissement (P4) de la couverture (P0-P3). Eviter de cumuler 2 changements de format en un sprint.

### D4 — Substituts pour templates archived

Les 4 templates archived (`upper-pecs-delts`, `upper-back-arms`, `lower-quad-bias`, `lower-posterior-bias`) **n'ont aucun substitut** ajoute dans cette matrice.

**Question :** OK pour les laisser tels quels (pas de regression sur historique mais pas d'enrichissement) ou ajouter des substituts pour coherence ?

Recommandation : **ne rien toucher** — ils sont explicitement deprecies, l'effort de substitution est mieux investi sur les core/specialization/utility actifs.

### D5 — Patterns muscle_mapping vs reformulation

Pour les 7 patterns manquants, alternative : **reformuler les noms de substituts** pour matcher des patterns existants (ex: "Pullover machine" → "Pullover machine pec" qui matchera "pullover câble" pattern... non, ca ne marche pas).

**Question :** OK pour ajouter les 7 patterns dans `muscle_mapping.py` (recommande) ou preferes-tu reformuler le maximum pour eviter de toucher au mapping ?

Recommandation : **ajouter les patterns** — c'est plus propre, les noms de substituts restent naturels, et le mapping s'enrichit de maniere additive (zero regression).

### D6 — Inclusion de `Reverse Nordic`

Substitut inhabituel pour leg extension. Mecanique : on s'agenouille, on se penche en arriere genoux fixes, ca recrute massivement les quads en etirement. Tres efficace mais peut etre percu comme un "exercice de niche".

**Question :** Garder ou retirer ?

Recommandation : **garder** — c'est le seul vrai fallback bodyweight credible pour leg extension. Si les machines sont occupees ET pas de cable dispo, c'est l'option restante.

---

## 8. Definition of Done — etape B

| Critere | Statut |
|---------|--------|
| Liste exhaustive des slots a substituer (avec priorite P0/P1/P2/P3) | ✓ §2 |
| Noms exacts catalogue verifies (zero divergence d'accent) | ✓ §2-§3 |
| Verification classifiability + identification patterns manquants | ✓ §4 |
| Vue cumulee avant/apres par slot | ✓ §3 |
| Regle de repos differenciee redigee | ✓ §5 |
| Plan d'execution etape A scripte (8 etapes) | ✓ §6 |
| Decisions ouvertes listees pour validation utilisateur | ✓ §7 (6 questions) |

---

## 9. Synthese executive

- **34 nouvelles relations** de substitution proposees (cible v9 : 9 → 34 actives, soit +278%)
- **26 / 45 slots core** auront >=1 substitut (vs 7 / 45 actuellement, soit 16% → 58%)
- **7 patterns muscle_mapping** a ajouter pour garantir classifiability
- **Regle de repos differenciee** integree dans `global_notes`
- **Cout build A estime :** 1.5h
- **6 decisions ouvertes** a valider avant lancement etape A

Pret pour validation utilisateur des 6 decisions D1-D6, puis lancement etape A.
