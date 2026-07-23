# Sprint Sb_ASSET_03.2 — BodyMap Prototype Technical Validation & Design-Source Intake — REPORT

**Statut** : 🟢 **CODE COMPLETE / TECHNICAL VALIDATION PASSED (package v2) / HUMAN REVIEW PENDING**
**Date** : 2026-07-23 · **Baseline** : `bd2811a` (= origin, vérifié)

---

## 1. Historique — l'échec n'est pas effacé

```
FIRST INTAKE:  BLOCKED — NON-REPRODUCIBLE OUTPUT
ROOT CAUSE:    INCOMPLETE EXECUTABLE BUILD GRAPH
FIX:           Sb_ASSET_03.1-fix / bd2811a
RESUMED INTAKE (v2):  TECHNICAL VALIDATION PASSED
```

Le premier intake (package v1) a **bloqué** : `servier_masks.py` consommait `servier_<zone>_raw.svg` sans
producteur packagé. Le correctif `Sb_ASSET_03.1-fix` a scripté le producteur, relocalisé les scripts, ajouté
graphe + entrypoint, et réémis un **package v2 déterministe**. Cet intake **reprend au §11** avec le v2.

## 2. Gates — tous PASS (validation indépendante)

| § | Gate | Verdict |
|---|---|---|
| 3-4 | Identité + sécurité + manifeste embarqué v2 | ✅ **38/38** — `62 = 61 + 1`, 61 membres re-hachés |
| 5 | Audit du correctif (117/157 IDs, graphe, AST) | ✅ `BUILD GRAPH: COMPLETE / NO ORPHAN INPUTS` |
| 7-8 | **Replay clean-room indépendant** | ✅ **6 hashes byte-identiques** (racine espace+Unicode vierge) |
| 9 | Validation SVG (2 validateurs) | ✅ master 40/40 + 66/66 · compact 41/41 |
| 9-10 | 3 méthodes géométriques + régression | ✅ Chrome + Inkscape concordent ; bbox rendues conformes |
| 11 | 32 previews + revue visuelle | ✅ états/zones/macros/couples/tailles/fonds |
| 12 | Provenance + attribution | ✅ CC BY 4.0 revalidée, 0 contamination |
| 14-16 | Intake design source + gardes | ✅ 2 SVG + registre + notices + test |

## 3. Le fait décisif — reproductibilité prouvée indépendamment

Chaîne rejouée **depuis un workspace vide**, scripts issus du package, sources re-hachées, aucun réseau :

| Artefact | Attendu | Obtenu |
|---|---|---|
| master | `dbb57db3…` | **identique** ✅ |
| compact | `8024fd4c…` | **identique** ✅ |
| package v2 | `f45e0dbf…` | **identique** ✅ |
| (+ slide3, lats_raw, core_raw) | — | **identiques** ✅ |

**Aucun hash de référence réécrit.** La cause du premier blocage est fermée par la preuve, pas par
déclaration.

## 4. Trois méthodes géométriques (recalculées sur le replay v2)
Chrome `getBBox()` et Inkscape CLI **concordent au centième** ; géométrie rendue conforme (`y ∈ [12,188]`,
safe area ≥ 8, gouttière vide, face/dos même échelle). La méthode 1 (enveloppe des points de contrôle) diverge
**par construction**, pas par désaccord — **sans le croisement à trois méthodes exigé, un faux blocage aurait
pu être prononcé sur le compact**.

## 5. Intake dans le design source

| Fichier | SHA-256 |
|---|---|
| `design/auren/source/bodymap/auren_bodymap_master.svg` | `dbb57db3…` (renommé, octets préservés) |
| `design/auren/exports/svg/auren_bodymap_compact.svg` | `8024fd4c…` (identique) |
| `design/auren/source/bodymap/auren_bodymap_source.yaml` | registre (hashes, sources, statut) |
| `design/auren/previews/bodymap/auren-bodymap-v0.1.0.html` | surface de revue hors runtime |
| `design/auren/LICENSES/{CC-BY-4.0.txt, bodyparts3d-NOTICE.md, servier-medical-art-NOTICE.md}` | attribution |

**Garde automatisé** : `tests/test_auren_bodymap_master.py` (**22 tests**, positifs + **7 cas négatifs**
prouvant l'échec sur ID dupliqué, script, URL externe, `zone-unknown`, zone retirée, couleur métier).
**Évolutions gouvernées** des gardes existants (allowlist SVG + LICENSES + master à côté du contrat), aucun
test affaibli.

## 6. Distinctions maintenues
- **Preuve Sb_ASSET_03.1** (build) ≠ **validation indépendante Sb_ASSET_03.2** (rejeu + re-hachage).
- **Observation visuelle humaine** ≠ **revue anatomique professionnelle** (`NOT CLAIMED`).
- **Statut juridique** : `LEGAL REVIEW REQUIRED`, `PROFESSIONAL LEGAL CLEARANCE: NOT CLAIMED`.

## 7. Scope Git
100 % `docs/**` **+ design/auren/** + tests. **2 SVG** de design (validés), 0 raster, 0 archive, 0 OBJ,
0 `.blend`, 0 PNG committé, **0 `app/**`**, 0 migration, 0 dépendance, 0 fichier Custom.

---

## Verdict

**Verdict :** 🟢 **Sb_ASSET_03.2: TECHNICAL VALIDATION PASSED (package v2) / HUMAN REVIEW PENDING.** L'intake
bloqué du package v1 (`NON-REPRODUCIBLE OUTPUT`) est **repris et résolu** avec le package v2, **validé
indépendamment** : identité exacte (`f45e0dbf…`, 62 entrées), sécurité et **manifeste embarqué** (`62 = 61 +
1`, 61 membres re-hachés), **replay clean-room byte-identique** du master, du compact, des 32 previews et du
package dans une racine vierge à espace+Unicode, SVG conformes au contrat (viewBox `0 0 240 200`, 14 IDs,
11 zones, 0 `zone-unknown`, surface statique sûre) avec **trois méthodes géométriques** (Chrome + Inkscape
concordants), provenance **CC BY 4.0 double** revalidée sans contamination. Le master et le compact entrent en
**design source** (octets préservés), avec registre, notices d'attribution et **garde automatisé** (positifs +
négatifs) ; les gardes existants ont évolué de façon **gouvernée**, aucun affaibli. **Rien n'entre dans
`app/**`** ; le prototype runtime n'est pas remplacé ; la surface d'attribution reste non implémentée.
`BODYMAP MASTER: TECHNICALLY VALIDATED / NOT YET HUMAN APPROVED` · `PROFESSIONAL ANATOMICAL REVIEW: NOT
CLAIMED` · `LEGAL REVIEW: REQUIRED` · `ATTRIBUTION SURFACE: NOT YET IMPLEMENTED` · `ASSET INTEGRATION GATE:
BLOCKED`.

**Prochaine action** (séparée, non commencée) : `GO HUMAN REVIEW — Sb_ASSET_03.2 Auren BodyMap Design Source`.
