# `design/auren/source/icons/` — Functional Icon Source

**Build** : `Sb_ASSET_02.1`. Source **gouvernée** des icônes fonctionnelles Auren. **Premier intake tiers.**

## Contenu
- [`auren_icon_subset.yaml`](auren_icon_subset.yaml) — registre machine-lisible (YAML 1.2 JSON-compatible, lu
  par `json` stdlib) : subset P0 v0.1.0, vendor épinglé, licence, provenance par fichier, invariants.
- [`vendor/tabler/v3.45.0/outline/`](vendor/tabler/v3.45.0/outline/) — **10 SVG Tabler outline** vendored
  (commit `975920ff…`), normalisés (commentaire d'en-tête retiré + LF + newline final ; **géométrie
  inchangée**).
- [`vendor/tabler/v3.45.0/README.md`](vendor/tabler/v3.45.0/README.md) — provenance du vendor Tabler.

## Ce qui n'est PAS ici
- **`vendor/health-icons/`** : **non créé** (Health Icons NOT REQUIRED FOR P0).
- **`custom/`** : **non créé** (CUSTOM GLYPH TRACK: NOT REQUIRED).
- **P1 icons** : non ingérés.
- **`app/static/`** : **aucun export** (intégration runtime = `Sb_ASSET_04.1`, après gate).

## Règle
```
Source de design gouvernée. La présence ici ≠ autorisation dans app/static/.
Tout nouveau vendor / nouveau SVG (BodyMap, P1…) exige une évolution GOUVERNÉE
de tests/test_auren_asset_governance.py (allowlist) + provenance + licence.
```
**Statut** : `legal-review-required` · **HUMAN REVIEW PENDING** · `ASSET INTEGRATION GATE: BLOCKED`.
