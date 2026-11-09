# Rapport ASSET-CONSUMER-01 — SPEC/readiness

9 novembre 2026. Base `fe9f6e9beb585a271ae2c2726e338359057b9f58`, worktree `/private/tmp/auren-asset-consumer-01`, branche `docs/asset-consumer-01`.
**Verdict : préparation PROPOSED ; NO_GO_BUILD / G1_PENDING / PIXELS_NOT_RECEIVED / NOT_ACTIVATED.** Aucun commit/push/PR.

## Brainstorming / Options / Risques / Choix retenu

1. Catalogue complet avant écran : donne du volume sans vérifier la consommation, contredit la séquence du5novembre. Écarté.
2. Introduire la paire directement dans l'exécution LOCKED : modifierait une composition acceptée, pourrait diluer son instrument et confondre illustration/localisation. Écarté pour cette proposition.
3. **Fiche secondaire native pilote**, une fenêtre et un sélecteur Début/Fin : cadre lisible, couple cohérent éprouvé avant série, retour au même appelant. **Choix proposé par l'agent**, aucune acceptation opérateur attribuée.

Le croquis est un artefact de SPEC, pas une UI ou des pixels. Aucune implémentation n'a précédé ce choix. Risques : master absent, droits dérivés non établis, compatibilité appareil/prise non acquise, vocabulaire SCI non identique au BodyMap, source d'instructions Smith absente. La matrice et les fallbacks empêchent de les masquer.

## Constat et provenance

| Objet inspecté | Fait établi sur disque | Conséquence |
|---|---|---|
| Mannequin V1 | README/YAML :5références1024² RGB, identités/SHA256, référence acceptée29octobre, génération Midjourney, droits déclarés complets par l'opérateur, revue légale waived, pas revue anatomique professionnelle | Pas d'asset final/vectoriel reçu ; runtime blocked ; aucun raster copié/inspecté ici |
| Manifest et provenance | Schéma du manifest impose statut/revues/licence/accessibilité ; origine mannequin déclarée, master NOT YET PRODUCED | IDs de la matrice restent propositions ; aucun manifest canonique modifié ni entrée approved fabriquée |
| Direction actuelle | Recadrage5novembre et chemin critique adoptent mannequin→Smith START/END→fiche pilote→7PushA | Voie indépendante ; pas de blocage nouveau de PLAN/DATA/RELEASE |
| Histoire DA | Backbone31octobre : reconstruction rejetée, DA-05.1 redéfini en exécution sans mannequin ; DA-01 passé ; VisualContract§24 LOCKED | Aucun gate historique rouvert, nouvelle piste ASSET-CONSUMER-01, pas de réception START/END déduite des acceptations antérieures |
| Push A | `reference_split.json`2026-09-28.v15,7codesE1–E7 ; E1Smith, E2ChestPress, E3Dips, E4ShoulderPress neutre, E5Latérales câble derrière dos, E6Arrière épaule câble, E7Triceps corde | Catalogue historique distinct du planSCI V3 et des calibrations ; slugs absents conservés UNKNOWN |
| Calibrations | SélectionV3 pinée7réalisations ; pilote+6extensions admis avec limites ; consommateur PLAN2 contrôlé | Six MACHINE_DISPLAY_KG (pilote inclus) + RDL PER_IMPLEMENT ; pas Smith ; aucune activation réelle inférée |
| BodyMap natif | `bodyGeometry.ts` : react-native-body-highlighter3.2.0 MIT vendorisé ; chemins intouchés et crédit central | C'est le corps actuellement dessiné ; onze zones et caméras gouvernées ; pas une image du geste |
| Master BodyMap design | BodyParts3D/Servier, CC-BY-4.0, sources/licences historiques conservées ; intégration interne sous contraintes | Source de conception, pas un remplacement du runtime MIT dans ce dossier |
| Muscle Focus | Registre0.2.0,3planches chest/shoulders/posterior, BodyParts3D4.0 CC-BY-4.0 ; revue synthétique, pas clearance professionnelle | Pas de START/END ni animation ; partition pectorale non acceptée, pas `delt_ant` métier ; aucune nouvelle source anatomique cherchée |
| Surfaces natives | ExecutionScreenV1, PlanV3ExecutionScreen, journal SessionSetDetails et acquisition PlanV3FirstUseScreen réels ; PROGRAMMES est encore PendingSpace vers/library | Pas de fiche autonome, DTOmédia ou notice Smith disponibles ; nouvelle composition seulement proposée |

Les sources sont inventoriées avec SHA256 dans `/private/tmp/auren-asset-consumer-01-review-evidence/source-inventory.json`. Les fichiers d'inventaire/preuves sont hors dépôt, ne servent jamais de source runtime. Les exports/fixtures SCI/lab ne sont pas utilisés comme autorité d'une fiche.

## Contrats incompatibles et limites conservés

