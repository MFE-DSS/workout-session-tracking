# REL-03 — contrat proposé de preuve OVH et de configuration

15 novembre 2026. Proposition d’amendement, aucune nouvelle autorité acquise par ce document. [Scope](OVH_AMENDMENT_SCOPE_20261115.md).

## Producteur d’image et acquisition indépendante

Le job proposé `prepare-qa-image` appartient au seul workflow versionné `.github/workflows/qa-release.yml` dans `MFE-DSS/workout-session-tracking`. Déclenchement manuel sur un SHA canonique exact, aucune publication au push. Source sans fichiers ambiants : archive Git inventoriée, pas de `.env`, DB, répertoire de travail sale ou secret dans le contexte. Le Dockerfile et les dépendances verrouillées restent identifiés, plateforme fixée `linux/amd64` pour le VPS x86 observé, à revérifier avant opération.

Le reçu `qa-image-build/1.0.0` contient : repository, workflow path/ref, run_id, attempt, job, source_sha, context_sha256, Dockerfile_sha256, base_image_digest réellement résolu, platform, exported_image_sha256, exported_image_bytes, image_id, artifact_id et completed_at. Le checksum exporté est celui des octets réellement transférables, pas le hash d’un JSON descriptif. image_id est le digest de configuration de l’image chargée ; ne pas le confondre avec le digest d’un manifeste multi-architecture.

Le release verifier choisit le repository/workflow à partir de sa politique versionnée et interroge GitHub lui-même : run au SHA exact, événement autorisé, tentative exacte, job complété avec succès, artefact immuable du même run, digest téléchargé recalculé. Aucun repli sur une copie fournie par le candidat. La preuve lie la source backend réelle du candidat ; elle peut être un ancêtre canonique du JS plus récent seulement si ses propres CI et les contrats API/schéma/SCI/configuration du candidat sont effectivement vérifiés. Une OTA JS compatible ne force donc pas un redéploiement backend par simple égalité arbitraire des SHA.

Le reçu public éventuel ne contient que des métadonnées techniques. Les octets d’image restent privés/chiffrés et leur upload n’appartient pas au GO technique. Transport séparé borné à 2 Gio, fichiers réguliers, destinations nouvelles, ciphertext/checksum et référence immuable vérifiés ; aucune hausse silencieuse des caps des preuves DB. Sans stockage/custodie/transfert autorisés, l’image n’est pas disponible au déploiement et l’état reste préparatoire.

## Observateur de l’hôte

Commande SSH fixe, sans shell libre, forwarding, agent forwarding ou PTY ; `BatchMode`, host key épinglée dans un known_hosts contrôlé et référence de credential d’audit distinct du compte applicatif. Le credential et le compte ne sont pas créés par le code préparatoire. Un forced-command installé et possédé par l’administrateur lit une politique hors checkout applicatif, sans fournir un accès au socket Docker au client QA.

Entrée fermée `qa-ovh-observation-request/1.0.0` : nonce aléatoire 32 octets hex, candidate_sha256, environment_id, nom de ressource exact `auren-qa-rel03`. Champs inconnus ou requête supérieure à 4 Kio refusés. Exécution bornée à 15 s, sortie JSON au plus 64 Kio. Le nonce n’autorise aucune mutation.

Sortie fermée `qa-ovh-observation/1.0.0` : nonce et candidate_sha256 reçus, observed_at, environment_id, container_id, image_id réellement inspecté, état/health, nombre de writers, UID, mounts autorisés, ports/réseau, restart policy, limites de ressources et digest de la politique d’activation/configuration. Aucun dump d’Env, secret, owner, ligne DB, contenu de volume ou inspection générale de l’hôte. Le client exige le même nonce/candidat, âge ≤60 s et skew futur ≤10 s. La host key vient de la couche SSH vérifiée ; une chaîne echo dans le JSON n’en est pas une preuve. Le document d’observation reste dans la preuve privée ; les logs ne publient pas son contenu. L’intégrité du mainteneur, de l’hôte qualifié et du collecteur administré reste une hypothèse de confiance explicite, pas une preuve contre un hôte compromis.

