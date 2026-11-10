# RELEASE-QA-02 — APK de recette distante

**APK autonome réellement construit ; recette physique en attente du bêta-testeur.**

L'opérateur n'a pas d'Android : la direction reçue remplace le premier projet USB par un téléchargement autonome et un backend HTTPS temporaire sur son poste. Le GO BUILD contrôlé est acquis. Aucun serveur partagé/production, Store, OTA, version SDK, lock, UI ou règle SCI n'est modifié.

Le [reçu APK](ARTIFACT_RECEIPT.json) porte URL EAS, binaire, SHA256, signature et identités exactes. Build EAS `1c56f099-734b-4bf9-87f5-189fef95ccc5`, source propre `5ed4e0e2ad8e8d80c43dc4049a30dad7f37f5c61`, version 0.0.1 (2), package `dev.auren.releaseqa02`. Les futurs commits documentaires ne changent pas cette provenance. Toute modification produit/config/lock impose un nouveau build, pas un réétiquetage du binaire.

Le véritable upload EAS de 59 956 222 octets (3066 entrées), empreinte `582bb829316ede805fd5a34931508044f65392702cc0e94759bd0445c28c386e`, est conservé hors dépôt avec correspondance des sources/config/lock. EAS a exécuté `:app:assembleRelease`, BUILD SUCCESSFUL, image ubuntu-26.04-jdk-17-ndk-r27b-sdk-58. Le binaire téléchargé vérifie sa signature RSA2048/v2. Le DEX contient ExpoTopicSubscriptionModule ; assets/app.config contient le SHA source et la cible HTTPS attendus. Le manifeste effectif cible API36/min24, non debuggable, sans autorisation de cleartext. Les permissions héritées notifications/stockage/overlay sont inventoriées, sans prétendre à une revue de diffusion Store.

## Backend borné

Backend app/SCI `b8f5ffc2d6671521cbc276ab87397540aed60bb7`, fichiers fonctionnels inchangés au commit APK. Nouvelle base SQLite synthétique réellement migrée base→head `plan_v3_20261107_01`, 41 tables, zéro erreur FK. Bundle privé `22b066a0fb363b1bd435323269bad8a7fa47e4149f18b91e4b039e89d8352dfc`, inventaire2 et autorité génération3 après retrait/restauration de test. Aucun create_all/stamp, import personnel ou fixture de succès dans le runtime.

Passerelle loopback bornée, authentification/inscription limitées aux comptes synthétiques attribués, aucun email réel ni route web/admin/fichier. HTTPS par tunnel Cloudflare temporaire ; sa terminaison TLS ne constitue pas une politique DATA. Le poste/backend/tunnel doivent rester disponibles. La route d'identité est un reçu de démarrage, pas un moniteur d'autorité actuel. Les vrais endpoints V3 contrôlent la génération. Si le hostname change, le build figé doit être remplacé.

## Vérifications constatées à publication

- Local : 86 tests backend ciblés/broad ; 74 suites/930 tests mobiles et TypeScript ; config finale17, gateway23. Scope ISOLATED : pas de full sweep backend local. Ruff neuf, budget260≤548, Bandit, Gitleaks, protocole/OpenSpec21/21 passants. Revues indépendantes sans Critical/Important résiduel ; défauts de frontière corrigés RED→GREEN avant exposition.
- API réelles : sept rencontres synthétiques guidées→V3 limité→BUDGET_UNCERTAIN/UNKNOWN→ack altéré409/exact ELIGIBLE→même séance7exercices/14séries→journal RDL PER_IMPLEMENT, propriétaire étranger404. Deux cohortes réussies ; un premier timeout35s conservé, non effacé par les suivantes. Une cohorte tracée :170appels/0timeout/max6,166s.
- HTTPS distant réel : login, inventaire/génération3, exécution séance2, rejeu CREATED identique et propriétaire étranger404. Cela ne prouve pas une interaction native ou physique.
- Retrait de test : nouvelle génération WITHDRAWN bloque guidage/applicability ; faits/relecture/CREATED conservés, puis restauration génération3. Ce test ne prétend pas avoir coupé tous les flags ni tester un rollback destructif.
- APK : installé sur émulateur neuf Android16/API36, vraie app lancée, inscription native sans email réussie, token restauré après force-stop, connexion native à la séance synthétique existante. Aucune exception de module natif. Recette complémentaire et CI finale/canonique encore à consigner après leurs résultats.

Le premier lancement via monkey a échoué dans l'utilitaire système ; lancement explicite de MainActivity réussi. Ce n'est ni un crash de l'app ni une preuve physique.

## Dette de dépendances et limites

Graphe SDK58/RN0.88 conservé ; install --check signale13alignements, EAS construit néanmoins le graphe existant. npm audit conserve29entrées (3high/25moderate/1low), dont node-forge/zod dans la chaîne CLI : aucune réparation forcée ni déclaration d'innocuité. L'export Android local source-map ne contient ni node-forge, zod ou code-signing-certificates ; il contient le shim metro-require CLI. Cette preuve de fermeture locale ne vaut pas audit CVE de tout l'APK. Signature effective vérifiée par apksigner ; aucune entrée PEM/PKCS12 non fiable ou serveur Metro exposé par ce banc. Réévaluation sécurité/dépendances requise avant élargissement sensible/production.

[Checklist unique](TESTER_CHECKLIST.md). Identifiants séparés hors Git/APK. Aucun exercice physique demandé : les valeurs de recette sont fictives. Progrès/Nutrition non intégrés et recette Android physique restent UNAVAILABLE, jamais PASS par extrapolation. CI/Sonar final, retour testeur, DATA et autorisation distincte de production restent des gates à consigner ; l'APK n'accorde ni conformité ni readiness production.
