# MOB-03 — compatibilité, recette et rollback

5 novembre 2026. **Plan exécutable, aucune recette physique ou autorisation de déploiement déduite.** PR353 reste la seule PR du change. Le SHA final testé/CI est consigné dans son reçu. Les versions ci-dessous désignent le code, pas un état de production inspecté.

## Matrice backend / client

| Backend | Client | Comportement attendu / limite | Décision de release |
|---|---|---|---|
| Canonique bf847c7 antérieur à #353 | Client canonique correspondant | Parcours historique auth/MISSION ; endpoints MOB03 ajoutés par #353 absents | Combinaison historique ; pas une livraison MOB03 |
| Backend #353 | Ancien client canonique | Routes historiques préservées ; champs/contrats ajoutés ne remplacent pas auth/MISSION | Tester la régression de séance avant rollout autorisé |
| Backend #353 | Client #353 | Signup/password et déclarations natifs ; GET poids read-only sous body_assessment_enabled + consentement actif ; premier usage honnête, snapshot/plan absents par défaut | Candidat compatible au niveau contrats/tests ; recette physique et GO déploiement encore nécessaires |
| Ancien backend | Client #353 | Nouveau GET ou déclarations peuvent répondre404 ; résultat indisponible/refusé, aucune source corporelle de repli ; signup ne doit pas être annoncé confirmé | Pas de rollout de cette combinaison ; déployer backend compatible avant client après GO |
| Backend #353 avec body_assessment_enabled=false ou sans consentement | Client #353 |403/body_consent_required ou feature désactivée ; aucune lecture de mesure, aucune obligation corporelle au premier usage | Préserver cette configuration par défaut ; ne pas activer implicitement |
| N'importe quel backend actuel | Nouveau service de demandes isolé | Aucun import de démarrage, migration, route app/web ou worker ; registre de politiques absent par défaut ; table proposée seulement en fixture | NOT_SERVED ; aucune commande de création de table en production |
| N'importe quel backend actuel | FirstUseController / FirstPlanClient | Pas d'URL/snapshot/producteur/démarrage SCI par défaut ; accès explicite à Aujourd'hui distinct d'un premier plan scientifique | NOT_SERVED ; ne pas importer les fixtures de protocole dans un adaptateur produit |

## Ordre d'une release future autorisée

1. Relever SHA backend/client, configuration réellement déployée, identifiants des builds et cible. Les valeurs `dev.auren.vnext.lab` du dépôt et version0.0.1 ne sont pas des identifiants Store approuvés. Préserver l'installation QA MOB02 ; utiliser appareil/application séparés si collision.
2. Vérifier CI obligatoire du HEAD exact, acceptations visuelles applicables, sécurité et compatibilité. Relever la politique du contrôleur et les producteurs effectivement servis ; laisser fermés ceux qui ne sont pas admis. Ni merge ni variables Expo ne valent GO de déploiement.
3. Après GO de déploiement distinct : backend compatible d'abord, puis build client identifié. Pas d'OTA vers un runtime incompatible, ni changement d'identifiant/runtime pour contourner une recette.
4. Sur environnement jetable/staging autorisé, exécuter la recette ci-dessous. Ne pas utiliser ni recopier les credentials QA privés dans un rapport. Aucune donnée réelle de mesure n'est nécessaire aux tests de compatibilité.
5. Publication externe seulement après preuves et critères de release. Le service d'effacement et la science conservent leurs propres gates : une page affichant leur absence ne prouve pas la conformité Store ou un plan utilisable.

## Recette physique — à renseigner, non exécutée par ce plan

Preuve par ligne : plateforme/versionOS, modèle, SHA/build, scénario, horodatage, résultat observé, capture/log expurgé, verdict opérateur. Android et iPhone requis ; capture web ou build Xcode ne les remplacent pas.

| Cas | Action / preuve attendue |
|---|---|
| Création / premier usage | Inscription une fois, confirmation puis page d'état ; aucune collecte obligatoire de poids/taille/matériel ; préférences, retour puis Aujourd'hui ; utilisateur reconnu ne repasse pas par une bienvenue |
| A/B | CompteA, préférences/poids sous consentement, logout puisB ; aucune valeur/commande/journal deA dansB ; réponse deA retardée neutralisée ; reconnexionA retrouve uniquement sa partition |
| Journal/reprise | Séries hors ligne, force-kill, relance ; faits conservés ; séance à reprendre prioritaire sur premier usage ; journal ancien non attribué jamais ouvert par simple nom de compte |
| Réseau | Couper durant lecture et pendant mutation de compte/préférences ; état inconnu, pas de rejeu automatique, lecture de récupération explicite ; données locales non envoyées conservées |
| Auth | Access expiré, refresh valide/refusé, changement de mot de passe et ancien credential ; retour de compte/onglet conservé, aucun logout issu d'un simple statut de demande |
| Poids | Consentement absent/retiré, vide, pages/curseur invalide, héritage sans date exclu ; aucune date inventée ou cache du propriétaire précédent |
| Suppression | Port absent : aucune demande prétendue acceptée. Tests de vrai producteur/statut après révocation seulement après politique/routes/migration et environnement autorisés ; aucun test destructif sur QA ou production |
| Accessibilité / format | VoiceOver et TalkBack, ordre du focus, tailles de texte, clavier/retour Android, petites/grandes largeurs, cibles44pt ; coque sous formulaire inaccessible aux gestes/lecteurs ; action Aujourd'hui atteignable |
| Science | Sans producteur : état explicite ; jamais READY de fixture. Vrai READY/démarrage et consentement pertinent seulement avec adaptateur admis et snapshot canonique ; aucun repli MISSION scientifique |

## Rollback sans perte des faits

- Arrêter le rollout client et revenir à un build/runtime identifié compatible. Ne pas effacer SecureStore, journal SQLite, outbox, partitions ou ancien journal pour faire fonctionner le rollback.
- Garder le backend additif compatible pendant le retour du client ; un retour backend antérieur aux nouveaux endpoints nécessite d'abord l'arrêt du client dépendant. Aucun downgrade DB destructif, DROP, reset ou réécriture de l'historique.
- Réauthentification via mécanismes canoniques si nécessaire ; un credential révoqué reste révoqué, aucune restauration de session_epoch ou de sauvegarde ne le réactive.
- Après future suppression irréversible autorisée : ne pas restaurer le compte par rollback applicatif. La protection d'effacement lors de restauration et le suivi par capacité relèvent de la politique/producteur encore bloqués.
- Consigner version retirée/remplaçante et preuves. Ce runbook ne fournit ni commande destructive ni autorisation d'exécution.
