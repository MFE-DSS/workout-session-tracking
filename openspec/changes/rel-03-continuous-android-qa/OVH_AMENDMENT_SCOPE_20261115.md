# REL-03 — adaptation technique du banc OVH existant

15 novembre 2026. Parent vérifié : **683e88313b0c2c5866f0594766213569628d1659**. **TECHNICAL_BUILD_AUTHORIZED / NO_DEPLOYMENT_AUTHORIZATION.** Le GO REL03 du 10 novembre, les merges BODY/NUT/MOB06/MOB07 et leurs validations restent acquis. Ce delta ne les rouvre pas. Il ne crée aucun service, domaine, secret ou binaire.

## Brainstorming / Options / Risques / Choix retenu

- Render impose un fournisseur supplémentaire que l’opérateur n’a pas retenu. Son chemin existant reste préservé, sans achat ni activation.
- Une simple URL de tunnel ou une déclaration `/__qa_version` ne prouvent ni stabilité ni source exécutée. Elles ne deviennent pas des substituts à l’observation authentifiée.
- **Proposition retenue pour ce delta :** adapter la préparation existante à un service QA isolé sur OVH, avec origine exacte proposée `https://qa.spignos.com`, preuve indépendante source→image→conteneur et configuration synthétique explicite des quatre fonctionnalités livrées. Cette origine reste non provisionnée ; son admission de politique n’est pas une opération DNS.

## Livrable technique borné

1. Distinguer les observateurs Render et OVH sans affaiblir le premier. La branche OVH requiert un reçu d’image acquis directement auprès de GitHub et une observation SSH fraîche du conteneur réellement actif ; ni le candidat, ni un label OCI, ni l’application ne s’auto-attestent. La chaîne de routage réelle doit relier l’origine HTTPS à ce même conteneur, pas à un responder distinct.
2. Admettre uniquement l’origine OVH exacte proposée, sous le profil OVH. Les racines spignos.com/www, domaines voisins, autres sous-domaines, tunnels, ports, credentials, fragments et redirections restent refusés. La configuration native finale et son fingerprint restent à produire sur la cible réellement autorisée.
3. Fournir une configuration privée optionnelle explicite BODY/NUT/LIB/Builder. Son absence conserve le comportement historique PLAN seul ; un candidat déclarant ces fonctionnalités exige leur configuration complète. Aucun héritage du `.env` partagé.
4. Séparer l’environnement du backend canonique de celui de la façade : transmettre `BODY_*` au backend ne doit pas faire échouer la garde de la façade, qui refuse justement ces variables ambiantes. Conserver SMTP/Sentry/log SQL sensibles désactivés.
5. Relier les contrats effectivement servis et les identités de fonctionnalités au candidat. Le schéma est déjà **program_builder_operations_01** : aucune nouvelle migration, aucun nouveau repair de backup. Les accords BODY et NUT restent indépendants et les permissions SCI viennent du runtime courant.
6. Conserver préparation non distribuable, approbation de release protégée, signature/package QA02, distinction native/JS, stockage possédé, export/restauration en copie et refus de rollback incompatible.

## Preuve source et transport d’image

Contrat détaillé : [OVH_EVIDENCE_AND_CONFIG.md](OVH_EVIDENCE_AND_CONFIG.md). Le producteur proposé est un job explicite de préparation d’image dans le workflow existant, au SHA exact. Son reçu immuable relie l’archive Git propre, le Dockerfile, la plateforme, le checksum de l’image exportée et son imageID. Le pipeline réacquiert run/job/artefact auprès de GitHub, sans prendre ces faits pour vrais depuis le candidat.

Le transfert de l’image réelle est séparé du paquet de preuves DB : **les limites DB 128 Mio/fichier et 256 Mio/paquet ne changent pas**. Transport d’image privé et chiffré, taille maximale proposée 2 Gio, aucun upload public. Créer/configurer le stockage privé et ses credentials, uploader une image ou la charger sur OVH restent des opérations externes non autorisées par ce GO technique. Sans ce transport, un reçu de préparation ne vaut pas déploiement. Une image fabriquée manuellement reste OPERATOR_ATTESTED ; elle n’est pas renommée preuve indépendante GitHub.

## Fichiers possédés, sans chevauchement produit

