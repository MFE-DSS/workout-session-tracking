# Full Body — Morphotype Priority (programme catalogue)

**Type :** ajout catalogue contrôlé (section `specialization`) · **Slug :** `full-body-morphotype-priority-v1`
**Version catalogue :** `data/reference_split.json` bump `2026-04-21.v13 → v14` · **0 migration, 0 modèle, 0 refonte.**

## Objectif

Séance **full body** orientée « priorités morphotype » : un stimulus prioritaire sur les points à développer, un volume **minimal efficace** sur les points déjà forts. Utilisable comme **séance signature**, **rattrapage morphotype**, ou **4ᵉ séance hebdomadaire** — **pas** un PPL complet, **pas** un remplacement permanent du split.

## Pourquoi / lien blueprint morphologique (Martin)

Fondé sur le blueprint morphologique de Martin (cf. `Sx_MORPHO_PROGRAM_01` / `Sb_MORPHO_PROFILE_01`) : taille relativement étroite, structure d'épaules favorable, priorité **deltoïde latéral** puis **haut des pectoraux**, profondeur **haut du dos / deltoïdes postérieurs**, spécialisation **mollets**, **quadriceps déjà forts** (maintien seulement, **ne pas sur-spécialiser**).

Priorités appliquées : **1** deltoïde latéral · **2** haut des pectoraux · **3** haut du dos + deltoïde postérieur · **4** mollets · **maintien/progression** : lats, quadriceps, chaîne postérieure.

> **Limites (garde-fous)** : ce programme n'est **pas un diagnostic médical** ni une prescription ; c'est une séance d'entraînement. Aucune revendication de posture/pathologie/insertion. Il **ne remplace pas** le PPL de façon permanente.

## Décision de nommage (référentiel fermé)

Le catalogue est un **référentiel fermé** : l'ensemble des noms (prescrits ∪ substituts) est verrouillé aux **103 noms canoniques de l'EKB** (snapshot opposable + QA CI). Les exercices et substituts sont donc mappés sur des **noms EKB existants** qui préservent l'**intention** de chaque slot (option validée par l'opérateur). Aucun nouveau nom, aucune expansion EKB.

## Exercices (8 slots, dans l'ordre)

| Slot | Nom catalogue (EKB) | Séries × reps | Repos | Zone | Intention |
|---|---|---|---|---|---|
| E1 | Développé incliné haltères 30° | 3 × 6–10 | 120–180s | pecs (haut) | `upper_chest_primary_press` — incliné 15–30°, pas un développé épaules |
| E2 | Rowing chest-supported | 3 × 8–12 | 120–180s | upper_back | `upper_back_depth_row` — buste soutenu, pause en contraction |
| E3 | Hack Squat machine | 2 × 6–10 | 150–210s | quads | `quad_minimum_effective_dose` — maintien, ne pas sur-spécialiser |
| E4 | Romanian Deadlift barre | 2 × 6–10 | 150–210s | posterior | `posterior_chain_hinge` — hip hinge, pas un soulevé lombaire max |
| E5 | Élévations latérales câble | 4 × 12–20 | 60–90s | delt_lat | `lateral_delt_priority` — strict, contrôle en bas, pas de shrug |
| E6 | Reverse fly machine | 3 × 12–20 | 60–90s | delt_post | `rear_delt_upper_back_accessory` — mener aux coudes, pas de trap shrug |
| E7 | Relevés mollets debout machine | 4 × 8–12 | 60–120s | calves | `calves_gastrocnemius_priority` — étirement complet, pas de rebond |
| E8 | Mollets assis machine | 3 × 12–20 | 60–90s | calves | `calves_soleus_priority` — genoux fléchis, étirement complet |

*(Repos & intentions vivent dans le champ `notes` de chaque exercice, faute de colonnes dédiées — 0 migration. La zone est **dérivée** par la taxonomie existante `classify_exercise`, jamais inventée.)*

## Substitutions

**Niveau 1 (équivalents stricts, intégrés au catalogue `substitutes` → N1 curaté du moteur existant)** — préservent l'intention du slot :

- **E1** : Incline Smith Press · Chest Press machine · Développé couché haltères
- **E2** : Rowing machine chest-supported · Rowing câble assis prise large · Rowing câble assis prise neutre
- **E3** : Squat Smith machine (pieds avancés) · Sissy squat machine
- **E4** : Romanian Deadlift haltères · Back extension 45° (bias ischios) · Hip thrust haltères
- **E5** : Élévations latérales machine · Élévations latérales haltères · Élévations latérales câble (derrière le dos)
- **E6** : Face pull câble · Écarté arrière d'épaule câble · Face pull câble (corde) *(tous classent en `delt_post` ; « Rear delt fly machine (pec deck inversé) » est **écarté** car « pec deck » le classerait en `pecs` au scoring — un swap fausserait l'attribution de volume)*
- **E7** : Relevés mollets debout · Calf press leg press
- **E8** : Calf press leg press · Relevés mollets debout machine

**Niveaux 2/3 (fallbacks plus larges) — documentés ici, non ajoutés au catalogue** (le modèle `substitutes` est un N1 curaté plat ; les N2/N3 dérivés proviennent du moteur `substitution.py` sur `exercise_properties.json`). L'intention prime : E1 peut devenir un incliné haltères/Smith/machine, **jamais des dips par défaut** (l'intention haut des pecs serait moins bien préservée). E4 leg curl seulement en dernier recours si le hinge est indisponible.

## Règles de non-régression (contrat de ce sprint)

- **Ajout additif uniquement** : version bumpée, 1 template ajouté ; **aucun template existant modifié/renommé** (push-a/b, pull-a/b, legs-a/b, liss-*, short-upper, catch-up-*, upper/lower-* intacts).
- **0 modèle backend refondu · 0 migration · 0 nouvelle table · 0 champ ajouté.**
- **Cartes exercice existantes réutilisées** (`_partials/exercise_card.html` inchangé) — mode focus, jump bar, save→next, timer, « dernière fois », mobile, no-JS **inchangés**. `machine_slug`/`machine_family` = `null` (dégradation gracieuse).
- **Système prévu/réalisé & historique intacts** : les `session_exercises` snapshottent nom/code au log ; les FK catalogue sont `ON DELETE SET NULL`.
- **Référentiel fermé préservé** : tous les noms ∈ 103 EKB → **pas de drift snapshot**, EKB inchangé, `canonical_count == 103`. Compteurs dérivés re-baselinés (templates 16→17, slots 98→106, prescrits 65→68, substituts 59→66).
- **Substitutions** : intégrées au format existant (N1 `substitutes`), sans nouveau moteur.

## Usage recommandé

Séance **signature** / **rattrapage morphotype** / **4ᵉ séance hebdomadaire**. À insérer en complément d'un split existant, pas en remplacement.
