# MOB04 MISSION — proposition préparatoire, sans GO BUILD

5 novembre 2026. Préparée **après fusion autorisée du socle #353**, merge `db37b76be1cb18d18675b47788b8e680a1dff752`. Aucune composition, baseline, route ou recommandation modifiée. MOB03 complet reste ouvert via DATA/PLAN/RELEASE. Cette proposition deviendra un change OpenSpec distinct avant apply, sans PR concurrente de code avec le socle.

## Objectif et autorité

Depuis Aujourd'hui, répondre « que faire maintenant, et pourquoi » à partir des faits disponibles, avec priorité à une séance déjà ouverte. Manifeste : comprendre→planifier→exécuter→mesurer→interpréter→adapter. Le read-model existant ne remplace pas l'interface scientifique de premier plan.

- UI : `MISSION-SCREEN-V1` LOCKED, `docs/strategy/AUREN_VISUAL_CONTRACT.md` §25, baselines `mission-390x844-{catch-up-shoulders,push-a,liss-abs,legs-a}`. Corps/zone par serveur, une information une seule fois, action visible ; aucun changement de pixels sans croquis/rendu acceptés.
- Domaine servi historique : `app/services/mobile_read_models.py::mission_read_model`, `GET /api/mobile/v1/mission`, `ServerMission` / `isStartable` dans `clients/mobile/src/api/types.ts`. États actuels READY/RESUME/NO_MISSION ; décision et empreinte restent celles du serveur.
- Science : BodyTrainingBlueprint/FirstPlanRecommendation v1, FirstPlanClient, moteur isolé1.0.0 ; politique0.1.0-proposed NOT_ADMITTED/NOT_SERVED. Une suffisance d'entrée n'est ni une admission de dose/temps ni une séance démarrable. Le vrai premier plan et son handoff restent PLAN01–07.

## États et action principale à contractualiser

| Contexte | Autorité / information utile | Comportement de proposition |
|---|---|---|
| Séance ouverte, serveur accessible | ServerMission.RESUME/session/position | Reprendre prioritaire ; aucune nouvelle proposition ne masque la séance |
| Séance possédée restaurée hors ligne | Journal attribué et exécution existante | Préserver reprise/faits/outbox et limites hors ligne ; absence SCI ne bloque pas une séance déjà commencée |
| MISSION historique READY | Payload du serveur, executable/first_exercise et décision valides | Démarrer seulement sous `isStartable` et applicabilité réelle ; ce READY n'est jamais une preuve de FirstPlanRecommendation.READY |
| Aucune MISSION | NO_MISSION/primary_action=null | Absence explicite, pas de programme ou équipement par défaut ; aide/édition progressive à faire composer sans commande de démarrage fictive |
| Lecture initiale / actualisation | Transport en cours, faits déjà disponibles | Distinguer chargement et vide ; conserver les faits possédés, pas une réussite inventée |
| Lecture perdue / auth expirée | Transport, AuthSession et génération | Relecture explicite, reconnexion si nécessaire ; aucune nouvelle mutation automatiquement répétée, aucun résultat du compte quitté |
| Premier producteur SCI absent/non admis | FirstPlanClient.unavailable/NOT_SERVED | État distinct du read-model historique ; ne pas appeler MISSION comme fallback scientifique |
| SCI insuffisant/conflit | Assessment canonique vérifié | Manques/actions liés à des champs réellement éditables ; priorité déclarée ≠ faiblesse analysée ; poids/taille non obligatoires par défaut |
| SCI valide sans séance exécutable | Résultat validé + handoff absent | Rester indisponible ; absence du handoff ne se résout pas par un clic vers Aujourd'hui |
| Adaptation | Contrat moteur, pending/refus/confirmé | Exposer seulement une action supportée et son résultat ; pas de nouvelle allocation/score côté interface |

## Contrat consommateur attendu à la future ouverture

Inventaire élément→source : titre/template, raison du serveur, décision/version/fingerprint, zones dérivées des exercices, session/position de reprise, absences/incertitudes. Aucun pourcentage de progrès, diagnostic de point faible, estimation de temps, intensité colorée ou chiffre décoratif sans producteur canonique et sens validés. Les projections compacte/détaillée partagent la même information, sans duplication ; leur composition reste à soumettre.

`docs/fixtures/mob04-mission.preparation.v1.json` contient des cas versionnés et des références immuables. Ils sont **SPEC_FIXTURE_NOT_SERVED**. Les payloads de reprise/absence suivent les types existants ; la référence READY historique pointe uniquement vers le banc LOCKED. Le cas de vrai premier plan reste bloqué et sans payload, plutôt qu'une fixture READY fabriquée.

## Acceptance proposée — toutes tâches ouvertes

- [ ] M04-01 : faire accepter le périmètre/gaps du futur OpenSpec et son ordre avec PLAN ; aucune modification du domaine scientifique de substitution ou d'allocation déduite.
- [ ] M04-02 : tests consommateurs sur tous les cas du fichier, propriétaire/versions/empreinte et priorité reprise ; provenance de chaque élément, aucun repli SCI vers MISSION.
- [ ] M04-03 : map des états du serveur aux actions UI, garde `isStartable`, résultat de démarrage perdu et réconciliation sans mutation rejouée ; contrat de premier handoff fourni avant d'en activer un.
- [ ] M04-04 : croquis borné comparé aux quatre baselines LOCKED ; expliquer/consentement/manque sans chiffres inventés ; approbation opérateur avant code et pixels avant commit.
- [ ] M04-05 : vérifier 320/390/430px, safe areas, grandes tailles, VoiceOver/TalkBack/retour/clavier applicables, offline et recette physique dans la suite release ; CI obligatoire du futur HEAD.
- [ ] M04-06 : rendre explicites les capacités scientifiques/données encore non servies et leurs versions ; aucune fermeture de MOB03 complet du fait de ce futur écran.

## Dépendances et frontières

PLAN : politique admise, snapshot canonique, vrai READY et commande de première séance. DATA : seulement pour traitements corporels effectivement consommateurs, pas consentement global imposé à MISSION. RELEASE : preuves appareils et déploiement séparés. L'inconnu matériel reste inconnu, aucun inventaire obligatoire. Social/paywall/photo/providers/récupération médicale hors périmètre.

Assets : réutiliser AurenMark/tokens/BodyMap fonctionnel existants ; aucun asset final généré par cette préparation. La file mannequin→Smith incliné START/END→fiche pilote reste dans ses tranches approuvées ; pas d'emplacement visuel remplissant implicitement un contrat scientifique manquant.
