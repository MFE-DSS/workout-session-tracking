# Sprint Sb_ASSET_02.1 — Vendored Icon Subset & License Intake — BUILD REPORT

**Statut** : 🟢 **CODE COMPLETE — CI PENDING — HUMAN REVIEW PENDING**
**Type** : premier **intake tiers** (design source) — 10 SVG Tabler v3.45.0 + licence MIT
**Date** : 2026-07-20 · **Baseline** : `fe97adc` (spec Sx_ASSET_02) · **Worktree** : `work/sb-asset-02-1-vendored-icon-intake`

> **PINNED UPSTREAM · EXACT TEN-FILE SUBSET · OFFICIAL LICENSE · COMMENTS-ONLY NORMALIZATION · GEOMETRY
> PRESERVED · MANIFEST-BACKED ALLOWLIST · NO HEALTH ICONS · NO CUSTOM · NO APP INTEGRATION · HUMAN REVIEW
> PENDING.** L'`ASSET INTEGRATION GATE` reste **BLOCKED**.

---

## 1-3. Baseline / worktree / collisions
HEAD = origin = `fe97adc`, clean. Worktree isolé sur `fe97adc`. Anti-collision `origin` contrôlé (stable).
Aucun build 02.1 préexistant.

## 4. Brainstorming (§6)
`PINNED UPSTREAM · EXACT TEN-FILE SUBSET · NO PADDING TO TWELVE · OFFICIAL LICENSE TEXT · ONE CANONICAL SVG
COPY · COMMENTS ONLY NORMALIZATION · GEOMETRY BYTE-SEMANTICS PRESERVED · MANIFEST-BACKED ALLOWLIST · NO HEALTH
ICONS · NO CUSTOM GLYPHS · NO APP INTEGRATION · HUMAN REVIEW PENDING · GATE REMAINS BLOCKED.`

## 5-9. Source officielle, tag, commit, licence, extraction
- **Source** : `https://github.com/tabler/tabler-icons` (clone `--filter=blob:none`, tag `v3.45.0` fetché).
- **Tag** `v3.45.0` → **tag object `64bfab222b4626fafb2301358dd41d3f3f3d84b2`** → **commit
  `975920ff99c12c4dc9e3fe61a03738330600f9b2`** (pins **vérifiés** avant toute copie).
- **Licence** : `LICENSE` (blob `3e82379dab3fe93d9ee22251949604ed63ddea39`), **MIT** © Paweł Kuna 2020-2026.
- Extraction par `git show <commit>:<path>` (0 URL flottante / npm / CDN / Iconify).

## 11. Subset exact (10 fichiers, ordre canonique)
| semantic_id | fichier |
|---|---|
| `auren.icon.action.substitute` | `arrows-exchange.svg` |
| `auren.icon.action.timer-start` | `player-play.svg` |
| `auren.icon.action.timer-pause` | `player-pause.svg` |
| `auren.icon.action.timer-reset` | `rotate.svg` |
| `auren.icon.action.expand` | `chevron-down.svg` |
| `auren.icon.action.collapse` | `chevron-up.svg` |
| `auren.icon.information.guidance` | `bulb.svg` |
| `auren.icon.information.warning` | `alert-triangle.svg` |
| `auren.icon.status.completed` | `check.svg` |
| `auren.icon.action.menu` | `menu-2.svg` |

**10 = subset canonique minimal** (spec §11). **Aucun padding à 12**, aucun P1, aucune nav inline copiée,
aucun Health Icons, aucun custom.

## 13-17. Normalisation & preuves (§21 — contrôle indépendant recomputé depuis le clone)
Transformation **bornée** : (1) commentaire XML d'en-tête retiré ; (2) LF ; (3) newline final. **Géométrie,
viewBox, stroke-width, fill, stroke, paths inchangés** — prouvé fichier par fichier : `local == (upstream −
commentaire, LF, newline)`.

