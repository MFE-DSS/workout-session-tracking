# AUREN — BodyMap Illustrator Brief

**Cycle** : `Sx_ASSET_03`. Direction artistique **normative** pour la production humaine du master BodyMap
(`male_neutral_v1`, P0). À lire avec le [contrat SVG](AUREN_BODYMAP_SVG_STRUCTURE_AND_DELIVERY_CONTRACT.md).

> Le master doit ressembler à un **instrument biomécanique**, **pas** à une planche médicale. Auren =
> instrument de progression biomécanique — **non médical, non atlas, non gamer, non pseudo-IA, non
> bodybuilding illustratif.**

---

## 1. Sujet & variante
- **`male_neutral_v1`** (P0) : adulte · **athlétique mais non hypertrophié** (non culturiste) · symétrique ·
  neutre · **sans genre encodé** dans les codes métier · sans détails sexuels · non médical.
- Reportées en **P2** (NON produites ici) : `female_neutral_v1`, `neutral_abstract_v1`, vue latérale.

## 2. Pose & vues
- Pose **neutre**, debout, **bras légèrement séparés du tronc**, **jambes légèrement écartées**.
- **Face et dos orthographiques** (0 perspective, 0 rotation de pose), **même échelle · même centre · mêmes
  proportions** (cf. grille viewBox `0 0 240 200`).

## 3. Style (exigences dures)
**Autorisé** : silhouette épurée, lignes claires, aplats sobres compatibles Auren Terminal (couleur pilotée
runtime, cf. §4 states).
**Interdits** : visage détaillé · veines · fibres musculaires · organes · ombrage réaliste · texture médicale ·
détails sexuels · **gradient** · effet gamer · esthétique pseudo-IA · **nouvelle palette** (0 couleur nouvelle ;
`currentColor`/tokens uniquement).

## 4. Granularité honnête (le dessin suit la donnée, jamais au-delà)
- **11 zones** exactement (cf. contrat) ; **jamais une 12ᵉ**.
- **`upper_back`** = **functional-aggregate** : ne PAS prétendre distinguer trapèzes/rhomboïdes/faisceaux/
  insertions.
- **`posterior`** = **functional-aggregate** : ne PAS prétendre séparer ischios/fessiers/adducteurs/insertions
  ni suggérer une activation différenciée.
- **Aucune apparence d'activation mesurée** (pas d'EMG, pas d'intensité). Le BodyMap **localise** une région,
  il **ne mesure pas**.

## 5. États (géométrie neutre — la couleur vient du runtime)
Le master fournit la **géométrie** des zones. Les 5 états (`neutral/primary/secondary/unknown/disabled`) sont
appliqués **au runtime** (fill/opacité/structure), **jamais** codés comme couleur métier dans le master.
`unknown` = **aucune anatomie active** (silhouette neutre, texte « À qualifier »).

## 6. Lisibilité (critères de réussite)
Identifiable et distinguable à **60 px · 80 px · 120 px**, et **côte à côte à 360 px** (face+dos). `primary`
identifiable en < 1 s ; `secondary` visible sans concurrencer `primary`. `biceps`/`triceps` distinguables ;
`lats`/`upper_back` distinguables sur le dos ; `quads`/`posterior`/`calves` distinguables sur les vues
pertinentes.

## 7. Références (voir due diligence)
- **BodyParts3D** (CC BY-SA) : **RÉFÉRENCE SPATIALE/volumétrique uniquement** (position, adjacence des
  régions). **INTERDIT** : extraction/vectorisation directe du maillage (ShareAlike → dériverait le master).
  Le master est une **création humaine ORIGINALE, redessinée**.
- **AnatomyTOOL** : uniquement des ressources **CC compatibles commercial** (CC BY / CC0), **qualifiées une par
  une** ; NC/étudiant écartés.
- Toute autre référence : déclarée (auteur/source/URL/date/licence/rôle/décision). **Aucune image de référence
  n'est committée dans Git.**

## 8. IA (strictement bornée)
IA autorisée **uniquement** pour : exploration de style · moodboard abstrait · variantes de composition **non
anatomiques**. **JAMAIS** comme : source anatomique · géométrie finale · master · validation · preuve de
provenance · remplacement du relecteur humain. **Toute** utilisation d'IA doit être **déclarée** (outil,
version, fonctions, finalité/prompts, parties affectées, méthode de redessin humain). **Géométrie générée non
déclarée = livraison bloquée.**

## 9. Accessibilité (rappel)
Le BodyMap runtime sera **décoratif** (`aria-hidden="true"`, `focusable="false"`) : le **texte adjacent** est
la vérité accessible. Master : **aucun texte incorporé**, aucune interaction, aucun focus, aucune information
par la seule couleur.

## 10. Livraison
Cf. [contrat SVG §6](AUREN_BODYMAP_SVG_STRUCTURE_AND_DELIVERY_CONTRACT.md) + [manifeste de livraison](AUREN_BODYMAP_DELIVERY_MANIFEST_TEMPLATE.md).
Master `auren_bodymap_master.svg` + source native + previews + déclarations. Statut final **jamais**
`approved`/`legally-cleared`/`runtime-integrated` avant toutes les revues.
