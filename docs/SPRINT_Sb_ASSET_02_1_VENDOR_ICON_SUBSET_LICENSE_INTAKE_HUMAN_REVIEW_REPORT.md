# Sb_ASSET_02.1 — Vendored Icon Subset & License Intake — HUMAN REVIEW REPORT

**Verdict :** 🔴 **HUMAN REVIEW: REJECTED — DARK PREVIEW DOES NOT REPRESENT A USABLE REVIEW SURFACE**
**Type** : human review — UPSTREAM REVERIFICATION + VISUAL REVIEW — **DOCS-ONLY**
**Date** : 2026-07-20 · **Commit audité** : `804b08c` · **HEAD canonique** : `6978a34` (baseline review `eafede6`)

> Un **seul** défaut matériel, mais **bloquant** par le critère §14 : la surface de revue graphite est
> inutilisable. **Les assets, la licence et la gouvernance sont, eux, intègres et vérifiés** (détail
> ci-dessous). L'intake est **REJETÉ sur la preview** ; une action corrective séparée est ouverte.

---

## 1-3. Baseline / ascendance / drift
Commit audité `804b08c`, **ancêtre** du HEAD canonique (`eafede6` au démarrage de la revue, puis `6978a34`
après avance Custom EKB_02 closeout — indépendante, linéaire). Diff descendant `804b08c..eafede6` = **EKB_02
Custom uniquement**. `git diff --quiet 804b08c..eafede6` sur `design/auren`, les 2 tests et le rapport de
build → **exit 0 : ZÉRO drift asset post-build**. Aucune revue préexistante.

## 4-5. Commit audité / diff
`804b08c` — 27 fichiers. `git diff fe97adc..804b08c` : **10 SVG** sous `vendor/tabler/v3.45.0/outline/`,
**1 licence** (`tabler-MIT.txt`), **1 vendor**, **0** Health Icons / custom / P1 / raster / `app/**` /
dépendance / fichier Custom. Composition conforme.

## 6. Incident CI (concurrency, ≠ failure)
Run initial **`29747917098`** (`804b08c`) : **lint success**, pytest+QA & SonarCloud **`cancelled`** —
**annulation par concurrency** (Custom Program a mergé PR #29 EKB_02 → merge `eafede6` pendant la CI ;
`cancel-in-progress`). **AUCUN job `failure`.** → `INITIAL RUN CANCELLED BY CONCURRENCY` (distinct de
`BUILD TEST FAILURE`).

## 7. CI descendante — CI VERIFIED: 3/3 SUCCESS ON CANONICAL DESCENDANT eafede6
Run **`29749856878`** (`eafede6`, qui **contient** `804b08c`) : pytest+QA ✅ · lint ✅ · SonarCloud ✅.
Aucun step obligatoire failed/skipped.

## 8-10. Revalidation upstream INDÉPENDANTE — UPSTREAM FIDELITY: VERIFIED FOR ALL 10 FILES
Re-clone officiel `github.com/tabler/tabler-icons`, tag `v3.45.0` :
- **tag object `64bfab222b4626fafb2301358dd41d3f3f3d84b2`** ✅ · **commit
  `975920ff99c12c4dc9e3fe61a03738330600f9b2`** ✅ (revérifiés par Git, sans se fier au rapport).
- Pour les **10 fichiers** : `upstream_blob_sha` == registre ✅ · raw sha256 recalculé == registre ✅ ·
  **`EXPECTED_NORMALIZED_BYTES == LOCAL_BYTES`** ✅ (normalisation bornée en mémoire : commentaire + LF +
  newline) · local sha256 == registre ✅ · tailles == registre ✅. **Aucune transformation non autorisée**
  (0 path/attribut/nombre modifié, 0 minification, 0 ID/title/class/style ajouté).

## 11. Contrat SVG & sécurité
Les 10 : `viewBox="0 0 24 24"` · `fill="none"` · `stroke="currentColor"` · `stroke-width="2"` ·
round caps/joins. **0** script/style/image/foreignObject/href/xlink/url()/filter/gradient/bitmap/hex/event.
Tailles **240-409 o** — toutes ≤ 2048. 0 symlink, 0 fichier caché, 0 copie raw, 0 doublon.

