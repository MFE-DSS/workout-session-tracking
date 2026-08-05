# AUREN — Style Rules

Règles stylistiques normatives du système d'assets Auren. Transcrites du *AUREN — Visual Asset Production
Brief v1.0* et alignées sur le runtime existant (Auren Terminal).

---

## 1. Positionnement
Auren est **un instrument de progression biomécanique**.
Auren **n'est pas** : médical · atlas anatomique · gamer · fitness générique · pseudo-IA (gradients) ·
bodybuilding illustratif.
Qualités : **précision perçue · honnêteté informationnelle · friction minimale.**

## 2. Palette
Runtime actuel = **Auren Terminal** : graphite (`--bg #0F1318`, surfaces `#151A21`/`#1B2029`) · typographie
**mono système** (0 webfont) · accent **ambre unique `#C8A24B`** (`--accent`) · `--on-accent #0A0C0F`.
- **Aucune** nouvelle palette · **aucune** couleur codée en dur dans un SVG d'icône.
- **`currentColor`** pour l'iconographie ; **tokens CSS** = source runtime des couleurs.
- **primary/secondary jamais distingués uniquement par teinte** (voir §Accessibilité).

## 3. Contrat SVG des icônes
```
viewBox="0 0 24 24"
stroke-width="2"
stroke-linecap="round"
stroke-linejoin="round"
fill="none"
stroke="currentColor"
```
Tailles autorisées : **16** (micro) · **20** (compact) · **24** (standard) · **32** (carte/empty) · **48**
(illustration exceptionnelle).

## 4. Interdits (icônes & SVG)
gradient · filtre · ombre SVG · bitmap embarqué · script · URL externe · emoji · webfont d'icônes · texte
dans un SVG (hors marque) · mix outline/filled non gouverné · **couleur hex codée en dur** (utiliser
`currentColor`/tokens).

