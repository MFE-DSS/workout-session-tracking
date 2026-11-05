# MOB-03 — socle de compte natif

Statut : SOCLE API VÉRIFIÉ LOCALEMENT — publication en PR draft autorisée ; aucune livraison UI, aucun déploiement.

## Mandat du 5 novembre 2026

L'opérateur, absent une heure, demande d'avancer sur les fonctionnalités du chemin critique et de préparer la suite avec les décisions de son architecte. Le chemin adopté du 3 novembre désigne MOB-03 après MOB-02. Ce mandat ouvre le build indépendant du compte ; il ne tranche pas les décisions D-MOB03-1 à 4 ni n'autorise une suppression, une nouvelle composition UI ou un déploiement.

## Brainstorming / Options / Risques / Choix retenu

1. Porter le formulaire web : écarté, car le natif doit conserver son transport Bearer et ses primitives.
2. Dupliquer les validations : écarté, divergence future entre web et API.
3. Extraire les opérations canoniques puis les exposer en JSON : retenu, même User/password_policy/session_epoch et mêmes quotas ; aucune migration.

Périmètre retenu par l'agent sous le mandat : inscription et changement de mot de passe JSON, tests et contrats. Les quatre décisions ouvertes concernent des sémantiques indépendantes et restent explicitement en attente. Risques : course d'unicité, secret tronqué par bcrypt, quotas contournés, credentials anciens non révoqués. Les tests traversent les routes réelles et les contraintes SQL. Réponse perdue : aucune seconde identité créée ; récupération par login existant, sans annoncer une création confirmée en l'absence de réponse.

## Séparation avec MOB-02

La recette iPhone reste ouverte, arrêtée au contrôle de validation après refus de substitution. Le client QA autonome, sa séance 133 et ses preuves restent préservés. Les résultats positifs antérieurs ne valent pas passe complète ni acceptation des futures surfaces.

## Décisions de l'architecte à reprendre

D-MOB03-1 objectifs/unités ; D-MOB03-2 source du poids et compatibilité ; D-MOB03-3 effacement/rétention et commandes locales ; D-MOB03-4 acquisitions, ordre reprenable et composition native. Pas de nouvel échange externe envoyé ; sources de référence : roadmap adoptée, proposition et design MOB-03.

## Inscription JSON — résultats intermédiaires

RED observé sur la vraie route absente (404 au lieu de 201), puis 17/17 nouveaux tests verts, incluant deux créations concurrentes contre la vraie contrainte SQL. Socle web/mobile de départ : 2 tests verts. Broad sweep inscription, politique de mot de passe, isolation, D9 et inventaire : 105 tests verts ; complément auth web, quota et intégrité des jetons : 35 tests verts. Deux avertissements de dépréciation de dépendances, sans échec. Nouveau service/tests propres sous Ruff. Aucun protocole UI ou appareil présenté comme exécuté par ces tests.

Décision de reprise après réponse perdue : le serveur refuse le rejeu d'un nom déjà créé, et le login existant retrouve la même identité ; le futur consommateur doit afficher le résultat inconnu et proposer cette vérification. Ce consommateur n'est pas encore câblé. Le changement de mot de passe est la partie suivante.

## Changement de mot de passe — réalisation locale

Route JSON propriétaire et service partagé avec le web. Politique de mot de passe inchangée, nouvelles paires émises dans la transaction et anciens Bearer/refresh/cookies invalides. Test RED de la route absente, puis GREEN. Cas supplémentaire RED : deux changements simultanés réussissaient à la même époque. Correction : UPDATE atomique gardé par hash/époque attendus ; un seul succès, l'autre 409 credentials_changed, sans credentials émis. Les 29 tests du socle compte passent, dont les deux courses SQL réelles. Une perte de réponse ne donne pas un second compte au rejeu.

## État de livraison et limite effective

