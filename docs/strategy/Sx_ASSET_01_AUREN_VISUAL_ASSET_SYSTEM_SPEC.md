# Sx_ASSET_01 — Auren Visual Asset Architecture, Governance & Production Gate — SPEC

**Type** : SPEC / AUDIT / GOUVERNANCE — **NO CODE / NO ASSET / NO CAPTURE**, docs-only
**Statut** : ✅ **SPEC RÉDIGÉE** (attente human review)
**Programme** : `Sx_ASSET` — Auren Proprietary Visual Asset System (**nouveau, indépendant de `Sx_UI`**)
**Date** : 2026-07-19
**Baseline auditée** : `e4624b7`
**Source directrice** : *AUREN — Visual Asset Production Brief v1.0 (2026-07-15)*

> `Sx_UI` reste **CLOSED / HUMAN REVIEW COMPLETE**. Ce programme **ne rouvre pas** le rebrand, le Focus
> Mode, le shell, l'accessibilité, la baseline visuelle ni le dogfood. Il définit un **système d'assets
> propriétaire, traçable et intégrable ultérieurement**, **sans modifier l'application** dans ce sprint.
> Auren doit apparaître comme un **instrument de progression biomécanique** — ni médical, ni atlas
> anatomique, ni fitness générique, ni dashboard gamer, ni interface « IA » à gradients, ni catalogue
> bodybuilding. Qualités : **précision perçue · honnêteté informationnelle · friction minimale.**

---

## 0. Étape 0 — Brainstorming / Options / Risques / Choix retenu

### 0.1 Règle centrale
Les assets sont produits à partir d'un **contrat sémantique stable** (taxonomie + IDs), **pas** page par
page. Chaque asset porte : identifiant stable · fonction · provenance · niveau de confiance · contrat
d'accessibilité · format canonique · surfaces autorisées · version · politique d'évolution.

### 0.2 Options
| Option | Description | Verdict |
|---|---|---|
| **A** | Spec d'**architecture + gouvernance + gate** (contrat sémantique, taxonomie figée, pipeline, provenance, queue bornée), **0 asset produit** | ✅ **RETENU** |
| B | Produire directement le BodyMap master / icônes | ❌ interdit sans gate humain/anatomique/juridique/mobile |
| C | Vectoriser une planche anatomique existante | ❌ licence/provenance non maîtrisées ; création originale requise |
| D | Générer l'anatomie par IA | ❌ IA = moodboard stylistique **uniquement**, jamais master anatomique |

### 0.3 Risques
| Risque | Parade |
|---|---|
| Semantic contract drift (12ᵉ zone inventée pour « améliorer » le dessin) | taxonomie **figée à 11 zones** = vérité fonctionnelle (§Taxonomie) |
| Asset ajouté page par page | contrat sémantique + manifest (§Manifest) |
| IDs minifiés/fusionnés par optimisation | IDs = **API** ; SVGO interdit de toucher viewBox/IDs/paths (§Pipeline) |
| Licence tierce non vérifiée | provenance + LICENSES + vérif source officielle au build (§Provenance) |
| Prétention médicale/EMG | positionnement **non médical** strict (§Non médical) |
| Dépendance runtime graphique | SSR sans SVGO/resvg/Node/Blender (§Pipeline runtime) |
| Master anatomique irréversible (genre encodé) | taxonomie **jamais** genrée ; variantes = contrat, pas dépendance |

### 0.4 Choix retenu
**Option A.** Gouvernance + architecture + gate, docs-only. **`AUREN ASSET PROGRAM: PRODUCTION QUEUE
READY`** sans autoriser l'intégration app (`ASSET INTEGRATION GATE: BLOCKED`).

---

## 1. Audit du repository (état réel, baseline `e4624b7`)

