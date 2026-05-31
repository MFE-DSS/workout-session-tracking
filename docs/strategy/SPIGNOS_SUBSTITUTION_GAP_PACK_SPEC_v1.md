# SPIGNOS — Substitution Gap Pack Spec v1 (Sx_22a)

**Date :** 2026-05-09
**Type :** SPEC ONLY — refonte agnostique du graphe de substitution.
**Prérequis :** Sx_21 méta-spec (classification dogfooding).
**Successeur build :** Sb_22a — implémentation du pack par lots priorisés.

---

## A. État actuel du graphe (audit chiffré)

Audit `data/reference_split.json` v13 :

| Template | Exos | Subs total | Exos sans sub |
|---|---|---|---|
| push-a | 7 | 4 | **4** |
| push-b | 7 | 10 | 2 |
| pull-a | 7 | 14 | 0 |
| pull-b | 7 | 14 | 1 |
| legs-a | 7 | 10 | 2 |
| legs-b | 7 | 14 | 1 |
| upper-pecs-delts | 7 | **0** | **7** |
| upper-back-arms | 7 | **0** | **7** |
| lower-quad-bias | 6 | **0** | **6** |
| lower-posterior-bias | 6 | **0** | **6** |
| short-upper | 7 | 9 | 3 |
| catch-up-shoulders | 6 | 9 | 2 |
| catch-up-arms | 7 | 7 | 4 |
| catch-up-back-width | 6 | 6 | 3 |

**Total : 48 exercices sans aucune alternative sur 95 exercices strength.** Les 4 templates "upper-*" et "lower-*" sont à 100 % non-substituables. Le user a raison sur le diagnostic : C1/C2 ferment 2 cas spécifiques, l'écosystème en a 46 autres.

## B. Cause systémique

Le graphe est **ad hoc** : chaque substitut est saisi à la main dans le JSON, sans heuristique. Quand le user ajoute un template (Sb_catalog_v12, v13), il oublie ou minimise les substitutions parce que ça scale mal.

**Manque dans le système :** une fonction `substitutes_for(exercise)` capable de **proposer** des alternatives à partir de propriétés de l'exercice plutôt que d'une liste figée.

## C. Modèle proposé

### C.1 — Trois niveaux de substitution (terminologie verrouillée v1.1)

| Niveau | Nom canonique | Source | Garantie | Précision |
|---|---|---|---|---|
| **N1** | **Équivalence stricte** | `template_exercises.substitutes_json` (curé humain) **OU** match `pattern_motor == X` AND `zone_primary == X` AND `equipment_family == X` AND `chain == X` | substitution sans perte d'intention | très haute |
| **N2** | **Fallback très proche** | proximity ≥ 70 (cf §C.3) avec **pattern_motor identique obligatoire** | substitution avec intention conservée mais variation équipement/chaîne | haute |
| **N3** | **Fallback zone-only** | même zone primaire, pattern différent | dernier recours, l'intention motrice change | basse — à activer par clic explicite |

Le drawer rend N1, puis N2, puis N3 si l'utilisateur clique "Voir plus". Chaque entrée porte un badge :
- `Équivalent` (N1)
- `Proche` (N2, avec sous-tag : `même pattern · autre équipement`)
- `Élargi` (N3) — toujours derrière un disclosure "Voir alternatives élargies"

**Règle stricte v1.1 — interdiction zone-only sans tag :** un suggéré ne peut **jamais** être affiché en N1 ou N2 sur la seule base de la zone musculaire commune. Le pattern_motor est obligatoirement vérifié pour N2, et N1 exige les 4 dimensions identiques. Une suggestion zone-only est **toujours** N3 et **toujours** étiquetée `Élargi`.

### C.2 — Propriétés d'exercice à indexer

Pour faire fonctionner N2, chaque exercice du catalogue doit exposer :

