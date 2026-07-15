# Human Review — Sb_UI_10.2 — PWA Manifest + App Icons Auren

**Verdict** : ✅ **HUMAN REVIEW ACCEPTED**
**Type** : HUMAN REVIEW — docs-only (aucun asset/manifest/template/test/code touché)
**Date** : 2026-07-15
**Worktree** : `work/auren-pwa-review-10-2` (isolé, mergé FF)

> Distinction d'état : **CODE COMPLETE** `9203e4c` (poussé) · **CI GREEN** run `29429846469` 3/3 ·
> **HUMAN REVIEW ACCEPTED** = le présent commit `docs(review)` séparé.

## 1. Baseline Git
Canonique `9203e4c` == origin, working tree **clean**. Aucune revue 10.2 préexistante.

## 2. Commit build examiné
`9203e4c` — feat(pwa): add approved Auren manifest and app icons. 19 fichiers : 6 icons
(2 SVG + 4 PNG) + manifest + 4 templates + 4 tests + 4 docs. **Aucun** route/service/model/migration/
data/CSS/JS/CI/dépendance (vérifié `git show --name-only`).

## 3. Verdict CI `29429846469` — 3/3 success
| Job | Résultat |
|---|---|
| pytest + QA scripts (dont migration + schema drift) | ✅ success |
| lint (ruff budget + bandit + actionlint + shellcheck) | ✅ success |
| SonarCloud | ✅ success |
SHA exact `9203e4c`. Aucun timeout / rerun / job skipped.

## 4. Décision graphique auditée
Glyphe d'haltère existant = symbole Auren, **géométrie strictement conservée**, fond `#0f1115`,
glyphe `#C8A24B`. Diff `favicon.svg` = **couleur seule** (`#f25f3a`→`#C8A24B`, path byte-identique).
`auren-mark.svg` = même path canonique. **Aucune interprétation graphique supplémentaire** ; aucun
monogramme inventé ; orange legacy absent.

## 5. Inspection (géométrie + palette, programmatique)
Faute d'affichage graphique, contrôle par analyse pixel (Pillow, audit only — **hors deps**) :
| Asset | Géométrie / palette |
|---|---|
| favicon.svg | path canonique intact, `viewBox 0 0 64 64`, `rx=14` conservé, fill ambre |
| auren-mark.svg | même path, canvas carré, fond graphite opaque, fill ambre |
| icon-192/512.png | **exactement 2 couleurs** rendues : graphite `(15,17,21)` + ambre `(200,162,75)` |
| icon-maskable-512.png | idem, fond opaque plein jusqu'aux bords, glyphe dans la safe zone (~22 %) |
| apple-touch-icon.png | graphite + ambre + **anti-aliasing de bord** `(131,107,54)` (mélange légitime à 180px) |

**Note mineure** : l'apple-touch (180px) présente des pixels d'anti-aliasing (transition graphite↔ambre
sur les contours du glyphe) — **artefact de rasterisation normal**, pas une couleur parasite
intentionnelle. Non-bloquant. Les icônes 512 (plus grandes) n'ont que 2 couleurs.

