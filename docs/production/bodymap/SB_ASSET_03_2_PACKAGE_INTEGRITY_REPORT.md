# SB_ASSET_03.2 — Package v2 Integrity Report

**Date** : 2026-07-23 · **Package** : `auren_bodymap_sb_asset_03_1_intake_package_v2.zip`

## Identité (§3-§4) — PASS
| Mesure | Attendu | Constaté |
|---|---|---|
| Taille | 1 449 359 | **1 449 359** ✅ |
| SHA-256 | `f45e0dbf…f2cb` | **identique** ✅ |
| Entrées ZIP | 62 | **62** ✅ |

## Sécurité avant extraction — PASS
0 chemin absolu · 0 `..` · 0 backslash · 0 doublon · 0 `.DS_Store` · 0 AppleDouble `._*` · 0 symlink ·
0 entrée chiffrée · 0 collision Unicode/casse · ratio de compression **1,03** (< 200) · 0 échappement hors
destination.

## Manifeste embarqué — PASS
`intake_package_manifest.json` **présent à la racine logique**. `manifest_scope:
all-package-members-except-this-manifest`. **`62 = 61 + 1`** vérifié. Manifeste **non auto-comptant**.
**Les 61 membres re-hachés indépendamment** : 0 absent, 0 supplémentaire, 0 divergence de taille ou SHA-256,
**rôle présent** sur chaque membre.

| Décompte | Manifeste | Fichiers réels |
|---|---|---|
| Scripts `.py` | 14 | **14** ✅ |
| Previews `.png` | 32 | **32** ✅ |
| master sha256 | `dbb57db3…` | inchangé ✅ |
| compact sha256 | `8024fd4c…` | inchangé ✅ |
| ai_usage | `none` | ✅ |

## Exclusions (§6) — PASS
`.blend` et `pipeline_log.json` **absents du package** — chemins absolus / spécifiques à la racine,
régénérables par `run_pipeline.py`. Le replay ne dépend d'aucun `.blend` ni journal historique.

## Verdict
**PACKAGE V2 INTEGRITY: PASS** — 38/38 contrôles indépendants. Le package est intègre, sûr et
auto-descriptif. Défaut du package v1 (manifeste externe) **corrigé**.