| Propriété | Source actuelle | Manquant ? |
|---|---|---|
| **zone primaire** | `muscle_mapping.classify_exercise()` | OK (Sb_07) |
| **zones secondaires** | idem (retourne `(primary, [secondary…])`) | OK |
| **pattern moteur** | aucune | **À ajouter** — enum verrouillé v1.1 (cf §C.2bis) |
| **équipement** | `machine_atlas.json` (8 familles) | OK partiel — pas tous les exos référencés |
| **chaîne (compound/isolation)** | inférable du nom | **À ajouter** comme champ explicite |
| **plan articulaire** | aucune | hors V1 (trop fin) |

### C.2bis — Enum `pattern_motor` (verrouillé v1.1)

Valeurs autorisées, exhaustives V1 :

```
push_horizontal   — bench press, pec deck, dips
push_vertical     — overhead press, military, arnold
pull_horizontal   — rowings (barre, machine, câble, haltère)
pull_vertical     — tirages haute, pulldowns, traction
squat             — back squat, front squat, hack squat, leg press
hinge             — RDL, hip thrust, good morning, kettlebell swing
lunge             — fente avant, bulgarian split, walking lunge
isolation_upper   — curls, extensions, élévations latérales, kickbacks
isolation_lower   — leg extension, leg curl, adduction, abduction, mollets
core              — planche, crunch, anti-rotation, dead bug
cardio            — run, bike, row, stairs (séances kind=cardio)
```

**Tout exercice doit recevoir exactement un `pattern_motor`** issu de cet enum. Aucune autre valeur n'est autorisée. Un script `scripts/catalog_pattern_qa.py` (livré en Sb_22a.1) refuse tout commit de catalogue avec un pattern invalide ou manquant.

### C.3 — Score de proximité

Pour 2 exercices A et B :

```
proximity(A, B) =
    50 * (A.zone_primary == B.zone_primary)
  + 20 * (A.pattern == B.pattern)
  + 15 * (A.equipment_family == B.equipment_family)
  + 10 * (A.chain == B.chain)            # compound vs isolation
  +  5 * |A.zones_secondary ∩ B.zones_secondary|
```

Score max ≈ 100 (mêmes zone + pattern + équipement + chaîne + 1 secondaire commune).

**Seuils (v1.1) :**
- `proximity ≥ 70` **ET** `pattern_motor identique` → N2 (suggéré fort)
- `50 ≤ proximity < 70` **ET** `pattern_motor identique` → N2 (suggéré faible)
- `pattern_motor différent`, peu importe le score → **N3 obligatoirement** (zone-only)
- `proximity < 50` → N3 même si pattern identique

**Garde-fou v1.1 :** la fonction `compute_n2_suggestions()` doit lever `ValueError` si on tente de remonter en N1/N2 une suggestion dont `pattern_motor` diffère de l'origine. Test unitaire obligatoire.

### C.4 — Substitutions transversales haute valeur

Cas que la proximité brute rate parce que le pattern diffère mais l'intention est la même :

| Origine | Cible transversale | Justification |
|---|---|---|
| Rowing horizontal | Tirage vertical | Épaisseur ↔ largeur — interchangeable si user veut varier ou si stations occupées |
| Squat | Hack squat / Leg press | Quad-dominant équivalent, moins de stress lombaire |
| Développé incliné barre | Développé incliné haltère / machine | Même angle, équipement substituable |
| Curl barre | Curl haltère / pupitre | Stéréotypique |
| Élévation latérale haltère | Élévation latérale câble / machine | Idem |
| Adduction assise | Adduction debout câble / couchée | Cas C1 du dogfood |

À encoder dans un **fichier `cross_pattern_substitutions.json`** que `substitutes_for()` consulte en complément du score proximité.

### C.4bis — Sous-lot MVP haute valeur (v1.1, priorité absolue Sb_22a)

Avant les 4 templates synthèse (upper/lower-*), traiter en **premier** ces 7 familles fonctionnelles que le user a explicitement identifiées comme haute valeur :