Le contrôle automatique a refusé le commit local : il demande un GO explicite de commit au titre d'AGENTS.md. Aucun commit alternatif, push, PR ou contournement exécuté. Le travail reste local et réversible pendant les vérifications/revue. Le GO permanent de merge ne vaut pas contournement des permissions gérées. Aucun endpoint nouveau n'est déployé ; les nouvelles compositions et le raccordement du vrai consommateur attendent les décisions et la revue visuelle.

## Revue indépendante et correction finale

Revue fraîche en lecture seule : aucun Critical, un Important et un Minor. L'Important portait sur les erreurs FastAPI 422 recopiant le corps JSON malgré SecretStr. Reproduit RED sur la route réelle puis corrigé par une classe de route limitée aux deux nouvelles API : seuls type/loc/msg sont restitués, sans input/ctx ; cache interdit. Six régressions vérifient champ manquant, type invalide et champ inattendu, pour inscription et changement. Les 35 tests du socle passent après correction. L'entrée MOB-03 contradictoire en double dans le registre est consolidée en une seule entrée courante.

Vérification finale après correction : **241 tests backend ciblés/broad verts, exit 0** ; **37 suites / 478 tests mobiles verts** ; **TypeScript exit 0** ; **Ruff nouveau code propre, budget 264 ≤ 548** ; **Bandit ciblé exit 0** ; **OpenSpec strict 5/5** ; **protocole et diff propres**. Deux avertissements de dépréciation de dépendances restent présents. Tier SHARED_CODE, aucun full sweep Python local supplémentaire. La CI réelle et Sonar de ce travail n'ont pas été exécutés, puisque commit/push restent bloqués ; aucun vert de livraison distante revendiqué.

## Choix et limites à relire

- Sous-ensemble API indépendant seulement : le gain est prêt côté serveur local, pas encore visible dans un nouveau parcours natif. Objectifs/unités, poids/compatibilité, suppression et UX restent ouverts.
- Garde atomique de concurrence : la requête devenue obsolète reçoit 409 et doit se reconnecter ; elle ne peut pas conserver une paire à une époque dépassée.
- Concurrence exécutée sur SQLite ; PostgreSQL examiné statiquement, pas exercé. Si cette cible est retenue, valider ces courses sur son runtime.
- Les écrivains existants reset/logout ne font pas l'objet d'un audit exhaustif de concurrence dans ce périmètre ; aucune certification globale d'authentification revendiquée.
- Les tests déjà verts n'ont pas été rejoués uniquement pour alimenter le journal de procédure ; le broad sweep a été rejoué après les vraies corrections.

## Résultat conservé pour revue

Le code, les tests et les contrats sont dans /private/tmp/auren-mob03-account-core, branche sb/mob-03-account-core-build, HEAD inchangé 2bb81c3. Sauvegarde locale durable du diff et des fichiers nouveaux : /Users/martinfeldmann/workout-session-tracking-mob02/.superpowers/continuity/mob03-account-core-20261105.zip et .patch, avec manifeste d'empreintes. Aucun secret de recette ni node_modules inclus. Aucun commit, push, PR, merge ou déploiement exécuté.

Contrat lisible : MOB03_ACCOUNT_API_CONTRACT.md. Arbitrages et croquis candidats : MOB03_ARCHITECT_DECISIONS_2026-11-05.md. Le commit a été refusé par le contrôle automatique au motif exact : « repository instructions require an explicit GO before committing, which the user has not provided ». La préparation d'un commit/push/PR draft attend donc une autorisation explicite reconnue par cet environnement. Le GO MERGE permanent n'est pas remis en question, ses conditions ne sont simplement pas encore atteintes pour ce change complet.

## GO de publication explicite reçu — 5 novembre 2026

L'opérateur confirme exactement « GO BUILD MOB-03 : commit, push et PR draft ». Ce GO couvre le socle API déjà testé et revu, son commit et sa publication en draft. Le refus automatique antérieur est levé par cette nouvelle autorisation explicite ; aucune autre méthode de commit n'a été utilisée entre-temps. Les 14 fichiers ont été comparés par empreinte à la sauvegarde vérifiée, sans écart avant cette seule mise à jour documentaire. Canonique relue sur le remote : toujours 90da846. Les nouvelles compositions, D-MOB03-1 à 4, la recette MOB-02 et le déploiement restent des étapes distinctes.

