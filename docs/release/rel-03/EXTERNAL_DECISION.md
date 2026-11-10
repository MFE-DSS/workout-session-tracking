# REL-03 — décision externe unique proposée

**À APPROUVER, non exécutée.** Code intégré d67f12a, CI canonique et workflow
PREPARE réels passants : [reçu](CODE_DELIVERY_RECEIPT.md). Ce paquet ne remplace
pas la revue protégée de chaque candidat APK/OTA final.

## Opération bornée proposée

1. Connecter/créer le compte opérateur Render, sans réutiliser un service existant. Créer **un** nouveau service QA synthétique, Frankfurt proposé, une instance `0.5c-512mb`, disque privé1GiB, hostname TLS `*.onrender.com`, auto-deploy off. Sources : [Docker/blueprint et protocole](../../../deploy/qa/README.md). Capacité/mémoire, permissions UID10001, readiness et latence à qualifier ; échec = arrêt, aucune montée de gamme automatique.
2. Créer sous le compte opérateur **un nouveau dépôt GitHub privé dédié aux preuves**, nom proposé `auren-qa-private-proofs-rel03` après vérification de disponibilité. Aucun fichier personnel, clé ou DB dans le dépôt produit public. Preuves de pilote synthétique uniquement, chiffrement AES256GCM avant upload. L'opérateur reste gardien de la clé, conserve une copie de récupération hors Git ; tokens distincts upload, lecture et audit aux droits minimaux. Configuration via canal contrôlé ou interfaces des fournisseurs, aucun secret dans le chat. Avant tout transfert : confirmer accès opérateur, export/récupération, limite de taille et décision de conservation/fin de pilote. Aucune suppression automatique d'histoire.
3. Configurer `qa-release` avec revue humaine directe effective, secrets et permissions minimaux documentés ; aucune modification des protections de branche. Inspecter les bindings EAS complets puis synchroniser seulement les trois variables preview QA autorisées. Refuser toute variable inattendue/shared/secret illisible, sans suppression automatique.
4. Lors d'un créneau annoncé, mettre **le seul banc QA02** en maintenance, drainer/arrêter tous ses writers y compris refresh, exporter la SQLite intégrale et l'ancre propriétaire en copie privée, restaurer sur le nouveau volume, vérifier schéma/FK/comptes/SCI et identité. Ne pas perdre ni resemer les faits. Garder la copie originale et les reçus, un seul writer actif. Un rollback de code doit utiliser l'état courant compatible ; ne jamais redémarrer une ancienne copie après des écritures plus récentes, sans réconciliation autorisée. Le hostname embarqué de l'ancien APK ne change pas : après fermeture de l'ancien banc, les téléphones restent hors connexion à celui-ci jusqu'à une mise à niveau compatible séparément approuvée et installée. Aucune durée de rétablissement n'est promise ; aucun nouveau tunnel durable n'est proposé.
5. Après reçu HTTPS/autorité réel et revue du candidat exact : **un build Android inclus** EAS, même package/signature QA, versionCode3 ; aucune option payante/overage ou production. Relire quota et certificat avant envoi, refuser si incompatibles. Installer/upgrade sur émulateur dédié sans désinstallation et vérifier auth/SQLite/SCI/module natif/session.
6. Exercer **une update QA JS/assets puis son rollback connu**, uniquement sur le build de test installé/émulateur dédié, runtime exact et candidat revu. Aucun OTA production. Publication aux téléphones externes reste une décision propre au candidat final avec kit et résultats séparés. Le retour physique du testeur reste UNAVAILABLE jusque-là.

L'opérateur du banc doit assurer une sauvegarde applicative quotidienne et sa copie chiffrée hors service, vérifiée par restauration en copie. Avant **chaque** release, y compris update/rollback : nouvelle préparation, capture live et export hors service de la DB courante, références liées au même run/candidat. La copie de cutover ne remplace pas ces preuves fraîches. Une absence de preuve ou une incompatibilité bloque la publication ; aucune restauration destructive automatique.

## Coût et contraintes à accepter

Render proposé : Hobby0USD, compute7USD/mois + disque0,25USD/mois, soit
**7,25USD/mois de base hors taxes/variables**. Trafic5Go inclus puis0,15USD/Go selon
le relevé conservé du10novembre. Limite de minutes supplémentaires à0 ; cette
limite **ne plafonne pas compute/disque/traffic**. Pas d'auto-upgrade, domaine,
autoscaling ou second service. Relire le devis affiché avant création ; si les
conditions diffèrent ou le compte exige un autre plan, arrêter et soumettre
l'écart. La fin du pilote exige une décision : arrêter le compute ne supprime
pas forcément le coût du disque.

GitHub Releases : aucun add-on payant prévu ; dépôt privé et permissions à
vérifier avant création. Documentation : fichiers <2GiB, pas de limite globale
de release/bandwidth ; notre transport reste borné par ses contrôles de taille.
Ne pas inventer une politique de conservation personnelle à partir de ces limites.
EAS read-only constaté10novembre12:23UTC : Free, Android5/15, dix restants ;
Updates0/1000, bandwidth0/100GiB, overage0. Ce reçu n'est pas un quota réservé.

Sources : [Render](https://render.com/pricing),
[disques](https://render.com/docs/disks),
[GitHub Releases](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases),
[tarifs Expo](https://expo.dev/pricing). Tarifs Render détaillés dans
[le relevé de préparation](../../../openspec/changes/rel-03-continuous-android-qa/HOSTING_DECISION.md).

## Réponse attendue

Autoriser ou refuser ce périmètre externe et son coût variable, confirmer le
compte propriétaire à connecter et le créneau de maintenance QA02. Les écrans
compte/paiement/secret seront préparés et laissés à l'opérateur si nécessaire.
Pas d'activation de données réelles, de production, de Store ou d'envoi automatique
au testeur. Sans cette décision, le code reste livré et les autres slices produit
peuvent avancer, mais REL-03 opérationnel reste BLOCKED_EXTERNAL.