| Famille fonctionnelle | Exemples d'exercices concernés | Cible substitutions |
|---|---|---|
| **Adduction** | adduction assise, adduction debout câble, adduction couchée | 3-4 |
| **Rowing ↔ Tirage vertical** | rowing barre, rowing machine, tirage haute neutre, pulldown | 4-5 cross-pattern |
| **Shoulder press** | OHP barre, OHP haltère, Smith OHP, machine shoulder press | 3-4 |
| **Leg extension / Leg curl** | leg extension, sissy squat machine, leg curl couché/assis, nordic curl | 3-4 paire |
| **Triceps** | extension poulie, dips, kickback, overhead extension, JM press | 3-4 |
| **Curl (biceps)** | curl barre, curl haltère, curl pupitre, curl marteau, curl câble | 4-5 |
| **Chest press / Incline** | DC barre, DC haltère, DC machine, DC incliné variantes | 4-5 |

**Effet escompté :** ~25-30 substitutions ciblées qui couvrent les patterns les plus exposés au "station occupée / pas envie aujourd'hui". Lot livrable en ~4 h avant les trous synthèse.

### C.4ter — Matrice de couverture par famille (avant/après obligatoire)

Sb_22a doit produire (en sortie de build, dans le sprint report) une matrice :

| Famille fonctionnelle | Exos catalogue | Exos avec ≥ 1 N1/N2 avant | Exos avec ≥ 1 N1/N2 après | Δ |
|---|---|---|---|---|
| Adduction | X | Y | Z | +N |
| Rowing horizontal | … | … | … | … |
| Tirage vertical | … | … | … | … |
| Shoulder press | … | … | … | … |
| Leg extension | … | … | … | … |
| Leg curl | … | … | … | … |
| Triceps isolation | … | … | … | … |
| Curl biceps | … | … | … | … |
| Chest press / incline | … | … | … | … |
| Squat / leg press | … | … | … | … |
| Hinge (RDL, hip thrust) | … | … | … | … |
| Élévations latérales | … | … | … | … |

Le sprint Sb_22a n'est **pas mergeable** tant que cette matrice n'atteint pas ≥ 80 % des familles couvertes (chaque exo de la famille → ≥ 1 suggestion N1 ou N2).

### C.5 — Trous critiques à combler MVP (priorité 1)

Top 10 manques bloquants pour V1 :

1. **upper-pecs-delts** (7 exos / 0 sub) — entier
2. **upper-back-arms** (7 exos / 0 sub) — entier
3. **lower-quad-bias** (6 / 0) — entier
4. **lower-posterior-bias** (6 / 0) — entier
5. **push-a E1-E7** (4 sans sub) — exos lourds
6. **legs-a E2, E6** (2 sans sub) — exos pivots
7. **catch-up-arms** (4 sans sub)
8. **short-upper** (3 sans sub)
9. **catch-up-back-width** (3 sans sub)
10. **push-b** (2 sans sub)

→ **48 substitutions à ajouter MVP** réparties sur 14 templates.

## D. Stratégie de comblement priorisée

### Phase 1 — Heuristique seule (Sb_22a.1, ~6 h)

- Ajouter champs `pattern_motor`, `chain_type`, `equipment_family` à chaque exercice du catalogue (script `scripts/enrich_catalog.py`).
- Implémenter `services/substitution.py::compute_proximity()`.
- Implémenter `compute_n2_suggestions(template_exercise)` retournant top 5 par proximité.
- Aucune nouvelle saisie manuelle.

**Effet attendu :** chaque exo sans sub explicite obtient automatiquement 3-5 suggestions N2.

### Phase 2 — Cross-pattern manuel (Sb_22a.2, ~3 h)

- Créer `data/cross_pattern_substitutions.json` avec les 12-15 transversales haute valeur.
- Brancher dans `substitutes_for()`.

### Phase 3 — Trous critiques validés (Sb_22a.3, ~4 h)

