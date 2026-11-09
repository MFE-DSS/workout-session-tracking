# DATA-ACT-01 — questionnaire et relevé unique

**D01 est PARTIELLE ; D02–D09 et C01–C11 restent OPEN.** Aucun choix pré-coché. Le
responsable fournit une réponse, son auteur habilité, sa date et sa référence
de validation ; l'agent vérifie ensuite la complétude technique sans signer à sa
place. `Non exploité` est une réponse possible uniquement avec un périmètre et
un constat opérateur. Une politique projetée n'est pas une configuration déployée.

## Décisions à signer ensemble

| ID / décision | Fait établi et question concrète | Réponse attendue du responsable | État / validation |
|---|---|---|---|
| D01 — identité / entité / juridiction | Le dépôt ne prouve pas l'identité légale publiable ni la juridiction. Réponse opérateur partielle consignée ci-dessous. | L'opérateur assume personnellement le service à ce stade ; formalisation envisagée ultérieurement. Restent à établir : identité légale exacte ou référence contrôlée, qualité/entité et coordonnées destinées à l'information publique, juridiction(s)/territoire(s), population visée et référence de validation. Aucune coordonnée privée à publier dans le dépôt. | PARTIELLE — opérateur, 9 novembre 2026, déclaration de session citée ci-dessous ; non admise comme politique |
| D02 — finalités et applicabilité du consentement | Le consentement `body_measurements` version 1 existe ; il n'autorise pas automatiquement limitations, préoccupations, observations, calibrage ou copies PLAN. **Quels traitements précis sont admis pour les catégories C01–C11 ?** | Pour chaque ligne : finalité déterminée, catégories nécessaires, destinataires, fondement et référence validée ; si consentement applicable, texte/version/action positive/preuve, effet du refus et du retrait. Si non applicable, justification approuvée spécifique à la finalité ; pas `NOT_REQUIRED` depuis l'absence de mensurations. Photo/provider restent hors activation proposée. | OPEN — matrice ci-dessous |
| D03 — effacement / conservation / exception d'invariance | Les traces OWNER_LIFETIME et six tables PLAN sont immuables ; les FK PLAN n'effacent pas par cascade. **Quel sort pour chaque catégorie et copie lors d'une demande volontaire ?** | Effacer ou conserver chaque catégorie ; si conservation : sous-ensemble minimal, motif/fondement vérifié, durée et point de départ, déclencheur final, accès et information ; exception explicite, bornée et approuvée à additive-only/invariance avant tout traitement destructif. Sinon OPEN, sans durée par défaut. | OPEN — matrice ci-dessous |
| D04 — local non envoyé / non attribué | Les partitions possédées, intentions et marques de retrait existent ; aucune identité ne peut être inférée pour `user_id NULL` ou un journal non attribué. **Que proposer pour les faits de l'ancien propriétaire non envoyés, et séparément pour les faits non attribués ?** | Choix utilisateur autorisé/texte et portée pour faits prouvés du propriétaire ; traitement des faits pending/inflight/failed/acked/résolus ; sort du journal non attribué avec consentement distinct si nécessaire ; exports locaux éventuels ; délai uniquement s'il est fourni et justifié. Aucun nettoyage sur logout, 401/404, timeout, demande pending ou compte différent. | OPEN |
| D05 — exports / social / publications | JSON de séances PLAN copie binding/opérations ; export téléchargé échappe au contrôle du serveur. Des références sociales et slugs publiés ne sont pas couverts par un DELETE users. **Quelles copies maîtrisées et quels liens partagés doivent être traités ?** | Inventaire des exports serveur/opérateur et destinataires contrôlés, mécanisme/sort approuvé par catégorie ; traitement des liens de squad, invitations, challenges et templates publiés sans détruire les faits d'autrui ; limites à communiquer pour copies déjà téléchargées ou détenues hors contrôle. Aucun engagement de reprise universelle des fichiers. | OPEN |
| D06 — sauvegardes / restauration | `30` jours est le défaut du helper, `0` désactive sa purge ; ni l'un ni l'autre n'est une politique approuvée. Le restore legacy refuse PLAN. **Quelles sauvegardes sont réellement exploitées et comment éviter la réapparition ?** | Déclaration opérateur des systèmes/emplacements logiques et copies hors site/DB/volumes/appareils, accès et opérateur responsable ; pour chacun rétention effective/purge approuvée, traitement des effacements, registre d'exclusion et procédure avant remise en service d'une restauration ; responsable de preuve et traitement des échecs. Pas de chemins privés ni secrets à publier. | OPEN |
| D07 — demandes / reçus / identités retirées | Le service isolé sait émettre/lire une capacité de suivi ; aucun exécuteur n'y démarre le traitement irréversible. Demande, hash, reçu et marque de retrait sont eux-mêmes des données. **Quelles preuves minimales restent après effacement, pendant combien de temps et qui y accède ?** | Champs minimaux/lien résiduel et fondement ; durées distinctes de conservation du reçu, disponibilité de suivi et validité de capacité (avec départ/expiration/récupération) ; accès app/web après révocation/perte de ticket/autre appareil ; mécanisme d'identité stable/tombstone empêchant réutilisation de l'ancien ID sans réattribuer les faits. Pas de durée infinie implicite. | OPEN |
| D08 — exécution / exceptions / suivi | Mode MANUAL ou AUTOMATED existe dans le contrat, pas d'opérateur ni de worker actif. **Qui exécutera et vérifiera réellement le périmètre approuvé ?** | Mode choisi, responsable opérationnel, vérificateur et preuve acceptée de révocation/effacement/protection de restauration ; délais annoncés et modalités d'information en cas d'attente/exception ; reprise après début irréversible et traitement d'incident. Aucun manuel fictif ni statut DELETED avant les trois preuves. | OPEN |
| D09 — information et URLs publiques | Le domaine d'un backend ou un lien technique n'est pas une URL de confidentialité ou une entrée web d'effacement approuvée. **Quelles deux ressources publiques réelles seront publiées ?** | URL HTTPS de confidentialité + URL HTTPS dédiée de demande web, propriétaire éditorial, textes/version, authentification et suivi décrits au public, langues, publication et vérification externe avant activation. À défaut : OPEN ; aucun lien factice ou formulaire sans traitement réel. | OPEN |

