# SCI-P02-INITIAL-POLICY-ADMISSION — tests à réaliser après GO

**DESIGN_ONLY / NO_TEST_CODE / NO_NEW_PASS_CLAIM.** Les probes de REPORT vérifient le système existant ; cette matrice est l'oracle futur d'un apply autorisé. Une fixture synthétique peut tester un refus ou du calcul, jamais conférer l'admission d'un registre.

| ID | Entrée / opération | Oracle obligatoire |
|---|---|---|
| A01 | C1..C6 indépendamment absentes/non admises, inputs suffisants | Pas READY ; gate, version et raison exactes ; pas de nouvelle mesure exigée pour masquer une politique manquante |
| A02 | Adulte non clinique/2–3/limitations explicitement vides, puis 1/4 séances, clinique/inconnu/limitation non prise en charge | Scope exact seulement, hors scope ≠ input artificiellement manquant ; pas de promesse comparative |
| A03 | Dose réelle du bundle : sept intentions × deux séries, cadence2/3 | 14 séries/séance, 28/42 totales ; plage8–12, cible2RIR, repos120/90 depuis politique exacte ; aucun raccourci de repos |
| A04 | Taille/poids/expérience UNKNOWN/WITHHELD sans usage | Pas de manque requis ni poids/sexe inféré ; required_fields reste canonique |
| A05 | Blueprint requis manquant/conflit avec politique absente | Priorité de statut SCI v1 conflit→manque→policy préservée ; mapping runtime futur distinct |
| B01 | Politique JSON APPROVED mais absent du registre admis, référence de test, engine incohérent | Refus ; aucune admission par libellé/schema valide |
| B02 | Same Blueprint + observations changées, même request fingerprint | Empreinte complète d'évaluation changée ; ancien résultat refusé ; aucune dépendance cachée |
| B03 | Engine/policy/source/evidence/catalogue/curation/pull/réalisation/digest changé | Invalidation/rejet explicite, pas de coercition v2 vers v1 ni réécriture des anciens pins |
| B04 | Résultat altéré : False→0, True→1, nombre→bool, int→float selon règle numérique publiée ; NaN/inf/modèle construit invalide | Bool/nombre strictement distincts ; révalidation récursive ; le choix int/float est spécifié avant implémentation ; pas de tolérance Python implicite |
| B05 | Ordre d'events/épisodes/composantes permuté à contenu identique ; doublon idempotent puis divergent | Canonicalisation stable ; séquence/id ambigus refusés, aucune mutation de l'entrée |
| C01 | Anciennes tentatives seules, started_at postérieur, aucun concern ni activité courante | NEEDS_CALIBRATION/null ; aucun label en cours ; historique intact |
| C02 | Familiarisation courante puis tentative/retry/acceptation sourcés | Transitions réelles, nouvel essai ≠ réécriture ; acceptation référence le réglage disponible et la bonne tentative |
| C03 | Ancien réglage comparable reconfirmé et accepté aujourd'hui, puis sans reconfirmation | Réemploi provisoire seulement si toutes conditions acquises ; sinon calibration requise, aucun TTL/rampe |
| C04 | Tentative achevée mais technique/gêne/succès inconnus, ou problème avant/après acceptation | Pas CALIBRATED ; arrêt de suggestion automatique, reprise non admise bloquée |
| C05 | Même tentative avec RIR manquant puis déclaré | Réglage opérationnel distinct ; effort_sufficiency UNKNOWN permis ; aucun RIR vrai inventé |
| C06 | Réglage appareil non massique/assistance/par-haltère/bilatéral/unilatéral | Unité/sémantique conservées ; aucun kg équivalent/transfert/appairage implicite ; READY seulement selon contrat admis applicable |
| D01 | Sept candidats effectifs qualifiés, puis simple AVAILABLE de G17 | Admission liée aux réalisations exactes ; rôle conditionnel G17 seulement en qualifié, jamais coefficient d'hypertrophie mesuré |
| D02 | G17 utilisable et les quatre autres pull retenus non résolus | Ces quatre ne bloquent pas artificiellement ce plan ; ils restent non admis |
| D03 | G17 exclu/indisponible et aucun autre pull admis | CATALOG_GAP réel ; ni réadmission held ni rowing/pullover arbitraire |
| D04 | Confirmation AVAILABLE/UNAVAILABLE contradictoire, autre sujet/appareil/contexte/côté | Blocage/rejet ; pas d'inventaire global requis, pas d'ownership inféré d'un snapshot_id |
| E01 | Draft v2 réel présenté au vrai validateur READY v1 | Refus sur les invariants manquants ; v1 et ses exports restent inchangés |
| E02 | Contrat successeur : quinze déclarations dont UNKNOWN ou NONE_KNOWN | Rapport complet ≠ crédit EXACT ; UNKNOWN n'est pas zéro, aucune croissance estimée ; pas de conversion silencieuse en v1 READY |
| E03 | Calibration bootstrap admise mais temps initial absent | Pas READY ; ne pas exiger charge connue comme substitut à la preuve temporelle |
| E04 | Mode non massique pleinement observé mais prescription v1 NOT_DEFINED | Pas READY v1 ; nouvelle union/version nécessaire avant acceptation opérationnelle |
| T01 | Repos seul, grand budget ; puis budget≤780 s sur l'allocation bilatérale réelle | UNKNOWN de durée dans les deux cas ; réfutation de cette configuration seulement au deuxième, pas NO_FEASIBLE_PLAN global |
| T02 | Données synthétiques complètes/10s, LIKELY_FITS1060 | Arithmétique exacte, Duration UNKNOWN ; pas admission de modèle ni fixture READY autoritaire |
| T03 | Observation historique min/max, moyenne d'étude, label VALIDATED_MODEL sans registre | Pas de borne future admise ; sources/limites exposées |
| T04 | Composante basse connue mais haute absente, structure disjointe applicable | Basse sûre éventuellement utile à réfutation ; aucune haute/Duration/READY inventée |
| T05 | Chevauchement repos/setup même horloge, gap, ordre invalide, appareils/horloges différents | Union sûre seulement sous conditions ; sinon UNKNOWN/rejet. Pas de double compte ni somme de basses chevauchantes |
| T06 | Source temporelle liée à autre prescription/calibration/setting/réalisation/côté | Scope mismatch/invalidation avant projection ; aucune tolérance parce que kg identiques |
| T07 | Modèle ou convention réellement admis, domaine/couverture complets puis composante essentielle retirée | Positif uniquement dans premier cas si haute≤budget et toutes gates réelles satisfaites ; second cas non READY |
| V01 | Anciennes versions/pins/v1/curation/pull/calibration-time rechargés | Rejeux historiques identiques ; ancienne version n'accepte pas nouvelle science par collision d'ID |
| V02 | Politique admise retirée/révoquée avant création de séance | Décision invalidée, handoff PLAN refusé ; ne pas supprimer les faits historiques |
| V03 | Version inconnue du contrat ou sidecar seulement présenté à FirstPlanClient v1 | Refus défensif/NOT_SERVED ; pas de transport implicitement servi |
| R01 | Admission véritable de toutes gates, inputs réels suffisants, vrai producteur et validateur du contrat choisi | Seulement alors générer fixture READY avec SHA/digests/bases/reviewers, résultat reproductible ; sinon marquer BLOCKED, aucun mock autoritaire |

Avant tests d'apply : `python scripts/check_scope.py`, puis minimum du tier réel (ciblés + broad science et consommateurs touchés, intégrité sources/exports, budget/protocole/etc. applicables). Aucun full sweep local pour ce design documentaire. Après code autorisé : vraie CI du HEAD final selon politique, revue code et science distinctes ; les résultats d'ingénierie ne valent pas validation empirique du temps. La commande de rejeu existante `python -m tools.science_initial_policy.v2_fixtures` sans `--write` est disponible pour vérifier les artefacts historiques ; elle n'admet rien.
