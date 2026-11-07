# Calibration/time01 — spécification de tests avant GO BUILD

**TEST_DESIGN_ONLY / NOT_IMPLEMENTED / NO_NEW_TEST_RESULT.** Ces cas sont à coder en RED après revue du design, puis implémenter en GREEN. Les valeurs d'essai représentent des faits synthétiques étiquetés, pas de nouveaux paramètres scientifiques. Ne pas confondre un test arithmétique positif avec un modèle de durée admis ou une fixture READY réelle.

## Contrats, provenance et replay

| ID | Cas | Oracle attendu |
|---|---|---|
| C01 | Même request/snapshot/bundle, deux évaluations | Sortie et deux empreintes identiques, aucune mutation des entrées |
| C02 | Événements réordonnés mais séquences valides identiques | Canonicalisation/replay identiques ; égalité d'ordre ambiguë refusée |
| C03 | Même event_id et payload répété | Déduplication idempotente, même digest ; payload divergent/sequence changée refusé |
| C04 | JSON sauvegardé puis relu par le vrai modèle | Mêmes transitions/empreintes, pas de nouvelle tentative créée ; test de fichier, aucune persistance app prétendue |
| C05 | Sujet A/B, contexte/appareil/côté/charge total-par-haltère différents | Aucun historique/calibrage inter-propriétaire ou contexte ; incompatibilité structurée/rejet de l'enveloppe |
| C06 | NaN/inf/bool comme nombre, unité inconnue, reps négatives, date future, seq invalide | Erreur de validation explicite ; pas correction silencieuse ou zéro |
| C07 | Observation modifiée avec même v1 request | request_fingerprint v1 inchangé, evaluation_fingerprint changé ; résultat ancien refusé par verify_evaluation |
| C08 | Engine/source/bundle/fingerprint périmé ou forgé, modèle construit sans validation | Refus ; libellé APPROVED ou clone muté ne contourne pas les digests/références |

## Calibration : vraie fonction de transition

| ID | Cas | Oracle attendu |
|---|---|---|
| L01 | Novice, contexte connu, aucun historique | NEEDS_CALIBRATION, charge null, aucun kg tiré de taille/sexe/âge |
| L02 | Anthropométrie/expérience absentes ou différentes, mêmes faits utiles | Même résultat ; pas nouveau manque requis |
| L03 | Appareil/charge disponible inconnus, ou seulement noms/slots E1…E7 | INSUFFICIENT_DATA/context pending ; aucune supposition de salle complète |
| L04 | Indisponibilité réelle confirmée, même si ancien essai accepté | UNAVAILABLE courant, ancien fait conservé |
| L05 | Familiarisation seulement démarrée, puis confirmée ; tentative non complétée | CALIBRATION_IN_PROGRESS ; confirmation nécessaire avant positif, aucun faux HISTORY_SUPPORTED |
| L06 | Charge disponible déclarée sans tentative observée | Non calibré ; pas confusion déclaration/performance |
| L07 | Tentative observée comparable, familiarisation confirmée (éventuellement par cette même tentative), reps dans plage, technique/gêne connues acceptables, SETTING_ACCEPTED précis | CALIBRATED opérationnel, réglage exact issu de la tentative citée, pas de double comptage en travail, confiance d'effort séparée ; sans familiarisation positive refusée |
| L08 | RIR absent, puis déclaré ; même réglage/reps | Absence permise comme fait, effort_sufficiency UNKNOWN ; aucune soustraction d'erreur moyenne ni preuve de vrai RIR |
| L09 | Gêne préoccupante, technique incertaine/UNKNOWN requis ou échec, avant/après acceptation ; tentative tardive favorable ; nouvel épisode avec/sans base de revue | Pas de calibration positive dans l'épisode bloqué ; suggestion null ; reprise sans règle/base applicable → INSUFFICIENT_DATA, anciens faits non réutilisés comme qualification ; aucune histoire écrasée |
| L10 | completed=true mais reps absentes ou succès non renseigné | Pas de calibration positive depuis le seul drapeau historique |
| L11 | Ancien exercice comparable et reconfirmation actuelle ; puis même historique sans reconfirmation | Référence traçable utilisable dans le premier cas ; NEEDS_CALIBRATION dans le second, pas TTL arbitraire |
| L12 | Autre exercice/substitution, grip/ROM/appareil/assistance/côté différents | Aucun transfert ou division bilatéral/unilatéral ; pas de conversion de pile en charge effective |
| L13 | Réglage non massique/assistance/poids du corps | Fait conservé dans son unité ; projection load_kg refusée si non représentable, pas0 fictif |
| L14 | Tentative refusée, charge suivante choisie par l'utilisateur | Pas de rampe calculée, nouvel event/source obligatoire ; ancien essai conservé |
| L15 | Correction de fait ou réponses tardives d'un ancien snapshot | Nouvelle évaluation/digest ; aucun résultat neuf attribué à l'ancien snapshot |

## Temps : modèle effectif, pas oracle mocké