Le conteneur inspecté doit utiliser l’image du reçu GitHub acquis, un seul writer, un UID non root, volume QA exact hors production, absence de mounts Docker/production, port prévu et limites approuvées. Un label OCI ou le seul fichier `.qa-source-sha` ne suffit pas. Référence de déploiement OVH propre, sans fabriquer des identifiants Render. L’observation est refaite avant la première action de publication et avant son reçu final ; incohérence → état inconnu/refus, jamais replay automatique.

HTTPS reste indépendant : validation TLS normale vers l’origine exacte, sans redirection, health de transport et version courante cohérents avec le candidat. **L’origine doit être reliée au conteneur inspecté** : politique de routage administrée et configuration runtime effectivement chargée, `server_name` QA exact → upstream QA exact → binding Docker loopback → container_id/image_id. Le collecteur ne retourne que cette correspondance QA et son digest approuvé, jamais la configuration générale nginx. Les observations avant/après les appels HTTPS doivent conserver la même chaîne ; un conteneur sain et un responder HTTPS distinct, même avec une version copiée, ne satisfont pas la preuve. L’adresse TLS effectivement jointe doit correspondre à l’hôte/routage approuvé ; CDN, proxy externe ou chaîne non attestée sont refusés dans ce premier profil. La santé ne confère pas une permission SCI ; retrait/génération inconnue restent traités par les vrais consommateurs.

## Origines et versions de cible

La seule exception OVH proposée est `https://qa.spignos.com`. Elle est conditionnée au profil OVH explicitement négocié et attesté ; aucun autre sous-domaine spignos n’est admis. HTTP, IP privée/publique directe, www/racine production, credentials, port explicite, chemin hors racine, query/fragment, sibling/tunnel et redirection sont refusés.

Introduire un profil de cible OVH v2 quand les champs fournisseur/configuration nécessaires sont présents. Garder le profil v1 Render strictement inchangé. Une cible OVH ne se présente jamais comme v1 Render, et un profil v2 incomplet ne redescend pas silencieusement. Les versions SCI/PLAN/contrats métier restent inchangées ; ce sont des métadonnées de packaging de QA.

## Configuration synthétique explicite et environnements distincts

L’ancienne configuration privée sans extension garde PLAN seul. La nouvelle extension déclarée comporte les fonctionnalités incluses et les seules références privées nécessaires. Aucun héritage de production, aucun secret inline dans Git/candidat/artefact public. Refuser doublons/champs inconnus, mauvais modes/owner/symlinks, identités vides, références absentes et clés de signature partagées entre familles.

| Famille | Paramètres du backend canonique, depuis les références privées |
|---|---|
| BODY | `BODY_ASSESSMENT_ENABLED` seulement ; `BODY_INTELLIGENCE_ENABLED` et `BODY_CAPTURE_QUALITY_ENABLED` restent désactivés. Accord courant requis pour l’acquisition, gestion minimale d’effacement conservée. |
| NUT | `NUTRITION_MANUAL_CONTROLLED_TEST_ENABLED`, `NUTRITION_BACKEND_IDENTITY`, `NUTRITION_SIGNING_KEY` |
| LIB | `LIBRARY_CONTROLLED_TEST_ENABLED`, `LIBRARY_BACKEND_IDENTITY`, `LIBRARY_SIGNING_KEY` |
| Builder | `PROGRAM_BUILDER_CONTROLLED_TEST_ENABLED`, `PROGRAM_BUILDER_BACKEND_IDENTITY`, `PROGRAM_BUILDER_SIGNING_KEY` |

Le flag BODY est celui réellement consommé par `app/routers/mobile_body_measurements.py:77,98` ; aucun nouveau flag de domaine n’est inventé. Les valeurs et références de clés demeurent privées, stables et distinctes, sans rotation implicite des références signées pendant le pilote. Configurer une capacité ne crée aucun accord BODY/NUT et n’admet aucun fait scientifique.

