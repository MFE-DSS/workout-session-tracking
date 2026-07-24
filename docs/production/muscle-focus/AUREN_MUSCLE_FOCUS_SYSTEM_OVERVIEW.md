# AUREN — Muscle Focus System Overview (`Sx_ASSET_03B`)

**Type** : vue d'ensemble opérateur — **DOCS-ONLY**. Ne produit aucun asset. `ASSET INTEGRATION GATE: BLOCKED`.
**Référence normative** : [`../../strategy/Sx_ASSET_03B_MUSCLE_FOCUS_TECHNICAL_SURFACE_SYSTEM_SPEC.md`](../../strategy/Sx_ASSET_03B_MUSCLE_FOCUS_TECHNICAL_SURFACE_SYSTEM_SPEC.md).

## Le système en 3 niveaux

```
NIVEAU 1 — Global BodyMap          (existant, reclassé)
  rôle : navigation · synthèse · score/analytics · localisation générale
  répond à : « OÙ et COMBIEN ? »           forme : inchangée (11 zones, 6 macros, 5 états)

  └── NIVEAU 2 — Regional Focus Plate        (8 plaques)
        rôle : zoom régional · lecture anatomique locale
        clefs : chest · shoulders · back · arms · core + quads · posterior · calves

        └── NIVEAU 3 — Muscle Focus / Exercise Mechanics Plate   (11 plaques)
              rôle : faisceaux · fibres · insertions · fonctions · exercices · patterns · rôle mécanique
              répond à : « COMMENT ce muscle existe, s'insère, se contracte, quels exercices le visent »
```

## Règles cardinales

1. **La profondeur se tire, elle ne se pousse jamais.** Le Niveau 1 se suffit ; N2/N3 sont optionnels, un tap
   par niveau, remontée constante.
2. **Aucun drill-down obligatoire pendant le logging.** Les plaques vivent à côté (récap post-séance) ou sur
   demande.
3. **Chaque plaque débouche sur une action de training** (ajouter un exercice) — jamais un cul-de-sac de
   connaissance. C'est l'ancrage exercice qui empêche la dérive vers l'atlas.
4. **Aucune 12ᵉ zone.** Les 11 codes métier restent l'API ; faisceaux/heads = géométrie Layer B (labels
   d'affichage), jamais des codes, jamais scorés.
5. **Non médical, non mesuré.** Zéro EMG, zéro activation chiffrée. Vecteurs schématiques, ROM fonctionnel,
   caption sobre.

## Points d'entrée produit

| Depuis | Vers | Question de l'utilisateur |
|---|---|---|
| Carte globale (tap zone) | Regional (N2) | « de quoi cette zone est-elle composée ? » |
| Récap de séance | Regional (N2) | « qu'est-ce que cette séance a touché ? » |
| Fiche exercice | Exercise Mechanics Overlay (N3) | « ce mouvement sollicite quoi, sous quel angle ? » |
| Score de zone | Regional → Muscle (N2→N3) | « pourquoi ce score ? » |
| Explore / curiosité | Muscle (N3) | « comment ce faisceau fonctionne ? » |

## Priorisation

- **P0** : spec + contrat d'IDs de plaque (docs) ; paires Regional+Muscle des **3 zones les plus critiquées** —
  `chest`/pecs, `shoulders`/delt_lat+delt_post, `posterior` (chaîne postérieure). Vues front/back, clean+caption.
- **P1** : `back`, `arms`, `quads`, `core`, `calves` ; Exercise Mechanics Overlay ; vues lateral/section ;
  overlays insertion/fibres.
- **P2** : comparative views ; contraction diagrams ; variantes female/abstract ; micro-animations.

## Statut

`MUSCLE FOCUS PLATES: CONCEPTUALLY DEFINED / NOT PRODUCED` · `GLOBAL BODYMAP: RETAINED` · `SOURCE STRATEGY:
DEFINED` · `RUNTIME INTEGRATION: NOT STARTED` · `ASSET INTEGRATION GATE: BLOCKED`. **Prochaine action :**
`GO BUILD — Sb_ASSET_03B.1 Muscle Focus System Blueprint & Plate Template` (non ouvert).
