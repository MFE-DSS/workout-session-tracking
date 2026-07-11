# Sx_DOGFOOD_01 — Load Hint / Substitution Coherence (AUDIT + SPEC ONLY)

**Statut** : 🟢 SPEC ONLY — pending human review
**Date** : 2026-07-11
**Type** : audit dogfood + spec de cadrage (docs-only, aucun code)
**Origine** : dogfooding — les suggestions de charge (poids/reps) peuvent devenir
**incohérentes** quand un exercice a été **substitué** (dans une séance passée ou courante).

---

## 1. Problème produit

Une suggestion de charge n'est fiable **que si elle correspond à l'exercice
réellement exécuté**. Aujourd'hui, plusieurs surfaces de la carte d'exercice
tirent leur donnée de `last_time_by_exercise_code()`, indexé sur le **slot**
(`exercise_code_snapshot`) **sans regarder la substitution** — elles peuvent donc
afficher la charge d'un exercice **différent** (ex. Leg Press affiché comme
« dernière fois » du prescrit Squat).

**Deuxième problème (UI mobile)** : les placeholders poids/reps dans les cases
(ex. « ≈ 102.5 ») peuvent être trop longs pour la largeur de l'input sur petit
écran ; l'unité (kg/reps) n'est pas séparée du placeholder.

---

## 2. Règle directrice

> **Silence plutôt que faux poids.** Une suggestion de charge n'est affichée que
> si elle correspond à l'exercice réellement exécuté ; sinon la surface devient
> silencieuse (fallback conservateur), jamais une valeur trompeuse.

---

## 3. Carte des producteurs de charge (audit)

| # | Producteur | Fichier | Identité utilisée | Substitution-aware ? |
|---|---|---|---|---|
| 1 | `last_time_by_exercise_code` (Référence précédente / Dernière fois) | `stats.py:118` | `(template_slug, exercise_code_snapshot)` | ❌ **NON** |
| 2 | `build_overload_input_for_exercise` (placeholder cible) | `overload_inputs.py:96/231` | code + **politique substitution stricte** | ✅ OUI |
| 3 | `compute_overload_hint` (engine) | `overload_engine.py:255` | consomme input déjà filtré | ✅ (par amont) |
| 4 | `explain_overload_hint` / `_build_overload_placeholder` | `overload_explainer.py` / `sessions.py:182` | — | ✅ (par amont) |
| 5 | `compute_delta` (delta) | `delta.py:38` | consomme `last_time.get(code)` | ❌ **NON** |
| 6 | `build_chip` (briefing « dernière fois ») | `briefing.py:86` | consomme `last_time.get(code)` | ❌ **NON** |
| 7 | `build_peek` (up-next) | `briefing.py:107` | consomme `last_time.get(code)` | ❌ **NON** |
| 8 | `compute_hints` (hints Sx_08 : +10% / reps drop) | `hints.py:32` | consomme `last_time.get(code)` | ❌ **NON** |

**Diagnostic** : `overload` est **déjà sûr** (silence si substitué) ; **5 surfaces
dérivées de `last_time` ne le sont pas** (Référence précédente, Delta, Hints Sx_08,
Chip, Peek). Ironie du code : `overload_inputs` prétend « s'aligner sur
`last_time_by_exercise_code` » (commentaire L117) mais `last_time` n'a pas la
politique de substitution.

---

## 4. Carte des identités d'exercice

| Attribut (`SessionExercise`) | Rôle | Utilisé comme identité de charge ? |
|---|---|---|
| `exercise_code_snapshot` | slot prescrit immuable (E1…E7) | ✅ clé de `last_time` (mais slot ≠ exercice réel si substitué) |
| `exercise_name_snapshot` | nom prescrit | affichage / fallback |
| `substituted_name` (nullable) | nom réellement exécuté si substitution | ✅ critère de la politique overload ; **ignoré par `last_time`** |
| `actual_exercise_name(se)` = `substituted_name or exercise_name_snapshot` | nom réel exécuté | utilisé par overload/descriptor, **pas** par `last_time` |

---

## 5. Matrice des 5 scénarios × surfaces (cœur de l'audit)

Notation : `prescrit` = pas de substitution ; `sub(X)` = substitué par X.

