# Sprint Sb_launcher_v1 Report — Intelligent Session Launcher

**Date:** 2026-04-14
**Status:** Complete
**Spec:** docs/strategy/SPIGNOS_INTELLIGENT_SESSION_LAUNCHER_SPEC.md
**Tests:** 494 passed, 0 failed

## Objective

Replace the flat /library entry with a guided /launcher — 2 steps max, with
dynamic branch resolution (empty branches never shown). Preserve /library
as a separate full-catalog access.

## Deliverables

| Artifact | Path |
|----------|------|
| Service | `app/services/launcher.py` (BRANCH_TREE, resolve_branch, get_available_*) |
| Route | `GET /launcher?type&variant` in `pages.py` |
| Template | `app/templates/launcher.html` (3 steps) |
| Home tile | `app/templates/index.html` (href → /launcher) |
| Tests | `tests/test_launcher.py` (7) + `tests/test_launcher_routes.py` (9) |

## 6 arbitrages respectes

- **(1) Branches vides jamais affichees** — `get_available_variants` filtre
  dynamiquement via `_existing_slugs(db)`. "Full lower court" et "Full body
  court" n'apparaissent pas dans la branche "Courte" en V1.
- **(2) Catalogue existant strict** — aucun nouveau template ajoute. Les
  slugs `short-lower` / `short-full-body` sont declares dans BRANCH_TREE
  mais filtres a l'execution.
- **(6) reference_split.json via DB** — `_existing_slugs(db)` lit
  WorkoutTemplate au moment du request, pas un snapshot hardcode.

## UX flow livre

```
Home tile "Nouvelle séance"
  → /launcher
      → Étape 1 : Séance standard / Séance courte / Cardio
      → Étape 2 (standard/short) : sous-options filtrees
      → Étape 3 (ou direct cardio) : liste de templates filtres
      → "Démarrer" (POST /sessions, inchange)

Échappatoire a toute etape :
  → "Voir tous les programmes →" (/library)

Nav topbar :
  → "Programmes" (/library) reste accessible directement
```

## Verification

```
pytest tests/test_launcher.py tests/test_launcher_routes.py -v
pytest --ignore=tests/test_deploy_artifacts.py --ignore=tests/test_v1_acceptance.py -q
```

## Coexistence /library

- Nav topbar "Programmes" : inchange, pointe toujours sur /library
- Lien "Voir tous les programmes →" : present a chaque etape du launcher
- Aucune route supprimee, aucun changement au POST /sessions

## Prochaines etapes

- Sb_cardio_capture : ajoute liss-only et la cardio branch resolvera les 2 templates
- Sb_science_page : renomme /rules en /science
