# Sprint Sb_UI_10.2a — PWA Asset Decision Gate — REPORT

**Statut** : 🔴 **BLOCKED — ASSET SOURCE REQUIRED**
**Type** : DECISION GATE / AUDIT ONLY — docs-only (aucun code/asset/manifest touché)
**Date** : 2026-07-15
**Worktree** : `work/auren-pwa-asset-gate` (isolé)
**Objet** : gate préalable à `Sb_UI_10.2` (PWA Manifest + App Icons Auren)

> Ce gate **n'implémente pas** `Sb_UI_10.2`. Il conclut par une décision unique : **BLOCKED**.

---

## 1. Baseline Git
Canonique `4f1b662` == origin, working tree **clean**. Aucun gate 10.2a préexistant. Audit conduit en
lecture seule ; documentation écrite dans le worktree isolé.

## 2. Décision : **ASSET GATE: BLOCKED — ASSET SOURCE REQUIRED**
Aucune **source graphique Auren canonique approuvée** n'existe dans le repository. Le seul asset présent
(`favicon.svg`) est **legacy** (identité SPIGNOS / orange abandonné `#f25f3a`). Produire un pack PWA
imposerait d'**inventer une identité visuelle non approuvée** (recoloration arbitraire ou nouveau
monogramme) — **formellement interdit** par le canon graphique (§4 du brief : pas de nouveau logo,
monogramme, symbole, palette).

---

## 3. Inventaire des assets (fait observé)

| Asset | Format | Dimensions | Transparence | Référencé par | Identité | Qualité source | Décision |
|---|---|---|---|---|---|---|---|
| `app/static/icons/favicon.svg` | SVG | viewBox 0 0 64 64 | non (fond plein `#0f1115`) | manifest + heads (base/login/register/welcome) | **legacy SPIGNOS** (path `#f25f3a`) | source vectorielle | **remplacer** |
| apple-touch-icon | — | — | — | — | **ABSENT** | — | à produire |
| maskable PNG (192/512) | — | — | — | — | **ABSENT** | — | à produire |
| favicon.ico / PNG | — | — | — | — | **ABSENT** | — | à produire |
| master SVG Auren | — | — | — | — | **ABSENT** | — | **requis** |

**Seul asset image dans `app/`** : `favicon.svg` (+ `science_diagram.svg`, un partial non-icône, hors
scope). **Aucun PNG, aucune apple-touch, aucune maskable, aucun .ico.**

## 4. Audit du manifest (`app/static/manifest.webmanifest`)
| Propriété | Valeur | Classification |
|---|---|---|
| `name` | « Workout Session Tracking » | **NEEDS_AUREN_MIGRATION** (générique, ni SPIGNOS ni Auren) |
| `short_name` | « Workout » | **NEEDS_AUREN_MIGRATION** |
| `start_url` / `scope` / `display` | `/` / `/` / `standalone` | COMPLIANT (ne pas changer) |
| `theme_color` / `background_color` | `#0f1115` | COMPLIANT (graphite Auren Terminal) |
| `icons` | 1× `favicon.svg`, `sizes:"any"`, `purpose:"any maskable"` | **GRAPHICALLY_BLOCKED** (asset legacy) + TECHNICALLY_OPEN (pas de PNG maskable dédié) |
| `orientation`/`lang`/`dir`/`id` | portrait/fr/ltr/`/` | COMPLIANT |

`name`/`short_name` génériques → migration Auren nécessaire (technique, faisable). Mais l'**icône**
reste bloquante (source legacy).

## 5. Audit des heads HTML
`base.html` + `login/register/welcome` (standalone) portent tous : `theme-color #0f1115` ✅,
`<link rel="manifest">`, `<link rel="icon" ... favicon.svg>`. **Aucun `apple-touch-icon`** (confirmé par
le test `test_pwa_public_auth_heads.py:122` qui **exige** actuellement son absence). Aucune maskable PNG.