- `PlanExercise` V1 est lié à la séance et au nom exécuté, pas à `realization_ref/equipment_ref`. Un média exact exige un contrat de liaison futur ; aucune résolution approximative par nom.
- V3 porte exercice/réalisation/contexte/côté/unité ; son identité n'ajoute pas un média, une disponibilité matérielle ou une notice. Le worker2 décrit le pilote en MACHINE_DISPLAY_KG dans l'inventaire contrôlé ; cela ne réécrit pas le bootstrap historique, qui accepte aussi d'autres sémantiques sous ses propres conditions.
- P:E2 `Chest Press machine` et C:`chest-press-machine` se ressemblent ; l'équivalence dépend de la réalisation réelle. Latérales câble derrière le dos et machine ne se confondent pas. Smith incliné n'est pas un membre des7calibrations.
- Un rôle SCI (`anterior_delts`, `rear_delts`, etc.) n'est pas automatiquement un code des11zones BodyMap. Seule la sortie canonique destinée à la localisation peut être présentée ; aucun alias manuel.
- Le repère statique et les planches Muscle Focus n'instruisent pas le geste, ne qualifient pas un réglage et ne montrent ni recrutement, contraction, activation ou efficacité.
- La note historique30° ne certifie ni machine réelle, ni appui, ni amplitude ou instructions actuelles. Aucune consigne physique nouvelle n'est écrite ici.

## Manques exacts avant build / réception

| Dépendance | Pièce attendue | État actuel |
|---|---|---|
| Master mannequin | Reconstruction vectorielle fidèle des5vues, masses/IDs11zones, pivots, fichier/version/hash et revues applicables | NOT YET PRODUCED ; référence seulement |
| Matériel Smith | Source/fichier/version/hash, banc/barre/rails/appuis/verrouillage, modèle ou limites de compatibilité et droits | UNKNOWN / NOT YET PRODUCED |
| Paire Smith | START+END de même version/caméra/échelle/équipement, cohérence contacts/prise/appuis, cadre commun et budget mesuré | NOT YET PRODUCED / NOT YET REVIEWED |
| Instructions | Source applicable au modèle/réalisation, contenu et provenance consultables, contrat de lecture ; pas simple note ou image | UNKNOWN — MANUAL VERIFICATION REQUIRED |
| Liaison consommateur | Contrat assetID/version↔exercice/réalisation/équipement ; refus d'incompatibilité et fallback | PROPOSED seulement ; aucun DTO/route média livré |
| Produit visuel | Décision G1 sur croquis, puis exposition des vrais pixels iOS/Android, petite largeur/texte130%, comparaison références, acceptation explicite | G1_PENDING / PIXELS_NOT_RECEIVED |
| Accessibilité et mobile | Ordre/labels/non-color cue,44pt, VoiceOver/TalkBack, retour/safe areas, format/résolution/poids/cache | NOT YET REVIEWED, cibles proposées uniquement |
| Provenance/réception | Auteur/outil/dérivés/matériel, droits/attribution, manifest/provenance et revues produit/technique/a11y/licence/mobile ; anatomique si applicable, sans certification professionnelle inventée | NOT YET REVIEWED ; aucun approved |
| Autorisation | GO BUILD borné pour étape concrète suivante ; pas réutilisation de GO PLAN/DA05.1/GOV-MERGE comme nouveau build | NO_GO_BUILD |
| Série | Fiche pilote effectivement consommatrice reçue avant7PushA puis règles série | NOT OPENED |

## Vérification documentaire

Résultats observés :

- `check_scope` : **DOCS**, neuf fichiers ; seul `check_spec_protocol` requis, sweeps/budget/migration légitimement non lancés.
- `check_spec_protocol.py` : **PASS**, exit0 (`strict mode: False`, politique normale du dépôt,35rapports/32specs historiques grandfathered).
- `openspec validate asset-consumer-01 --strict` : **PASS**, exit0, « Change 'asset-consumer-01' is valid ».
- `git diff --check` : exit0 ; liens locaux du package : aucune cible absente.

Le binaire `python` n'est pas présent dans le PATH de ce shell ; les deux scripts prescrits ont été exécutés avec `/Users/martinfeldmann/workout-session-tracking/.venv/bin/python`, sans changer d'environnement ni installer quoi que ce soit. Le RTK.md demandé n'existe pas dans le worktree ; son instruction locale a été lue dans `/Users/martinfeldmann/.claude/RTK.md`.

Preuves : `/private/tmp/auren-asset-consumer-01-review-evidence/{check-scope.txt,check-spec-protocol.txt,openspec-strict.txt,source-inventory.json}`. Aucun test app, rendu ou sweep exécuté pour cette préparation docs. Les succès documentaires ne valent ni GO BUILD, ni réception humaine/assets. Aucune CI distante lancée ou revendiquée, aucun commit/push/PR.

## Périmètre tenu

Quatre documents dans `docs/assets/asset-consumer-01`, quatre Markdown de delta OpenSpec, append au registre. Aucun changement à l'app, SCI, données, CI, manifests, références ou baselines ; aucun achat, recherche externe, image, code produit ou activation. Les points encore ouverts sont conservés tels quels pour la revue parent/opérateur.
