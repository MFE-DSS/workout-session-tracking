# PLAN-CAL-01 — contrat consommateur contrôlé

9novembre2026. Implémentation locale, publication/CI/pixels suivis dans DELIVERY et le receipt. Aucun GO d'activation ou de déploiement fourni par ce document.

## Versions et compatibilité

- Runtime `first-session-runtime/3.0.0`, rencontre `first-calibration-encounter/1.0.0`, request/recommendationV3 et exécutionV3 inchangés.
- Inventaire privé nouveau `plan-calibration-inventory/2.0.0`, annoncé explicitement et réémis dans `X-Auren-Calibration-Inventory`. Packaging conserve son format1.0.0 ; worker fixe v2 choisi par métadonnée attestée, pas un chemin caller.
- L'absence de ce header reste le chemin historique du pilote, pas une négociation implicite des six rencontres. Inventaire inconnu/non servi :406. V1 firstPlan.ts/firstPlan.contract.json et leurs pins ne sont pas remplacés.
- Les anciennes données C3 brutes et replays restent lisibles ; elles ne constituent pas une qualification guidée nouvelle sous inventaire2. Il faut acquérir la rencontre réellement applicable, sans réécrire les faits/hashes historiques.

## Autorité et acquisition

Builder : `tools.plan_calibration_runtime_bundle.build_bundle`, dans un répertoire nouveau/immuable. Il préserve le builder historique et ferme les sources de la publication SCI livrée. Ne pas importer le module d'artefacts, utiliser compile_candidate comme fallback ou recopier un payload positif.

Worker : `app.services.plan_v3.science_worker_v2` appelle les vrais `load_authority/evaluate/validate_result` des six extensions ; pilote et V3 utilisent leur worker historique attesté. Les flags runtime/autorité opérationnelle courante restent nécessaires même si les sources SCI sont admises.

`CalibrationV1Client.open/read/record/select` et `FirstUseV3Controller` utilisent le ledger propriétaire existant. La sélection ajoute `CALIBRATION_ENCOUNTER_SELECTED` via la route observations existante ; lecture seule ne sélectionne rien. L'owner vient de l'auth. Le contexte lie canonical_exercise_id/realization_ref/context_ref/equipment_ref/side/load_semantics, puis notice/setup applicables, choix disponible, contexte confirmé, familiarisation exacte, essai et acceptation exacts. Référence de notice et déclarations ne prouvent pas matériellement l'appareil : acquisition réelle et conservation de leur provenance restent nécessaires.

Cinq profils MACHINE_DISPLAY_KG et RDL PER_IMPLEMENT, bilatéraux exacts ; pas de transfert entre appareils, prises, côtés ou unités. Poids/taille/expérience/inventaire global facultatifs et UNKNOWN conservé. Ni charge à froid, ni incrément générique, ni travail hypertrophie déduit d'une rencontre.

## États et reprise

| Porteur | Sens exploitable |
|---|---|
| progress + provenance du motif | Faits historiques possédés ; pas permission actuelle |
| result + allowed_actions + authority/generation | Décision SCI recomputée applicable à la lecture courante, limitée par le serveur |
| result null / absence d'autorité | Aucune nouvelle consigne physique ; faits lisibles/enregistrables |
| OBSERVED | Examiner l'essai ou demander explicitement un réessai selon permissions, pas auto-retry |
| QUALIFIED | Réglage observé provisoire accepté, confianceLOW ; à réessayer, jamais optimum |
| CONCERN_REVIEW/WITHDRAWN | Aucune nouvelle consigne ; nouvelle identité de contexte ne purge pas l'histoire |
| pending/unknown local | Même commande/identité à réconcilier ; pas un refus ou succès inventé |

Le brouillon contient owner/encounter/draft_ref, phase, réglage choisi et réglage réellement utilisé séparés, reps/complétion/succès/qualité/gêne/motif/date/heure. Un reçu exact après réponse perdue ferme le formulaire correspondant ; sauvegarde retardée ne le rouvre pas. CompteA/B, révision auth, séquence d'interaction et sources empêchent un résultat tardif de réactiver des instructions anciennes.

## Handoff vers la séance existante

Projection du snapshot : sélectionner par candidat, revalider les rencontres via vrais SCI, inclure seulement leurs épisodes actuels qualifiés et conserver toute l'histoire de refus/préoccupation. Construire le lieu après cette projection ; conflit reste UNKNOWN. Capture factuelle sans autorité ne crée aucune admission.

Le snapshot propriétaire et les empreintes V3 canoniques restent les entrées. Runtime/inventaire/package/génération doivent encore correspondre au moment de evaluate/ack/start/applicability. Sept preuves applicables du scénario limité → vrai V3/validate_admitted_exchange_v3 → SCIENTIFICALLY_READY, UNKNOWN/BUDGET_UNCERTAIN et REQUIRES_TIME_ACK. Seule l'action humaine liée aux empreintes exactes peut produire ELIGIBLE. Aucun tempsSUPPORTED ou promesse d'achever.

Commande de première séance existante : clé/corps durables, idempotence, reçu CREATED et GET/handoff du même session_id après perte de réponse. Journal natif et identité canonique d'exercice/intention préservés. Calibration n'est pas comptée comme travail ; RDL par haltère et masse machine affichée ne deviennent pas weight_kg total.

## Erreurs et dépendances

406 de contrat/inventaire absent ou incompatible ;409 de révision/idempotence ;404 propriétaire inconnu/étranger ; refus métier et manque SCI explicites ;503 producteur/autorité/runtime indisponible ; timeout reste transport inconnu. Ne pas remplacer par une MISSION historique ou une fixture.

La preuve HTTP nouvelle couvre les sept rencontres et les gates réelles. DATA/copies/consentement/effacement, activation d'autorité/runtime et recette de release Android/iPhone restent distincts. Les surfaces de proposition/ack/exécution déjà acceptées sont réutilisées ; les pixels de cette acquisition ont été explicitement acceptés, sans valoir recette physique.