## Réponse partielle D01 — 9 novembre 2026

Déclaration exacte de l'opérateur, reçue dans la session le 9 novembre 2026 :

> Moi même simplement c'est mon service et mon application qui dans le cas échéant, sera legalisé avec tout ce que ça implique en fonction de si je mets en place le produit sur google store

Fait déclaré : l'opérateur assume personnellement le service et l'application à
ce stade ; il envisage une formalisation ultérieure, en évoquant une éventuelle
mise sur Google Store. Cette déclaration n'établit ni identité légale publiable,
coordonnées, entité formalisée, juridiction, public visé, ni texte public approuvé.
Elle n'est pas une politique admise, un fondement, une durée ou une autorisation
de traitement/activation. Aucune conclusion sur le déclenchement d'obligations
par le Store n'est tirée de cette intention. D02–D09 et C01–C11 restent OPEN.

## Matrice de catégories à renseigner, pas une politique recommandée

Chaque ligne doit porter **finalité/fondement (D02)**, **sort/durée/départ/exception
(D03)** et **copies/destinataires concernés (D05–D07)**. Les regroupements ci-dessous
servent la lecture ; le responsable peut séparer des sous-catégories si leur sort
diffère. Références : [matrice historique](../../MOB03_DATA_RETENTION_MATRIX.md)
et [graphe complémentaire PLAN](PLAN_COPY_GRAPH.md).

| Catégorie | Données et copies incluses | Finalité / fondement / consentement | Sort / durée / départ / exception | Destinataires / copies / preuve |
|---|---|---|---|---|
| C01 identité et accès | users, sessions d'appareils, refresh/reset/cookies, SecureStore/mémoire | OPEN | OPEN | OPEN |
| C02 faits d'entraînement | workout_sessions/session_exercises/set_logs, notes et données de séance, non-attribués séparés | OPEN | OPEN | OPEN |
| C03 déclarations et états | training_preferences, readiness_entries, plan_adaptation_dismissals | OPEN | OPEN | OPEN |
| C04 programmes/publication | user_programs et quatre descendants, slugs/templates publiés/références | OPEN | OPEN | OPEN |
| C05 traces et recommandations | decision_traces OWNER_LIFETIME, recommendation_episodes | OPEN | OPEN | OPEN |
| C06 corporel et consentement | body_measurements, body_consents et preuve/version/retrait ; ancien profil User distinct | OPEN | OPEN | OPEN |
| C07 social | squads, memberships, challenges, codes, partages et recommandations ; faits des tiers distingués | OPEN | OPEN | OPEN |
| C08 PLAN sources et copies | six tables possédées, sept rencontres/calibrages, limitations/préoccupations, snapshots, inputs/results SCI, ack, commandes, bindings, observations/reçus | OPEN | OPEN | OPEN |
| C09 appareil / faits locaux | partitions propriétaire/legacy, journal_v3_set_operations, journal_sets/outbox/active_session/lab, métadonnées d'attribution et demandes/retrait | OPEN | OPEN | OPEN |
| C10 exploitation et copies externes | exports JSON/CSV, backups DB/fichiers/hors site, logs/monitoring/support et opérateurs réellement déclarés ; autorité PLAN sans owner_id distincte | OPEN | OPEN | OPEN |
| C11 preuve après effacement | demandes/reçus, capacités hashées, identités retirées/exclusions de restauration, preuves d'exécution | OPEN | OPEN | OPEN |

Photo/provider : aucune donnée utilisateur correspondante prétendue présente ou
purgée ; une activation future requerrait son propre inventaire et consentement
granulaire. Le texte Body historique est une contrainte de produit à relire, pas
la preuve d'une qualification juridique actuelle de chaque donnée.

## Acte d'admission à remplir après réponses

Référence/version du paquet : OPEN. Déclaration de prise en charge personnelle :
D01 PARTIELLE du 9 novembre 2026 ci-dessus ; identité légale/signature d'admission :
OPEN. Date d'admission : OPEN.
Décisions admises et réserves ligne par ligne : OPEN. Documents contrôlés cités :
OPEN. Revue juridique/sécurité applicable et référence réelle : OPEN.

Une admission partielle doit nommer les traitements qu'elle autorise et ceux qui
restent bloqués. Les lignes ouvertes ne deviennent pas des valeurs techniques.
L'admission ne vaut ni GO BUILD du producteur, ni exception destructive tacite,
ni GO migration sur une base réelle, ni GO activation/déploiement/Store.
