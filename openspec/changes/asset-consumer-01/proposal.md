# Proposal — ASSET-CONSUMER-01

## Why

La voie assets indépendante du recadrage du 5 novembre exige un consommateur natif pilote avant la série Push A. Le pack mannequin accepté est une référence, sans master vectoriel exploitable ni autorisation runtime ; aucun écran autonome de fiche d'exercice ne le consomme aujourd'hui. Spécifier la jonction permet de nommer les manques sans inventer des assets ou des données.

## What Changes

- Package SPEC/readiness `docs/assets/asset-consumer-01/` : matrice des cinq références, du couple Smith START/END, des sept Push A historiques et des sept calibrations distinctes.
- Une seule composition de fiche native, **PROPOSED / G1_PENDING / PIXELS_NOT_RECEIVED**, et inventaire des vraies sources de chaque information.
- Contrat documentaire d'identité, provenance, cadrage, accessibilité et fallback ; réception des assets et build restent futurs.
- Ordre conservé : mannequin → Smith incliné → fiche pilote → sept Push A. Les étapes suivantes ne sont pas ouvertes.

## Capabilities

### New Capabilities

- `mobile/exercise-asset-consumer` : contrat proposé de consommation d'illustrations exactes, sans activation.

### Modified Capabilities

Aucune. `EXECUTION-SCREEN-V1` et les contrats SCI existants restent intacts. Le DA-05.1 historique du 31 octobre demeure l'exécution sans mannequin ; aucun gate déjà accepté n'est rouvert.

## Non-goals (hors périmètre)

Aucune image, génération, vectorisation, implémentation UI/API, nouvelle source anatomique, donnée SCI, production série, activation ou déploiement. Aucun nouveau GO BUILD, G1 ou pixel reçu par cette documentation.

## Dépendances bloquantes

Master vectoriel canonique et articulation validés ; sources/droits et géométrie du matériel Smith ; identité/réalisation et instructions applicables ; paire START/END cohérente ; réception des revues produit/technique/a11y/licence/mobile ; choix G1 opérateur et exposition des vrais rendus avant commit UI. Les instructions appareil restent acquises auprès des sources applicables et jamais extraites d'une image.

Primitives à réutiliser : tokens AUREN, Frame C, Recessed Window, BodyMap fonctionnel MIT et contrôles natifs existants ; aucun redessin de primitive LOCKED. La nouvelle composition et le slot illustré exigent leurs propres revues opérateur.

## Impact

Documentation et delta seulement. Aucun fichier client, serveur, données, design source ou baseline changé. Une PR future par change ; application uniquement après GO BUILD borné.
