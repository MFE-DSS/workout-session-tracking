# AUREN — Muscle Focus Overlay / Accessibility / Mobile Contract (`Sb_ASSET_03B.1`)

**Type** : contrat normatif des **couches (clean/overlay)**, de l'**accessibilité** et du **mobile** — **DOCS-ONLY**.
Fige la séparation clean↔technique, l'a11y et les règles 360px **sans produire aucune surface**.
`ASSET INTEGRATION GATE: BLOCKED` · `PLATE GEOMETRY: NOT PRODUCED`.
**Références** : spec §5-§9 · [`AUREN_MUSCLE_FOCUS_DESCRIPTOR_SCHEMA.md`](AUREN_MUSCLE_FOCUS_DESCRIPTOR_SCHEMA.md) ·
`AUREN_STYLE_RULES §4/§5/§7` · [`AUREN_MUSCLE_FOCUS_GOVERNANCE_AMENDMENT.md`](AUREN_MUSCLE_FOCUS_GOVERNANCE_AMENDMENT.md).
**`CONTRACT VERSION: 0.1.0`**.

---

## 1. Deux couches — clean (défaut) / technical overlay (activable)

| Couche | Contenu | IDs | a11y |
|---|---|---|---|
| **Clean view** (défaut) | silhouette muscle + faisceaux (`part-*`) en aplats, hiérarchie 3 rangs | `geom-*`, `part-*` | portée par la **caption** |
| **Technical overlay** (activable) | insertions/origines, direction de fibres, raccourcissement fonctionnel | `overlay-insertion`, `overlay-fiber`, `overlay-shortening`, `mark-*` | `aria-hidden="true"` **car** la caption la reflète (§3) |
| **Exercise overlay** | rôles d'exercice projetés (principal/synergiste/adjacent) | `overlay-exercise` | contrôle avec accessible name ; clef **zone** |

- **Profondeur par le trait** : superficiel = aplat plein ; profond = contour **pointillé atténué** sous la
  couche superficielle. **Aucun gradient, aucune ombre portée** (héritage `§4`).
- **≤ 3 teintes actives** par plaque ; couleur = **tokens runtime** (Auren Terminal), jamais hex codé en dur.
- **Divulgation progressive stricte** : *la profondeur se tire, ne se pousse jamais*. Clean se suffit ; overlay
  est **opt-in**.

## 2. Renommage anti-mesure (module 7)

Le module 7 « **Contraction / ROM indicator** » est **renommé** `overlay-shortening` — **« schéma de
raccourcissement fonctionnel »** (adversarial #6). Motif : « contraction/ROM » peut se lire comme une **mesure**
(activation, %, EMG). Le schéma est **fonctionnel et non médical** : il montre le **sens de raccourcissement**
(flèche le long des fibres), **jamais** une magnitude, un pourcentage, un recrutement.

**Jetons interdits** (caption, label, descripteur, futur registre) — cible du futur guard, en miroir de
`test_registry_status_never_approved` : `EMG` · `%` · `activation` · `recruitment` · `mesure` · `clinique` ·
`diagnostic` · `prescription`. **Autorisé** : « région principalement travaillée », « estimation indicative »,
« sens de raccourcissement », « rôle mécanique » (héritage `§9`).

## 3. Accessibilité — la caption est la vérité (garde-fou dur)

**Invariant `caption_mirrors_overlay` (adversarial #4)** : **tout fait anatomique rendu visuellement dans un
overlay** (origine, insertion, direction de fibre, rôle mécanique) **doit avoir une forme textuelle dans la
caption** (module 9). Conséquence : l'overlay décoratif **peut** être `aria-hidden="true"` / `focusable="false"`
**précisément parce que** la vérité vit au texte. Sans ce miroir, un lecteur d'écran n'obtiendrait que la
silhouette + une ligne de fonction, et **aucune** anatomie N3 — inacceptable.

- **Caption = HTML, pas SVG** : le texte de caption vit dans le **HTML adjacent**, **pas** dans le SVG de la
  plaque (héritage `§4` « pas de texte dans un SVG hors marque » ; cf. amendement §2).
- **Surface décorative** : `aria-hidden="true"`, `focusable="false"` (héritage `§7`).
- **Contrôles interactifs** (`view-*`, `layer-toggle`, `overlay-exercise`) : **accessible name** visible/associé,
  **cible tactile suffisante**, **focus visible**, **état jamais porté par la seule couleur** (remplissage/
  opacité/contour/texte — jamais 2 nuances d'ambre seules, héritage `§7`).
- **Rôles d'exercice** projetés sur les 5 états figés : principal→`primary`, synergiste→`secondary`,
  adjacent→`neutral` + annotation — **jamais distingués par la seule teinte**.

## 4. Mobile 360px (divulgation progressive)

- **Clean + caption + un SEUL accordéon** d'overlay. **Repliés par défaut** : overlay technique, fibres,
  raccourcissement, coupe (`section`), comparative.
- **Toggle de vue** limité à `front`/`back` ; `lateral`/`section` derrière un « plus ».
- **Exercices en liste**, jamais en overlay sur figure à 360px.
- **Plaque N3 = sheet plein écran** — avec **dismiss/back toujours disponible**, **sans focus-trap**, remontée
  d'un tap (adversarial, note mobile). Le **côte-à-côte 360px reste réservé au compact global** (jamais deux
  plaques juxtaposées à 360px).
- **Anti-blob** : ne pas empiler overlay + fibres + raccourcissement + section + comparative dans **un même**
  accordéon dense — séquencer (un sous-groupe visible à la fois). *Note de design, à re-figer en spec de build.*
- **Desktop** : overlays dépliables/juxtaposables, 4 vues, comparative, Exercise Overlay interactif sur figure.

## 5. Invariants (futur guard)

1. `caption_mirrors_overlay == true` **et** couverture réelle : chaque fait d'overlay a un équivalent caption.
2. Aucun **jeton interdit** §2 dans caption/label/descripteur.
3. Overlay décoratif `aria-hidden` **seulement si** la caption le reflète (sinon l'info est inaccessible).
4. Contrôles interactifs : accessible name présent ; état non porté par la seule couleur.
5. Caption **hors SVG** (dans le HTML). Aucune couleur métier hex codée en dur dans le SVG.
6. Mobile : overlays repliés par défaut ; aucun côte-à-côte de plaques à 360px ; sheet N3 dismissible sans
   focus-trap.

---

## Verdict

**Verdict :** 🟢 **`MUSCLE FOCUS OVERLAY / A11Y / MOBILE CONTRACT v0.1.0: LOCKED (DOCS-ONLY).`** Séparation
clean↔technical-overlay figée, **caption = vérité accessible** (miroir obligatoire de l'overlay → `aria-hidden`
sûr), module 7 renommé `overlay-shortening` (anti-mesure) + jetons interdits pour le futur guard, mobile 360px
en divulgation progressive (sheet N3 dismissible, no focus-trap, pas de côte-à-côte). **Aucune surface
produite.** `PLATE GEOMETRY: NOT PRODUCED` · `ASSET INTEGRATION GATE: BLOCKED`.
