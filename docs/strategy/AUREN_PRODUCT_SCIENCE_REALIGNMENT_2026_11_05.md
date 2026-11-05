# AUREN — recadrage produit, science et direction artistique

Date : 5 novembre 2026. Statut : transcription opérationnelle du recadrage transmis par l'opérateur, avec propositions et inconnues séparées.

## Source et portée

Sources de session : document « AUREN — Recalage de la roadmap produit, scientifique et artistique », puis mandat « AUREN — SCIENCE / INTELLIGENCE AGENT — SPIKE S0 ». Le second définit la mission scientifique ; il indique lui-même qu'un manifeste canonique v1.0 sera fourni. Le texte intégral a été transmis ensuite par l'opérateur : [AUREN_MANIFESTO_V1.md](AUREN_MANIFESTO_V1.md), version 1.0 du 5 novembre. Il est conservé sans réécriture ; le mandat S0 ne s'y substitue pas.

Ce recadrage précise la direction produit et le pilotage. Il ne modifie pas silencieusement les contrats scientifiques, visuels ou les comportements de production. Les conflits avec un contrat versionné doivent être signalés et résolus par un changement explicite. Pas de nouveau GO BUILD, de déploiement ou de validation visuelle implicite.

## Direction produit désormais utilisée

AUREN construit un **cockpit personnel de bodybuilding**. La migration des capacités web sert la boucle :

`COMPRENDRE → PLANIFIER → EXÉCUTER → MESURER → INTERPRÉTER → ADAPTER`

Chaque tranche doit indiquer la décision utilisateur qu'elle améliore, les faits qu'elle consomme, sa source d'interprétation et son comportement quand elle ne sait pas. La réussite du premier usage est une première proposition exploitable et la possibilité de démarrer, **ou** une indication claire de ce qui manque. Le nombre de champs remplis n'est pas un critère de succès.

## Brainstorming / Options / Risques / Choix retenu

Le document reçu conserve l'ordre technique des tranches et renforce leurs critères d'acceptation. Repartir sur une refonte générale ou remplacer les domaines existants sortirait de ce mandat. Le choix de pilotage est donc d'amender la lecture du chemin critique, de garder MOB-03 prioritaire et d'expliciter ses dépendances scientifiques. Cette passe produit des documents, sans toucher au moteur ni à l'UI.

Risques : confondre cible produit et capacité servie ; collecter des données non consommées ; fabriquer la confiance côté mobile ; traiter une référence artistique comme un asset de production ; mélanger audit scientifique S0 et implémentation mobile. Les statuts du registre lié ci-dessous évitent de déclarer ces dépendances acquises.

## Responsabilités et coordination

| Responsable | Décisions et livrables |
|---|---|
| Agent produit/mobile | Navigation, parcours, saisie, composants, rendu, persistance client, appels API, erreurs, accessibilité, présentation des résultats |
| Agent science/intelligence | Sémantique des données, taxonomies, règles, preuve, paramètres, calculs déterministes, confiance/incertitude, contrats de décision et tests de domaine |
| PO / direction artistique / opérateur | Hiérarchie de l'expérience, compositions et assets, arbitrages transversaux, acceptation visuelle ; opérateur pour stockage/rétention/effacement |

Le dépôt est le support de coordination. Réutiliser OpenSpec, les contrats canoniques et le [registre de dépendances](AUREN_PRODUCT_SCIENCE_DEPENDENCIES.md). Ne pas modifier la doctrine de l'autre volet ni les mêmes schémas indépendamment. Un handoff lisible n'est pas une livraison reçue ; aucun échange avec un agent externe n'est revendiqué ici.

Pour chaque future capacité : question → état réel → preuve → options → décision → contrat → implémentation minimale si justifiée → tests → handoff. Chaque spike a ses non-objectifs et critères de sortie. Le S0 est un audit/conception scientifique : il n'autorise pas un nouvel algorithme d'entraînement ni une refonte UI.

## Direction MOB-03 issue du recadrage

| Sujet | Direction fournie | Limite / travail restant |
|---|---|---|
| P01 | Une seule entrée de marque composée avec connexion et inscription ; utilisateur reconnu sans écran de bienvenue répété | Hiérarchie fournie, rendu réel pas encore accepté |
| P02 | « Ton entraînement, construit autour de toi. » | Proposition éditoriale à rendre et revoir, sans landing commerciale |
| P03/P04 | Création par identifiant, mot de passe et confirmation ; email selon besoin réel, pas obligatoire artificiellement | API existante avec email facultatif ; expliciter récupération sans email et aide avant finalisation du parcours |
| P05/P06 | Body & Training Blueprint en quatre moments : point de départ ; disponibilité ; physique souhaité ; premier plan | Cible UX, pas autorisation de créer toutes les persistances ou prescriptions ; qualifier données indispensables/facultatives et consommateurs |
| Poids | Mesure datée et historisable ; poids hérité sans date conservé distinct | Chronologie existante à réutiliser ; compatibilité et protocole de mutation à spécifier avant réalisation |
| P07 | Préparer suppression et confidentialité avec politique backend réelle | Arbitrage opérateur toujours ouvert ; aucune suppression implémentée ; exigences Store à vérifier sur sources officielles dans la tranche concernée |
| P08/P09 | Première valeur exploitable ou manque explicite ; intégrité du journal impérative | Statuts de reprise/réseau/refus à détailler ; attribution serveur du journal déjà acceptée, pas encore implémentée |