| Fichier | blob SHA | raw SHA-256 | local SHA-256 | raw B | local B | transformation |
|---|---|---|---|---:|---:|---|
| `arrows-exchange.svg` | `721498aad6eefa7795af38c50d7990dc4ed81ddf` | `b37e7394c5fbeb57fd6303a77415c579d914d267dde77641f3399d91ab457a8a` | `b6e118f2c7b47a6249644fc3da37ede2b2abe52e44976125750e3cbe0dc96660` | 415 | 268 | comment+LF+newline |
| `player-play.svg` | `bb84dbe9e4166071e66414ab6ce1a3b12cc6fd5a` | `0178cf0262ec89422d632f6122c6be34a8b57db32dd1aea38dd283bdeecbfc2f` | `635b17e8ab5d04da3e906b38cdf93610c6570d503cef317cff12a3c2ab625ce7` | 396 | 244 | comment+LF+newline |
| `player-pause.svg` | `b2a2a253d45357d8d3dceebbb84a8dc08050eda6` | `d7ad7676cd255ce1032aec7af31c96ca99609dfee562a24f153475c0e992a664` | `d0b40a7a745f9083e36ddfe33ef2f20be4f7a6ad4aae2880ad00803f84e6510c` | 542 | 397 | comment+LF+newline |
| `rotate.svg` | `abc20f17dfe83cbf7d5065f62c922a34217ae54d` | `795d0fb5a27b04d34378c30086a8f25af4129b9d928b27a4d231fe2a7f8b8455` | `98e321e256a58222ceb301d7422519c9606b3486becb4139e16c79ef7f112d18` | 414 | 260 | comment+LF+newline |
| `chevron-down.svg` | `8650685dc264b07d6a93c11c3efa40ac2a39c327` | `06bd20b8cbe565b97046c5d0ec917f11ed6b29c0e4885a82ae057325c972bf9a` | `aef395a3cdd9fd8de6024f86a6f8ddbd6320cd97c78f749010af7cdd564baaa4` | 377 | 237 | comment+LF+newline |
| `chevron-up.svg` | `194897aea5092cde42532d7984e3bbd56a588edc` | `bfe732786b05d90a0e4840eb6d6a36fabd8a67ad6258170f09e2883b3b5a1851` | `a60e86e1f61a67f28ebd4efbad87c6c9bbfb15009ac588644b5b5e2fbc71ce63` | 378 | 238 | comment+LF+newline |
| `bulb.svg` | `b6577b33d7f502a1c4c211da3252e3ccb0b7f7fd` | `3617f3cd3f835b03b9d8d4feeaa180fa3d436a01de8e109ced052e419f9fa7e0` | `dacbb19c084baafb6ac0a2c0c85306f85d93d0d67878f36f8ef79332211fa652` | 518 | 395 | comment+LF+newline |
| `alert-triangle.svg` | `8d9332ef3ad33b78200e5df0dba04be9c06fdbb7` | `fc82f02dc9702293cb8609a8aed3242c0fe5f5b3337d79d341aa9343b4526ad4` | `fa52e1980826c8fa3cf9881cf93d8d6709985a339956b213d41386cbe58e823b` | 563 | 409 | comment+LF+newline |
| `check.svg` | `6e9114c4255cc68b82c6193418d1f02297edb8bf` | `fe359b27c74ed0f4f72bfabbe5ca969a8bb13a5f39648bae63f9e798034ebed3` | `9c2121aef5a60a02a3bf4a6cd3c8a42d2dbc453acdad84288108c2228de9e743` | 395 | 240 | comment+LF+newline |
| `menu-2.svg` | `277dd841bddb1b972a32186a2740079375cb7358` | `a0080a4db00a4168cfea54a74724e4147cbd9d003f65e70fa367ae797b9cfed8` | `30db8248598fa11626ad6e40525c78fc073ac15d114011d33821f028064dd702` | 446 | 285 | comment+LF+newline |

Tailles locales **240-409 o** — toutes **≤ 2048** ✅.

## 18. Licence (hash)
`LICENSE` upstream sha256 = local sha256 = **`b740a1d46122672da62833e97f7e7c8a13fa85cbc7445b584b297cc00dde93db`**
→ **byte-identique**. Copié dans `design/auren/LICENSES/tabler-MIT.txt` (avis officiel MIT + Paweł Kuna).

## 12/19/20/21. Semantic map / machine registry / manifest / provenance / README / style / preview
- **Semantic map** : `AUREN_ICON_SEMANTIC_MAP.md` (4 nav `existing-runtime-keep` non copiées ; 10 vendored ;
  P1 différé ; typographic-only ; rejetés ; custom NOT REQUIRED ; gate).
- **Registre machine-lisible** : `source/icons/auren_icon_subset.yaml` (JSON-compatible, `json.loads`, 14
  champs top-level, 10 icônes, preuves par fichier, invariants).
- **Manifest** : §5ter, **10 entrées** `functional-icon` / `legal-review-required` / `runtime_file: NOT
  APPLICABLE` — **0 approved**.
- **Provenance** : §5.5, 10 entrées `source_type: vendor` / `usage_nature: modified-derivative` /
  `owner: … NOT AUREN IP OWNERSHIP` / `ip_ownership_status: not-legally-reviewed` — **0 verified**.