## Recadrage produit / science / artistique — suite du 5 novembre

L'opérateur transmet un recalage du chemin critique puis le mandat de l'agent scientifique S0. Le [relevé de direction](strategy/AUREN_PRODUCT_SCIENCE_REALIGNMENT_2026_11_05.md) consigne la boucle bodybuilding, l'entrée composée retenue, le Blueprint cible et les responsabilités. Le [registre science→produit](strategy/AUREN_PRODUCT_SCIENCE_DEPENDENCIES.md) exprime les besoins consommateurs, versions, inconnues et compatibilité sans adopter un payload hypothétique. Le brief PO designer et le chemin critique sont actualisés ; le texte intégral du manifeste cité restait alors à référencer (reçu et conservé ensuite, voir reprise ci-dessous).

Brainstorming / Options / Risques / Choix retenu : conserver l'ordre technique et expliciter les dépendances, plutôt qu'ouvrir une refonte ou des algorithmes. Les propositions de Blueprint ne sont pas promues en persistance ou prescriptions ; aucune règle scientifique, UI, baseline, asset ou donnée de production changé. MOB-02 n'est pas présenté comme bloqué par le design du bilan ; sa recette physique reste à clôturer. Les livrables S0 appartiennent au volet scientifique, aucun audit S0 complet revendiqué par cette passe produit.


## Reprise native — mandat PRODUCT DELIVERY

Le manifeste canonique v1.0 est conservé intégralement dans strategy/AUREN_MANIFESTO_V1.md (empreinte identique à la pièce opérateur). Nouveau périmètre autorisé : consommateurs natifs MOB-03, sous OpenSpec et revue visuelle avant commit UI ; pas de déploiement. Plan : openspec/changes/account-onboarding-native/native-account-delivery.md.

Réalisation locale actuelle : inscription/changement de mot de passe AuthSession, résultat incertain sans retry, génération des opérations et store sérialisé ; partition par propriétaire et inspection sans mutation du journal historique ; restauration ConnectedApp après résolution, neutralisation des retries d'un ancien moteur. Les nouveaux formulaires ne sont pas encore réalisés ; croquis consolidé soumis selon G1. Les six gaps Blueprint/compte sont dans MOB03_NATIVE_UI_DATA_GAPS.md, sans persistance de labo ou faux effacement.

Vérification intermédiaire : 39 suites Jest / 503 tests passants, TypeScript passant, OpenSpec strict 5/5 et spec protocol passants ; budget Ruff 264 ≤ 548. Revue indépendante du sous-ensemble natif en cours, donc aucune readiness finale revendiquée. Pas de nouveau commit/push, planche acceptée, CI de nouveau HEAD, build appareil ou déploiement pour cette reprise.


### Revue du socle natif et correction avant livraison

Trois constats Important de la revue indépendante corrigés : résolution propriétaire clôturée par génération jusque dans les transactions de métadonnées ; snapshot d'annulation et timer neutralisés lors du passage de compte avec garde de l'ancien callback ; validation structurelle du snapshot avant attribution, sans réparation des faits. Les scénarios de génération différée, compte A→B via Annuler et snapshot incomplet sont couverts par les vrais consommateurs ; les échecs ont été constatés avant la correction, puis les tests sont verts.

Vérification finale locale du sous-ensemble : **40 suites / 512 tests mobiles verts**, TypeScript vert ; **85 tests backend ciblés verts**, deux avertissements de dépréciation de dépendances. Les mocks de frontière SQLite ne prouvent ni rollback physique ni force-kill : preuve appareil toujours requise. Croquis de la planche toujours soumis ; aucun formulaire nouveau ni Blueprint complet livré, pas de commit/push de cette reprise et pas de CI d'un nouveau HEAD. La suite attend l'acceptation du croquis imposée par G1, puis le rendu réel et les contrats consommateurs manquants.
