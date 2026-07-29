# AUREN — Muscle Focus Source Strategy (`Sx_ASSET_03B`)

**Type** : stratégie de sources condensée (exécutable au build) — **DOCS-ONLY**. Relevés **2026-07-24**.
**NON une conclusion juridique.** `PROFESSIONAL LEGAL CLEARANCE: NOT CLAIMED` · `ASSET INTEGRATION GATE:
BLOCKED`. **Détail et sources** : [`../../research/AUREN_MUSCLE_FOCUS_REFERENCE_RESEARCH.md`](../../research/AUREN_MUSCLE_FOCUS_REFERENCE_RESEARCH.md).

## ⚠️ SOURCE RESET — Sb_ASSET_03B.2R (BodyParts3D-primary) — prioritaire

> **Amendement normatif (2026-07-29), postérieur à la revalidation ci-dessous.** La hiérarchie « Servier-primary »
> qui suit est **conservée pour l'historique** mais **superseded** pour la géométrie de body-fitting. Doctrine
> courante : [`../../strategy/Sb_ASSET_03B_2R_BODYPARTS3D_SOURCE_RESET_SPEC.md`](../../strategy/Sb_ASSET_03B_2R_BODYPARTS3D_SOURCE_RESET_SPEC.md).
>
> ```
> PRIMARY DERIVATION:  BodyParts3D 4.0 — official DBCLS distribution — CC BY 4.0
> PLAN A: deterministic BodyParts3D derivation
> PLAN B: conditional human-only controlled sculpting (no free invention; before/after; traceability;
>         change-log; qualified anatomical review; never automated by the agent)
> PLAN C: Open3DModel — conditional, CC BY-SA provenance branch, separated, NOT authorized for P0
> VALIDATION / REFERENCE: Visible Human & approved references under their precise terms
> SUPERSEDED: Servier Medical Art — for BODY-FITTING GEOMETRY only (historical candidates preserved)
> ```
> BodyParts3D est **géométrie source traçable**, **pas** une vérité anatomique canonique (référence masculin
> adulte, non universelle, peut contenir des erreurs). `PROFESSIONAL LEGAL CLEARANCE: NOT CLAIMED` ·
> `AI GENERATION OF ANATOMY: FORBIDDEN` · `QUALIFIED ANATOMICAL REVIEW: REQUIRED` · `RUNTIME: BLOCKED`.
> Segmentation prouvée : pectoral = mesh source **entier** (partitions functional-visual) ; deltoïde =
> **source-segmenté** (clavicular/acromial/spinal → antérieur/latéral/postérieur).

## Hiérarchie retenue (source-reuse-first, cohérente BodyMap) — ⚠️ SUPERSEDED pour body-fitting (voir reset ci-dessus)

```
PRIMARY DERIVATION (géométrie du livrable)
  Servier Medical Art — CC BY 4.0        socle + continuité visuelle avec le BodyMap
  OpenStax A&P 1ʳᵉ éd. (2013) — CC BY 4.0 planches musculaires locales (crédit PAR figure) [+ clause anti-IA¹]
  Domaine public CONDITIONNEL : Gray's 1918 · atlas historiques
                                          relief fin / coupes profondes — PD par édition/scan/juridiction²

ANATOMICAL VALIDATION (lecture seule — JAMAIS de mesh tracé)
  BodyParts3D / Anatomography — CC BY 4.0 (DBCLS officiel, maj 2025-02-27)  attaches / FMA / nommage
  NLM Visible Human — TERMS-BASED gov. data (attribution + non-endossement + fraîcheur)³  validation par défaut
  Z-Anatomy — CC BY-SA 4.0                 couches superficiel/profond
  AnatomyTOOL (CC BY / CC0 items) · Kenhub  croisement pédagogique

REFERENCE / INSPIRATION ONLY (consulter, jamais dériver)
  MuscleWiki (copyright) · BioDigital · BioRender · Complete Anatomy · Muscle&Motion
  → conventions de cadrage/zoom UX seulement

EXCLUS
  OpenStax A&P 2ᵉ éd. — CC BY-NC-SA (NC)
  Wikimedia « Muscles front and back.svg » — CC BY-SA (prototype jetable, hors master livré)
```

> **Revalidation 2026-07-24** (détail : [`AUREN_MUSCLE_FOCUS_SOURCE_LEDGER.md`](AUREN_MUSCLE_FOCUS_SOURCE_LEDGER.md)) :
> **¹** OpenStax 1ʳᵉ éd. porte une **clause anti-ingestion IA** (les 2 éditions) : jamais d'usage comme entrée
> d'entraînement/LLM sans permission. **²** Gray's/atlas = **PD conditionnel** (édition/scan/juridiction +
> absence de couche moderne ; couche Lewis †1964 encore protégée en UE). **³** NLM Visible Human **n'est pas**
> « zéro contrainte » : donnée gouvernementale **terms-based** (attribution « Courtesy of the U.S. National
> Library of Medicine » + non-endossement + fraîcheur, mesh protégé) → **rôle validation/référence par défaut**,
> promotion en dérivation seulement après vérification plaque par plaque.

## Règles dures

1. **CC BY** = dérivation propriétaire licite **+ attribution irrévocable**. **CC BY-SA** = copyleft →
   validation/inspiration seulement. **NC** = éliminatoire. **CC0/PD** = liberté totale.
2. **Un mesh 3D est une expression protégée** même quand le fait anatomique ne l'est pas → on **redessine à
   partir du savoir** (multi-sources), on ne **trace/retopologise jamais** un mesh sous copyleft.
3. **BodyParts3D = CC BY 4.0** (source officielle DBCLS). Un relevé « CC BY-SA » vient du **miroir GitHub
   figé en 2011** — ne jamais qualifier depuis le miroir. Rôle retenu ici = **validation** (mesh protégé).
4. **Agrégateurs = licence par fichier**, jamais globale (Wikimedia, AnatomyTOOL, Sketchfab). Remonter à la
   source, journaliser licence + URL par asset.
5. **Séparation physique** des espaces de travail géométrie-CC BY vs référence-SA/NC ; **un prototype
   ShareAlike ne se blanchit pas.**
6. **IA = plan B/C borné** (moodboard/compo/style sur géométrie déjà validée de source propre) ; **jamais
   géométrie livrée** ; **toujours déclarée** ; **jamais** d'image propriétaire en entrée.
7. **Aucune archive/image committée dans Git** à ce stade.

## Attribution à provisionner (dette héritée)

`ATTRIBUTION SURFACE: NOT YET IMPLEMENTED` (héritée du BodyMap, non aggravée). Le produit devra porter, dans
une surface de crédits :
```
BodyParts3D, © The Database Center for Life Science — CC Attribution 4.0 International   (si validation citée)
Servier Medical Art — Les Laboratoires Servier — CC BY 4.0                               (si géométrie incorporée)
OpenStax Anatomy & Physiology (1ʳᵉ éd., 2013) — CC BY 4.0                                (si figure incorporée)
```

## Registre d'assets (obligatoire au build)

Par plaque et par asset : `source · url_licence_exacte · role(géométrie|style|validation|inspiration) ·
attribution_required · ai_assisted(flag+role) · access_date`. Aucune entrée `approved` / `verified` /
`legally-cleared` tant que la revue professionnelle n'a pas abouti.
