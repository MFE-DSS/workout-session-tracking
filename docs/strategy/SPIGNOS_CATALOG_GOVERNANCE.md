# SPIGNOS Catalog Governance

## Source of Truth

`data/reference_split.json` is the single source of truth for the exercise catalog.
All workout templates, exercises, rep targets, and metadata originate from this file.

## Versioning Convention

Format: `YYYY-MM-DD.vN`

Every change to the catalog JSON must bump the version. The seed service
(`app/services/seed.py`) is idempotent and keyed on this version string:
new version = full re-seed of catalog tables on next boot.

## Modification Workflow

1. Edit `data/reference_split.json`
2. Bump the `version` field
3. Run `python scripts/catalog_qa.py` and verify the report is clean
4. Run `pytest tests/test_catalog_integrity.py` — must pass
5. Commit and push
6. On next deploy, the seed service detects the new version and re-seeds

## Focus Field Role

The `focus` field is **editorial** — it serves the UI (library display, template
cards, suggested labels) and human readability.

It is **NOT** the analytical truth. The analytical truth comes from
`app/services/muscle_mapping.classify_exercise()`, which maps exercise names to
muscle zones using substring pattern matching.

The focus field and the mapping should be directionally aligned, but the mapping
is what drives scores, dashboards, and analytics. Do not encode scoring logic
into the focus text.

## Analytics Impact Policy

Scoring uses exercise names captured at session creation time (immutable
snapshots in `session_exercises.exercise_name_snapshot`). Changing catalog
focus or mapping affects future scores only — never historical data.

Session FK to catalog uses `ON DELETE SET NULL`, so catalog rewrites
never break historical sessions.

## Known Structural Decisions

These are intentional design choices, not bugs:

1. **pull-a has no direct biceps isolation** — by design (width focus).
   Vertical pulls contribute biceps as secondary zone in the classifier.

2. **push-a E6 "Écarté arrière d'épaule câble"** is a pull-pattern movement
   in a push template — common PPL practice for complete shoulder coverage
   on push day.

3. **Archived templates overlap with core templates** — the 4 archived
   templates are pre-PPL-split legacy. Retained for users who started
   sessions with them. Hidden from the catalog UI but still functional.
