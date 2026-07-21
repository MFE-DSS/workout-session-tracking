# Sprint Sb_ASSET_02.1-fix — Review Preview Rendering Fix — BUILD REPORT

**Statut** : 🟢 **PREVIEW FIXED — CI PENDING — RE-REVIEW REQUIRED**
**Type** : correctif borné (preview + test + docs) — corrige l'unique motif de rejet de `Sb_ASSET_02.1`
**Date** : 2026-07-21 · **Baseline** : `64ab789` (rejet Sb_ASSET_02.1) · **Worktree** : `work/sb-asset-02-1-fix-preview-rendering`

> **CSS MASK RENDERING · ONE CANONICAL SVG COPY · AMBER ON GRAPHITE · DARK ON LIGHT · NO IMG SVG RENDERING ·
> NO INLINE GEOMETRY · NO SOURCE ASSET CHANGE · NO LICENSE/GOVERNANCE CHANGE · NO APP INTEGRATION ·
> RE-REVIEW REQUIRED.**

---

## 1. Contexte du rejet
`Sb_ASSET_02.1` (build `804b08c`) a été **REJETÉ** en human review (`64ab789`) pour un **unique** motif :
`DARK PREVIEW DOES NOT REPRESENT A USABLE REVIEW SURFACE`. Assets, licence et gouvernance étaient (et
restent) **VÉRIFIÉS — no rework required**.

## 2. Cause racine
La preview rendait les icônes via `<img src="…svg">`. Un SVG en `<img>` est un **document isolé** : son
`stroke="currentColor"` résout `currentColor` contre le `color` **par défaut du document (noir)**, jamais
contre le CSS parent. Résultat : icônes **noires**, invisibles sur le fond graphite `#0F1318`.

## 3-4. Correction appliquée — technique CSS mask
Chaque icône est désormais un `<span class="ic icon-mask icon-<name> icon-<size>">` :
```css
.icon-mask{ display:inline-block; background-color:currentColor;
  -webkit-mask-repeat:no-repeat; mask-repeat:no-repeat;
  -webkit-mask-position:center; mask-position:center;
  -webkit-mask-size:contain; mask-size:contain }
.icon-<name>{ -webkit-mask-image:url("…/<name>.svg"); mask-image:url("…/<name>.svg") }
```
Le span est un rectangle rempli de `background-color: currentColor`, **découpé par l'alpha du SVG** (mask).
`currentColor` prend le `color` du contexte → la couleur du parent **colore réellement** l'icône (spec CSS
Masking), ce que `<img>` interdisait.

## 5. Conservation des chemins
Les 10 `mask-image` référencent les 10 SVG canoniques par **chemin relatif** exact
(`../../source/icons/vendor/tabler/v3.45.0/outline/<name>.svg`). **Aucune copie, aucun base64, aucune
duplication.** Les 10 URL résolvent vers des fichiers réels (vérifié).

## 6. Absence de duplication géométrique
**0 `<path>` / 0 `<svg>` inline** dans le HTML (vérifié). La géométrie reste dans les 10 SVG sources.

## 7. Tailles
`icon-16` / `icon-20` / `icon-24` (16/20/24 px). Chaque icône apparaît **6×** : 2 fonds (clair/graphite) × 3
tailles (60 spans au total).

## 8. Couleurs clair / graphite
`.light{ color:#0F1318 }` → icônes **graphite** sur fond clair `#F4F5F6`. `.dark{ color:#C8A24B;
background:#0F1318 }` → icônes **ambre Auren** sur fond graphite. `currentColor` porte la couleur au
`background-color`, révélé par le masque.

## 9. Vérification visuelle
- Les **10 mask-image** résolvent vers les **10 SVG réels** (vérifié fichier par fichier).
- Mécanisme **déterministe** (spec CSS Masking) : `background-color: currentColor` + `mask-image` colore
  l'icône avec le `color` du contexte → **graphite lisible sur clair**, **ambre lisible sur graphite**. Plus
  aucune icône noire invisible. Compatibilité standard + WebKit (deux préfixes déclarés).
- La preview reste servable en local (`python -m http.server`) si un navigateur bloque les masks en `file://`
  — **0 CDN, 0 URL distante, 0 dépendance réseau**.

## 10. Non-régression des preuves (§14)
Byte-identiques à `64ab789` : **10 SVG vendor** · **registre `auren_icon_subset.yaml`** · **LICENSES/** ·
**manifest** · **provenance**. Aucune valeur de preuve (pins, blob SHA, sha256, normalisation, géométrie,
licence MIT, garde `ALLOWED_VENDOR_SVGS`) ne change. Tests gouvernance + intake : **45 passed**.

## 11. Tests mis à jour
`tests/test_auren_icon_vendor_intake.py` — le test preview devient `test_preview_uses_css_mask_not_img` :
0 script · 0 http(s) hors namespace · **0 `<img `** · `mask-image` + `-webkit-mask-image` présents · **10
URL SVG distinctes** vers fichiers réels · `background-color:currentColor` · modes `.light`/`.dark` colorés ·
classes 16/20/24 · **0 géométrie inline** (`<path`/`<svg`) · 0 `approved`. **Aucun test d'intake affaibli**
(fidélité SVG / licence / manifest / provenance / garde / non-intégration inchangés).

## 12-14. Scope / non-modification / non-intégration
- **Modifiés** : `previews/icons/auren-icon-subset-v0.1.0.html` · `tests/test_auren_icon_vendor_intake.py`
  (test preview) · ce rapport · `SPEC_REGISTRY.md` · `ROADMAP_AND_NEXT_STEPS.md` ·
  `AUREN_ASSET_PROGRAM_ROADMAP.md`.
- **NON touchés** (byte-identiques) : les 10 SVG, la licence, le registre, le manifest, la provenance.
  **Fichiers optionnels `source/icons/README.md` et `AUREN_ICON_SEMANTIC_MAP.md` NON modifiés** (la technique
  de preview n'appartient pas au contrat sémantique).
- **0** `app/**` / `data/**` / migration / `.github/**` / `scripts/**` / Custom.
- Le **rapport de human review du rejet reste inchangé** (preuve historique).

## 15. Statut
🟢 **PREVIEW FIXED — CI PENDING — RE-REVIEW REQUIRED.** `ASSET INTEGRATION GATE: BLOCKED` inchangé ; 10
icônes **NOT AUTHORIZED FOR APP INTEGRATION**.

---

## Verdict

**Verdict :** 🟢 **Sb_ASSET_02.1-fix — PREVIEW FIXED (CI + re-review pending).** L'unique motif du rejet est
corrigé : la preview n'utilise plus `<img>` mais un **rendu CSS mask** (géométrie dans les 10 SVG canoniques
référencés par `mask-image`, couleur par `background-color: currentColor`) → icônes **graphite lisibles sur
clair** et **ambre lisibles sur graphite**, 16/20/24 px, 10 URL distinctes, **0 géométrie inline**, 0 JS/CDN.
**Aucune preuve d'intake ne régresse** : 10 SVG / licence / registre / manifest / provenance **byte-identiques**,
garde inchangée, 45 tests verts. Le test preview est renforcé (`test_preview_uses_css_mask_not_img`). **0**
modif SVG/licence/gouvernance/app. `ASSET INTEGRATION GATE` reste **BLOCKED**.

**Prochaine action** (séparée, non commencée) : `GO VALIDATE — Sb_ASSET_02.1 Vendored Icon Subset & License
Intake` (re-review après correctif preview).