### 1.A Contrat BodyMap (source de vérité)
- **`app/services/body_map_descriptor.py`** : produit `status` (`mapped`|`unknown`), `primary_zone`,
  `secondary_zones` (role primary/secondary), `source`/`resolution_path` (`db_lookup`|`substring_fallback`|
  `unknown`). **« No anatomy is invented »** — `unknown` → descriptor explicite « À qualifier ».
- **`app/services/muscle_mapping.py`** : `ZONE_LABELS` = **les 11 zones canoniques** (labels FR).
- **Consumers** : `recommendation*`, `body_intelligence*`, `session_recap`, `narrative`,
  `routers/sessions.py`, `_partials/exercise_card.html`.
- **Rendu actuel** : `_partials/worked_area_body_map.html` (Sb_BODYMAP_01.1) — **SVG inline CSS/SSR,
  décoratif** (`aria-hidden`), mapping **11 zones → 6 macro-régions déjà défini** (`_WA_ZONE_TO_REGION`).
  **= PROTOTYPE** (à remplacer par le master original après gate).

### 1.B Assets PWA actuels (`app/static/icons/`)
`auren-mark.svg`, `favicon.svg`, `apple-touch-icon.png`, `icon-192.png`, `icon-512.png`,
`icon-maskable-512.png` — livrés par `Sb_UI_10.2` (Sx_UI_10). **Assets provisoires déjà en production**
(brand-bearing). **Ne pas les supprimer** ; les auditer comme provisoires.

### 1.C Iconographie fonctionnelle
SVG inline (base.html : 4 bottom-nav + 4 rail ; welcome ; worked_area). **Pas de bibliothèque vendored** ;
icônes custom inline (currentColor, décoratives). Rest timer / substitution / historique / guidance :
mélange texte + inline.

## 2. Classification des assets

