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

## Volume Policy (v10+)

Sessions are designed to fit within **~1h15 max** of gym time. With
warmups and rest, this corresponds to roughly **~21 work sets per
session**.

When a template would exceed this budget, the catalog favors **trimming
non-essential or duplicate exercises** rather than enriching shorter
templates. Rationale:

- A user can always **add an exercise manually** at the gym if they have
  extra time
- A user **cannot remove** a prescribed exercise without breaking the
  template's coherence
- Shorter templates respect the time constraint by default; users with
  more time use that flexibility actively

Reference benchmark for v12:

| Template | Exercices | Work sets | Duree estimee |
|----------|-----------|-----------|---------------|
| push-a | 7 | 21 | ~74 min |
| push-b | 7 | 22 | ~77 min |
| pull-a | 7 | 20 | ~70 min |
| pull-b | 7 | 20 | ~70 min |
| legs-a | 7 | 22 | ~77 min |
| legs-b | 7 | 22 | ~77 min |

Templates a 22 sets sont accepts comme borderline. Au-dela de 22 sets,
le sprint Sb_catalog_balance applique une reduction (cf. v10).

## v12 — Pull A balance (benchmark review chantier 3)

**Arbitrage Option B — enrichir Pull A plutot qu'alleger Push A.**

Pull A passe de 5 ex / 15 sets a 7 ex / 20 sets, aligne avec la densite
des autres templates core. Deux exercices ajoutes, tous deux focus
largeur (classifies `lats` par `muscle_mapping`) :

- **E6 Pullover machine** (3x 10-15) — complement largeur via le pattern
  pullover. Lien atlas `pullover-machine` (famille `back-vertical`).
- **E7 Straight-arm pulldown câble** (2x 12-15) — finisher lats bras
  tendus. Pas de machine atlas dedie — lien famille `back-vertical`
  uniquement.

Le focus du template reste **"Dos largeur, Deltoides posterieurs"** :
aucun ajout sur l'epaisseur du dos (pas de rowing horizontal) ni sur
les biceps (assume par design — focus largeur strict).

Pourquoi Option B et pas Option A (alleger Push A) :
- Push A a 21 sets = borderline mais acceptable (~74 min gym)
- L'allegement aurait retire des exercices deja bien choisis
- Pull A sous-dimensionne (15 sets) etait sous le seuil de stimulation
  meme pour un focus etroit

Livrable : catalog `2026-04-18.v12`, additif pur, zero migration, zero
code, full suite 635 passed.