- Saisir manuellement les 48 substitutions des 4 templates upper/lower-* (les heuristiques V2 ne suffisent pas pour ces templates "synthèse").
- Bump catalogue v13 → v14.

### Phase 4 — Drawer UI (Sb_22a.4, ~3 h)

- Drawer substitution affiche les 3 niveaux empilés avec badges.
- Compteur "X suggestions disponibles" pour annoncer la richesse.

**Effort total Sb_22a : 16 h** sur ~2 semaines, étalable.

## D.bis — Contrat prévu/réalisé (verrouillé v1.1)

Trois invariants **hard** que Sb_22a ne peut pas casser :

1. **Conservation du prévu** — `template_exercises` (le programme) n'est jamais modifié rétroactivement. L'enrichissement `pattern_motor`/`chain_type`/`equipment_family` est ajouté sur les **lignes catalogue**, jamais sur les snapshots de séance.
2. **Conservation du réalisé** — `session_exercises.substituted_name` et `exercise_name_snapshot` restent intacts. Aucune migration ne touche ces colonnes.
3. **Aucune réécriture historique** — les sessions passées affichent le drawer N1/N2/N3 calculé **sur la base du catalogue actuel**, mais leur historique réel (ce qui a été fait) n'est ni modifié ni recalculé. La séparation prévu (template) / réalisé (session_exercise) est sacrée.

## E. Acceptance criteria Sx_22a (v1.1)

| Critère | Mesure | Bloquant |
|---|---|---|
| Pas d'exo sans aucune sub visible | 100 % des 95 exos strength → ≥ 1 entrée N1/N2/N3 | ✅ |
| Enum `pattern_motor` complet et validé | Tous les exos catalogue ont un `pattern_motor` valide (script QA refuse l'invalide) | ✅ |
| Proximity fonction documentée | Spec §C.3 + tests unitaires (incl. test "pattern différent → N3 obligatoire") | ✅ |
| Cross-pattern fichier livré | `data/cross_pattern_substitutions.json` ≥ 12 entrées | ✅ |
| Drawer affiche 3 niveaux avec badges | UI screenshot + badge `Équivalent`/`Proche`/`Élargi` visible | ✅ |
| Sous-lot haute valeur livré en premier | 7 familles §C.4bis couvertes avant les templates synthèse | ✅ |
| Matrice avant/après publiée | Tableau §C.4ter dans le sprint report, ≥ 80 % familles couvertes | ✅ |
| Aucune réécriture historique | `session_exercises` colonnes intactes, test de régression sur 5 sessions tests existantes | ✅ |
| `template_exercises` non modifiés rétroactivement | Diff Alembic = pas d'`ALTER` sur `template_exercises.substitutes_json`, juste ADD COLUMN sur exercices catalogue | ✅ |
| 0 régression tests existants | 739 tests verts | ✅ |

## F. Limites assumées

1. **Pas de proxy biomécanique précis** — pas de plan articulaire ni d'analyse vidéo. La proximité reste lexicale/catégorielle.
2. **Pas d'apprentissage auto** — la fonction reste déterministe. Pas de "les users qui ont swappé A ont aussi swappé B".
3. **Catalogue toujours editable à la main** — l'heuristique aide mais ne remplace pas la curation V1.
4. **N3 fallback peut suggérer du bruit** — explicitement étiqueté "Élargi", à activer par clic utilisateur.

## G. Risques

| Risque | Mitigation |
|---|---|
| Sur-suggestion → user perdu | Limiter à 5 N2 max, 5 N3 max, ordre proximité décroissante |
| Cross-pattern controversé (rowings ↔ tirages) | Documenter l'intention "largeur vs épaisseur" dans le tooltip de l'entrée |
| Tag pattern erroné sur 1 exo casse tout | Script QA `scripts/catalog_pattern_qa.py` à ajouter |
| Drawer trop chargé mobile | Repli avec onglets `Sélectionné / Suggéré / Élargi` |
