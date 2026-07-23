# Auren Visual Asset System — `design/auren/`

**Programme** : `Sx_ASSET` — Auren Proprietary Visual Asset System
**Ce scaffold** : `Sb_ASSET_01.1` — Governance Scaffold & Provenance Registry
**Spec** : [`../../docs/strategy/Sx_ASSET_01_AUREN_VISUAL_ASSET_SYSTEM_SPEC.md`](../../docs/strategy/Sx_ASSET_01_AUREN_VISUAL_ASSET_SYSTEM_SPEC.md)

> Porte d'entrée du **système de gestion des assets** Auren. Ce dossier gouverne la production, la
> provenance et l'intégration des assets visuels — **il ne contient pas encore d'asset produit**.

## Identité
```
Auren   = identité PRODUIT VISIBLE
SPIGNOS = identité INTERNE du repository, du domaine et de l'architecture
```
`Sx_UI` (transformation UI) est **CLOSED / HUMAN REVIEW COMPLETE**. Ce programme est **indépendant** et ne
le rouvre pas.

## Statut
```
Asset system scaffold : active
Asset source intake     : Tabler P0 v0.1.0 ingested / human review pending (Sb_ASSET_02.1)
BodyMap design source   : master + compact ingested / human review pending (Sb_ASSET_03.2)
                          derived from BodyParts3D + Servier Medical Art (both CC BY 4.0)
                          reproducibility independently verified (package v2 f45e0dbf…)
Runtime integration     : not started / blocked
Asset integration gate  : BLOCKED PENDING HUMAN / ANATOMICAL / LEGAL / MOBILE APPROVALS
Auren name              : WORKING PRODUCT NAME — EXTERNAL PROFESSIONAL CLEARANCE OPEN
```

## Principes
- **Contrat sémantique avant dessin** (taxonomie 11 zones + IDs stables, jamais dérivés).
- **Provenance avant intégration** (aucun asset tiers sans entrée de provenance complète).
- **SVG canonique** (icônes/BodyMap/mark/wordmark) ; PNG réservé PWA/previews/exports.
- **Aucun asset tiers non déclaré.**
- **Aucune dépendance graphique runtime** (le SSR fonctionne sans SVGO/resvg/Node/Blender/Figma).
- **Aucune promesse médicale** (Auren = instrument de progression biomécanique, non médical).
- **Texte adjacent = vérité accessible** (BodyMap décoratif `aria-hidden`).
- **Validation mobile 360 px avant intégration.**

## Navigation
- [`AUREN_VISUAL_ASSET_MANIFEST.md`](AUREN_VISUAL_ASSET_MANIFEST.md) — schéma + entrées d'assets (statuts bornés) + contrats sémantiques
- [`AUREN_BODY_ZONE_TAXONOMY.md`](AUREN_BODY_ZONE_TAXONOMY.md) — **taxonomie normative** des 11 zones, 6 macros, IDs SVG (Sb_ASSET_01.2)
- [`source/bodymap/auren_bodymap_mapping.yaml`](source/bodymap/auren_bodymap_mapping.yaml) — **contrat de mapping** versionné (0 géométrie)
- [`AUREN_STYLE_RULES.md`](AUREN_STYLE_RULES.md) — positionnement, palette, contrat SVG, anatomie, a11y
- [`AUREN_ASSET_PROVENANCE.md`](AUREN_ASSET_PROVENANCE.md) — registre de provenance
- [`AUREN_ASSET_INTAKE_CHECKLIST.md`](AUREN_ASSET_INTAKE_CHECKLIST.md) — accepter/refuser un futur asset
- [`LICENSES/README.md`](LICENSES/README.md) — procédure licences (0 licence tierce à ce jour)
- Spec programme : [`Sx_ASSET_01_..._SPEC.md`](../../docs/strategy/Sx_ASSET_01_AUREN_VISUAL_ASSET_SYSTEM_SPEC.md)
- [`AUREN_ICON_SEMANTIC_MAP.md`](AUREN_ICON_SEMANTIC_MAP.md) — **iconographie fonctionnelle** (subset Tabler P0, Sb_ASSET_02.1)
- [`source/icons/auren_icon_subset.yaml`](source/icons/auren_icon_subset.yaml) — **registre machine-lisible** du subset (preuves SHA)
- Roadmap programme : [`AUREN_ASSET_PROGRAM_ROADMAP.md`](../../docs/strategy/AUREN_ASSET_PROGRAM_ROADMAP.md)

## Architecture cible (documentée — dossiers créés au fur et à mesure)
```
design/auren/
├── README.md                          # ce fichier
├── AUREN_VISUAL_ASSET_MANIFEST.md     # créé (Sb_ASSET_01.1)
├── AUREN_STYLE_RULES.md               # créé (Sb_ASSET_01.1)
├── AUREN_ASSET_PROVENANCE.md          # créé (Sb_ASSET_01.1)
├── AUREN_ASSET_INTAKE_CHECKLIST.md    # créé (Sb_ASSET_01.1)
├── AUREN_BODY_ZONE_TAXONOMY.md        # créé (Sb_ASSET_01.2)
├── AUREN_ICON_SEMANTIC_MAP.md         # créé (Sb_ASSET_02.1)
├── LICENSES/                          # README + tabler-MIT.txt (Sb_ASSET_02.1 — 1 licence tierce : Tabler MIT)
├── source/bodymap/                    # créé (Sb_ASSET_01.2 : README + auren_bodymap_mapping.yaml — CONTRAT, 0 dessin)
├── source/icons/                      # créé (Sb_ASSET_02.1 : README + auren_icon_subset.yaml + vendor/tabler/v3.45.0/outline/*.svg ×10)
├── previews/icons/                    # créé (Sb_ASSET_02.1 : auren-icon-subset-v0.1.0.html — revue statique)
├── references/{anatomy,licences,review-notes}/   # futur (Sx_ASSET_03) — non créé
├── source/{brand,icons/{vendor/health-icons,custom}}/  # futur — non créé (Health Icons/custom NOT REQUIRED)
├── tokens/auren.tokens.json           # futur (build ultérieur) — non créé
└── exports/{svg,png,pwa}/             # futur (03.2/04.1) — non créé
```
> Les dossiers non créés **ne le sont pas vides** : ils apparaîtront quand un build y déposera un contenu
> réel. `source/bodymap/` = contrat (Sb_ASSET_01.2) ; `source/icons/` + `previews/icons/` +
> `LICENSES/tabler-MIT.txt` = **premier intake tiers Tabler** (Sb_ASSET_02.1). `source/icons/vendor/health-icons/`
> et `source/icons/custom/` restent **non créés** (Health Icons & custom NOT REQUIRED pour P0).

## Règle importante
```
La présence d'un fichier dans design/auren/ NE signifie PAS qu'il est
autorisé dans app/static/. L'intégration runtime exige le franchissement
de l'ASSET INTEGRATION GATE (15 approbations : humaine, anatomique,
juridique, mobile) — cf. la spec Sx_ASSET_01.
```

Ce scaffold **ne constitue aucune conclusion juridique** sur les sources tierces (Tabler, Health Icons,
BodyParts3D, AnatomyTOOL) : la vérification des licences se fera au moment d'un intake réel.
