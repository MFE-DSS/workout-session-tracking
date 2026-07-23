# SB_ASSET_03.2 — Reproducibility Report (independent clean-room replay)

**Date** : 2026-07-23 · **Racine de replay** : `…/Independent Replay é/` (**vierge**, espace + Unicode).

## Méthode
Aucun artefact intermédiaire de `Sb_ASSET_03.1` ou `-fix` en entrée. Entrées autorisées : archives
officielles **re-hachées**, PPTX Servier **re-haché**, **scripts issus du package v2**, outils documentés.
Aucun réseau. Chaîne complète exécutée par `run_pipeline.py` (dry-run puis run complet).

## Sources re-hachées avant replay
| Source | SHA-256 |
|---|---|
| `isa_BP3D_4.0_obj_99.zip` | `40665852c49f218326590e204db91064a1ecfc3c6f8cbd7bbbcaac62c7cd409e` |
| `SMART-Muscles.pptx` | `ad8e04e0b98f99d9196ef3966c2228137e18ed0afda9a85996d2e4116cb66d68` |

## Résultats — byte-identiques (§8)
| Artefact reconstruit | SHA-256 attendu | Obtenu |
|---|---|---|
| `servier_slide3.svg` | `789fb3af…d459e188` | **identique** ✅ |
| `servier_lats_raw.svg` | `dc04a017…114bca1b` | **identique** ✅ |
| `servier_core_raw.svg` | `fe01dc94…4950e96b` | **identique** ✅ |
| **master** | `dbb57db3…266ee9ecfa73` | **identique** ✅ |
| **compact** | `8024fd4c…3c3e5a4676c9a` | **identique** ✅ |
| **package v2** | `f45e0dbf…c092957029` | **identique** ✅ |

Package rejoué : **1 449 359 o**, **62 entrées**, manifeste **61 membres + lui-même**, **0 chemin absolu**
dans aucun membre, **32 previews**.

## Portée
Le maillon jadis manquant (production des régions Servier) est désormais **scripté et rejoué** : la chaîne
`PPTX → slide3 → régions → masques → scène → rendus → master/compact → previews → package` est **complète et
exécutable depuis un workspace vide**, par une **partie indépendante du build**.

## Verdict
**REPRODUCIBILITY: INDEPENDENTLY VERIFIED USING PACKAGE V2.** Six hashes reproduits exactement dans une
racine vierge à espace+Unicode. **Aucun hash de référence n'a été réécrit** ; aucune ressemblance visuelle
acceptée en substitut. La cause de blocage du premier intake est **définitivement fermée**.
