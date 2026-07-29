# Sprint Report — Sb_ASSET_03B.2R : BodyParts3D Source-Contract Reset

**Type** : rapport de sprint — **DOCS-ONLY + tests de policy**. Aucune géométrie, aucun binaire, aucun runtime.
**Spec** : [`strategy/Sb_ASSET_03B_2R_BODYPARTS3D_SOURCE_RESET_SPEC.md`](strategy/Sb_ASSET_03B_2R_BODYPARTS3D_SOURCE_RESET_SPEC.md).

## Brainstorming / Options / Risques / Choix retenu

- **Option 1** — garder Servier-primary et forcer un fitting corps-entier depuis des planches fragmentées.
  *Rejeté* : pas de repère commun, fitting macro insuffisant.
- **Option 2** — BodyParts3D officiel (CC BY 4.0) comme dérivation primaire, repère corps-entier, IDs FMA exacts.
  **Retenu** (confirmé produit par Martin, scope method+governance-only).
- **Option 3** — Open3DModel (CC BY-SA). *Repoussé en Plan C conditionnel* (branche SA séparée, non autorisé P0).
- **Risques** : (a) confondre traçabilité et vérité anatomique → mitigé par gate anatomique qualifié obligatoire ;
  (b) sur-revendiquer la licence → PDF officiel type-vérifié + attestation manuelle, `LEGAL CLEARANCE NOT CLAIMED` ;
  (c) résolution par nom → **corrigée** (proof exact-FMA ; un premier proof sous-chaîne matchait des artères).

## Ce qui est fait (ce lot)

1. **§2 gate revalidé** : decisions `CONFIRMED/VALID`, `§2 GATE: PASS`, archives ISA `40665852…` / PART-OF `9fbc713f…`.
2. **§3 couverture vérifiée** : 35 représentations P0, résolution `exact-FMA-curated`, **0 match artériel**, tous
   les membres OBJ traçables + hashés (`02_catalog/bodyparts3d_p0_selected_mapping.json`).
3. **Doctrine réinitialisée** : BodyParts3D-primary ; Servier `SUPERSEDED FOR BODY-FITTING GEOMETRY` (historique
   préservé) ; Plan A/B/C ; IA générative interdite ; double gate de revue.
4. **Contrat de segmentation corrigé** : pectoral = mesh source entier / partitions functional-visual ;
   **deltoïde = source-segmenté** (clavicular/acromial/spinal → antérieur/latéral/postérieur) ; posterior
   N2 `muscle-heads`, N3 `grouped-honest` inchangés.
5. **Tests de policy** : `tests/test_auren_muscle_focus_source_policy.py`.

## Ce qui n'est PAS fait (volontairement)

Aucune production géométrique (Blender / OBJ / rasterisation / SVG candidat), aucun handoff Plan-B, aucune HTML de
revue, aucun intake, `§5bis` non enacté, aucun runtime, **aucun commit/push/PR**.

## Statut

```
SOURCE RESET:              COMPLETE LOCALLY / UNCOMMITTED
P0 COVERAGE:               PROVEN (exact-FMA, 35 reps, 0 conflit)
P0 GEOMETRY:               NOT PRODUCED
ANATOMICAL REVIEW:         REQUIRED_PENDING
PRODUCT REVIEW:            AWAITING PLATE PRODUCTION
ASSET INTEGRATION:         BLOCKED
RUNTIME:                   NOT STARTED / BLOCKED
```

## Tests exécutés

Voir §10 (commandes + résultats consignés à l'exécution). Assertions sémantiques stables (pas de snapshot de
document entier). Aucun binaire brut (`.zip/.obj/.blend`, PDF licence, image opérateur) ajouté au Git.

## Verdict

🟢 **`SOURCE DOCTRINE: RESET LOCALLY`** · **`P0 SOURCE COVERAGE: PROVEN`** · géométrie non commencée. Le lot
géométrie futur (Blender déterministe) consomme cette doctrine mais reste **revu indépendamment** (produit +
anatomique qualifié) avant toute acceptation ou runtime.