## 6-8. Audit binaire — dimensions & opacité
| Fichier | file(1) | sips | opacité réelle |
|---|---|---|---|
| icon-192.png | PNG 192×192 RGBA | 192×192 | **alpha_min=255 / alpha_max=255** (opaque) |
| icon-512.png | PNG 512×512 RGBA | 512×512 | alpha 255/255 |
| icon-maskable-512.png | PNG 512×512 RGBA | 512×512 | alpha 255/255 |
| apple-touch-icon.png | PNG 180×180 RGBA | 180×180 | alpha 255/255 |
**RGBA mais intégralement opaque** (alpha=255 partout) → conforme §8 (le mode RGBA n'est pas un motif
de rejet dès lors que l'image est 100 % opaque). Dimensions **exactes** conformes au contrat.

## 9. Reproductibilité
Génération par **`sips`** (macOS natif). **Aucune dépendance projet ajoutée** (requirements/pyproject
non touchés — vérifié). PNG **committés** = source de vérité ; le build applicatif **ne dépend pas** de
sips (uniquement pour reproduire). Tests CI **ne nécessitent ni macOS ni Pillow** (dimensions lues via
IHDR stdlib dans `test_auren_pwa_assets.py`). **Risque mineur documenté** : la *reproduction* des PNG
requiert macOS (ou autre rasteriseur) — pas une dépendance runtime.

## 10. Audit du manifest
JSON valide. `name` == `short_name` == **« Auren »**. Champs core **inchangés** : `id`/`lang`/`dir`/
`start_url`/`scope`/`display`/`orientation`/`background_color`/`theme_color`. **3 icônes** :
icon-192 (any), icon-512 (any), icon-maskable-512 (maskable) — chemins/tailles/types exacts. **Aucun
champ superflu** (pas de description/screenshots/shortcuts/categories/service worker). 0 `Workout`/
SPIGNOS/Orion.

## 11. Audit des heads (rendu HTTP réel)
| Surface | status | apple-touch | manifest | icon | theme |
|---|---|---|---|---|---|
| `/` (base authentifié) | 200 | 1 balise | ✅ | ✅ | `#0f1115` |
| `/login` (anon) | 200 | 1 balise | ✅ | ✅ | ✅ |
| `/register` (anon) | 200 | 1 balise | ✅ | ✅ | ✅ |
| `/welcome` (anon) | 200 | 1 balise | ✅ | ✅ | ✅ |
**Exactement 1 balise apple-touch** par surface (pas de doublon, confirmé source : 1 dans chaque
template). Titres Auren, bodies/forms/routes inchangés. (En client authentifié `/login`+`/register`
redirigent 303→`/` — comportement normal, non pertinent pour l'audit head.)

## 12. Audit du service statique
Tous servis (HTTP 200, content-type cohérent) : manifest (`application/manifest+json`), 2 SVG
(`image/svg+xml`), 4 PNG (`image/png`). Aucun chemin cassé, aucun redirect anormal.

## 13. Audit des tests
- **`test_auren_pwa_assets.py`** (nouveau) : manifest identité + core + 3 icônes + fichiers + dimensions
  (IHDR stdlib) + path canonique + palette + heads + service HTTP + 0 SPIGNOS/Workout/Orion.
- **Ré-orientations honnêtes** : `test_pwa_public_auth_heads` (apple-touch absent→présent) + 2 sentinelles
  10.1/10.3 obsolètes (« Sb_UI_10.2 owns it » / « must not create static file ») → assertions **positives**
  sur le contrat 10.2. **Aucune assertion affaiblie** (au contraire renforcées : ajout d'assertions
  négatives `"Workout" not in`). Aucun invariant légitime 10.1/10.3 supprimé (nav/logout/forms préservés).

## 14. Non-régressions (confirmées)
Aucune route / service / modèle / migration / donnée / CSS / JS / dépendance / workflow CI / service
worker / logique offline. Scope = manifest + assets + heads + tests PWA + docs. Suite CI 3/3 verte.

## 15. Risques résiduels
- Anti-aliasing sur apple-touch 180px (cosmétique, normal).
- Reproduction PNG macOS-dépendante (mineur, PNG committés = source de vérité).
- RGBA opaque (accepté par le mandat §8).

---

## Verdict

**Verdict :** ✅ **Sb_UI_10.2 — HUMAN REVIEW ACCEPTED.** Le glyphe approuvé (haltère recoloré
`#f25f3a`→`#C8A24B`, **path canonique strictement conservé**) est livré en pack PWA complet : source
`auren-mark.svg`, `favicon.svg` recoloré, 4 PNG aux **dimensions exactes** (192/512/512/180),
**intégralement opaques** (alpha 255), palette graphite+ambre. Manifest migré **name/short_name Auren**
+ 3 icônes PNG, champs core préservés, 0 champ superflu, 0 Workout/SPIGNOS/Orion. apple-touch-icon
référencé (1 balise) sur les 4 heads, assets servis 200. Génération `sips` déterministe **sans
dépendance ajoutée** ; tests CI portables (no macOS/Pillow). Tests ré-orientés honnêtement (nouvelle
vérité, non affaiblis). Aucun backend/route/CSS/JS/dépendance/service worker. CI 3/3 verte sur
`9203e4c`. Aucune collision.

**Prochaine étape** (non commencée) : **`GO CLOSEOUT — Sx_UI_10`** — `Sb_UI_10.2` était le dernier
bloqueur du closeout, désormais levé. Dogfood Focus F1/F2/F3 reste un chantier séparé.