## 12. Licence — OFFICIAL MIT LICENSE EVIDENCE: VERIFIED AT PINNED SOURCE
`LICENSE` upstream (commit épinglé) **byte-for-byte identique** à `tabler-MIT.txt` (`cmp` + sha256 =
**`b740a1d46122672da62833e97f7e7c8a13fa85cbc7445b584b297cc00dde93db`**). Texte MIT complet, **avis Paweł
Kuna** conservé, 0 traduction/reconstruction/modification d'année/auteur, 0 licence Health Icons.
**PROFESSIONAL LEGAL CLEARANCE: NOT CLAIMED.**

## 13/19. Semantic map — jugement des 10 métaphores
Toutes jugées compréhensibles et sans collision. Points explicites : `rotate`→reset (acceptable dans le
contexte du contrôle timer, à confirmer par le label adjacent) ; `arrows-exchange`→substitute (échange
réversible/neutre, non destructif) ✅ ; `bulb`→guidance (sobre, non « IA ») ✅ ; `check`→completed (jamais
seul sans texte accessible — semantic map le prescrit) ✅. **Aucune ambiguïté matérielle** justifiant à elle
seule un rejet.

## 14. Revue visuelle — 🔴 DÉFAUT MATÉRIEL BLOQUANT
La preview charge les 10 SVG via **`<img src="…svg">`**. Un SVG référencé en `<img>` est un **document isolé
(mode statique sécurisé, spec W3C)** : `stroke="currentColor"` y résout `currentColor` contre le `color`
**par défaut du document SVG (noir)**, **jamais** contre le CSS parent. La règle `.dark .ic{color:#C8A24B}`
**n'a aucun effet** sur un `<img>`, et **aucun `filter`** de recoloration n'est appliqué.
- **Conséquence** : les 10 icônes s'affichent en **noir** sur les deux colonnes. Colonne fond clair
  (`#F4F5F6`) : lisible. **Colonne fond graphite (`#0F1318`) : noir sur graphite = quasi invisible.**
