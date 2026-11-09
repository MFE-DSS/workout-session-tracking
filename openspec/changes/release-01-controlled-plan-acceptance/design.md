# Design — recette synthétique versionnée

## Context

Mandat opérateur reçu le9novembre : « Prepare an isolated QA environment using
synthetic accounts and data » ; « Perform simulator/emulator tests where
available » ; arrêt pour décisions réelles du responsable, destructif non
autorisé, déploiement, interaction physique requise ou faille matérielle.
Cela autorise la préparation/recette locale non destructive ; pas de GO de
déploiement ou d'ouverture réelle. UX-CAL-02 a son scope/croquis distinctement
acceptés ; ses futurs pixels ne remplacent pas cette preuve de basefe9.

## Brainstorming / Options / Risques / Choix retenu

Reprendre une DB QA ancienne brouillerait les preuves ; utiliser production
sortirait du mandat. Choix : nouvelle DB/bundle/serveur loopback, APP_ENV=test,
comptes synthétiques, capacités effectivement lues et reçus par scénario.
Coût : recette contrôlée uniquement, politique/finalités/persistances réelles
et compatibilité de la cible finale à faire accepter séparément.

## Environment

Source serveur et JS : fe9f6e9, copie isolée /private/tmp/auren-release-01.
Bundle inventory2 neuf via vrai builder dans une destination privée neuve,
manifeste/hash + sources effectivement vérifiés. DB synthétique neuve uniquement,
bootstrap exact et DDL PLAN existant explicites ; aucun Alembic head supposé
depuis create_all. Inventorier tables/indexes et empreinte du schéma réel.
Autorité opérationnelle génération/pins activée uniquement dans ce banc test,
flags de collecte/évaluation/création/guidage observés, off dans dépôt inchangé.

Ports réservés8130backend/8131Metro, loopback ; Android reverse local si nécessaire.
Nouvelle app/projet QA privé peut importer le vrai ConnectedApp et les dépendances
déjà installées ; source de chaque module et version d'hôte natif relevées.
Expo Go n'est pas un APK autonome AUREN ni une release signée. Toute limite est
rapportée ; pas d'installation sur appareil utilisateur sans besoin/autorisation.

## Acceptance and evidence

Signup/auth/ownership, première ouverture sans réglage, sept profils et unités,
choix/familiarisation/observations/qualification, interruption/relance/réseau,
A/B, vraiV3/ackexact/idempotence/exécution/journal historique. Pour chaque ligne :
source/version, environnement, actions effectivement effectuées, donnée
synthétique, preuve et résultat. Tester via HTTP réel et natif quand disponible ;
ne pas rebaptiser un test serveur en test natif.

Appareils : discovery read-only d'abord ; ne manipuler que simulateurs/AVD
attribués au banc et processus possédés. Device/OS/build/backend exacts exigés
sur physique. Absence d'appareil/confiance/build compatible demeure OPEN.

## Rollback and quality

Couper flags d'acquisition/évaluation/création/guidage, conserver DB/faits/bundle
et lecture/reconciliation. Vérifier refus de nouveau travail sans effacement,
ne pas downgrader DDL. Arrêter seuls processus possédés après reçu ; conserver
preuves horsWT. Réutiliser contrôles CI canoniques exacts comme preuve historique,
sans revendiquer de nouveau run avant publication réelle d'une PR.

Relire B404/B603 packaging : chemin/interpréteur/worker fixes attestés, pas de
shell, JSON stdin, timeout et erreur neutralisée. Vérifier source réellement
appelée et menaces d'hôte/bundle mutable ; aucun verdict global false positive.
Une faille confirmée est STOP ; pas de seuil ou issue modifiée.

## Observed acceptance and remaining target work — 9 novembre 2026

[Identité du banc](../../../docs/release/release-01/QA_ENVIRONMENT.md),
[résultats](../../../docs/release/release-01/QA_RESULTS.md),
[brief des artefacts internes](../../../docs/release/release-01/INTERNAL_BUILD_BRIEF.md).
La chaîne HTTP réelle a traversé les sept profils synthétiques, snapshot/V3,
ack altéré refusé, ack exact, même séance et journal PER_IMPLEMENT. Le retrait
réel observé est génération3 ACTIVE →4 WITHDRAWN →5 ACTIVE de test : autorité
servie absente/applicabilité BLOCKED sous retrait, faits et lectures conservés.
Le flag configuré de guidage reste true ; la sonde a été corrigée pour ne pas
le confondre avec l'autorité. Coupure de tous les flags et matrice exhaustive
des nouvelles mutations sous retrait restent à éprouver. Le rejeu CREATED
n'est pas une permission courante ; aucun fallback permissif V1.

iOS : vrai ConnectedApp dans ExpoGo58.0.7/iOS26.3, connexion/récupération/
revalidation/ouverture de saisie observées ; signup, décimal, écriture native,
accessibilité et parcours entier non prouvés. Shutdown inattendu du simulateur
attribué, cause non établie ; appareil personnel préservé. Android : vrai
ConnectedApp bloqué par ExpoTopicSubscriptionModule absent dans Go58.0.5,
version encore annoncée dans le reçu officiel SDK58. Aucun PASS natif Android.

Un client natif compatible et des artefacts installables attestés restent à
préparer ; aucun APK produit. Java25 seul ne valide pas la toolchain :
SDKplatform/build-tools absents et capacité disque de build non établie.
Le profil EAS pilot existant pointe le backend public, donc ne constitue pas
la configuration isolée du banc. Toute future cible QA doit être revue et
joignable depuis les vrais appareils ; la distribution interne d'un APK ne
requiert pas de publication Store. Aucun changement de profil ou build ici.
Le physique, la politique DATA et le GO de déploiement restent distincts.
