# Tests de contrat et d'admission à implémenter après GO

Spécification d'essais, **aucun nouveau test exécutable ou PASS produit revendiqué**.

| ID | Cas et assertion pertinente |
|---|---|
| B01 | Zéro charge/épisode/expérience : ouverture CALIBRATION_REQUIRED, aucune exigence sept contextes ni poids/taille/sexe |
| B02 | Informations manquantes : aide/collecte permise, pas essai chargé ; famille/salle ne confirme pas appareil |
| B03 | Pilote exact, contexte/instructions compris, sans setting : familiarisation seulement, aucune masse0/minimale ou incrément |
| B04 | INITIATE_TRIAL exige choix réel de setting typé + familiarisation antérieure et vraie autorité ; INITIATE_FAMILIARIZATION est séparé ; RECORD_TRIAL seul n’autorise jamais un essai |
| B05 | Arrêt USER_STOPPED/TIME_LIMIT, completed=False/successful=null, qualité ACCEPTABLE/gêne NO_CONCERN réelles : OBSERVED non qualifié ; reason UNKNOWN ou signaux inconnus => pas nouveau guidage avant clarification |
| B06 | Dernière tentative actuelle acceptable 8–12 + acceptation exacte : QUALIFIED provisoire, RIR inconnu accepté sans devenir mesuré |
| B07 | Parité stricte de toutes préconditions _prescription/_qualified_order : imports anciens, familiarisation après essai, faux contexte/réalisation/côté/unités, acceptation ancienne/horsordre refusés |
| B08 | successful=False/FAILURE/concern/technique ou gêne inconnues : CONCERN_REVIEW ; aucun remapping vers null pour rejouer ; nouvel encounter ou historique filtré ne fait pas disparaître blocage |
| B09 | Refus de complétude/provenance/autorité, retrait/inactivité actuelle : aucun nouveau guidage physique ; lecture de faits et retrait distingués |
| B10 | Même réglage machine/PER_IMPLEMENT/total : sémantiques distinctes, aucune conversion ; types bool/NaN/inf/copie Pydantic altérée rejetés strictement |
| B11 | Cadence/budgets absent pour rencontre : pas de faux manque ; ces manques restent nécessaires au vrai plan |
| B12 | Six autres candidats sans procédure de rencontre admise : aide/collecte ou qualification historique possibles, pas nouvelle permission positive de premier usage |
| B13 | Trajectoire reproductible réelle de l'évaluateur : ouverture→familiarisation→essai→observation→acceptation, tous faits synthétiques étiquetés, pas de génération de faits par le moteur |
| B14 | Pont : épisode du pilote + six autres épisodes explicitement synthétiques, loader/producteur/validateur V3 réels ; un seul épisode ne satisfait pas sept, sept satisfaisant toutes conditions peuvent donner SCIENTIFICALLY_READY/REQUIRES_TIME_ACK, ack exact seulement ensuite ELIGIBLE |
| B15 | Calibration jamais SetLog de travail/credit d'exposition ; observation n'est pas instruction de répétition ; aucun appel API/app/import startup nouveau |
| B16 | Registre de rencontre modifié/retiré/pins divergents ou fausse admission body : refus fermé, ancien binding V3 toujours byte-identique |
| B17 | Rejeu/hashes/manifeste/export des sources et sorties historiques V1/V2/V3, pins SDK inchangés |
| B18 | As_of explicite, tri/identités/digests déterministes, événement divergent ou autre propriétaire refusé ; aucune horloge cachée |

Broad ciblé futur : contrats v1/v2/v3, calibrage/temps, admission/production V3, curation et nouvelle rencontre selon check_scope. Revues scientifique et code indépendantes du builder ; réel CI HEAD/canonique avant closeout. Pas de test clinique, mesure utilisateur, appareil ou disponibilité d'assistance prétendus depuis ces essais. Si une admission de procédure ne résiste pas à la revue SCI, consigner la preuve/décision étroite manquante plutôt que fabriquer un positif.

## Ordre de preuve et autorité

B04/B13 : avant admission, compilation candidate déterministe `DRAFT_EVALUATION_SYNTHETIC_NOT_AUTHORITY`, sans permissions publiques. Le vrai évaluateur reste fermé sans autorité. Après revue SCI favorable du bundle effectif et publication réelle de l'autorité, rejouer via vrai loader/évaluateur/validateur ; aucun registre de test faussement ADMITTED. Le même noyau de calcul est utilisé, sans logique positive parallèle ou mock d'approbation. B14 vérifie séparément le registre V3 réellement admis préexistant ; il n'admet pas la nouvelle rencontre par transitivité.
