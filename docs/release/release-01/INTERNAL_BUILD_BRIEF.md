# RELEASE-01 — prérequis du prochain build interne installable

9 novembre 2026. **BRIEF_ONLY / NO_APK_PRODUCED / NO_BUILD_OR_DEPLOY_EXECUTED.**
Objectif : obtenir des artefacts Android et iPhone dont la provenance et le
backend QA sont attestés, pour reprendre la recette autorisée. Ce document
n'exécute aucun build, provisioning, upload, installation, Store ou déploiement.

## Constat sur les cibles disponibles

La source testée contient Expo 58.0.17, React Native 0.88.0 et notamment
expo-notifications 58.1.6 ; aucune dépendance n'a été modifiée. Le vrai
ConnectedApp fonctionne partiellement sur iOS/Expo Go 58.0.7, tandis qu'Android
Expo Go 58.0.5 échoue sur `ExpoTopicSubscriptionModule`. La présence du SDK 58
ou d'un hôte Expo Go ne démontre donc pas à elle seule la compatibilité native.
Un dev client compatible, puis un artefact QA autonome attesté, sont les
cibles utiles pour poursuivre ; la composition native doit inclure les modules
réellement importés, sans retirer un contrôle pour faire disparaître l'erreur.

Le profil existant `clients/mobile/eas.json` nommé `pilot` décrit déjà une
distribution interne Android `buildType: apk`, `developmentClient: false`.
Il pointe toutefois `EXPO_PUBLIC_API_URL` vers le backend public configuré.
Ce profil n'est pas la configuration du banc synthétique et n'a pas été lancé.
Il faut une cible QA explicite revue avant toute construction ; réutiliser
aveuglément ce profil mettrait en cause l'isolation et la traçabilité attendues.
Aucune publication Google Play ou App Store n'est nécessaire pour un APK QA
installable distribué en interne.

## Conditions à satisfaire avant construction

| Condition | État observé / opération attendue |
|---|---|
| Source finale | Pinner SHA propre du produit et lockfile, dépendances/plugins/config, puis hash du manifeste JS ; toute évolution UX-CAL ultérieure a sa propre recette |
| Point d'entrée | `EXPO_PUBLIC_API_URL` doit sélectionner le vrai ConnectedApp et la cible QA ; `EXPO_PUBLIC_GALLERY` absent. Aucun fallback de galerie ou fixture READY |
| Compatibilité native | Produire/identifier un dev client correspondant au graphe natif réel et confirmer le chargement Android/iOS ; Expo Go observé n'est pas un substitut à ce contrôle |
| Backend accessible | Choisir un accès QA joignable depuis la cible, sans credentials production. Loopback de l'hôte n'est pas celui d'un téléphone ; établir transport, accès et restrictions de réseau explicitement avant usage physique |
| Base / science | DB neuve synthétique, migration réellement appliquée/empreinte, bundle/pins exacts, provenance et permissions, génération ACTIVE de test et flags observés ; ne pas revendiquer un replay Alembic depuis create_all |
| Comptes / données | Comptes synthétiques dédiés, aucun compte personnel réutilisé, credentials hors dépôt et APK ; cycle de conservation du banc consigné. Traitement personnel/effacement réel attendent politique applicable |
| Toolchain locale Android | Java 25 détecté mais compatibilité Gradle/JDK cible non validée ; SDK platform et build-tools requis absents. Établir les versions depuis la configuration native générée du SHA retenu, puis fournir une toolchain compatible |
| Capacité du poste | Environ 8,9 Gio libres au relevé ; budget de build non établi. Prévoir une capacité suffisante ou un builder autorisé, sans effacer le travail opérateur ni télécharger automatiquement de gros SDK |
| Choix local / EAS | Trancher explicitement. La voie distante exige compte/service, accès réseau, coût, credentials et autorisations applicables ; aucune soumission distante déduite de ce brief |
| Identité / signature | Android package/versionCode et signature QA à attester ; iPhone : bundle/version/build, profil, signature et appareils cibles autorisés. Ne pas écraser le build personnel existant sans interaction requise |
| Résultat installable | Android : véritable APK avec SHA256, taille, package/version/signature, logs et provenance de build. iPhone physique : artefact signé compatible et installation réelle attestée ; un binaire simulateur ne suffit pas |

Les versions SDK/JDK finales, identité de signature, distribution iOS et URL QA
physique sont **à établir**, pas des valeurs inventées ici. La présence de Java,
d'ADB, d'un émulateur ou d'une identité locale ne prouve pas qu'un build a réussi.
Un client de développement dépendant de Metro doit être distingué du binaire
QA autonome ; ce dernier doit être éprouvé installé avec son vrai bundle JS.

## Reçu minimal après construction et installation

Pour chaque artefact, relever SHA source et lockfile, versions de toolchain,
commande/profil effectifs, logs, identifiant de build, empreinte de l'artefact,
plateforme/architecture, application/version/build, signature, backend et
configuration sans secret. Après installation : device/modèle/OS, build
réellement lancé, source/backend attestés et scénarios effectivement exécutés.
Les IDs personnels/signatures détaillées restent dans le dossier de preuves
privé, avec un résumé publiable expurgé.

Reprendre ensuite tous les scénarios natifs ouverts de [QA_RESULTS](QA_RESULTS.md),
puis la matrice physique Android/iPhone. Une réussite de compilation ne ferme
pas ces scénarios. Le téléphone actuellement installé 0.0.1(1), dont le SHA et
le backend restent inconnus, ne peut pas être réétiqueté comme nouveau build QA.

## Rollback, risque et décision de release

Sur la cible choisie, préparer la fermeture contrôlée des flags applicables et
le retrait de l'autorité sous une génération nouvelle, en conservant faits,
snapshots, commandes et lectures. Vérifier l'applicabilité BLOCKED et le rejeu
CREATED sans nouvelle permission ; aucun fallback permissif V1, effacement,
downgrade DB ou restauration de données supprimées. La sonde locale a éprouvé
le retrait d'autorité, pas un rollback de binaire/cible réelle ni la coupure
de tous les flags. Une restauration d'autorité nécessite les pins, l'accord
applicable et une nouvelle génération ; elle ne doit pas être automatique
pour contourner un retrait.

Avant exposition externe, compléter la revue privacy/sécurité et les contrôles
d'hôte décrits dans [PACKAGING_SECURITY_REVIEW](PACKAGING_SECURITY_REVIEW.md),
la politique DATA applicable et le plan de rollback propre à la cible. Les
quatre contrôles GitHub obligatoires et Sonar consultatif restent en place.
La demande finale de déploiement n'est pas prête : cible, artefacts, recette
physique et risque restent incomplets. Le GO de déploiement est une décision
distincte de la livraison documentaire et de GOV-MERGE-01.
