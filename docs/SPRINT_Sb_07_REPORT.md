# Sprint Sb_07 Report — Machine Knowledge & Substitution Surface

**Date:** 2026-04-18
**Type:** Build Atlas + UX machine knowledge
**Prerequisite:** Sx_09 figé, Sb_05 + Sb_06 livrés
**Débloque:** Sb_08

---

## 1. Objectif

Rendre les machines du plateau exploitables depuis la carte exercice : fiche d'exécution (cues + erreurs) en ligne, picker de substitution refactoré en drawer, page atlas consultable hors séance. Zéro JS, zéro migration destructive.

---

## 2. Décisions d'implémentation

### D1 — Atlas en JSON versionné, loader in-memory

- `data/machine_atlas.json` v1 (8 familles, 29 machines, version `2026-04-15.v1`).
- `app/services/machine_atlas.py` charge le JSON une fois, cache en mémoire, expose `get_machine(slug)`, `get_family(slug)`, `family_of_machine(slug)`, `all_families()`, `get_for_template_exercise(te)`.
- Pas de table DB pour l'atlas : fichier statique, réactualisé à chaque déploiement.

### D2 — Liens catalogue via deux nouveaux champs nullable

- Migration `a19c4e3b7f21_add_machine_atlas_links.py` ajoute `template_exercises.machine_slug` + `template_exercises.machine_family`.
- **Additif only** : pas de NOT NULL, pas de contrainte FK (l'atlas n'est pas en DB).
- `reference_split.json` v10 → **v11** : 62 exercices sur 96 liés à une machine d'atlas (31 exercices isolation / accessoires restent non liés — comportement attendu).

### D3 — Surface carte : `<details>` native

- Nouveau bloc `<details class="machine-panel">` inséré entre le scheme et la substitution, juste avant last-time / delta.
- Affiche : 3 cues d'exécution, 2-4 erreurs fréquentes, note de convention de charge.
- Fermé par défaut, ouvrable sans JS.

### D4 — Substitution drawer (refacto)

- L'ancien `<details class="substitute-picker">` devient `.substitute-picker--drawer` :
  - Header avec label explicite « Remplacer cet exercice » + badge count « N alternatives ».
  - Corps avec hint métier + options empilées (segmented stacked).
- Comportement fonctionnel inchangé (mêmes inputs radio `substituted_name`, même lock après 1ʳᵉ série travail).

### D5 — Page `/science/atlas`

- Route GET `/science/atlas` → template `atlas.html`.
- Liste des 8 familles avec TOC en ancres.
- Par machine : nom, équipement, aliases, variantes, cues, erreurs, convention charge + latéralité.
- Lien depuis `/science` via nouvelle section « Atlas des machines ».

---

## 3. Changements effectués

| Fichier | Type | Nature |
|---------|------|--------|
| `data/machine_atlas.json` | New | Atlas v1 (8 familles, 29 machines) |
| `app/services/machine_atlas.py` | New | Loader + lookups + cache in-memory |
| `scripts/machine_atlas_qa.py` | New | QA structurelle atlas (PASS) |
| `scripts/apply_machine_atlas_links.py` | New | Script one-shot mapping catalogue → atlas |
| `migrations/versions/20260418_add_machine_atlas_links.py` | New | `machine_slug` + `machine_family` sur `template_exercises` |
| `app/models/catalog.py` | Modify | Deux colonnes ajoutées au modèle `TemplateExercise` |
| `app/services/seed.py` | Modify | Lecture des deux nouveaux champs lors du seed |
| `data/reference_split.json` | Modify | v10 → v11 : 62/96 exercices liés à l'atlas |
| `scripts/catalog_qa.py` | Modify | Nouveau check `machine_links` (errors si slug inconnu ou famille incohérente) |
| `app/routers/sessions.py` | Modify | `atlas_data` passé au template session ; nouvelle route `/science/atlas` |
| `app/templates/session_detail.html` | Modify | Bloc `machine-panel` + refacto drawer substitution |
| `app/templates/science.html` | Modify | Section « Atlas des machines » + CTA vers `/science/atlas` |
| `app/templates/atlas.html` | New | Page atlas (TOC + 8 familles × N machines) |
| `app/static/css/app.css` | Modify | `.machine-panel*`, `.substitute-picker--drawer`, `.atlas-*` |
| `tests/test_machine_atlas.py` | New | 15 tests loader |
| `tests/test_atlas_routes.py` | New | 6 tests route `/science/atlas` + lien depuis `/science` |
| `tests/test_machine_atlas_surface.py` | New | 3 tests surface sur carte exercice |
| `docs/SPRINT_Sb_07_REPORT.md` | New | Ce rapport |

**Zéro JS ajouté. Migration additive uniquement (nullable). Atlas versionné séparément du catalogue.**

---

## 4. Tests

