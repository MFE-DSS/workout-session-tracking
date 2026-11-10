# RELEASE-QA-02 — fiche courte du testeur Android

**Build de recette synthétique. Acceptation physique encore à retourner.** L'APK, son lien EAS, son empreinte et sa version sont fournis dans le reçu de livraison ; ne pas utiliser un ancien APK du pilote public.

1. Télécharger l'APK attesté et installer **AUREN QA**, package `dev.auren.releaseqa02`. Si Android le demande, autoriser l'installation depuis le navigateur utilisé. Ne pas désinstaller une application personnelle pour résoudre un conflit de signature ; transmettre l'erreur à l'opérateur.
2. Lancer directement : aucun Expo Go, Metro, câble USB ou ordinateur de développement sur le téléphone. Le backend HTTPS de recette exige cependant que le poste de l'opérateur reste disponible pendant la fenêtre convenue. Une indisponibilité ne doit pas conduire à changer de serveur ou à employer un compte réel.
3. Employer seulement les identifiants de recette attribués séparément. Le compte neuf ouvre le premier passage ; le compte de démonstration contient une séance et des observations **synthétiques préparées via les vraies API**, sans preuve de réalisation physique. L'inscription, si demandée, utilise uniquement le nom attribué et un email laissé vide. Aucun vrai nom, email, mot de passe habituel, mesure ou réglage personnel.
4. Ne pas réaliser un exercice ou choisir une charge corporelle pour cette recette logicielle. Les observations fictives de test ne sont ni données personnelles utilisables pour un plan réel, ni prescription, ni validation médicale.

Pour chaque ligne, retourner **PASS / FAIL / UNAVAILABLE**, version installée, modèle/OS Android, actions et erreur exacte. Captures sans mot de passe/token. L'opérateur renseigne les preuves HTTP/émulateur séparément : elles ne remplacent pas ce retour physique.

| Test | Attendu |
|---|---|
| Installation/lancement | Vraie app AUREN QA ; aucune exception ExpoTopicSubscriptionModule |
| Inscription attribuée, login et relance | Compte possédé, token restauré ; email réel refusé par le banc |
| Retour Android et clavier décimal | Navigation cohérente, saisie/fermeture accessibles, unité lisible |
| Compte neuf et sept rencontres | Aucune charge historique exigée à l'ouverture ; contexte/réglage/familiarisation/essai/observations distincts et reprise fidèle |
| Plan et accord de temps | Incertitude visible ; accord exact explicite avant création |
| Création/reprise | Même séance possédée après réponse perdue ; aucune nouvelle clé pour réessayer |
| Journal machine/haltères | kg affichés et kg par haltère distincts, jamais additionnés en masse totale |
| Force-kill et SQLite | Saisie pending conservée, relance/relecture sans duplication ni attribution à un autre compte |
| Réseau | Couper puis rétablir la connexion du téléphone ; état hors ligne honnête, même commande réconciliée |
| A/B | Les faits et brouillons deA ne deviennent pas ceux deB ; retour àA fidèle |
| Fin de séance | Statut/faits typés relus, sans score SCI ou historique complet inventés |
| Progrès/Nutrition absents du build | UNAVAILABLE ; ne pas déclarer ces produits intégrés |

Toute préoccupation ou état inconnu reste bloquant selon le contrat ; aucune relance automatique de travail. La recette ne certifie ni sûreté, conformité, traitement réel ou production. Le retrait de l'autorité de test conserve les faits/lectures et bloque le nouveau guidage ; l'opérateur gère cette opération.
