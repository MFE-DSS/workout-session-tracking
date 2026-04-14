# Sprint Sb_cardio_capture Report — Cardio Data Capture + liss-only

**Date:** 2026-04-14
**Status:** Complete
**Spec:** docs/strategy/SPIGNOS_SESSION_ENTRY_AND_SCIENCE_TRANSVERSAL_NOTES.md
**Tests:** 499 passed, 0 failed

## Objective

Make cardio sessions loggable with proper data (duration, BPM avg, machine
calories, machine type). Add `liss-only` template for cardio pur sans abdos.
Enforce anti-pseudo-science wording.

## Deliverables

| Artifact | Path |
|----------|------|
| Migration | `migrations/versions/20260414_add_cardio_fields.py` |
| Model | `app/models/session.py` +4 cardio fields + template relationship |
| Catalog | `data/reference_split.json` v7→v8 with `liss-only` |
| QA script | `scripts/catalog_qa.py` relaxed for cardio templates |
| Integrity tests | `tests/test_catalog_integrity.py` updated |
| Router | `app/routers/sessions.py` parses cardio fields + loads template |
| Template | `app/templates/session_detail.html` cardio section |
| Export | `app/services/export_builder.py` cardio fields JSON+CSV |
| Launcher | `app/services/launcher.py` cardio branch resolves liss-only + liss-abs |
| Tests | `tests/test_cardio_capture.py` (5) |

## 6 arbitrages respectes

- **(3) Option A : 2 templates separes** — `liss-only` ajoute, `liss-abs`
  preserve pour l'historique (ADD, pas rename).
- **(6) reference_split.json bumped v7→v8** — source de verite unique.
- **Calories labeled "(indicatif)"** — anti-pseudo-science explicit.
- Disclaimer UI : "Donnees operatoires saisies. Elles ne sont pas une verite
  physiologique."

## Nouveaux champs sur WorkoutSession

| Champ | Type | Nullable | Usage |
|-------|------|----------|-------|
| cardio_duration_min | INT | Oui | Duree brute saisie |
| cardio_bpm_avg | INT | Oui | BPM moyen (montre/cardiofrequencemetre) |
| cardio_machine_calories | INT | Oui | Valeur machine indicative |
| cardio_machine_type | VARCHAR(32) | Oui | velo/marche/rameur/elliptique/autre |

## Nouveau template (catalog v8)

| Slug | Kind | Exercices | Section |
|------|------|-----------|---------|
| liss-only | cardio | 0 | utility (display_order 10) |
| liss-abs | cardio | 4 (abdos) | utility (preserve) |

## Launcher integration

Branche cardio resout maintenant : `liss-only` (prefere) → `liss-abs`.

## Zero impact scoring

- Les champs cardio ne contribuent a AUCUN axe du dashboard (progression,
  physique zones, equilibre).
- Les seances cardio completees comptent dans la regularite comme toute
  seance terminee : 1 seance = 1 seance. Pas de valorisation differentielle.

## Verification

```
pytest tests/test_cardio_capture.py -v           # 5/5
pytest tests/test_launcher.py -v                 # 7/7 (liss-only)
pytest tests/test_catalog_integrity.py -v        # 10/10
pytest --ignore=tests/test_deploy_artifacts.py --ignore=tests/test_v1_acceptance.py -q  # 499 passed
```

## Prochaine etape

Sb_science_page : renomme /rules en /science, integre la doctrine cardio dans la section 3.