| Surface | S1 P→P | S2 P→sub | S3 sub→P | S4 sub→même sub | S5 sub→autre sub |
|---|---|---|---|---|---|
| `last_time` (Réf. précédente / Dernière fois) | ✅ | ❌ faux | ❌ faux | ✅ | ❌ faux |
| overload placeholder (cible) | ✅ | ✅ silence | ✅ | ✅ silence | ✅ silence |
| delta | ✅ | ❌ inter-exercice | ❌ inter-exercice | ✅ | ❌ inter-exercice |
| hints Sx_08 | ✅ | ❌ faux signal | ❌ faux signal | ✅ | ❌ faux signal |
| chip / peek briefing | ✅ | ❌ | ❌ | ✅ | ❌ |

- **S1 (prescrit→prescrit)** et **S4 (substitué→même substitut)** : cohérents partout.
- **S2 / S3 / S5** : `last_time` et ses dérivés affichent une charge d'un **exercice
  différent** → faux « dernière fois », faux delta, faux hint.

---

## 6. Analyse des transitions & décision « silence »

| Transition | `last_time` doit renvoyer | Décision |
|---|---|---|
| prescrit → prescrit | dernier **prescrit** du slot | inchangé (déjà correct) |
| prescrit → substitué | rien pour le prescrit ; overload déjà silencieux | **silence** sur Réf. précédente / delta / hint |
| substitué → prescrit | dernier **prescrit** (sauter les substitutions) | filtrer `substituted_name IS NULL` |
| substitué → **même** substitut | dernier historique du **même** `substituted_name` | afficher (utile — l'utilisateur réutilise l'alternative) |
| substitué → **autre** substitut | rien de fiable | **silence** |

**Politique retenue V1** : `last_time` (et ses consommateurs) doivent adopter la
**même politique de substitution que `overload_inputs`** : prescrit ↔ prescrit
strict, substitué ↔ **même** `substituted_name` strict, sinon **silence**. Aucune
proposition de charge inter-exercice.

---

## 7. Options comparées

| Option | Description | Verdict |
|---|---|---|
| **A** | Rendre `last_time_by_exercise_code` **substitution-aware** (même politique que `overload_inputs`) ; les 5 consommateurs héritent automatiquement | ✅ **RECO build minimal** — corrige la source unique, cohérent avec overload |
| **B** | Service central `exercise_load_identity` (identité canonique consommée par tous) | 🔵 **architecture future** — plus propre, plus large |
| **C** | Masquer toute Réf. précédente / cible dès qu'une substitution existe | ❌ trop conservateur (perd S4, cas fréquent « même alternative ») |
| **D** | Héritage N1/N2/N3 avec facteur de transfert de charge inter-machine | ❌ **rejeté V1** — trop risqué sans données |

**AUDIT ONLY** — aucun patch codé ici. La reco de build est **Option A** (minimal),
**B** en cible d'architecture, **D** rejeté.

---

## 8. Découpage build proposé (review-gated, sur override séparé)

- **`Sb_DOGFOOD_01.1`** — `last_time` substitution-aware : ajouter à
  `last_time_by_exercise_code` la clé `(template_slug, exercise_code, substitution_key)`
  où `substitution_key = substituted_name` (ou `None` pour prescrit), avec la même
  politique que `overload_inputs`. **Silence** si aucun historique aligné. Tests
  des 5 scénarios.
- **`Sb_DOGFOOD_01.2`** — propager aux consommateurs dérivés (delta, hints Sx_08,
  chip, peek) : ils reçoivent une `last_time` déjà filtrée → cohérence automatique.
  Vérifier que delta/hints deviennent silencieux en S2/S3/S5.
- **`Sb_DOGFOOD_01.3`** — mobile placeholder proportion (§9), CSS-only.

Contrat immuable sur tout le cycle : **placeholders seulement, jamais `value=`** ;
aucun préremplissage automatique ; aucun recalcul historique inventé.

---

## 9. Section mobile — proportion placeholder

### Constat
- L'unité (kg/reps) **n'est pas séparée** : le placeholder est soit « kg »/« reps »
  (vide), soit la valeur cible chiffrée (`_ph.weight`, ex. « ≈ 102.5 »). Tout tient
  dans le `placeholder=` de l'input.
- Media queries `@max-width: 380px` existent mais pas de contrôle de la proportion
  texte cible / largeur d'input.