| Fichiers | Delta autorisé après décision |
|---|---|
| `tools/qa_delivery/pipeline.py`, nouveau `ovh_observation.py` | Dispatch fournisseur, acquisition GitHub du reçu et observation SSH bornée ; contrôles avant et après publication conservés. |
| Nouveau `image_receipts.py`, script d’observation sous `deploy/qa/` | Producteur/validateur du reçu et commande fixe d’audit ; aucune installation distante par le pipeline. |
| `tools/qa_delivery/server.py`, `identity.py` | Configuration privée des fonctionnalités et environnements enfants distincts, contrats de transport explicites. |
| `tools/qa_delivery/releases.py`, `clients/mobile/qa-delivery.config.js` | Origine OVH exacte et profil de cible versionné ; anciennes cibles Render restent strictes, aucun downgrade implicite. |
| `.github/workflows/qa-release.yml` | Préparation d’image explicite non distribuable, credentials sélectionnés par fournisseur, aucun acte de déploiement ou publication au push. |
| `tests/test_qa_delivery_{pipeline,server,bootstrap,releases,identity,proofs}.py`, nouveaux tests observation/image, `clients/mobile/src/native/qaDeliveryConfig.test.ts` | Témoins de confiance, isolation, compatibilité et refus ; aucun changement de seuil. |
| `deploy/qa/README.md`, documents REL03, registre et change existant | Reçus, préflights et séparation des autorisations. |

`app/`, modèles/migrations, consommateurs ConnectedApp, journal métier, scientifique, primitives DA08, package/lock et SDK sont hors scope. Si un changement s’y révèle nécessaire, il doit être exposé séparément avant application.

## Gates d’exécution après GO technique

- RED→GREEN : faux reçu candidat, mauvais workflow/run/SHA/attempt/digest, imageID différent, nonce rejoué, host key/compte/origine différents, observation périmée, double writer ou config/volume non conforme → aucune publication.
- Tests réels locaux : base synthétique déjà migrée, serveur supervisé et quatre familles HTTP, accords distincts, anciennes commandes/reçus préservés ; secrets uniquement dans références privées et aucun POST automatique de reprise.
- Compatibilité ancienne configuration PLAN/Render et refus des anciennes versions OVH incomplètes ; nouveau profil sans cible attestée reste non distribuable.
- `check_scope` avant checks. YAML/outils partagés : tier effectif respecté, sweep local borné seulement s’il est requis, aucun `pytest -n auto`. CI réelle du HEAD exact, sécurité, revue indépendante et merge sous GOV-MERGE-01.
- Pas de nouveaux pixels : aucun écran, bouton ou composant visuel n’est modifié. Un delta visible imprévu sort de ce scope et retrouve son gate propre.

## Frontières opérationnelles conservées

Ubuntu 25.04 observé sur le VPS est hors support : qualification/mise à niveau par le mainteneur avant nouvelle exposition. Aucun upgrade/reboot ou changement de service existant ici. L’utilisateur d’audit, host key, politique d’observateur, volumes, DB synthétique, secrets, DNS/TLS et règles réseau exigent un paquet opérationnel et un GO distincts. Aucun compte cloud ou coût supplémentaire n’est supposé accepté.

L’ancien QA02 ne reçoit ni OTA ni nouveau backend par ce delta. Continuité de son DB/secret/ownership encore non établie : aucune réutilisation d’identifiants dans une base neuve. APK/OTA, activation réelle, appareils externes et acceptation physique restent séparés.

## Décision reçue, après cette proposition

Autoriser **la seule adaptation technique** décrite ici : observateur OVH et reçu d’image, politique d’origine exacte proposée, configuration synthétique explicite, tests/revue/CI/livraison du code préparatoire. Aucun service, secret, DNS/TLS, transfert d’image, build APK/OTA ou déploiement n’est inclus. Le prochain candidat reste NOT_READY jusqu’aux preuves opérationnelles et installées.

GO reçu : « Autoriser le build technique REL‑03 OVH », call_657199a80f2441d3b3bd3d450dfaaabf. [Reçu exact](OVH_BUILD_AUTHORIZATION.json). La proposition ci-dessus reste le scope accepté ; aucune opération externe n’en découle.