Hiérarchie d'entrée transmise, **pas une maquette acceptée ni une nouvelle baseline** :

```text
[vrai composant AurenMark]
AUREN
Ton entraînement, construit autour de toi.

Ton espace d'entraînement
Identifiant
Mot de passe
[Se connecter]
[Créer mon compte]
Récupération du compte · Confidentialité
```

Les liens doivent avoir une destination réelle adaptée à leur authentification ; aucun Bearer en URL. Si une destination de confidentialité manque, ne pas livrer un lien factice.

### Blueprint — informations à confronter au domaine

| Moment cible | Informations proposées | Contrat à obtenir avant collecte produit |
|---|---|---|
| Ton point de départ | Taille, poids avec unité, expérience | Source/validation, caractère nécessaire ou facultatif, stockage, consentement applicable, unités supportées |
| Ta disponibilité | Fréquence, durée habituelle, environnement | Distinction déclaré/absent ; quels paramètres influencent réellement la proposition servie |
| Le physique que tu veux construire | Développement global/priorités, exercices évités, limitations pertinentes | Taxonomie et usage scientifique ; aucune déduction morphologique ou médicale inventée |
| Ton premier plan | Résumé du connu, des inconnues, proposition du moteur | Suffisance des inputs, prescription réellement disponible, raisons et état d'incertitude |

Mensurations détaillées, photos et questionnaire approfondi sont différés après la première valeur. Un moteur qui ne consomme pas encore un champ ne justifie pas une promesse de personnalisation de ce champ.

## Chemin critique et conditions renforcées

L'ordre adopté le 3 novembre est conservé, y compris UX-LAB-PROFILE avant MOB-11. MOB-03 est le premier véritable parcours connecté AUREN ; MOB-04 à MOB-12 restent des tranches distinctes. Le bilan MOB-02 a déjà sa surface et son intégration ; **son design n'est pas présenté comme un blocage actuel**. Les recettes et clôtures restantes gardent leurs preuves propres.

| Tranche | Critère lié au recadrage |
|---|---|
| MOB-03 | Compte → données utiles → proposition exploitable ou manque explicite ; propriétaire du journal sûr |
| MOB-04 | MISSION compréhensible et action immédiate à partir de la recommandation réellement servie |
| MOB-05 | Séances/performances/tendances fondées sur l'historique réel et interprétations traçables |
| MOB-06/07 | Choix/activation puis construction selon catalogue validé, intentions et prescriptions supportées |
| MOB-08 | Fiche native pilote et instructions/illustrations cohérentes |
| MOB-09/10 | Salle déclarée et substitutions issues du graphe canonique |
| UX-LAB-PROFILE → MOB-11 | Profil explicable ; dimensions calculables établies avant octogone |
| MOB-12 | Récupération/contexte avec limites scientifiques explicites |
| BIZ / PLAT / alpha | Fiabilité, données, sécurité, distribution et offre selon leurs gates ; comptes Store toujours au jalon alpha prévu |

## Voie artistique révisée

`master mannequin → Smith incliné START/END → fiche d'exercice native pilote → sept Push A → règles de production série → catalogue restant`

Ce séquencement remplace la production de tout le catalogue avant essai du composant consommateur. Cinq vues raster sont décrites comme références acceptées par le document reçu ; cela ne prouve pas qu'un master final exploitable ni les droits d'usage sont livrés. Les pièces exactes restent à rattacher au manifeste d'assets avant production.

- Réutiliser logo, icône, tokens, instruments, BodyMap et surfaces LOCKED. Ne pas confondre BodyMap fonctionnel et mannequin d'illustration.
- Formulaires, étapes et graphiques : code React Native/SVG déterministe après composition validée, aucune image générée pour représenter des données.
- Exercices : provenance, identifiants, continuité START/END, cadrage et intégration dans la fiche pilote avant série.
- MOTION-V2 reste différé ; une illustration ne prouve aucune activation ou contraction musculaire.

## File future — cadrage seulement

Nutrition, rapports hebdomadaires et photos de progression sont des capacités cibles à proposer dans des changes séparés. Aucun n'est une dépendance de MOB-03. Le recadrage ne livre ni leur contrat ni leur GO BUILD ; ne pas créer de fonctionnalité, d'analyse photo ou de récit scientifique depuis un placeholder.

## Sortie de cette passe

Documents produit actualisés et registre science→produit préparé. Aucun nouveau code, schéma, seuil, collecte corporelle ou asset généré. La PR API existante reste distincte de cette préparation ; aucun commit, push, merge ou déploiement effectué à cette passe. Ce paragraphe décrit la passe documentaire antérieure au mandat PRODUCT DELIVERY : le manifeste complet est maintenant reçu ; les livrables S0 restent à référencer à réception. L'exécution native MOB-03 a ensuite repris selon le nouveau mandat.
