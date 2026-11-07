# SCI-P02-CALIBRATION-TIME-01 — réalisation isolée

6 novembre 2026. **Build autorisé, producteur isolé ; NOT_ADMITTED / NOT_SERVED / READY_NOT_PRODUCED.** L'opérateur a répondu « Valider le build isolé proposé ». Le GO autorise la réalisation et sa livraison sous GOV-MERGE-01, pas l'activation ou une admission scientifique implicite.

## Règles réalisées

`initial-policy-producer/2.0.0` compose les références figées du producteur, de l'admission partielle, de la curation et du pull. La politique de travail est `initial-hypertrophy-policy/0.3.0-proposed`. Les37sources antérieures et les11sorties du producteur v1 restent inchangées ; le registre effectif successeur possède ses propres digests/version. Aucun appel v2 n'est réécrit en v1 pour contourner une validation d'engine.

La calibration rejoue un snapshot sourcé par propriétaire/exercice/appareil/réalisation/côté, avec cinq états internes. Familiarisation confirmée, tentative comparable achevée, signaux technique/gêne connus, plage de répétitions applicable et acceptation actuelle sont nécessaires pour le seul résultat opérationnel CALIBRATED : **réglage observé à réessayer, pas vrai RIR, charge optimale ou aptitude médicale**. RIR facultatif, confiance LOW/UNKNOWN ; pas d'ajustement kg, ratio corporel, transfert ou incrément inventé. Échec/préoccupation bloque l'épisode ; aucune politique de reprise après préoccupation n'est admise. Les réglages non représentables en masse externe restent tels quels, sans conversion en kg.

Le temps utilise travail, repos, préparation/calibration et opérations sourcés, leur couverture et structure ; union d'horloges comparables pour ne pas compter deux fois installation/repos. Historique, moyenne d'étude ou label VALIDATED_MODEL ne prouvent aucune borne prédictive individuelle. Les quatre ordinaux restent conditionnels. Même LIKELY_FITS expérimental laisse Duration UNKNOWN et le plan indisponible. Aucun temps universel par répétition/transition, réduction du repos ou suppression d'intention ne force une réussite. Une contrainte temporelle porte sur cette configuration seulement.

Le producteur affecte réellement les sept intentions et appelle calibration/temps par séance. Préférence de contexte : confirmation courante, puis absence de matériel requise selon référence canonique, puis inconnu ; égalité départagée par ID, sans classement biologique. Les souhaits musculaires ne sont pas des faiblesses analysées. L'inventaire n'est pas imposé, anthropométrie inconnue non bloquante ; contexte inconnu reste inconnu. Le rôle G17 conditionnel reste qualitatif et lié à sa réalisation, sans fraction d'hypertrophie ou réécriture historique. Le diagnostic n'agrège pas de crédit numérique d'exposition ; sa future admission reste explicite.

## Artefacts et reproduction

- `EvaluationRequest` / `EvaluationResult` et deux schémas versionnés : enveloppe de recherche, avec recommandation SCI v1 validée à l'intérieur ; aucun nouveau transport mobile servi.
- Douze cas : novice, retour avec observations synthétiques, matériel inconnu, temps limité, fréquence3, G17 qualifié/non qualifié, verticals retenus exclus, calibration en cours, données manquantes/conflictuelles et contexte conflictuel. Les entrées sont SYNTHETIC ; les sorties viennent du **vrai producteur**, non de JSON READY attendu.
- `python -m tools.science_initial_policy.v2_fixtures` vérifie cas/schémas/manifest ; `--write` régénère pour revue. Le chiffre40kg et les intervalles10s sont des faits de test explicitement synthétiques, jamais des prescriptions initiales ou constantes temporelles.
- `verify_evaluation` recalcule toute la décision avec son bundle figé ; empreinte complète des observations en plus du fingerprint SCI v1. Les timings lient prescription, identité/réalisation, contexte et état de calibration ; changer d'appareil ou de préparation invalide le périmètre même à kg identique. Un côté isolé n'alimente pas un slot bilatéral.

Le registre d'admission et celui de reprise sont vides. Aucun endpoint, table applicative, migration, acquisition persistée, composition mobile, contrat visuel, rail E7, donnée E0 ou catalogue source n'est modifié. Les tests ne certifient pas les déclarations d'un client non fiable : futur adaptateur authentifié propriétaire/consentement nécessaire.

## Admission suivante, non activée

Le [paquet d'admission](INITIAL_POLICY_ADMISSION.md) distingue preuves disponibles et conditions encore absentes. Le premier plan réellement utilisable et le démarrage d'une séance possédée restent bloqués. FirstPlanClient demeure défensif et NOT_SERVED ; aucun READY synthétique n'est branché en production. La sortie de ce spike n'est pas une recette MOB03, une acceptation globale ou un GO déploiement.

## Vérification et livraison

Les preuves locales, revues distinctes, SHA de publication, CI du HEAD, merge et contrôle canonique seront consignés après exécution dans le reçu de PR et le closeout ; aucune réussite distante n'est anticipée ici.

## Revues et décisions de réalisation

Revues fraîches distinctes : scientifique et code, sans réécriture par leurs agents. Trois Important acceptés puis corrigés en un passage RED→GREEN : G17 depuis contexte complet/direct/disponible, ordre repos entre séries en horloge commune, validation récursive de modèles imbriqués (charge négative/unité non supportée/non-fini). Le rejeu temporel invalide aussi les snapshots d'appareil/préparation périmés. Pas de nouvelle admission scientifique déduite de ces corrections.

Trois Minor différés : ancien historique seul étiqueté en cours plutôt qu'à calibrer (sans charge fournie) ; égalité booléen/nombre tolérée par la comparaison de résultats (le vérificateur retourne néanmoins la décision canonique recalculée) ; borne basse de composante inutilisée quand sa borne haute manque (UNKNOWN conservateur). Aucun de ces constats n'autorise READY ; ils restent des conditions de durcissement du futur adaptateur/admission, pas des réussites maquillées.

Arbitrages de l'agent, avec coût explicite : consommer les enregistrements curation/pull validés sans réécrire l'engine v2 en v1 (risque de divergence d'éligibilité, couvert en tests) ; privilégier confirmation actuelle puis absence de matériel requise puis inconnu (ordre opérationnel à réadmettre, pas supériorité scientifique) ; publier rôles qualitatifs et séries physiques sans crédit d'hypertrophie G17 chiffré (projection future toujours à admettre).

Les limites écartées par les deux reviewers restent assumées comme ouvertes : optimalité/sécurité clinique globale (aucune promesse), validité prédictive du temps (READY bloqué), autorité de reprise après préoccupation (registre vide), authentification/consentement/complétude des sources externes (adaptateur futur), UI/API/persistance/rail/déploiement (hors scope), nouvelles conclusions musculaires/admission des candidats retenus (non rouvertes). Chaque coût est un travail futur explicite. La vérification du HEAD/CI/merge est une responsabilité de livraison de l'agent, pas une approbation implicite des reviewers.

Vérification locale finale après corrections : **431tests backend ciblés/broad passants** (14modules, deux avertissements de dépendances), dont129nouveaux cas de calibration/temps/intégration ; pas de full sweep local ISOLATED. Ruff fichiers neufs, budget264≤548, Bandit ciblé, protocole documentaire et OpenSpec strict8/8 passants. Douze fixtures et deux schémas reproduits,37sources pinées et11sorties v1 préservées ; Gitleaks du diff sans fuite. Les contrôles distants restent à vérifier sur le HEAD publié, pas déduits de ces preuves locales.
