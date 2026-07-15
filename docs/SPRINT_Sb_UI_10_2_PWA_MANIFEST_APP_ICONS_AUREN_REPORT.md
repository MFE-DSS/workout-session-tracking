# Sprint Sb_UI_10.2 — PWA Manifest + App Icons Auren — BUILD

**Statut** : 🟢 **CODE COMPLETE — CI PENDING — HUMAN REVIEW PENDING**
**Type** : CODE BUILD — assets PWA (SVG + PNG) + manifest + heads + tests, aucun runtime/dépendance
**Date** : 2026-07-15
**Worktree** : `work/auren-pwa-assets` (isolé)
**Gate préalable** : `Sb_UI_10.2a` — débloqué par décision opérateur (glyphe approuvé)

> Ne prétend **pas** ACCEPTED. CI et human review = étapes séparées.

## 1. Baseline Git
Canonique `74af5c0` == origin, working tree clean. Aucun build 10.2 préexistant. Aucun PNG présent.

## 2. Décision graphique humaine (mandat)
Le pictogramme d'haltère de `favicon.svg` (path canonique existant) devient le **symbole officiel Auren**.
Recoloration **`#f25f3a` → `#C8A24B`** ; fond graphite `#0f1115`. Gate `10.2a` : **GO — HUMAN SOURCE
APPROVED**. Aucun autre arbitrage graphique ouvert.

## 3. Source canonique
`app/static/icons/auren-mark.svg` (nouveau) — canvas 64×64, fond graphite opaque carré, glyphe ambre,
géométrie du path **inchangée**. Source de tous les dérivés.

## 4. Géométrie préservée
Path canonique conservé **à l'identique** dans favicon.svg ET auren-mark.svg :
`M14 26h4v12h-4z…M46 26h4v12h-4z`. `viewBox="0 0 64 64"` inchangé. Aucun redessin/lissage/arrondi de
blocs. favicon garde `rx="14"` (conteneur arrondi) ; auren-mark carré.

## 5. Palette
**Graphite `#0f1115`** (fond) + **ambre `#C8A24B`** (glyphe) uniquement. **0 `#f25f3a`** (vérifié
grep + inspection PNG : top-2 couleurs = `(15,17,21,255)` et `(200,162,75,255)`). 0 autre couleur, 0 Orion.