| ID | Cas | Oracle attendu |
|---|---|---|
| T01 | Seulement repos connu ; budget supérieur à sa borne | UNKNOWN, pas prédiction positive |
| T02 | Budget égal/inférieur au rest-floor et travail positif | LIKELY_EXCEEDS pour cette configuration ; aucun repos réduit |
| T03 | Intervalles synthétiques complets/disjoints, borne haute≤budget | LIKELY_FITS conditionnel dans le diagnostic ; nature de base TEST_ONLY explicite ; aucune admission ou READY |
| T04 | Basse≤budget<haute | BORDERLINE ; égalité à la borne haute tient sous les hypothèses, pas marge inventée |
| T05 | Borne basse>budget | LIKELY_EXCEEDS ; composants responsables et portée conservés |
| T06 | Préparation/calibration/setup/attente essentiel inconnu ou base non applicable | UNKNOWN même si travail+repos semblent courts |
| T07 | Setup observé pendant repos avec même horloge | Union des intervalles, une seule comptabilisation ; bornes désordonnées/horloges non comparables refusées ou UNKNOWN explicite |
| T08 | Structure superset/non supportée, tentative de moyenne/multiplicateur d'étude | UNKNOWN de total, pas réduction automatique de37% ou constante de transition |
| T09 | Durée globale d'une séance passée ou completed_at successifs seulement | Historique réel conservé, aucune décomposition/borne prédictive fabriquée |
| T10 | Min/max observés sans validation de prédiction ; hypothèses produit non admises | Pas de future borne admise ; séparer diagnostic expérimental et Duration v1 UNKNOWN |
| T11 | Repos manquant, un set, cas unilatéral/côtés, travail préparatoire | Aucun repos0 inventé ni doublage automatique ; couverture explicite ou UNKNOWN |
| T12 | Temps insuffisant pour configuration, autres configurations non évaluées | Blocage structuré ; pas de NO_FEASIBLE_PLAN global, retrait d'intention ou compression de repos |
| T13 | Modèle réellement admis fourni par registre versionné et contexte applicable | Projection Duration ESTIMATED possible si toutes bases réelles sont prouvées ; tester l'absence de cette autorité par défaut |

## Producteur réel et cas Phase D

| ID | Entrée du vrai produce_v2 | Vérification intégrée |
|---|---|---|
| P01 | Novice sans historique | Allocation/diagnostics réels, calibration pending, NOT_ADMITTED ; pas de READY ou kg artificiel |
| P02 | Retour avec exercice/historique comparable et confirmation actuelle | Référence d'observation exacte, incertitude maintenue et évaluation de temps réelle |
| P03 | Matériel UNKNOWN, confirmations contradictoires ou autre contexte | UNKNOWN/revue/rejet selon contrat ; pas d'inventaire imposé ni sélection réputée complète |
| P04 | Temps limité et grand budget | Contrainte de configuration ou UNKNOWN selon bases ; grand budget ne débloque pas l'admission |
| P05 | Cadences2/3 puis1/4/5/7 | Répartition du périmètre D1 conservée ; hors champ connu ≠ manque artificiel ; toutes sessions évaluées |
| P06 | Blueprint requis manquant/conflit et optional inutilisé absent | Priorité v1 exacte, empreinte/used_fields canoniques ; aucune métrique corporelle requise |
| P07 | G17 qualifié puis simple AVAILABLE sans réalisation confirmée | Projection conditionnelle seulement dans premier cas ; delta non appliqué à l'historique ; aucun nouvel UNKNOWN rempli |
| P08 | Quatre autres verticaux retenus ; aucun candidat valide ; seul G17 exclu | Pas de réadmission des held, fallback row/pullover ou gagnant inventé ; CATALOG_GAP honnête |
| P09 | Calibration en cours/failed et temps incomplet | Diagnostics incorporés à la sortie du vrai successeur, pas un rapport séparé ou mock READY |
| P10 | Tentative de politique/reference TEST_ONLY ou JSON APPROVED | Blocage ; validate_exchange ne reçoit aucune fausse autorité de production |
| P11 | Même cas sous v1 et v2 ; vieux bundle/fixtures/pull/E0 | Onze sorties v1 et hashes historiques identiques ; ancien snapshot refusant nouveau rôle/engine |
| P12 | Tous diagnostics ingénierie « bons » mais temps/selection non admis ; modes OBSERVED_REFERENCE et BOOTSTRAP_PROTOCOL | POLICY_UNAVAILABLE par défaut ; effort inconnu ≠ manque universel, bootstrap ne contourne aucune gate ; épisode actif/problème et temps non soutenu bloquent selon DESIGN§5 ; NOT_SERVED / READY_NOT_PRODUCED |
| P13 | Éventuelle admission complète réellement obtenue après revues | Seulement alors générer une première fixture READY par le vrai producteur et vérifier validate_exchange ; sinon cas BLOCKED documenté, pas test d'approbation fictive |

## Vérification après apply autorisé

Avant tests locaux : check_scope. Tier attendu isolated/shared selon le diff réel ; Ruff neufs, budget, Bandit, protocole, ciblés puis broad scientifique couvrant v1/v2/contrats/curation/pull/exposition/slots et consommateurs potentiels selon verdict. Aucun full sweep local systématique. Revues scientifique et code distinctes ; Critical/Important corrigés et tests repassés. CI réelle du HEAD final et canonique après merge ; Sonar réel conservé consultatif. Aucun nouveau build, résultat de test fonctionnel, revue de code d'implémentation ou CI de ce spike n'est revendiqué par cette spécification.