### Nouveaux tests — 24 au total

- `tests/test_machine_atlas.py` (15) — version, familles, slugs uniques, lookups, enums valides, cache reset
- `tests/test_atlas_routes.py` (6) — rendu page, TOC, families listées, machines avec cues/mistakes, lien depuis science
- `tests/test_machine_atlas_surface.py` (3) — panel affiché sur carte exercice liée, drawer substitution stylé

### Régression

- Full suite : **595 passed** (vs 571 avant Sb_07, +24 nouveaux).
- QA atlas : 8 familles, 29 machines, 0 erreur.
- QA catalog v11 : 16 templates, 96 exercises, 0 erreur, 0 warning.

---

## 5. Garde-fous Sx_02 et Sx_05 respectés

| Garde-fou | Statut |
|-----------|--------|
| SSR + zéro JS | ✓ (tout en `<details>` natif) |
| Une seule carte active | ✓ (mécanisme Sb_02 préservé) |
| Save-on-next / save-on-prev | ✓ (Sb_05 inchangé) |
| Jump bar 4 états | ✓ |
| Footer sticky CSS | ✓ |
| Position picker substitution | ✓ (drawer refacto, même mécanisme form) |
| Snapshots immutables | ✓ (atlas additif, ne touche pas `exercise_name_snapshot`) |
| Zéro migration destructive | ✓ (deux colonnes nullable) |
| Load convention | ✓ (atlas rend explicite le `load_semantics` sur chaque fiche) |

---

## 6. Vérification

```bash
# QA atlas + catalogue
python scripts/machine_atlas_qa.py
python scripts/catalog_qa.py

# Tests cibles Sb_07
pytest tests/test_machine_atlas.py tests/test_atlas_routes.py tests/test_machine_atlas_surface.py -v

# Régression session + catalog
pytest tests/test_session_flow.py tests/test_mobile_polish.py tests/test_substitution.py tests/test_session_nav.py tests/test_catalog_integrity.py -q

# Full suite
pytest --ignore=tests/test_deploy_artifacts.py --ignore=tests/test_v1_acceptance.py -q

# Serveur local
alembic upgrade head
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Recette manuelle

- [ ] Démarrer Push A → sur E1 (Incline Smith Press), le bloc « Comment bien exécuter… » apparaît ; l'ouvrir affiche 3 cues + 2 erreurs.
- [ ] Sur E3 (Shoulder press), le drawer « Remplacer cet exercice » affiche le badge « N alternatives » ; choisir une sub ; cliquer Enregistrer → sub persistée, carte E4 active.
- [ ] Une fois la 1ʳᵉ série travail cochée, le drawer substitution disparaît (lock Sb_03).
- [ ] `/science/atlas` s'ouvre, TOC cliquable, 8 familles listées, lien retour vers `/science` fonctionnel.
- [ ] Viewport 320px : panel + drawer tiennent sur une ligne, polices lisibles.

---

## 7. Critères d'acceptation

| Critère | Statut |
|---------|--------|
| Atlas JSON versionné v1 avec 8 familles / 29 machines | ✓ |
| Loader + QA + tests unitaires (≥10 tests) | ✓ (15) |
| Migration additive `machine_slug` + `machine_family` | ✓ |
| Catalog v11 avec ≥30 exercices liés | ✓ (62) |
| Panel machine affiché sur carte exercice (quand lien) | ✓ |
| Substitution drawer refactoré (count + wording) | ✓ |
| Route `/science/atlas` + lien depuis `/science` | ✓ |
| Zéro JS | ✓ |
| Full suite verte | ✓ (595) |

**Build Sb_07 : OK, prêt à merger.**

---

## 8. Limites et non-objectifs

- 31 exercices (curls, triceps accessoires, core, shrugs, adductors) non liés à l'atlas — intentionnel : l'atlas cible les machines principales du plateau.
- Pas d'images / SVG sur les fiches atlas (textuel only).
- Pas de recherche / filtre sur la page atlas (TOC + ancres suffisent pour V1).
- Pas d'alias inverse : si l'utilisateur substitue vers un nom non présent comme alias/name, aucun panel ne sera rendu. Cas bord documenté dans Sx_09.
- L'atlas n'est pas éditable depuis l'UI (fichier JSON en dur).

---

## 9. Synthèse exécutive (5 lignes)

- Atlas machines V1 livré : 8 familles, 29 machines, JSON versionné, loader in-memory.
- Carte exercice enrichie d'un panel `<details>` « cues + erreurs » sur les 62 exos liés.
- Substitution picker refactoré en drawer (badge count + wording explicite), comportement Sb_03 intact.
- Nouvelle page `/science/atlas` consultable hors séance, linkée depuis `/science`.
- Prochain sprint : Sb_08 Session Review Intelligence (anomalies + hints + score confiance, 4-6h).