- **README** : `Asset source intake: Tabler P0 v0.1.0 ingested / human review pending` ; architecture réelle.
- **Style rules** : §10 subset Tabler (contrat SVG, 0 filled, 0 Health, 0 runtime).
- **LICENSES/README** : premier intake tiers Tabler MIT enregistré ; Health Icons ABSENT.
- **Preview** : `previews/icons/auren-icon-subset-v0.1.0.html` — statique, 0 JS/CDN, 10 refs locales, 16/20/24
  px, fond clair + graphite, 0 géométrie inline, aucun APPROVED.

## 23. Évolution du garde (`tests/test_auren_asset_governance.py`)
- Garde binaire **permanent** : raster/font (`.png/.webp/…`) toujours interdits. `.svg` **retiré** du garde
  binaire, désormais gouverné par allowlist.
- **`ALLOWED_VENDOR_SVGS`** = les 10 chemins exacts ; test **`actual == ALLOWED_VENDOR_SVGS`** (égalité —
  détecte manquant ET intrus).
- `ALLOWED_STRUCTURED_FILES` += `auren_icon_subset.yaml` (tout autre YAML/JSON refusé).
- LICENSES : `README.md` + `tabler-MIT.txt` **exactement** ; 0 Health Icons / 0 fabriquée.
- Documenté : futur SVG (Health Icons, BodyMap, nouveau vendor) = **nouvelle évolution gouvernée** du test.

## 24-25. Tests ajoutés / modifiés
- **Ajouté** : `tests/test_auren_icon_vendor_intake.py` (**20 tests**, stdlib only) — registre (schema/pins/
  10 icônes/ordre/unicité/0 approved/geometry false), fichiers (contrat Auren/sécurité/≤2Ko/sha256=registre),
  licence (officielle/sha256), manifest/provenance (10 entrées/0 approved/0 verified), preview (statique/10
  refs locales/0 inline), non-intégration (0 app/static, 0 référence app).
- **Modifié** : `tests/test_auren_asset_governance.py` (garde SVG allowlisté, LICENSES exact, provenance
  Tabler). 23 → **25 tests**.

## 26. Résultats locaux
- `test_auren_icon_vendor_intake.py` : **20 passed** · `test_auren_asset_governance.py` : **25 passed**.
- **Contrôle indépendant §21** (recompute depuis le clone) : 10 fichiers = upstream normalisé ✅ · licence
  upstream = locale ✅.
- ruff clean · budget · spec PASS · check_scope (voir §Validation).

## 27-30. Scope & garanties
- **10 SVG** · **1 licence tierce** (Tabler MIT) · **1 vendor** · **0** Health Icons/custom/PNG/WebP/ICO.
- **0** `app/**`/`data/**`/migration/dépendance/package lock/fichier Custom/runtime integration/`approved`.
- **ASSET INTEGRATION GATE: BLOCKED** — les 10 icônes = **NOT AUTHORIZED FOR APP INTEGRATION**.

## 33. Éléments différés
`Sb_ASSET_02.2` (custom glyphs) = **NOT REQUIRED** · human review (séparée) · emoji replacement / Jinja
partials / app export = builds ultérieurs après gate · `Sx_ASSET_03` BodyMap · Health Icons (si besoin futur).

## 34. Statut
🟢 **CODE COMPLETE — CI PENDING — HUMAN REVIEW PENDING.**

---

## Verdict

**Verdict :** 🟢 **Sb_ASSET_02.1 CODE COMPLETE (CI + human review pending).** Premier intake tiers réel :
**10 SVG Tabler v3.45.0** (commit `975920ff…`, tag object `64bfab…`, pins vérifiés) ingérés dans la source de
design gouvernée, **licence MIT byte-identique** (`b740a1d4…`), **provenance complète par fichier** (blob SHA
+ raw/local sha256 + tailles), **normalisation bornée** (commentaire+LF+newline, **géométrie inchangée**,
prouvé indépendamment). Semantic map + registre machine-lisible + manifest (10 entrées, **0 approved**) +
preview statique. Garde évolué en **allowlist exacte** (SVG égalité stricte ; YAML allowlisté ; LICENSES =
README + tabler-MIT). **20 + 25 tests** stdlib verts. **0 Health Icons · 0 custom · 0 app/** · 0 dépendance**.
`ASSET INTEGRATION GATE` reste **BLOCKED** ; les 10 icônes **NOT AUTHORIZED FOR APP INTEGRATION** ;
`Sx_ASSET_01`/`Sx_UI` restent CLOSED ; sections EKB/Custom préservées.

**Prochaine étape** (séparée, non commencée) : `GO VALIDATE — Sb_ASSET_02.1 Vendored Icon Subset & License
Intake`.
