# SB_ASSET_03.2 — Visual Review Surface Report

**Date** : 2026-07-23 · **Surface** : `design/auren/previews/bodymap/auren-bodymap-v0.1.0.html`

## Nature
Surface de revue **statique, hors réseau, sans JavaScript**. Master et compact **inlinés** (zones en
**classes** pour éviter la duplication d'IDs), états pilotés par CSS. **Ne modifie aucun `app/**`.** Rendue et
inspectée en navigateur réel (Chrome headless).

## Contenu affiché
- **5 états** : `neutral · primary · secondary · unknown · disabled`.
- **11 zones** en `primary`.
- **6 macros** : chest · shoulders · back · arms · legs · core.
- **6 couples** `primary + secondary` : pecs+delt_lat · lats+upper_back · biceps+triceps · quads+posterior ·
  core+pecs · calves+quads.
- **Tailles** 360 / 120 / 80 / 60 px.
- **Fond clair et fond graphite**.
- Master **vs** compact côte à côte.

## Contrôles visuels (§11) — PASS
- **32/32 previews** présentes (matrice bornée), 6 couples conformes, aucun doublon.
- `neutral`/`unknown` : silhouette neutre, **aucune anatomie active**.
- **primary distinct de secondary autrement que par la couleur** : aplat + contour plein vs opacité réduite +
  contour **pointillé** — vérifié visuellement (ex. biceps+triceps).
- Aucune inversion **face/dos** (biceps=face, triceps=dos), aucune inversion **gauche/droite**.
- Aucune zone **rognée** ; lisible à 60/80/120 px ; rendu 360 sans scroll horizontal.
- Lisible sur **graphite** (ambre `#C8A24B`) comme sur **clair**.

## Verdict
**VISUAL REVIEW SURFACE: READY / OBSERVED.** Surface hors runtime opérationnelle, couvrant états, zones,
macros, couples, tailles et les deux fonds. Contrôles visuels humains passés. **Ceci n'est pas** une revue
anatomique professionnelle (`NOT CLAIMED`) : c'est le support de la revue humaine à venir.