## 6. Outils de génération
**`sips`** (macOS natif, `/usr/bin/sips`) — **déterministe** (hash identique sur runs répétés),
dimensions exactes, **aucune dépendance projet ajoutée** (pas dans requirements/pyproject).
*(Pillow a été installé temporairement dans le venv pour l'AUDIT d'opacité uniquement — pas dans les
deps, non requis par le build ni les tests, qui lisent l'IHDR PNG en stdlib.)*

## 7. Commandes de génération (reproductibles)
```bash
cd app/static/icons
sips -s format png -z 192 192 auren-mark.svg --out icon-192.png
sips -s format png -z 512 512 auren-mark.svg --out icon-512.png
sips -s format png -z 512 512 auren-mark.svg --out icon-maskable-512.png
sips -s format png -z 180 180 auren-mark.svg --out apple-touch-icon.png
```
favicon.svg = recoloration in-place du fill (`#f25f3a`→`#C8A24B`).

## 8. Fichiers produits + dimensions (audit binaire)
| Fichier | Format | Dimensions | Fond |
|---|---|---|---|
| `auren-mark.svg` | SVG | 64×64 viewBox | graphite opaque |
| `favicon.svg` | SVG | 64×64 viewBox, `rx=14` | graphite |
| `icon-192.png` | PNG RGBA | **192×192** | graphite opaque (alpha=255 partout) |
| `icon-512.png` | PNG RGBA | **512×512** | graphite opaque |
| `icon-maskable-512.png` | PNG RGBA | **512×512** | graphite opaque plein jusqu'aux bords (safe zone ~22 % ≥ 20 %) |
| `apple-touch-icon.png` | PNG RGBA | **180×180** | graphite opaque |
Coins opaques vérifiés (min_alpha=255 sur échantillonnage) → conforme Apple/maskable.

## 9. Manifest avant / après
```diff
- "name": "Workout Session Tracking",   "short_name": "Workout",
+ "name": "Auren",                       "short_name": "Auren",
- "icons": [ { favicon.svg, "any", svg+xml, "any maskable" } ]
+ "icons": [ icon-192 (any), icon-512 (any), icon-maskable-512 (maskable) ]
```
Préservés : `id`/`lang`/`dir`/`start_url`/`scope`/`display`/`orientation`/`background_color`/`theme_color`.
Aucun champ ajouté (pas de description/screenshots/shortcuts/categories/service worker).

## 10. Heads modifiés
`base.html` + `login.html` + `register.html` + `welcome.html` : ajout de
`<link rel="apple-touch-icon" sizes="180x180" href="{{ url_for('static', path='icons/apple-touch-icon.png') }}" />`
après le `<link rel="icon">`. Style `url_for` du repo respecté (le mandat montrait un href absolu ; j'ai
suivi la convention existante, plus robuste). Manifest/favicon/theme-color/titres/body/nav/forms inchangés.

## 11. Tests adaptés / créés
- **`tests/test_auren_pwa_assets.py`** (nouveau) : manifest (name/short_name Auren, champs core, 3 icônes
  exactes, pas de champ superflu, 0 SPIGNOS/Workout/Orion), fichiers présents, **dimensions PNG exactes
  via IHDR stdlib** (no Pillow → CI-safe), favicon palette + path canonique, heads apple-touch, manifest
  + icônes servis (HTTP 200, content-type image).
- **`tests/test_pwa_public_auth_heads.py`** : `apple-touch-icon not in src` → **`in src`** (ré-orienté).
- **Extension de périmètre justifiée** : `tests/test_auren_public_auth_strings.py` et
  `tests/test_auren_visible_product_strings.py` contenaient des sentinelles **explicitement scopées à
  10.1/10.3** (« Manifest stays generic — **Sb_UI_10.2 owns it** », « This sprint must not create any
  static file ») **devenues obsolètes par ce sprint** → ré-orientées vers la nouvelle vérité (manifest =
  Auren, pack présent). Aucune assertion affaiblie ; nouvelle vérité assumée.

## 12. Résultats locaux
- `test_auren_pwa_assets` + `test_pwa_public_auth_heads` + `test_pwa_installability` = **39 verts**.
- Suite affectée (auth strings/auth/nav/visible strings + PWA) = **94 verts**.
- Sweep large (pwa/manifest/icon/head/auth/nav/auren/welcome) = **263 passed / 0 échec**.
- ruff clean · budget **543 ≤ 548** · spec protocol **PASS** · check_scope **ISOLATED**.

## 13. Scope
15 fichiers : manifest + 2 SVG + 4 PNG + 4 templates + 3 tests + ce rapport (+ registry/roadmap).
**Aucun** route/service/model/migration/data/CSS/JS/CI/dépendance touché.

## 14. Risques
- **Assets binaires committés** : les 4 PNG sont générés par `sips` (déterministe) ; reproductibles via
  les commandes §7. Métadonnées binaires : PNG RGBA standard, pas de timestamp variable observé.
- **`sips` = macOS-only** : la *reproduction* des PNG nécessite macOS (ou un autre rasteriseur) ; les PNG
  committés sont la source de vérité. Documenté.
- **apple-touch RGBA avec alpha** : tous pixels opaques (vérifié) — iOS applique son propre masque.

## 15. Non-régression PWA (confirmée)
Aucun service worker · aucune logique offline · aucune route/backend modifié · aucune dépendance runtime.
`start_url`/`scope`/`display` inchangés · installabilité préservée (tests verts).

---

## Verdict

**Verdict :** 🟢 **Sb_UI_10.2 — CODE COMPLETE (assets PWA Auren).** Le glyphe approuvé (haltère recoloré
`#f25f3a`→`#C8A24B`, path canonique **inchangé**) est livré en pack PWA : source `auren-mark.svg`,
`favicon.svg` recoloré, PNG `192/512/maskable-512/apple-touch-180` (dimensions exactes, fond graphite
opaque, générés par `sips` déterministe **sans dépendance ajoutée**). Manifest migré → **name/short_name
« Auren »** + 3 icônes PNG (champs core préservés). apple-touch-icon ajouté sur les 4 heads. **0 #f25f3a /
0 SPIGNOS visible / 0 Orion.** Aucun backend/route/CSS/JS/dépendance/service worker. 3 tests (1 nouveau +
2 sentinelles ré-orientées + 1 assertion pwa-heads) ; 263 sweep verts.

**Recommandation** : push branche → CI 3/3 (ou FF canonique + CI), puis `GO VALIDATE Sb_UI_10.2`. `Sx_UI_10`
Closeout ensuite (10.2 était le dernier bloqueur).