## 6-7. Source Auren candidate + analyse maskable
**Candidat unique** : `favicon.svg`.
- **Provenance** : Sprint 0 bootstrap (`9903d08`). Motif abstrait de segments (pictogramme, pas une lettre).
- **Technique** : carré (64×64), vectoriel, dérivable en toutes tailles ; zone centrale utilisable maskable.
- **Cohérence produit** : ❌ **path en `#f25f3a`** = orange **legacy SPIGNOS explicitement abandonné**
  (`app.css:6` « l'ancien thème dark/orange #f25f3a est retiré » ; `Sx_UI_01:191` « éliminé du
  branding » ; `VISUAL_IDENTITY_V2:69` « #f25f3a = identité visuelle SPIGNOS »). **Ne respecte PAS**
  la palette Auren Terminal (ambre `#C8A24B`). Aucune approbation comme asset Auren ; au contraire, la
  spec `Sx_UI_10` (l.138) liste « favicon Auren » comme **à produire**.

**Analyse maskable** : le favicon a un fond plein (bon pour maskable) mais son symbole n'est pas Auren
→ inexploitable en l'état.

## 8-9. Analyse technique / produit
- **Technique** : rien ne bloque la *pipeline* (SVG→PNG rasterisation, tailles, maskable) — la
  transformation est réalisable.
- **Produit** : **le contenu graphique manque.** Il n'existe aucun symbole/monogramme Auren approuvé.
  Recolorer le motif legacy en ambre = **réinterprétation non validée** (le motif reste un symbole
  SPIGNOS d'origine) ; dessiner un « A » / un glyphe = **invention interdite** (§4).

## 10. Options évaluées
| Option | Évaluation | Verdict |
|---|---|---|
| **A** — réutiliser une source Auren existante | **impossible** : aucune source Auren n'existe | ❌ |
| **B** — dériver un monogramme depuis l'UI | **interdit** : aucun symbole Auren rendu (brand = texte, pas de glyphe) ; créer un « A »/rune = invention | ❌ |
| **C** — conserver les anciennes icônes | favicon legacy `#f25f3a` = **PAS un closeout Auren** | ❌ REJECTED FOR CLOSEOUT |
| **D** — demander un asset source dédié | **RETENU** | ✅ **BLOCKED — ASSET SOURCE REQUIRED** |

## 11. Pack cible à spécifier (pour `Sb_UI_10.2`, une fois la source fournie)
| Sortie | Chemin cible | Format | Dimensions | Fond | Purpose | Source |
|---|---|---|---|---|---|---|
| master vectoriel Auren | `app/static/icons/auren.svg` (à définir) | SVG | — | — | génération | **asset approuvé (à fournir)** |
| favicon | `app/static/icons/favicon.svg` (remplace) | SVG | any | `#0f1115` | browser | master |
| icône manifest `any` | `app/static/icons/icon-192.png`, `icon-512.png` | PNG | 192, 512 | transparent/`#0f1115` | any | master |
| maskable | `app/static/icons/maskable-512.png` | PNG | 512 | opaque `#0f1115` | maskable (safe zone ≥ 20%) | master |
| apple-touch-icon | `app/static/icons/apple-touch-icon.png` | PNG | 180 | opaque `#0f1115` | apple | master |

> Aucune dimension imposée par les tests actuels (le SVG `sizes:"any"` suffit aujourd'hui) → ces tailles
> sont un **contrat proposé**, à confirmer humainement au build.

## 12. Transformations AUTORISÉES (pour 10.2, sur source approuvée)
Rasteriser le SVG master · ajouter un fond graphite `#0f1115` · appliquer l'accent ambre `#C8A24B` ·
ajouter une marge de sécurité maskable · produire la variante maskable · optimiser le poids · préserver
les proportions · gérer la transparence selon la cible.

## 13. Transformations INTERDITES
Redessiner/réinventer le symbole · modifier ses proportions · ajouter ombre/gradient non approuvé ·
changer la palette (autre que graphite/ambre) · incruster du texte « Auren » dans une petite icône ·
générateur aléatoire · logo tiers · asset sous licence inconnue · **réutiliser le `#f25f3a` legacy** ·
introduire « Orion ».

## 14. Plan de tests `Sb_UI_10.2` (à créer/adapter, pas maintenant)
1. manifest accessible + JSON valide · 2. `name`/`short_name` = **Auren** · 3. zéro Orion · 4. zéro
SPIGNOS visible · 5. chaque fichier déclaré **existe** · 6. tailles déclarées == fichiers · 7. types MIME
cohérents · 8. maskable présente si retenue · 9. **apple-touch-icon présent** → **ré-orienter**
`test_pwa_public_auth_heads.py:122` (qui exige aujourd'hui son ABSENCE) · 10. heads inchangés hors
références attendues · 11. installabilité non cassée · 12. start_url/scope/display inchangés · 13. assets
servis sans erreur · 14. pas de service worker (préserver `test_pwa_installability.py:141`) · 15. pas de
dépendance runtime.

## 15. Risques
- **Contrat de test à faire évoluer** : `apple-touch-icon not in src` deviendra faux → réalignement
  honnête requis dans 10.2 (documenté ici).
- **Licence/provenance** de la future source : à garantir (asset original, pas de logo tiers).
- **Lisibilité petite taille** de la source à fournir : contrainte à respecter au design.

---

## Verdict

**Verdict :** 🔴 **ASSET GATE: BLOCKED — ASSET SOURCE REQUIRED.** Le repository ne contient **aucune
source graphique Auren canonique approuvée**. Le seul asset (`favicon.svg`, Sprint 0) est **legacy
SPIGNOS** (orange `#f25f3a` explicitement abandonné, ≠ ambre Auren Terminal `#C8A24B`), et la spec
`Sx_UI_10` liste elle-même le « favicon Auren » comme **à produire**. Options A/B rejetées (aucune
source Auren, invention interdite), C rejetée pour closeout (asset legacy). **`Sb_UI_10.2` reste
bloqué.**

### Ce qui doit être fourni pour débloquer (Option D)
**Un asset source Auren maître**, avec ces contraintes :
- **Format** : SVG vectoriel (carré, dérivable sans perte).
- **Contenu** : symbole/monogramme Auren **approuvé humainement** (pas d'invention automatique).
- **Palette** : graphite `#0f1115` + accent ambre `#C8A24B` **uniquement** (interdits : `#f25f3a`,
  autre couleur, second accent).
- **Lisibilité** : nette à petite taille (16-32px), contours suffisants, pas de texte fin.
- **Zone maskable** : élément central dans la safe zone (≥ 20 % de marge), pas de détail coupé au crop.
- **Licence** : asset original, aucune dépendance tierce.
- **Décision humaine requise** : le choix du symbole (recolorer le motif existant vers l'ambre **avec
  validation** vs nouveau monogramme) relève d'un arbitrage graphique — pas d'une décision technique.

Fichiers à produire **après approbation** (§11) : master SVG + favicon + icon-192/512 PNG +
maskable-512 + apple-touch-icon 180.

---

**Statut : BLOCKED — ASSET SOURCE REQUIRED.** `Sb_UI_10.2` non commencé. `Sx_UI_10` Closeout reste
bloqué par `10.2`. Prochaine action (hors ce gate) : fournir/approuver la source graphique Auren
demandée ci-dessus.