| Asset / famille | Emplacement | Consumer | Provenance | État | Action |
|---|---|---|---|---|---|
| BodyMap silhouette (SVG inline) | `_partials/worked_area_body_map.html` | exercise_card / body-intelligence | interne (Sb_BODYMAP_01.1) | **PROTOTYPE — TO REPLACE AFTER GATE** | master original commandé |
| `ZONE_LABELS` (11 zones) | `services/muscle_mapping.py` | descriptor + consumers | interne | **EXISTING — ACCEPTED RUNTIME ASSET** (contrat métier) | figer (Layer A) |
| `auren-mark.svg` | `static/icons/` | manifest/head | Sb_UI_10.2 (glyphe haltère recoloré) | **EXISTING — PROVISIONAL** (brand-bearing) | audit, provisoire |
| `favicon.svg` | `static/icons/` | head | Sb_UI_10.2 | **EXISTING — PROVISIONAL** | audit |
| `icon-192/512/maskable-512.png` · `apple-touch-icon.png` | `static/icons/` | manifest/head | Sb_UI_10.2 (sips) | **EXISTING — ACCEPTED RUNTIME ASSET** (provisoire jusqu'à mark final) | conserver |
| Icônes nav/rail (SVG inline) | `base.html` | shell | interne custom | **EXISTING — ACCEPTED RUNTIME ASSET** | inventorier dans semantic map |
| Wordmark commercial | — | — | — | **MISSING — BRAND-BEARING, PROVISIONAL UNTIL PROFESSIONAL CLEARANCE** | conditionnel au nom |
| Master BodyMap original | — | — | — | **MISSING — EXTERNAL HUMAN PRODUCTION REQUIRED** | Sx_ASSET_03 |

*(Aucun asset supprimé dans cette session.)*

## 3. Contrat sémantique BodyMap — Taxonomie canonique (FIGÉE)
Exactement **11 zones** (+ `unknown` = état métier neutre, **pas** une région anatomique) :
```
pecs · delt_lat · delt_post · lats · upper_back · biceps · triceps · quads · posterior · calves · core
```
**Ne jamais inventer une 12ᵉ zone pour améliorer le dessin.** Correspond **exactement** au code réel
(`ZONE_LABELS`) — **aucun semantic contract drift**.

### Six macro-régions (rendu compact)
| Macro | Zones |
|---|---|
| **Chest** | pecs |
| **Shoulders** | delt_lat · delt_post |
| **Back** | lats · upper_back |
| **Arms** | biceps · triceps |
| **Legs** | quads · posterior · calves |
| **Core** | core |
Le **master futur** contient les **11 zones** ; le **rendu compact** peut utiliser les 6 macros (comme le
prototype actuel).

## 4. Séparation des quatre layers
- **Layer A — métier** : codes zones · principal · secondaires · mapped · unknown (**API stable**, ne
  change jamais pour un changement de silhouette).
- **Layer B — géométrie** : variante corporelle · vue face/dos · IDs SVG · macro-région · paths.
- **Layer C — présentation** : `neutral · primary · secondary · unknown · disabled`.
- **Layer D — surface** : `session-compact · program-card · history · progress-overview ·
  body-intelligence · onboarding`.
**Un changement de silhouette (Layer B) ne doit jamais migrer les données métier (Layer A).**

## 5. IDs stables (traités comme une API)
```
auren-bodymap · body-front-base · body-back-base
zone-pecs · zone-delt_lat · zone-delt_post · zone-lats · zone-upper_back
zone-biceps · zone-triceps · zone-quads · zone-posterior · zone-calves · zone-core
```
Règles : **aucun** renommage auto · ID minifié · ID dupliqué · path fusionné entre zones · suppression par
optimisation. Toute évolution incompatible = **nouvelle spec + migration**.

## 6. Variantes corporelles (contrat, pas production)
`male_neutral_v1` · `female_neutral_v1` · `neutral_abstract_v1`. **La taxonomie n'encode jamais le
genre.** V1 potentielle = `male_neutral_v1`, **sans** en faire une dépendance irréversible (le Layer A
reste indépendant de la variante).

## 7. Doctrine anatomique
Hiérarchie : (1) taxonomie Auren = vérité fonctionnelle · (2) BodyParts3D = référence spatiale · (3)
AnatomyTOOL = contrôle pédagogique · (4) illustrateur vectoriel = **création originale** · (5) relecteur
anatomique/biomécanique · (6) dogfood mobile. **Interdits** : copier une planche · vectoriser une image
sans licence · IA comme anatomie de référence · prétendre représenter une activation EMG · représenter une
mesure non mesurée · précision > données. **IA = moodboard stylistique uniquement.**

## 8. Direction artistique BodyMap (master futur)
Adulte · athlétique (non culturiste) · symétrique · neutre · bras/jambes légèrement écartés · vues
orthographiques · face+dos même échelle · **sans** visage détaillé/veines/fibres/organes/ombrage réaliste/
détails sexuels · lisible **60–120 px** · exploitable côte à côte à **360 px**. Le BodyMap **localise** une
région du catalogue ; il **ne mesure pas** l'intensité physiologique.

## 9. Iconographie
- **Primaire** : **Tabler Icons**, sous-ensemble **figé et vendored** (pas d'install runtime de toute la
  lib). Processus futur : version précise · date d'accès · vérif licence officielle actuelle · sélection
  minimale · copie SVG approuvés · conservation licence · normalisation attributs · provenance+version.
- **Secondaire** : **Health Icons** uniquement pour concepts corps/mesure non couverts par Tabler
  (audit source officielle + normalisation).
- **Custom Auren possibles** : Body Intelligence · confidence score · zone worked · push/pull · surcharge
  proposée · substitution préservant le pattern · historique substitué · historique exclu.
- **Restent typographiques** (pas de pictogramme devant chaque métrique) : kg · reps · numéro de série ·
  cible · RIR · durée précise · score numérique.

## 10. Contrat SVG des icônes
Canon : `viewBox="0 0 24 24"` · `stroke-width="2"` · `stroke-linecap/linejoin="round"` · `fill="none"` ·
`stroke="currentColor"`. Tailles : **16** (micro) · **20** (compact) · **24** (standard) · **32** (carte/
empty) · **48** (illustration exceptionnelle). **Interdits** : hex dans le SVG · filtre · ombre · gradient ·
bitmap · webfont · emoji · texte dur · script · URL externe · mix outline/filled non gouverné.

## 11. Accessibilité
- **BodyMap** décoratif (texte adjacent = vérité) : `<svg aria-hidden="true" focusable="false">`.
- **Icônes d'action** : label visible/accessible · cible tactile suffisante · focus visible · état **non**
  porté par la couleur seule.
- **Primary/secondary** : ne pas distinguer par 2 nuances d'ambre seules → aussi remplissage plein vs
  opacité réduite · contour · structure · texte adjacent.

## 12. Formats
Canonique = **SVG** (BodyMap · icônes · mark · wordmark · glyphes · schémas). **PNG** uniquement PWA/
previews/captures/exports. **WebP** uniquement images complexes éventuelles — **jamais** BodyMap ni icônes.

## 13. Pipeline cible
- **Optimisation** : **SVGO production only**. Config future **interdit** : suppression viewBox ·
  minification IDs · fusion paths · suppression groupes sémantiques · suppression metadata requises ·
  réordonnancement instable.
- **Rasterisation** : **resvg production only** (PWA PNG · maskable · previews · golden renders).
- **Runtime** : **aucune** dépendance à SVGO/resvg/Blender/Figma/Node/lib graphique distante. Le SSR
  fonctionne sans ces outils (le BodyMap inline = 0 requête réseau).

## 14. Architecture cible `design/auren/`
```
design/auren/
├── AUREN_VISUAL_ASSET_MANIFEST.md · AUREN_ASSET_PRODUCTION_BRIEF.md · AUREN_STYLE_RULES.md
├── AUREN_ASSET_PROVENANCE.md · AUREN_ICON_SEMANTIC_MAP.md · AUREN_BODY_ZONE_TAXONOMY.md
├── references/{anatomy,licences,review-notes}/
├── source/{bodymap/{auren_bodymap_master.svg, auren_bodymap_mapping.yaml}, brand/, icons/{vendor/tabler/, custom/}}
├── tokens/auren.tokens.json
├── exports/{svg,png,pwa}/
├── previews/{bodymap,session,home,body-intelligence}/
└── LICENSES/
```
**Dans Sx_ASSET_01** : architecture **documentée uniquement** — **pas** de faux masters, pas de SVG vide,
pas de licence fictive, pas d'asset tiers copié. Le **scaffold réel = premier build** (`Sb_ASSET_01.1`).

## 15. Schéma du manifest
Champs : `id · version · type · status · format · source_file · semantic_contract · surfaces ·
accessibility · license · provenance · review · budgets · consumers · deprecated_by`. Statuts : `draft ·
provisional · human-review-required · anatomical-review-required · legal-review-required · approved ·
deprecated · rejected`. **`approved` interdit avant les revues effectives.** (Exemple conceptuel du master
BodyMap : `status: human-review-required`, 11 zones, `accessibility.role: decorative`,
`semantic_source: adjacent-text`.)

## 16. Provenance & licences
Formaliser : auteur · projet source · version · date d'accès · URL interne · **identifiant SPDX** · texte
de licence · attribution · nature d'usage (intégration/modification/référence) · fichiers sources remis ·
outil utilisé · validateur. Prévoir `LICENSES/`, `REUSE.toml`/`.license`, SPDX, manifest de provenance.
**Toute affirmation de licence = vérifiée sur la source officielle au build** ; **aucun agrégateur** comme
source juridique primaire.

## 17. Positionnement non médical
**Interdits éditoriaux** : diagnostic · mesure d'activation · détection de blessure · prescription ·
preuve de récupération · validation clinique. **Autorisé** : zone associée · région principalement
travaillée · estimation indicative · classification d'exercice · représentation non médicale · données
insuffisantes · à qualifier.

## 18. Budgets techniques (objectifs de production)
BodyMap compact optimisé ≤ **12 Ko** · icône SVG ≤ **2 Ko** · mark SVG ≤ **8 Ko** · wordmark SVG ≤ **15
Ko** · favicon SVG ≤ **5 Ko** · PNG PWA 512 ≤ **200 Ko** · texture ≤ **80 Ko** · requête réseau BodyMap
actif = **0 si inline**.

## 19. Inventaire priorisé
- **P0 — fondations** : BodyMap (face/dos · 11 zones · 6 macros · neutral/primary/secondary/unknown ·
  compact export · previews 360px) · iconographie (repos/substitution/historique/guidance/programme/BI/
  info/completed/partial/trend up-stable-down) · marque/PWA (audit mark/wordmark/app-icon/maskable/
  favicon) · gouvernance (manifest/provenance/licences/taxonomie/style rules).
- **P1 — extension** : glyphes par zone · archétypes de programmes · empty states · confidence glyph ·
  timeline markers · historique substitué/exclu · progression par zone.
- **P2 — futur** : silhouette féminine · abstraite · vue latérale · micro-animations · texture graphite ·
  visuels éditoriaux. **P2 hors première queue de build obligatoire.**

## 20. Gate d'intégration
**Aucun sprint d'intégration `app/`** avant approbation des **15 éléments** : (1) taxonomie 11 zones · (2)
mapping 6 macros · (3) silhouette · (4) contrat PI · (5) provenance références · (6) master BodyMap · (7)
subset icônes · (8) règles tokens · (9) previews 360px · (10) états primary/secondary/unknown · (11)
icônes PWA · (12) contrôle anatomique · (13) contrôle licence · (14) manifest complet · (15) validation
mobile.
```
ASSET INTEGRATION GATE: BLOCKED PENDING HUMAN / ANATOMICAL / LEGAL / MOBILE APPROVALS
```

## 21. Build queue (bornée)
| Sprint | Portée | Type |
|---|---|---|
| **`Sx_ASSET_01`** | architecture/gouvernance/gate (ce doc) | spec |
| **`Sb_ASSET_01.1`** | Governance Scaffold & Provenance Registry (`design/auren/`, manifest, provenance, LICENSES, style rules ; 0 asset tiers) | build docs/scaffold |
| **`Sb_ASSET_01.2`** | Body Zone Taxonomy & Mapping Contract (11 zones, 6 macros, mapping YAML, tests IDs/schéma ; 0 dessin) | build |
| **`Sx_ASSET_02`** | Functional Iconography Selection Spec (semantic map, métaphores, liste Tabler, gaps custom, licence/version à vérifier) | spec |
| **`Sb_ASSET_02.1`** | Vendored Icon Subset & License Intake (subset minimal, provenance, licence, SVG normalisés, tests) | build |
| **`Sb_ASSET_02.2`** | Custom Auren Functional Glyphs (gaps démontrés uniquement) | build |
| **`Sx_ASSET_03`** | BodyMap Human Production Package (brief illustrateur, contrat cession, références, plan de revue, grille anatomique ; 0 génération auto) | spec |
| **`OPERATOR_ASSET_03.1`** | Human BodyMap Master Production | **action externe/humaine** |
| **`Sb_ASSET_03.2`** | BodyMap Master Intake & Technical Validation (XML/IDs/viewBox/budgets/provenance/resvg/previews ; 0 intégration) | build |
| **`Sx_ASSET_04`** | Asset Integration Slots & Consumer Mapping (après gate) | spec |
| **`Sb_ASSET_04.1`** | Controlled Runtime Integration (remplacement ciblé prototype BodyMap + icônes ; CI + baseline + review) | build app |
| **`Sx_ASSET_05`** | Final Asset Pack Closeout | closeout — **pas ouvert pendant 01** |

## 22. Dépendances avec les autres programmes
- **Exercise System** : le graphe de substitution pourra consommer une icône future
  `substitution-preserving-pattern` — mais `Sx_ASSET` **ne modifie pas** la logique de substitution.
- **Body Intelligence** : le BodyMap futur peut remplacer la géométrie prototype — **sans** ajouter de
  zone / changer les scores / activer une feature / inventer des données.
- **PWA** : icônes existantes **restent en production** ; le pack futur ne les remplace qu'après clearance
  nom + validation mark + contrôle maskable + baseline visuelle.
- **Sx_UI** : **CLOSED** — aucun changement documentaire ne le rouvre.

## 23. Statut du nom Auren (brand-bearing assets)
Auren = **WORKING PRODUCT NAME · EXTERNAL PROFESSIONAL CLEARANCE OPEN**. Peuvent avancer (indépendants du
nom) : taxonomie · BodyMap · iconographie fonctionnelle · pipeline · gouvernance · provenance ·
accessibilité. Restent **conditionnels** (`BRAND-BEARING ASSET — PROVISIONAL UNTIL PROFESSIONAL
CLEARANCE`) : wordmark commercial final · logo définitif · dépôt de marque · packaging store · achat
domaine · campagne. Les assets PWA Auren existants **restent** (provisoires, déjà intégrés).

## Non-goals
- ❌ Dessiner le BodyMap final · générer une anatomie IA · produire un logo commercial définitif.
- ❌ Intégrer un asset dans `app/` · modifier templates/CSS · remplacer le BodyMap existant.
- ❌ Installer SVGO/resvg/Node/Blender · télécharger une lib d'icônes complète · acheter une licence ·
  contacter un illustrateur.
- ❌ Créer `design/auren/` / manifest / licence / SVG / subset dans cette **spec** (= premier build).
- ❌ Déclarer Auren juridiquement disponible · rouvrir `Sx_UI` · modifier un fichier Custom · toucher au
  métier/substitution/scores/données.

## Verdict

**Verdict :** ✅ **AUREN ASSET PROGRAM: PRODUCTION QUEUE READY.** Le système d'assets propriétaire Auren
est **architecturé et gouverné** : **taxonomie figée à 11 zones** (= `ZONE_LABELS` réel, **0 semantic
contract drift**) + 6 macro-régions (= mapping déjà présent dans le prototype), **4 layers séparés**
(métier/géométrie/présentation/surface), **IDs stables traités comme API**, contrat SVG icônes, pipeline
SVGO/resvg **production-only** (0 dépendance runtime), provenance/licences SPDX, positionnement **non
médical** strict, budgets, inventaire P0/P1/P2, **manifest** schématisé. Le BodyMap actuel
(`worked_area_body_map.html`) et les icônes PWA (`Sb_UI_10.2`) sont **audités comme prototype/provisoires**
— **aucun supprimé**. Le nom Auren reste **WORKING PRODUCT NAME** ; les assets brand-bearing sont
**PROVISIONAL UNTIL PROFESSIONAL CLEARANCE**. **`Sx_UI` reste CLOSED.** Aucun asset/SVG/PNG/licence/fichier
applicatif produit (docs-only).

**`ASSET INTEGRATION GATE: BLOCKED PENDING HUMAN / ANATOMICAL / LEGAL / MOBILE APPROVALS`** — le verdict
`PRODUCTION QUEUE READY` **n'autorise pas** l'intégration app.

**Recommandation** : **GO COMMIT SPEC** (docs-only), puis premier build **`Sb_ASSET_01.1` Governance
Scaffold & Provenance Registry** (crée `design/auren/` + manifest + provenance + LICENSES + style rules,
**0 asset tiers**).
