# MOB-03 — contrats manquants du consommateur natif

5 novembre 2026, après mandat PRODUCT DELIVERY et lecture du manifeste v1.0 reçu. Ce registre borne la première planche et le premier raccordement ; un champ présent en base ne prouve pas une API mobile utilisable ni un effet scientifique.

| ID / consommateur bloqué | Input requis | Sortie / contrat attendu | Inconnu / repli courant | Producteur |
|---|---|---|---|---|
| UI_DATA_GAP-01 · point de départ | Taille et expérience déclarées, poids daté/unité/provenance | Lecture/écriture mobile propriétaire, consentement applicable, validation et protocole de réponse perdue ; poids via chronologie BodyMeasurement, jamais User.weight_kg antidaté | /auth/me sert seulement id/username ; pas de formulaire prétendant enregistrer le Blueprint tant que ses routes manquent ; pas d'import du labo | Produit/API avec doctrine Blueprint science |
| UI_DATA_GAP-02 · disponibilité | Fréquence, durée, environnement concret | Contrat de mutation et reprise ; absence distincte de vide, IDs matériels validés, consommateurs réels explicités | GET /me/training-preferences ne sert que sessions_per_week ; modèles/services existants mais pas mutation mobile complète dans le socle courant | Produit/API + science pour l'effet sur le plan |
| UI_DATA_GAP-03 · priorités / contraintes | Priorités bodybuilding, évitements, limitations pertinentes | Vocabulaire et ordre, source déclarée, effet autorisé, validation et persistance | Ne pas recopier les objectifs lab/profile ; aucune inférence anatomique ni effet de prescription revendiqué | Science SCI-P01 + produit/API |
| UI_DATA_GAP-04 · premier plan | Faits effectivement connus et contexte | FirstPlanRecommendation avec inputs utilisés, suffisant/manquant, explication et confiance/incertitude définies | MISSION existante READY/RESUME/NO_MISSION reste consommable ; NO_MISSION ne prouve pas à lui seul quelles données manquent. Aucun diagnostic manquant fabriqué côté UI | Science SCI-P01/P02 + API |
| UI_DATA_GAP-05 · compte/données | Décision d'effacement/rétention, responsable, URL publique | Cycle de suppression avec réauthentification, résultat réel et chemin externe ; information confidentialité | Aucun bouton de faux effacement ; paramètres sur banc indiquent indisponibilité. Lien confidentialité seulement avec destination confirmée | Opérateur/STORE-00 + architecte |
| UI_DATA_GAP-06 · récupération d'un compte sans email | Contrat du compte créé sans courriel | Aide claire et voie de récupération réellement possible | Email facultatif selon API, ne pas promettre une récupération automatique ; /forgot-password existe côté web | PO + propriétaire compte |

## Liens web réels et frontières

`/forgot-password` est public ; `/export` requiert une session web distincte du Bearer mobile. Le futur lien export doit annoncer une éventuelle connexion sur le site. Aucun token en URL, aucune assertion que le navigateur partage la session de l'app. La destination publique de confidentialité reste à confirmer ; pas de lien factice ajouté.

## Ordre de résolution

La garde propriétaire et les mutations de compte peuvent avancer indépendamment. La planche peut exposer les acquisitions comme candidates avec leurs gaps, mais ne doit pas les transformer en écritures fictives. Pour finir le parcours connecté : fournir les contrats de champs supportés, leurs routes et fixtures, puis tester le vrai chemin compte → déclarations confirmées → première proposition réelle. Ni la planche ni les tests du socle auth ne prouvent encore ce chemin complet.


## Avancée du sous-ensemble déclarations — 5 novembre

[Adaptateur versionné des déclarations](MOB03_TRAINING_DECLARATIONS_API_CONTRACT.md) implémenté localement : fréquence, priorités par axes et familles d'équipement existantes, sans nouvelle règle. UI_DATA_GAP-02/03 sont partiellement réduits, pas clôturés : durée et limitations restent absentes, le choix d'environnement concret garde son contrat séparé, et le formulaire Blueprint n'est pas raccordé. Ce sous-ensemble n'établit pas la suffisance d'un premier plan (UI_DATA_GAP-04).
