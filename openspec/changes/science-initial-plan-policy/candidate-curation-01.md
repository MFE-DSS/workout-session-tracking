# SCI-P02-CANDIDATE-CURATION-01 — overlay scientifique isolé

6 novembre2026. Base7e295c0. Mandat opérateur : curation des40candidats/sept intentions, artefact versionné, résolveur/validateur pur, tests et revues distinctes ; aucun binding producteur, API/UI ni temps positif. SCI-P02-ADMISSION-01 reste fermé ; cette tranche avance le change global encore actif.

## Brainstorming / Options / Risques / Choix retenu

A. Modifier directement catalogue/E0 : affecterait sci_catalogue/sci_exposure, génération (sources_digest), pins de la politique0.1.0 et recommandations historiques. Écarté dans cette tranche.
B. Inventer un score ou combler les UNKNOWN pour satisfaire v1 : rejeté scientifiquement.
C. Overlay versionné, descriptions contextuelles, dispositions explicites et preuves : retenu. Le catalogue, crédit, E0, objets, schémas et producteur1.0.0 restent byte-identiques. La curation conditionnelle d'une intention ne constitue pas une exposition15zones complète ni un plan exécutable.

Inconnus réels : géométrie de rowing, tenue du good morning, posture câble, répartition pec/rear delts en tirage. Pas de résolution automatique en MINOR. Tout changement futur devra avoir un delta d'autorité versionné ; ce format conserve les catégories source et leur incertitude. Deux variantes de presse reçoivent une correction explicite de base de preuve (longitudinal_trial → joint_action_anatomy), car le protocole primaire ne teste ni leurs positions de pieds ni la généralisation « a fortiori » ; aucune catégorie n’est réattribuée. La presse pieds hauts/larges a une généralisation longitudinale non démontrée ; ne pas la promouvoir depuis le nom du mouvement.

## Design retenu

- `docs/science/sci-p02-initial-policy/curation-01/` : sources/hashes avant analyse, overlay `candidates.v1.json`40dispositions, matrice7×15 générée, delta de rôles, delta E0 proposé/non appliqué, preuves/régions et handoff préparation/calibration sans minutes/kg.
- `tools/science_initial_policy/curation.py` : modèles stricts, chargement vérifié par digest, validation contre source canonique et pool épinglés ; résolveur non classant par intention, lecture des confirmations v1, exclusions et limitations, aucun ordre par efficacité ni choix par défaut.
- `tools/science_initial_policy/curation_fixtures.py` : génération déterministe de la matrice et scénarios de résolution sans READY ; aucun import par l'ancien producteur.
- Rôles : source canonique conservée explicitement ; absence de ligne = NONE_KNOWN selon la comptabilité source, pas preuve de zéro biologique. Pour chaque zone, union des classifications par candidat ; aucune somme synthétique ni score esthétique.
- Support décrit par faits du catalogue (banc, Smith, station, autostabilisé) avec origine ; machine_unspecified ne révèle pas stack/plate ou stabilité individuelle. Pas de champ ordinal stability.
- Calibration : classes d'objets/résistances effectivement spécifiés ; machine/câble non spécifié reste à confirmer. Répétitions atteignables UNCONFIRMED, notamment poids du corps. Latéralité conservée, pas de transfert de charge.
- Préparation : contexte/setup + calibration ; familiarisation conditionnée à une exécution non familière. Aucun nombre de séries d'échauffement ni durée nouvelle.
- Résolution : lit FirstPlanRequest v1 pour identité/provenance/contexte, sans exiger anthropométrie. Admission scientifique conditionnelle séparée de compatibilité et de l'autorisation d'exécuter ; `execution_ready=false` et `ready_fixture=NOT_PRODUCED`. Confirmation matérielle ne prouve ni calibration ni tolérance. Conflit de confirmations → UNKNOWN/revue ; limitation personnelle → revue, pas diagnostic. Aucun inventaire ou TTL.

## Plan inline et focus de revue

1. Recherche primaire des ancres demandées ; revue par candidat/intent, E0 existant prioritaire. Nouvelles preuves restent delta E0 compatible explicite, pas second registre servi.
2. Tests RED des frontières (UNKNOWN, EMG-only, identité/pool immuables, variantes/régions, objet≠disponibilité, aucun score/charge/READY, conflit/limitations, CATALOG_GAP et latéralité) ; implémentation minimale GREEN.
3. Artefact40dispositions et descriptions vérifiées ; matrice7×15, fixtures, preuves et rapport. Toute admission reste conditionnelle et non servie.
4. Scope puis broad scientifique, statique/sécurité/protocole/OpenSpec ; revue scientifique fraîche distincte du code ; corrections dans ce périmètre ; publication et merge sous GO permanent après readiness.
5. Closeout borné de cette opération ; pas d'archive du change global, pas de GO BUILD runtime implicite.

Focus : jugement d'admission ≠ choix par défaut ; UNKNOWN ≠ absent ; mode machine ≠ dispositif de résistance connu ; fait régional limité à la configuration étudiée ; traces historiques inchangées ; aucune donnée utilisateur manquante convertie en fait.
