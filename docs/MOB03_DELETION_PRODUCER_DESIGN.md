# MOB-03 — producteur d'effacement : design et arbitrages restants

5 novembre 2026. **Proposé, NOT_SERVED : aucune route/table serveur ou suppression ajoutée.** Inventaire d'implémentation : [matrice](MOB03_DATA_RETENTION_MATRIX.md), [graphe des23tables](MOB03_ACCOUNT_DATA_GRAPH.json). Le mandat DATA COMPLETION autorise préparation du producteur et fixtures, pas un effacement destructif sans politique. Les choix techniques ci-dessous sont des contraintes de réalisation, pas des questions à rouvrir.

## Autorité et cycle proposé

1. Entrées mobile et web dédiées partagent le même service : mobile Bearer ; web session/CSRF ; jamais token dans URL ni attribution par username. Les routes futures et leur migration OpenSpec doivent être revues avant apply. Aucun endpoint proposé n'est présenté comme déjà exposé.
2. Réauthentifier via account_lifecycle, vérifier identité active/hash/epoch puis CAS avant acceptation. Aucun mot de passe dans demande/reçu/log/outbox. Une simple vérification cliente n'est pas une autorisation serveur.
3. Demande durable liée à propriétaire + request_id, contrainte d'unicité et contrôle concurrent transactionnel. Une même clé rend la même opération ; une autre clé ne crée pas deux opérations actives pour un propriétaire. Erreur avant commit ne signifie pas acceptation. Aucun retry automatique d'une mutation après réponse perdue.
4. Avant politique admise : refus autoritaire explicite ou POLICY_REQUIRED, jamais acceptation/revocation/purge simulée. PENDING veut dire demande acceptée en attente, pas effacement réussi. Une demande rejetée peut être relue puis renouvelée explicitement avec lien vers la précédente ; unknown/submitted/pending ne se renouvellent pas silencieusement.
5. Worker seulement après politique revue, scope figé, preuve d'appartenance du graphe et verrou/CAS. Révocation de l'époque et fermeture aux nouvelles écritures au **commit de la transition autorisant le début irréversible**, pas lors d'une validation/attente/refus. Aucun credential ne peut écrire pendant un effacement commencé. Les erreurs avant cette transition ne révoquent rien ; après début irréversible, ne pas prétendre restaurer un compte par un simple REJECTED.
6. Chaque étape de graphe/purge/copie est idempotente, avec reprise et preuve d'avancement. Les FK CASCADE déclarées ne suffisent pas : références sociales sans cascade, traces immuables OWNER_LIFETIME, programmes publiés/faits d'autrui, exports et sauvegardes doivent suivre la politique approuvée. Aucun UPDATE d'anonymisation de traces immuables ni DELETE users aveugle.
7. DELETED seulement après preuves de révocation, effacement du périmètre et protection de restauration. Reçu authentifié, owner_id/request_id/version/policy_ref/instant explicites et portée vérifiable ; champs JSON seuls ne prouvent rien.401/404, token révoqué ou compte disparu restent unknown.

## Reprise après révocation et propriétaire supprimé

Un GET /auth/me ne pourra plus authentifier un compte supprimé. Le futur serveur doit donc fournir **avant** la transition irréversible une capacité de suivi propre à la demande, conservée séparément des credentials et du journal. Elle ne permet que lire le résultat de cette demande ; aucune création de séance ou suppression d'un autre compte. Transport hors URL, preuve cryptographique serveur, rotation/révocation et accès web équivalents ; pas de fallback username/email public.

Contenu de reçu, lien avec ancien propriétaire et durée de disponibilité nécessitent la décision de politique ci-dessous. Aucune clé/ticket secret ou table de suivi serveur n'est créée dans cette passe. Le port actuel reste absent ; la récupération hors token de compte est un contrat futur à tester avec le vrai producteur, pas une capacité prétendue livrée par les tests SQLite locaux.

## Client réalisé et garanties vérifiées

Le client vérifie /auth/me avant demande, conserve une clé non secrète dans SQLite de métadonnées, réserve/claim atomiquement, relit après interruption et ne rejoue pas la mutation. Refus non vérifié→unknown. La marque propriétaire retirée est persistée avant logout/nettoyage ciblé ; les réponses d'un compte quitté sont neutralisées. Aucun reset global du journal.

Tests d'intégration : vrai AuthSession/createTransport, vraie fermeture/réouverture SQLite Node, un envoi concurrent, intention conservée/relecture pending, retrait persistant et resolveJournal réel refusant l'ancien propriétaire en ligne/hors ligne ; un autre propriétaire reste valide. Cela ne prouve ni force-kill natif ni protection de sauvegarde/reinstallation sans le futur producteur serveur. Aucune suppression réelle exécutée.

[Fixtures de protocole](fixtures/mob03-deletion-producer.v1.json) : SYNTHETIC_TEST_ONLY_NOT_SERVED, incluant pending, politique absente, refus vérifié/non vérifié, inconnu, preuve incomplète et completion simulée. Elles testent le consommateur ; aucun reçu de suppression réel ni autorité de production n'en découle.

## Seuls arbitrages légaux / de politique encore ouverts

| Choix restant | Décision attendue du responsable | Dépendance concrète |
|---|---|---|
| Sort des catégories de données | Effacer/conserver, motif légal précis, durée si conservation et responsable ; exception explicite à l'invariance pour suppression volontaire | Matrice et graphe existants, notamment traces OWNER_LIFETIME, mesures/consentements et références sociales/publications |
| Copies et sauvegardes exploitées | Inventaire réel des copies, durée/purge, responsable, exclusion après restauration et communication des limites | Aucun délai arbitraire choisi depuis le défaut30jours d'un script ; exports déjà téléchargés à distinguer |
| Faits locaux non envoyés / non attribués | Sort de ces faits lors de fermeture de compte, conservation/effacement volontaire et durée éventuelle | Pas de purge d'un journal non attribué depuis l'identité courante |
| Demandes/reçus après effacement | Contenu minimal, lien résiduel à l'ancien propriétaire, base légale et durée de disponibilité/conservation des preuves | Rend possible le suivi après révocation sans conserver implicitement une identité complète |
| Responsable et information publique | Responsable/juridiction, URL réelles confidentialité et demande web, textes de finalité/retrait/suivi | Aucun lien Store ou conformité fictifs ; le parcours app/web technique est déjà une contrainte acceptée |

Aucun arbitrage sur «quelle chronologie ?», inventaire matériel, géométrie UI, réauthentification ou idempotence n'est redemandé. Les politiques choisies ouvriront le design d'exécution/migration et sa revue, puis les tests destructifs uniquement sur fixtures isolées autorisées. Elles ne valent pas GO déploiement.
