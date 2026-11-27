# Une décision requise — image exacte et banc natif isolé

27 novembre 2026 — Europe/Paris. **PROPOSÉ, NON EXÉCUTÉ.** Préparation locale autorisée par le mandat SCI-OPS-QUALIFY-01 ; cloud, transfert et nouveau banc distant en attente de ce GO précis. L'ancien GO SCI03 était limité à l'image déjà présente et au montage source historique.

## Source et chaîne existante
Source unique : `1ac401f44b8af9444a8521b30cd47b7201fd1c8e`.
Archive Git locale : 73 318 400 octets, 3 367 fichiers réguliers, SHA256 `7b1230ccb42986b0533d567b6f4502d6ef202922bea1019ad9e1414cdabd857b`.
Dockerfile : `deploy/qa/Dockerfile`. Lock : `requirements-lock.txt`. Outils inchangés : `tools.qa_delivery.image_receipts` et `image_transport`.
La CI canonique 45896913157 a ses quatre checks obligatoires completed/success, relus auprès de GitHub. SonarCloud Code Analysis est failure consultatif ; le job SonarCloud réussi ne change pas ce verdict.

## Actions demandées en un seul GO
1. Déclencher **une seule tentative PREPARE_IMAGE** du workflow existant `.github/workflows/qa-release.yml` à ce SHA/ref exact, sans changement de workflow. Aucune relance après réponse perdue : retrouver d'abord le run/tentative. Ne pas poursuivre si protections, garde privée ou source divergent.
2. Attendre l'approbation humaine du run dans `qa-release`, commentaire exact `APPROVE_QA_IMAGE 1ac401f44b8af9444a8521b30cd47b7201fd1c8e`. Le présent GO permet le déclenchement ; il ne fournit pas cette approbation GitHub et l'agent ne s'auto-approuve pas. Protection relue : MFE-DSS seul, prevent_self_review=false, bypass administrateur=false.
3. Réutiliser seulement la garde privée/configuration/clés déjà existantes. Un upload chiffré par tentative, intention durable avant POST ; UNKNOWN impose lecture de cette même tentative. Archive claire ≤ 2 Gio−46 octets ; ciphertext strictement < 2 Gio. Aucun asset/image dans le dépôt public, aucun nouveau secret, dépôt, abonnement ou achat.
4. Acquérir et vérifier run/job/attempt/SHA/checks/assetID/digest, déchiffrer dans une destination privée neuve ; refuser destination existante et authentification incomplète. Transférer la même archive vérifiée au VPS existant par SSH strict ; `docker load` uniquement après contrôle des octets. Inspecter source embarquée, imageID/config, plateforme, UID, Entrypoint/Cmd et couches. Aucun tag mutable utilisé comme identité.
5. Sur le VPS `vps-491c685f` existant, créer uniquement des éléments neufs préfixés `auren-sciops01-` et label `auren.scope=sci-ops-qualify-01` : répertoire privé, conteneurs et volumes locaux sans options/bind vers données personnelles ou QA. Base **neuve synthétique**, jamais copie de la DB QA. Aucune modification Docker daemon, système, DNS, TLS, service, réseau QA, volume QA ou secret existant.
6. Runtime de qualification : network=none, aucun port publié, restart=no, UID/GID10001, rootfs ro, cap-drop ALL, no-new-privileges, 1 CPU, 2 Gio mémoire et swap total 2 Gio,128 PID, tmpfs /tmp64 Mio, logs10 Mio×3. Stage root ponctuel limité à CHOWN sur les seuls volumes neufs pour préparer permissions et fixtures ; jamais sur source/image/service existant. Vérifier le GID réel de l'image avant de fixer celui de la campagne.
7. Interdire tout overlay de source ou bundle : produit issu de l'image. Harness/profil montés séparément en ro ; fixtures read-only pour les lectures. Un clone synthétique distinct sert au témoin de concurrence, avec writer de test explicitement séparé. Les appels HTTP restent dans le namespace réseau fermé. L'activation du lecteur dans ce banc est uniquement un paramètre de fixture, sans changement du QA actif.
8. Rejouer la matrice EXECUTION_PLAN.md et relever CPU user/system, wall, RSS/AS, SQL/VM, JSON, digest, refus/reap/slots. Garder CPU enfant2/3s, AS512Mio, supervisor3s et tous les budgets canoniques. Pas d'optimisation ou hausse de plafond pour forcer PASS.
9. Précondition de mutation : ≥20 Gio libres sur Mac et VPS, mémoire disponible VPS≥3 Gio ; sinon HOLD sans purge implicite. Acquisition privée opérationnelle≤2 Gio au total (conserver séparément l'archive locale source73Mio) ; pas de purge des anciennes preuves pour faire de la place. Arrêt si conflit, ressource insuffisante ou identité divergente. En cas de manque d'espace, présenter ce seul blocage avant transfert.
10. Conserver reçus/campagnes et empreintes, puis supprimer seulement nos conteneurs/volumes après preuve de leur ID/label et absence de travail unique. Aucun prune. Conserver l'image tant que ses références/consommateurs ne permettent pas sa suppression bornée. Comparer avant/après les identités des services et ressources QA/personnelles sans afficher leurs secrets.

## Activation et rollback
Aucun démarrage de QA avec cette image. Aucun remplacement de son conteneur, config ou profil. Le rollback de la qualification est l'arrêt des seuls éléments `auren-sciops01-*` puis conservation/nettoyage vérifié de ces éléments. L'image historique et le service actuel restent les références de fonctionnement existantes.

Le raccordement SCI du lanceur QA n'existe pas encore. Après qualification, préparer SCI-ACTIVATE-01 : trois paramètres SCI, profil attesté, preuve de confiance du vrai montage et delta contrôlé du schéma de configuration/lanceur. Cet acte et ses éventuelles modifications produit seront soumis séparément ; aucun flag, chemin ou digest n'est ajouté maintenant.

## Formulation de décision
« J'autorise le PREPARE_IMAGE protégé au SHA 1ac401f44b8af9444a8521b30cd47b7201fd1c8e, la garde/transmission privée de cette même image et sa qualification dans le banc natif SCI-OPS-QUALIFY-01 décrit ici, sans modification ni activation du QA existant. L'approbation GitHub du run exact reste distincte. »