### Contraintes V1 (CSS-only, `Sb_DOGFOOD_01.3`)
- Le placeholder cible chiffré ne doit pas déborder sur input étroit (≤ 360px).
- Options de format : `≈ 102.5` → `102.5` (retirer le `≈`) **ou** réduire la
  taille de police du placeholder sur mobile via `::placeholder` + media query.
- Envisager une **unité séparée** (span `kg`/`reps` adjacent, hors input) pour
  libérer la largeur — mais cela touche la structure de la row : à évaluer en `.3`.
- Tap target 44×44 conservé.
- Aucun JS.

### Sujets clivants mobile (tranchés en §10)
- Format : `≈ 102.5` vs `102.5` vs réduction typo → **`102.5` (retirer `≈`) + typo réduite mobile**.
- Séparer numérique / unité → **évaluer en `.3`** (structure de row), non tranché V1.

---

## 10. Sujets clivants — décisions (audit)

| # | Sujet | Décision |
|---|---|---|
| 1 | Identité fiable d'un exercice | **`(exercise_code_snapshot, substitution_key)`** où `substitution_key = substituted_name` ou None |
| 2 | Prescrit vs alternative = 2 historiques séparés ? | **Oui** (politique overload étendue à `last_time`) |
| 3 | Alternative N1 hérite du prescrit ? | **Non** V1 (silence ; héritage = Option D rejetée) |
| 4 | N2/N3 toujours silencieuses ? | **Oui** V1 sauf « même substitut » (S4) |
| 5 | Réf. précédente quand dernière occ. substituée (courant prescrit) | **prescrit précédent** ou **silence** |
| 6 | Placeholder cible quand courant substitué | **silence** (déjà le cas overload) sauf même substitut |
| 7 | Recalcul placeholders après substitution via redirect SSR | **hors V1** (le POST substitution redirige déjà ; recalcul naturel au prochain render) |
| 8 | Service central `exercise_load_identity` vs patch `last_time` | **patch `last_time` (Option A)** V1 ; service central = Option B future |
| 9 | « Ne rien proposer » plutôt qu'un faux | **Oui — règle directrice** |
| 10 | Microcopy quand cible masquée pour cause d'alternative | **microcopy neutre courte** (ex. « Pas de repère pour cette alternative ») — à finaliser en `.1` |
| 11 | Format mobile `≈ 102.5` | **`102.5`** (retirer `≈`) + typo réduite mobile |
| 12 | Séparer numérique / unité | **évaluer en `.3`** (touche la structure de row) |

---

## 11. Non-goals

- Pas de migration · pas de modèle · pas de schema.
- Pas de Body Intelligence · pas de substitution graph · pas de recalcul historique.
- Pas d'algorithme de transfert de charge inter-machine (Option D rejetée).
- Pas de JS · pas de préremplissage automatique des champs · **pas de `value=`
  (placeholders seulement)**.
- Pas de changement `body_map_descriptor` / `muscle_mapping` / scoring / coach.

---

## 12. Critères d'acceptation de la spec

- [ ] Carte producteurs/consommateurs/identités validée (§3-4).
- [ ] Matrice 5 scénarios validée (§5).
- [ ] Politique « silence plutôt que faux poids » + politique substitution (§6) confirmées.
- [ ] Option A retenue comme build minimal, B future, D rejetée (§7).
- [ ] Découpage `.1`/`.2`/`.3` validé (§8).
- [ ] Contraintes mobile placeholder (§9) validées.

---

## Verdict

**Verdict :** 🟢 **READY FOR HUMAN DECISION.**

L'audit confirme une **asymétrie réelle** : `overload` est déjà substitution-aware
(silence si substitué), mais `last_time_by_exercise_code` **ne l'est pas** — il
contamine 5 surfaces (Référence précédente, Dernière fois, Delta, Hints Sx_08,
Chip/Peek) qui affichent une charge d'un exercice **différent** dans les scénarios
S2/S3/S5. La règle « **silence plutôt que faux poids** » + l'alignement de
`last_time` sur la politique de substitution d'`overload_inputs` (Option A) donnent
un build minimal, review-gated (`.1` source, `.2` consommateurs, `.3` mobile
placeholder). Option B (service central) = architecture future ; Option D (transfert
de charge) rejetée V1. **Aucun code touché par cette spec.**
