# SCI-P02-INITIAL-POLICY — réalisation du producteur isolé

5 novembre 2026. **Producteur implémenté ; politique0.1.0-proposed non admise ; NOT_SERVED.** Engine `initial-policy-producer/1.0.0`, contrats SCI v1 inchangés. Base canonique5fd18c3291cd93533cf7b1f7ab50862c85a7a205. GO BUILD reçu : **« Valider le build isolé proposé »**. Aucun endpoint, UI, modèle partagé ou activation de production.

## Brainstorming / Options / Risques / Choix retenu

Le [design accepté pour build isolé](../../../openspec/changes/science-initial-plan-policy/design.md) écarte l'admission automatique des gabarits hérités et l'optimisation individuelle non justifiée. Le producteur pur renvoie des résultats v1 réels et les diagnostics détaillent séparément la politique proposée. Les valeurs2séries,8–12reps,2RIR,90/120s restent non admises : le GO BUILD ne leur fournit pas de preuve scientifique nouvelle.

## Implémenté

- Registre dédié immuable et épinglé par SHA-256 : catalogue scientifique/crédit/preuves/objets/contrat existants,7intentions neutres propres au bundle. Aucune modification des données partagées. Une dérive de fichier ou une version d'engine étrangère est refusée.
- `inspect_policy` : sélection par identité CANONICAL, rôle PRIMARY et mouvement ; confirmations contextuelles/exclusions, affectation globale distincte déterministe ; allocation proposée pour2/3séances, calibration sans charge déduite ; attribution brute et crédit séparés sur15zones.
- Rôles UNKNOWN conservés comme inconnus, avec CATALOG_GAP ; ni crédit0 ni exposition complète artificielle. Aucun inventaire obligatoire ; données ou confirmations absentes ne deviennent pas une salle complète.
- `produce` : sortie FirstPlanRecommendation v1, vrai fingerprint, provenance des champs utilisés, conflits facultatifs signalés sans les employer. Priorité conflit/manque requis puis POLICY_UNAVAILABLE. Aucun mécanisme permettant de déclarer arbitrairement le bundle approuvé.
-11fixtures générées par **le producteur réel**, depuis des inputs synthétiques, validées par validate_exchange. Elles sont NOT_SERVED et ne contiennent **aucun READY**, car dose/sélection/temps ne sont pas admis. Une fixture positive de protocole n'a pas été recyclée en preuve scientifique.
- CLI `python -m tools.science_initial_policy.fixtures` vérifie la régénération ; `--write` régénère uniquement l'artefact dédié. Les8fixtures canoniques SCI-P01/02 restent inchangées.

## Ce qui est exécutable et ce qui ne l'est pas

Le producteur Python et ses diagnostics sont exécutables isolément. Les diagnostics portent `executable:false` ; ils ne sont pas un Plan v1 prêt à démarrer. v1 ne possède pas de review_state PROPOSED : candidate_plan reste null, sans étiqueter abusivement ce nouvel archétype LEGACY_UNVALIDATED ou REVIEWED.

L'API, la persistance de nouveaux inputs, le producteur de production, le démarrage mobile et toute prescription admise restent absents. Le cadre hors population v1 est rejeté en amont ; une autre confirmation de contexte est rejetée, pas ignorée. La réponse individuelle reste NOT_ESTIMATED.

## Vérifications

TDD observé :23tests rouges avant module ; tests additionnels rouges puis verts pour rôle inconnu, alternatives dupliquées, conflit mal étiqueté et traçabilité/non-blocage des champs facultatifs. Suite producteur+contrats :72passants. Broad scientifique final :503passants/1ignoré. Deux avertissements de dépendances existants.

Contrôle consommateur réel :11sorties Python passent dans AuthSession/FirstPlanClient du worktree MOB-03 à0ee7ba3 avec vérification canonique via Python. L'absence de producteur garde NOT_SERVED sans requête de recommandation. Aucun fichier mobile modifié ; pas de fausse passe réseau/API ou appareil.

check_scope ISOLATED : Ruff des fichiers neufs, budget264≤548, Bandit ciblé, protocole et OpenSpec strict6/6 passent. Aucun full sweep local ; CI réelle obligatoire avant merge. Revue indépendante sans Critical/Important ; mineur des priorités différé. CI finale et canonique réussies ; reçu exact dans [DELIVERY_RECEIPT.md](DELIVERY_RECEIPT.md), avec les SHA, runs et distinction Sonar PR OK/canonique ERROR historique.

## Décisions d'exécution et limites

- Diagnostics séparés du Plan v1 : préserve le contrat et empêche une prescription non admise de devenir exécutable ; coût assumé : pas de READY tant que la vraie admission manque.
- Binding explicite à l'engine1.0.0 ; un appelant doit demander cette version, pas obtenir un autre moteur par relabeling silencieux.
- Un oracle de test initial attendait un crédit exact ; les rôles UNKNOWN réels du catalogue ont conduit à corriger cette attente, sans falsifier les sources.

## Gates restantes

[Décisions/handoff](DECISIONS_AND_HANDOFF.md) : D5 GO BUILD reçu ; D1–D3 demeurent des propositions scientifiques/de couverture à admettre ou amender, et D4 manque de bases temporelles couvrant préparation/apprentissage/transitions. Sans politique temps admise, POLICY_UNAVAILABLE prévaut ; un modèle admis non applicable garderait TIME_UNCERTAIN. Aucun overhead numérique inventé pour réussir READY.

Inputs requis du profil v1 : objectif, population déclarée, cadence, budget par séance et réponse sur limitations. Taille/poids/priorités facultatifs ; expérience inconnue explicite. Les nouvelles acquisitions et leur stockage ne sont pas livrés par ce module.

La première vraie fixture READY est donc **toujours bloquée scientifiquement**, malgré le producteur testé. Mobile attend l'admission et ses bases, puis la version de producteur autorisant la prescription et l'adaptateur propriétaire. Les gates effacement, consentement et appareils de MOB-03 restent indépendantes. Le change ne prétend pas achever le critical path ou activer une recommandation.