- Comportement **déterministe** (spec, non dépendant du navigateur) → conclusion sans rendu pixel.
- Le build **documente honnêtement** la limite (commentaire CSS : « currentColor sur les `<img>` ne
  s'applique pas… la revue humaine ouvre aussi les .svg directement ») — mais §14 exige une surface de revue
  graphite **utilisable telle quelle**, ce qui n'est pas le cas.

→ **HUMAN REVIEW: REJECTED — DARK PREVIEW DOES NOT REPRESENT A USABLE REVIEW SURFACE** (décision opérateur
sur §14). La preview graphite ne permet **pas** de juger lisibilité/poids optique/contraste des icônes en
identité Auren Terminal (ambre sur graphite).

## 15. Preview (checks structurels — OK mais insuffisants)
0 JS · 0 CDN · 0 réseau · 10 chemins SVG locaux distincts (tous résolvent) · 0 géométrie inline · labels FR
+ semantic_id + nom vendor visibles · statut `human-review-pending` visible · aucun `APPROVED`. **Ces checks
structurels sont verts mais NE suffisent pas** (§14 : ne pas accepter sur la seule base des tests structurels).

## 16. Registre machine-lisible
`json.loads` OK · schema `auren.functional-icon-subset` v0.1.0 · vendor Tabler / tag `v3.45.0` / commit exact
/ style outline / MIT · **10 entrées**, ordre canonique, asset_ids/semantic_ids/chemins uniques · hashes &
tailles complets (non tronqués) · `geometry_modified: false` · review human pending · **0 approved/integrated/
legally-cleared**.

## 17-18. Manifest / provenance
Manifest : 10 entrées `functional-icon` / `legal-review-required` / `runtime_file: NOT APPLICABLE` / MIT ·
**0 `status: approved`** (regex ligne YAML). Provenance : source/tag/commit/blob SHA/sha256/licence/date ·
`owner: … NOT AUREN IP OWNERSHIP` · `ip_ownership_status: not-legally-reviewed` · **0 `verified`** · pas de
transfert de droits inventé vers Auren.

## 19. Garde de gouvernance — effective (test négatif)
`actual_svg_files == ALLOWED_VENDOR_SVGS` (égalité stricte, 10 chemins, pas de glob large). YAML subset
allowlisté ; LICENSES == README + tabler-MIT exactement ; Health Icons absent ; rasters/masters toujours
interdits ; gate bloqué. **Test négatif exécuté** : 11e SVG intrus → échoue ✅ ; SVG retiré → échoue ✅ ;
restauration → repasse, worktree propre.

## 20. Tests dédiés
`test_auren_icon_vendor_intake.py` (20) : lisent réellement fichiers/YAML/manifest/provenance/licence/preview,
**non tautologiques**, 0 réseau, 0 SHA du repo courant, sha256 recalculé et comparé au registre, refusent un
11e SVG.

## 21. Non-intégration runtime
`git diff --quiet fe97adc..804b08c -- app/` → **0**. `rg` du subset dans `app/` → **∅**. Pas de
`app/static/icons/functional/`, pas de partial/macro/import/loader/CSS runtime, aucun remplacement de
`✓ ⚠ 💡 ☰`. ✅

## 30-33. Risques / dettes
- **[BLOQUANT — §14] Preview graphite inutilisable** : `<img>` + `currentColor` → icônes noires invisibles
  sur `#0F1318`. **Motif du rejet.**
- Corrélé : la colonne « fond clair » est **trompeusement** lisible (noir sur clair) — elle ne représente
  pas non plus l'identité Auren Terminal (ambre).

## 24-25. Décision
🔴 **HUMAN REVIEW: REJECTED — DARK PREVIEW DOES NOT REPRESENT A USABLE REVIEW SURFACE.**
Non-employé : LEGALLY CLEARED · RUNTIME APPROVED · INTEGRATION READY · ASSET PACK COMPLETE.

**Ce qui reste valide et n'est PAS remis en cause** (aucun re-travail requis) : fidélité upstream des 10
SVG · licence MIT byte-identique · registre/manifest/provenance · garde de gouvernance · CI descendante 3/3.
**Le rejet porte uniquement sur la surface de revue** (preview), pas sur les assets ni la gouvernance.

## Action corrective séparée (à ouvrir)
**`Sb_ASSET_02.1-fix — Review Preview Rendering Fix`** (build séparé) : corriger
`design/auren/previews/icons/auren-icon-subset-v0.1.0.html` pour un **rendu graphite fidèle** (ambre sur
graphite) — SVG **inline** dans le HTML de preview (currentColor hérite alors du CSS), ou technique
`mask`/`-webkit-mask` colorée par `background-color: currentColor`. **Sans** modifier les 10 SVG source, la
licence, le registre, le manifest ni la provenance (tous vérifiés). Puis re-soumettre à `GO VALIDATE`.

## 35. Statut & prochaine action
```
Sb_ASSET_02.1              : CODE COMPLETE · CI GREEN · HUMAN REVIEW REJECTED (preview only)
ASSETS / LICENSE / GOVERNANCE : VERIFIED (non remis en cause)
ICON SOURCE INTAKE         : NOT ACCEPTED (blocked by unusable review surface)
10 TABLER ICONS            : NOT AUTHORIZED FOR APP INTEGRATION
CUSTOM GLYPH TRACK         : NOT REQUIRED
ASSET INTEGRATION GATE     : BLOCKED
Sx_ASSET_01 · Sx_UI        : CLOSED
```
**Prochaine action** (séparée, non commencée) : **`GO BUILD — Sb_ASSET_02.1-fix Review Preview Rendering
Fix`** (corriger la preview), puis re-`GO VALIDATE`. Le closeout `Sx_ASSET_02` reste **conditionné** à une
acceptation.

---

## Verdict

**Verdict :** 🔴 **HUMAN REVIEW: REJECTED — DARK PREVIEW DOES NOT REPRESENT A USABLE REVIEW SURFACE.** La
revalidation upstream indépendante est **totalement verte** (pins tag object + commit ; 10 SVG byte-for-byte
fidèles, normalisation bornée, géométrie inchangée ; licence MIT byte-identique `b740a1d4…` avec avis Paweł
Kuna ; registre/manifest/provenance complets 0 approved/0 verified ; garde effective par test négatif ; CI
descendante `29749856878` 3/3 sur `eafede6` ; 0 app change ; 0 Health Icons/custom). **Le seul défaut est
matériel et bloquant** : la preview charge les SVG via `<img>`, `currentColor` n'y est pas transmis → icônes
noires **invisibles sur fond graphite**, rendant la surface de revue graphite inutilisable (§14). Assets et
gouvernance **restent valides** ; corriger **uniquement la preview** (build séparé) puis re-soumettre.

**Prochaine action** (séparée, non commencée) : `GO BUILD — Sb_ASSET_02.1-fix Review Preview Rendering Fix`.