`backend_env` contient les paramètres canoniques autorisés ; `facade_env` contient uniquement le minimum de façade et le chemin de configuration. Tous deux sont reconstruits depuis une liste fermée dans un cwd privé vide. La façade ne reçoit pas les variables BODY qui déclencheraient `_safe_environment`; elle reste capable de refuser une contamination ambiante. SMTP, Sentry, SQL/perf sensibles restent coupés dans les deux processus. Les clés de signature n’apparaissent pas dans la version publique.

Le superviseur exige que les fonctionnalités annoncées par le candidat soient effectivement configurées et servies ; sinon refus avant exposition. L’identité de transport ajoute la liste exacte des profils effectivement servis, sans transformer une configuration en autorité de données. Les GET/version/health ne seedent, ne migrent ni ne requalifient. Le schéma est déjà program_builder_operations_01 ; seuls les consommateurs de cette tête sont réutilisés.

## Vérifications minimales du delta

Tests de reçus GitHub forgés/stales/autre workflow/SHA/attempt/image et d’observation rejouée/mauvaise clé/double writer/mount inattendu ; guards Render conservés. Test obligatoire : conteneur sain inspecté mais origine publique routée vers un autre upstream (y compris version JSON identique) → refus. Tests Python/JS symétriques de l’origine exacte et refus de toutes les autres. Tests du vrai superviseur avec environnements séparés, cas ancien PLAN seul et refus de fonctionnalités promises sans configuration. Parcours HTTP synthétiques BODY/NUT/LIB/Builder et journal/reçus possédés, sous accords applicables, sans déploiement distant.

Référence initiale de revue indépendante : `/Users/martinfeldmann/auren-review/rel03-ovh-amendment-20261115/REVIEW.md`. Une fois le contrat et son scope acceptés, le plan d’implémentation précis et les leases seront figés avant code. Les validations opérationnelles et installées restent distinctes.

## OPS-02 — garde privée qualifiée,17novembre2026

Parent canonique `d48a460fcfca5c7dfd6b6de4d9114d791d10b72d`. L'opérateur a répondu « ok » au paquet opérationnel, puis « ok continue » ; le GO est conservé dans le reçu de session et [la progression opérationnelle](../../../docs/release/rel-03/ops02/PRIVATE_CUSTODY_PROVISIONING_20261117.md). Le second approbateur humain n'est pas encore désigné. Aucun environnement protégé incomplet, rôle, secret ou build n'est créé pour contourner ce manque.

### Brainstorming / Options / Risques / Choix retenu

Attendre toutes les identités empêcherait aussi le travail indépendant sur la garde ; publier malgré leur absence affaiblirait les gates. Choix : qualifier uniquement le dépôt/release privés autorisés et livrer leur référence publique non secrète. La valeur CONFIGURED signifie référence de stockage qualifiée, pas droits d'upload disponibles ni release approuvée. Le préflight réel doit toujours revérifier private/full_name/release_id ; le workflow conserve le refus de l'environnement ou de l'approbation absente.

Référence acquise par l'accès authentifié existant : `MFE-DSS/auren-qa-private`, repository_id1461698730, ownerMFE-DSS/id156458952/typeUser, private=true. Release de garde `qa-custody-v1`, release_id448927197, cible `e58904577ab54ef5c4dd97b1c8414e6d590471d6`, draft=false, zéro asset. Aucun secret, donnée ou ciphertext téléversé. Aucun nouvel abonnement. La référence `docs/release/rel-03/proof-store.json` peut donc devenir CONFIGURED pour ce seul dépôt ; aucun identifiant secret dans ce delta.

Fichiers possédés : cette annexe, la référence JSON et le reçu documentaire lié. Tier effectif à vérifier avant contrôles ; protocole et CI réelle du nouveau SHA, quatre checks requis et merge gardé sous GOV-MERGE-01. La source image future doit être le nouveau canonique contenant CONFIGURED avec **ses propres checks**, jamais le parent d48a460. Image, QA distant, DNS/TLS, backup/rollback opérationnels et APK restent non réalisés.
