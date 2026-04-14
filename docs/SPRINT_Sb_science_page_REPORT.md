# Sprint Sb_science_page Report — Science Page + Architecture Diagram

**Date:** 2026-04-14
**Status:** Complete
**Spec:** docs/strategy/SPIGNOS_SCIENCE_PAGE_SPEC.md
**Tests:** 507 passed, 0 failed

## Objective

Transform /rules into /science with 5 editorial sections
(pratique → principes → materialisation → architecture) and an SVG
SSR static architecture diagram.

## Deliverables

| Artifact | Path |
|----------|------|
| Route | `GET /science` (named `science_page`) in `pages.py` |
| Redirect | `GET /rules → 301 /science` |
| Template | `app/templates/science.html` (5 sections) |
| SVG partial | `app/templates/_partials/science_diagram.svg` |
| CSS | `.science-section`, `.science-diagram` in `app.css` |
| Home tile | `app/templates/index.html` (Science tile) |
| Tests | `tests/test_science_page.py` (8) |
| Legacy tests updated | test_session_flow.py, test_auth.py, test_security.py |

## 6 arbitrages respectes

- **(4) Manuel d'usage, PAS manifeste de marque** — 5 sections factuelles,
  zero rhetorique marketing, zero superlatif, zero "AI/powered by".
- **(5) SVG SSR statique** — pas de Mermaid, pas d'interaction hover.
  Le SVG est un partial Jinja inclus dans la page.
- **Ordre editorial** : pratique → principes (methode) → principes (cardio)
  → materialisation (manuel produit) → architecture (diagramme).

## Structure editoriale livree

```
/science
├── Section 1 — Pourquoi noter change la progression  (pratique)
├── Section 2 — Methode d'entrainement               (principes)
│   └── 8 method_rules preserves avec deep-link anchors
├── Section 3 — Place du cardio                      (principes)
│   └── Doctrine anti-pseudo-science : "donnees operatoires"
├── Section 4 — Comment SPIGNOS materialise          (manuel produit)
│   ├── Programmes et seances
│   ├── Exercices et series
│   ├── Score derive
│   ├── Historique
│   ├── Synthese et physique
│   └── Ce qui reste prive
└── Section 5 — Architecture du produit              (diagramme SVG)
```

## SVG diagramme

- Dimensions : `viewBox="0 0 800 520"`, responsive via `max-width:100%`
- 9 nodes : Programmes, Etat du jour, Mesures, Seance, Historique, Synthese,
  Physique, Classement, Squads
- Edges differenties :
  - `stroke=#9aa3ad` plein pour flux public
  - `stroke=#6e7785 dasharray` pour donnees privees
- Legende integree (flux principal vs donnee privee)
- `title` + `desc` pour accessibilite
- Couleurs hardcodees (tokens CSS ne propagent pas en SVG sans JS)

## Verification

```
pytest tests/test_science_page.py -v            # 8/8
pytest --ignore=tests/test_deploy_artifacts.py --ignore=tests/test_v1_acceptance.py -q  # 507 passed
```

## Coexistence /rules

- `/rules` → 301 redirect vers `/science` (preserve les anciens bookmarks)
- Le lien inline "Voir toutes les regles" dans `session_detail.html` continue
  de pointer sur `/rules` qui redirige — fonctionnellement equivalent. Pourrait
  etre migre vers `/science` directement en V2 si desire (changement template
  mineur, non bloquant).

## Cloture du chantier editorial

Les 3 chantiers de spec (launcher, cardio, science) sont maintenant build.
L'entree produit a ete repensee, le cardio est captrable proprement, et la
page Science donne le cadre pedagogique et l'architecture du produit.
