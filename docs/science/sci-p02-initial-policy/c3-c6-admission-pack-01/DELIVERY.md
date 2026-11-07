# C3/C6 — livraison du contrat v3 isolé

7 novembre 2026. **Stage1 implémenté, revu et fusionné PR373 ; suivi canonique/closeout en cours. NOT_ADMITTED / NOT_SERVED.** Autorisation : « Valider v3 et ce build isolé ». Base a5720797f14902bf7ef7248765ae716f107113b0. Aucun READY réel, binding ou producteur positif.

## Brainstorming / Options / Risques / Choix retenu

Le design antérieur compare une relaxation silencieuse de v2, un refus uniforme et un successeur explicite. Choix approuvé : v3 garde les faits et sources existants, sépare science, temps et permission. Un temps inconnu ne devient pas une durée supportée. La direction produit permet conditionnellement l’exploration sous reconnaissance explicite liée au plan ; le registre vide interdit toute permission réelle dans cette livraison.

## Code et artefacts

- `bootstrap_protocol_v3.py` : quatre phases typées, revue d’essai liée à son occurrence/contexte, effort inconnu préservé, arrêt/préoccupation, transition vers un réglage réellement disponible selon ordre d’effort sourcé. Aucune charge ou causalité d’échec déduite. Le diagnostic réutilise la borne structurelle de repos existante ; R≥budget réfute une séance non vide, R<budget ne prouve aucun fit.
- `blueprint_first_plan_v3.py` : requête/résultat3.0.0, trois empreintes distinctes, reconnaissance liée au sujet/snapshot/révision/faits/observations/plan+temps/politique/date. Forme hypothétique distincte de l’autorité ; frontière réelle réutilise la validation négative v2 et le vrai registre vide.
- `first_plan_v3_fixtures.py` : export explicite et vérification par défaut de neuf fichiers, dont cinq schémas, neuf exemples négatifs, un exemple de protocole non admis et deux manifestes. Les artefacts ne sont pas des sorties de producteur positif.

## Limites et suites

Les cinq faits minimaux restent objectif/population/cadence/budgets/limitations ; anthropométrie et priorités facultatives. Aucun inventaire imposé. V1/v2, SDK, app, API, UI, registre historique et activation inchangés. Le protocole typé est un contrat cohérent, pas une admission opérationnelle. Un acquittement JSON ne prouve ni authentification ni décision du responsable.

Étape2 : véritable admission C1–C6 sur le bundle exact, C3 utilisable/arrêt/réessai, convention temporelle et politique d’exploration applicables, puis scope séparé du binding/producteur. Étape3 PLAN : snapshot propriétaire, négociation v3, adaptateur et séance possédée. DATA/RELEASE restent distincts ; MOB03 complet reste ouvert.

## Vérification en cours

**73 nouveaux cas passants**, broad ciblé **510 tests / 15 modules**, deux avertissements de dépendances. Ruff fichiers neufs/budget264≤548, Bandit ciblé, protocole, OpenSpec strict11/11, artefacts et intégrité historique passants. Gitleaks vérifié sur les commits de livraison. Pas de sweep complet local, tier ISOLATED.

Revues fraîches code et SCI distinctes : quatre Important code dont un commun à SCI, corrigés dans une passe RED→GREEN (14 cas rouges, puis 15 verts incluant un témoin cohérent). Suite73/73 et broad510/510 repassés. Aucun Critical ou mineur de revue. Copies natives revalidées sans coercition JSON des booléens, contexte complet avant transition, borne haute supportée strictement supérieure aux repos connus et structure inconnue conservée sans champ de structure dans PlanV2. V1/v2 inchangés.

La PR373 et le closeout consignent HEAD, CI et Sonar après exécution réelle ; aucun résultat distant anticipé.

## Décisions d’exécution et limites de revue

- Exécuter le design explicitement approuvé et le GO MERGE permanent sans nouvelle question : coût en cas d’erreur, maintenir toute capacité publique inactive et revoir toute extension substantielle.
- Séparer empreintes faits/observations/évaluation et plan+temps pour éviter une reconnaissance circulaire : coût en cas d’erreur, refus des références incohérentes plutôt qu’autorité inventée.
- Stage1 représente revue/transition/protocole et diagnostic structurel existant, sans nouvel algorithme d’ajustement ou moteur négatif : coût, admission et vrai producteur restent étape2.
- Les reviewers ne certifient ni C1–C6 positifs ni authentification/UI/transport ; leur absence est la frontière étape2/PLAN, pas une omission du contrat. Coût, aucun raccordement positif sans preuve/scope ultérieurs.
- Les validateurs historiques sont des dépendances pinées, sans corrections étrangères au périmètre : coût, tests d’intégration futurs requis avant runtime.
- CI/Sonar/canonique/cleanup sont vérifiés par l’agent de livraison, pas par les reviewers : coût, arrêt et conservation des preuves si ces conditions échouent.

Aucun mineur de revue différé. Les remarques Sonar éventuelles restent une catégorie de qualité séparée. La revue SCI est une cohérence de contrat, pas une nouvelle revue systématique, validation biologique/personnelle ou borne temporelle réelle.

## Reçu code vérifié

PR373 : HEAD **d56fe2d78078cc80c16f49193dd2bc185ce9d8de**, merge **4694ae9391ecac2622f4d0493818aac1d4a23f2e**. CI PR42393674309 completed/success, neuf jobs : **7 733 backend passants/trois ignorés,54suites/676mobile+TypeScript**. Base a572079 relue avant merge, garde exacte du HEAD, aucun bypass/force-push ; zéro revue/thread bloquant.

Sonar PR : ERROR consultatif/Major, six remarques de structure des tests (4S9073 assertions composites,2S5778 invocation des tests d’exception), zéro bug/vulnérabilité/hotspot sur ce diff ; couverture app93,8%, nouvelle couverture non fournie. Dette qualité séparée, sans seuil/issue modifié. Le seul run d’ancien HEAD42393077099 a été annulé comme obsolète ; le run final a entièrement réussi.

La CI canonique42395374363 et les contrôles du closeout sont suivis dans CLOSEOUT/PR de maintenance ; aucun succès futur n’est anticipé. La maintenance sera fusionnée seulement après succès canonique du code et CI de son propre HEAD.
