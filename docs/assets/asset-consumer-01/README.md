# ASSET-CONSUMER-01 — préparation du consommateur d'illustrations

9 novembre 2026. Base inspectée `fe9f6e9beb585a271ae2c2726e338359057b9f58` ; branche `docs/asset-consumer-01`.
**SPEC / READINESS ONLY · PROPOSED · NO_GO_BUILD · G1_PENDING · PIXELS_NOT_RECEIVED · NOT_ACTIVATED.**

Le mandat prépare la voie assets indépendante du [recadrage du 5 novembre](../../strategy/AUREN_PRODUCT_SCIENCE_REALIGNMENT_2026_11_05.md#voie-artistique-révisée) et du [chemin critique mobile](../../strategy/AUREN_MOBILE_CRITICAL_PATH_2026_11_03.md#voie-assets-indépendante) :

`master mannequin → Smith incliné START/END → fiche native pilote → sept Push A → règles de série → catalogue restant`

Le consommateur pilote précède la série. Cette préparation ne bloque pas les voies PLAN/DATA/RELEASE et n'ouvre ni MOB-08 global ni la production du catalogue.

## Livrables à relire

- [Matrice de readiness](ASSET_MATRIX.md) : identités proposées et existantes, réalisations, droits, masters, états, cibles, cadrage, accessibilité et fallback.
- [Une composition native proposée](NATIVE_COMPOSITION_PROPOSED.md) : croquis, inventaire de chaque information et vraies sources ; ce document n'est pas un écran livré.
- [Rapport de préparation](REPORT.md) : options, preuves, incompatibilités et manques exacts.
- [Delta OpenSpec](../../../openspec/changes/asset-consumer-01/proposal.md).

## Autorités et histoire conservées

La référence canonique `auren.mannequin.canonical.v1` version `1.0.0` est un pack de cinq vues générées par l'opérateur avec Midjourney, approuvées le 29 octobre. Les rasters sont conservés hors du dépôt public et identifiés par SHA256. Leurs droits d'usage sont **déclarés complets par l'opérateur** ; la revue juridique a été waived-by-operator, sans clearance professionnelle revendiquée. Ce fait ne prouve pas les droits d'un futur matériel, d'une dérivation ou d'un nouveau master.

Le [README source](../../../design/auren/source/mannequin/README.md), le [registre](../../../design/auren/source/mannequin/auren_mannequin_v1_source.yaml), le [manifest](../../../design/auren/AUREN_VISUAL_ASSET_MANIFEST.md) et la [provenance](../../../design/auren/AUREN_ASSET_PROVENANCE.md) ne livrent aucune reconstruction vectorielle : `vector-reconstruction-required`, `runtime_authorization: blocked`, revue anatomique professionnelle `not-claimed`. Aucune image n'a été inspectée ou reçue dans cette passe ; les cinq références ne sont jamais réputées assets finaux.

Le [Backbone §8.4](../../strategy/AUREN_VISUAL_BACKBONE.md#84-roadmap-da--amendée-par-lopérateur-le-2026-10-25-supersède-lordre-du-83) conserve la décision du 31 octobre : reconstruction précédente rejetée, mannequin sorti du critical path ; DA-05.1 est depuis **l'écran d'exécution sans mannequin**, accepté sous `EXECUTION-SCREEN-V1`, et DA-01 est déjà passé. La voie indépendante reprise le 5 novembre est préparée ici sous le nouvel identifiant ASSET-CONSUMER-01. Aucun gate historique n'est rouvert, aucune approbation DA-05.1 n'est transférée au nouveau couple START/END.

## Frontières de sens

Le mannequin montre un geste illustré ; BodyMap localise une zone fonctionnelle ; Muscle Focus porte des planches régionales gouvernées. Les silhouettes et licences ne sont pas interchangeables. Une illustration n'est ni une instruction applicable au modèle réel, ni une validation de technique, de sécurité, d'anatomie, d'activation, d'EMG ou d'effet.

Les sept calibrations sont `leg-extensions-assises`, `chest-press-machine`, `rowing-chest-supported`, `romanian-deadlift-halteres`, `tirage-poulie-haute-prise-neutre`, `elevations-laterales-machine`, `releves-mollets-debout-machine`. Ce ne sont pas les sept exercices historiques Push A listés dans la matrice. Smith incliné ne fait pas partie de ces calibrations.

## Non-goals

Aucun code, UI, image, SVG, génération, reconstruction, activation, nouvelle source anatomique, recherche externe, contrat SCI, mapping, seuil, poids, incrément, durée, baseline ou source canonique modifiés. Aucun commit, push ou PR dans cette passe. La proposition reste à revoir avant tout GO BUILD distinct ; G1 puis vrais pixels iOS/Android et revues d'assets restent requis avant intégration.