## 5. Anatomie (BodyMap master futur)
adulte · athlétique (non culturiste) · symétrique · neutre · bras/jambes légèrement écartés · vues
**orthographiques** · face/dos **cohérents** (même échelle) · **non médical** · **aucune activation
mesurée prétendue** (pas d'EMG/mesure physiologique). Sans visage détaillé/veines/fibres/organes/ombrage
réaliste/détails sexuels. Lisible **60–120 px**, exploitable côte à côte à **360 px**. Le BodyMap
**localise** une région du catalogue ; il **ne mesure pas** l'intensité.

## 5bis. Surfaces Muscle Focus (N2/N3, `auren-plate-*`) — carve-out gouverné
> **Enacté `Sb_ASSET_03B.2R-D1`** (atomiquement avec le guard `tests/test_auren_muscle_focus_plates.py` et
> la première géométrie P0). Portée **strictement bornée aux surfaces Muscle Focus Plate** (Niveaux 2 et 3,
> IDs `auren-plate-*`).

Par exception **strictement bornée aux surfaces Muscle Focus Plate** (Niveaux 2 et 3, IDs `auren-plate-*`),
sont **autorisés, schématiques et non médicaux** : (a) la **direction de fibres** (vecteurs le long de l'axe
réel, **jamais** histologie/veines) ; (b) les **marqueurs d'origine/insertion** ; (c) un **schéma de
raccourcissement fonctionnel** (sens le long des fibres — **jamais** EMG/activation/%/recrutement) ; (d) une
**vue `section` (coupe locale) schématique** — **sans viscère, sans organe, sans rendu médical**.
**Restent interdits partout** : rendu médical réaliste, activation mesurée/EMG, viscères/organes, gradients/
ombres, détails sexuels, visage détaillé.
**Le contrat du BodyMap global (silhouette master) reste inchangé** : **§5** (vues orthographiques, non
médical, pas de fibres/organes) **continue de lier** `auren-bodymap` et le compact global. Le carve-out **ne
s'applique qu'aux plaques `auren-plate-*`**.
**Texte hors SVG** (**§4**) : la **caption** (module 9) vit dans le **HTML adjacent**, jamais dans le SVG de
la plaque ; elle **reflète** tout fait rendu par un overlay (invariant `caption_mirrors_overlay`).
**Bornes dures** : n'autorise pas de toucher le master global, ni une 12ᵉ zone, ni un code hors des 11 ; ni
activation mesurée/EMG/%/recrutement ; ni viscères même en `section`. La première géométrie P0 intakée
(`Sb_ASSET_03B.2R-D1`) est **clean** (aucun overlay fibre/insertion/section produit à ce stade) ; ces
overlays restent gouvernés par le présent carve-out pour les builds ultérieurs.

## 6. Taxonomie (figée — contrat normatif)
**11 zones** : `pecs · delt_lat · delt_post · lats · upper_back · biceps · triceps · quads · posterior ·
calves · core` (+ `unknown` = état métier neutre, **pas** une zone anatomique). **6 macros** : Chest ·
Shoulders · Back · Arms · Legs · Core. **Ne jamais inventer une 12ᵉ zone pour améliorer le dessin.**
Contrat normatif complet (labels FR, mapping, IDs SVG stables, séparation `RADAR_AXES`) :
[`AUREN_BODY_ZONE_TAXONOMY.md`](AUREN_BODY_ZONE_TAXONOMY.md) +
[`source/bodymap/auren_bodymap_mapping.yaml`](source/bodymap/auren_bodymap_mapping.yaml). Les IDs SVG
(`zone-<code>`) sont une **API figée** : toute évolution incompatible = nouvelle spec + migration de contrat.
**`BODYMAP COMPACT MACROS ARE NOT RADAR_AXES`** (macros visuelles ≠ axes analytics — ne pas fusionner).

## 7. Accessibilité
- **BodyMap décoratif** (texte adjacent suffit) : `aria-hidden="true"` · `focusable="false"`. Le texte
  reste la **vérité accessible**.
- **Icônes d'action** : label visible/accessible · cible tactile suffisante · focus visible · état **non**
  porté par la couleur seule.
- **primary / secondary** : distinguer par remplissage plein vs opacité réduite · contour · structure ·
  texte adjacent — **jamais** par 2 seules nuances d'ambre.

## 8. Formats
Canonique = **SVG** (BodyMap · icônes · mark · wordmark · glyphes · schémas). **PNG** = PWA/previews/
captures/exports uniquement. **WebP** = images complexes éventuelles — **jamais** BodyMap ni icônes.

## 9. Non médical (formulations)
**Interdits** : diagnostic · mesure d'activation · détection de blessure · prescription · preuve de
récupération · validation clinique.
**Autorisé** : zone associée · région principalement travaillée · estimation indicative · classification
d'exercice · représentation non médicale · données insuffisantes · à qualifier.

## 10. Functional icon source subset — Sb_ASSET_02.1
Premier **intake tiers** de la source de design : **Tabler outline v3.45.0** (commit `975920ff…`), **MIT**.
10 SVG P0 dans `source/icons/vendor/tabler/v3.45.0/outline/`. Contrat par fichier :
```
viewBox="0 0 24 24" · stroke-width="2" · stroke-linecap/linejoin="round" · fill="none" · stroke="currentColor"
```
- **Commentaire de métadonnées Tabler retiré** ; **géométrie NON modifiée** ; LF + newline final.
- **Aucune icône filled** · **aucune Health Icon** · **aucun glyphe custom** (NOT REQUIRED) · **0 runtime**.
- Labels & accessibilité : cf. [`AUREN_ICON_SEMANTIC_MAP.md`](AUREN_ICON_SEMANTIC_MAP.md) — icône seule
  réservée aux contrôles universels (timer play/pause/reset, menu) avec accessible name ; nav primaire &
  Body Intelligence restent **textuels**.
- **Statut** : `legal-review-required` · **HUMAN REVIEW PENDING** · **NOT AUTHORIZED FOR APP INTEGRATION**.
- Tout nouveau vendor / SVG BodyMap = **nouvelle évolution gouvernée** du garde
  (`tests/test_auren_asset_governance.py`) + provenance + licence.
