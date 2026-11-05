# SCI-P02-INITIAL-POLICY — décisions et handoff

5 novembre 2026. **Producteur isolé IMPLEMENTED / NOT_SERVED ; politique PROPOSED.** Base5fd18c3291cd93533cf7b1f7ab50862c85a7a205. Branche isolée `spec/sci-p02-initial-policy`, worktree `/private/tmp/auren-sci-p02-initial-policy`. La PR353 et ses fichiers canoniques restent inchangés à0ee7ba3.

## Paquet prêt pour revue

- [Proposition OpenSpec](../../../openspec/changes/science-initial-plan-policy/proposal.md), [design](../../../openspec/changes/science-initial-plan-policy/design.md), [26scénarios de tests](../../../openspec/changes/science-initial-plan-policy/test-specification.md).
- [Audit et sources](EVIDENCE_AND_AUDIT.md) et [preuves statiques/probes/hashes](AUDIT.json).
- Les contrats1.0.0 et leurs8fixtures sont déjà reçus ; aucun nouveau schéma ni moteur servi n'est livré ; le producteur Python isolé et ses tests sont désormais réalisés, sans fixture READY. Les paramètres0.1.0-proposed ne sont pas enregistrés comme approuvés. Le GO BUILD isolé est maintenant reçu : « Valider le build isolé proposé ». Le rapport courant décrit les tests/11sorties réellement générées, sans READY.

## Décisions pour ouvrir un build concret

| ID | Proposition à trancher | Ce que la décision permet / n'établit pas |
|---|---|---|
| D1 | Sous-ensemble initial adultes/non clinique, cadence2ou3 ;7intentions corps entier ; autres cadences à revoir explicitement | Borne le premier producteur ; ne dit pas qu'une autre cadence serait inefficace ou une population inapte |
| D2 | Revoir/admettre ou amender le démarrage2séries/intention,8–12reps,2RIR,90/120s, calibration sans charge déduite | La combinaison est une convention proposée, pas un optimum démontré. Expérience inconnue et précision du RIR restent limites explicites ; acceptation produit ne remplace pas admission scientifique |
| D3 | Curation des candidats/intentions dédiés15zones et règle de confirmation contextuelle sans inventaire ; priorités sans multiplicateur de dose | Clarifier validité/révocation des confirmations et cas sans couverture directe ; aucune salle supposée complète. Les confirmations se font au fil d'une proposition/substitution, pas par un inventaire préalable imposé |
| D4 | Faire produire protocole et bases de durée (préparation/apprentissage, travail, repos, transitions), ou garder un producteur bloqué sur temps | Aucune constante d'overhead choisie pour réussir READY. Un budget75min ne crée pas une borne haute valide à lui seul |
| D5 | GO BUILD distinct sur ce design pour module **pur isolé**, registres dédiés, tests et fixtures réellement générées ; sans API/UI/activation | Autorise implementation/TDD et livraison sous GO permanent après checks. Un modèle temps absent ou règle non admise garde son état bloquant ; aucune obligation de produire un faux READY |

D1/D2/D3 sont des propositions concrètes ; l'opérateur peut approuver le périmètre de build tout en laissant une politique non admise. D4 requiert des éléments réels, pas seulement le mot « approuvé ». D5 ne vaut jamais déploiement ou ouverture d'un moteur médical/adaptatif global.

## Entrées à préparer côté mobile/API, après coordination

| Entrée | État actuel | Nécessité |
|---|---|---|
| Objectif/cadre d'usage et provenance | Contrat v1 ; collecte/éligibilité à confirmer | Requis par profil existant ; ne pas inférer âge/aptitude |
| Cadence | TrainingPreferences et éditeur natif de PR353 | Requis, sans défaut local |
| Budget par séance et réponse sur limitations | Contrat v1, pas nouvelle persistance/API canonique | Requis opérationnels ; ne pas réutiliser durée de template comme temps utilisateur |
| Expérience | Contrat, pas champ utilisateur canonique ajouté | Facultative selon démarrage admis ; inconnue explicitée |
| Taille/poids daté | Domaine existant ; GET poids PR353 | Facultatifs pour ce dosage ; consentement et source conservés |
| Priorités | PR353, souhait facultatif | Pas de diagnostic ni de poids arbitraire |
| Confirmation exercice/contexte | Contrat v1 ; comportement runtime futur à définir | Permet compatibilité sans inventaire ; UNKNOWN→revue |

## Protocole direct vers FirstPlanClient

Le client réel lu dans `/private/tmp/auren-mob03-account-core` à0ee7ba3 expose FirstPlanProducer.read/verify. Requête d'entrée `{request, fingerprint}` ; enveloppe attendue `{owner_id, kind:'result', result:<FirstPlanRecommendation v1>}`. Le futur adaptateur ajoute ownership, auth/consentement et génération ; le producteur scientifique pur ne reçoit ni token ni compte SQL.

`.verify` doit vérifier decision_fingerprint et validate_exchange avec le vrai ReferenceSnapshot/bundle. Une validation JSON ne certifie pas la politique. Les sorties pending/unavailable/rejected de transport ne remplacent pas les statuts scientifiques. Pas de changement de JSON Schema v1 requis par le design actuel, ni de nouveau statut LOW.

Quand le producteur est livré : handoff requête/sortie générées, engine/policy versions, hashes de bundle/catalogue, journal de tests et limites ; test consommateur coordonné sur une fixture de producteur réel. La fixture READY synthétique de test mobile actuelle reste SYNTHETIC_TEST_ONLY_NOT_SERVED et ne devient pas la fixture scientifique officielle.

## Table des dépendances restantes

| Dépendance | Responsable | Statut / résultat honnête tant que manque |
|---|---|---|
| GO BUILD isolé / admission | Opérateur, scientifique/architecte pour admission | Build reçu et réalisé ; admission scientifique reste distincte |
| Dose/effort et calibration initiale | Science, après périmètre accepté | POLICY_UNAVAILABLE ; pas d'emprunt automatique du catalogue |
| Intentions/candidats/bornes15zones | Science/catalogue dédié | Revue de cohérence ; CATALOG_GAP si trou |
| Temps avec bases et applicabilité | Science + architecture, protocole explicite | POLICY_UNAVAILABLE tant que temps non admis ; ensuite TIME_UNCERTAIN si contexte non couvert ; aucun READY |
| Snapshot réel et nouveaux inputs | MOB-03/API dans son OpenSpec | Non persistés par cette tranche ; pas de données LAB promues |
| Adaptateur servi et démarrage séance | MOB-03/MOB-04 après contrats/tests | NOT_SERVED ; producteur pur ne signifie pas parcours livré |
| Données/consentement/recettes/déploiement | Responsables de MOB-03 | Gates indépendantes, aucune clôture implicite |

Aucun message externe envoyé ; ce dossier constitue le passage de relais. Aucune modification concurrente de shared API/schema. Le registre n'ouvre pas le build par son seul ajout.
