# REL-03 — décision externe à finaliser après préparation du code

**INFORMATION / NON APPROUVÉ.** Aucun fournisseur connecté ni ressource créée. Vérification de présence locale : pas de CLI/config/token Render/Railway/Fly détecté ; ce n'est pas la preuve que l'opérateur n'a aucun compte. Session/projet EAS existants accessibles, plan/consommation encore non attestés. Ne fournir aucun secret en réponse de chat.

## Proposition portable et coût vérifié le 10 novembre 2026

Render workspace Hobby (0USD de base), service `0.5c-512mb` **7USD/mois**, disque persistant1Go **0,25USD/mois** : base **7,25USD/mois hors taxes**, dimensionnement conditionné au test de mémoire/latence. Le service fournit un hostname stable `*.onrender.com` et TLS, sans domaine acheté. Nom exact/disponibilité ne sont pas inventés avant création.

Coûts variables : Hobby inclut5Go de trafic sortant ; au-delà **0,15USD/Go** selon tarif courant. Minutes de build supplémentaires selon tarif ; limite de dépense de pipeline à régler à0 au-delà des incluses. **Cette limite ne plafonne pas compute/disque/bandwidth** : ne pas annoncer un hard cap7,25/10USD qui n'existe pas. Pas d'auto-upgrade de plan, autoscaling ou nouveau service payant. Une semaine donne seulement un ordre de grandeur proratisé, pas un devis garanti ; confirmer les conditions affichées avant achat.

Le gratuit Render se met en veille et perd le FS local sans disque ; ce n'est pas la cible de continuité. Postgres géré est une alternative plus coûteuse nécessitant driver/qualification et son devis complet ; pas un changement implicite du scope. VPS existant : coûts/capacité/accès/isolation non établis, aucun acte partagé autorisé.

## Action exacte à soumettre lorsque le code est prêt

1. Confirmer choix fournisseur/plan/budget variable accepté et région du seul banc synthétique ; connecter/créer compte Render et moyen de paiement si ce fournisseur est retenu. Ne pas autoriser de déploiement par simple consultation de cette fiche.
2. Revoir le Docker/blueprint testé au SHA canonique exact ; créer **un nouveau service**, jamais nommer une ressource existante : une instance, auto-deployoff, disque1Go privé, health/version, aucun compte/email réel.
3. Configurer les références secrètes par canal contrôlé : seul secret QA existant, allowlist synthétique et copie QA complète après gel autorisé ; EXPO_TOKEN de publication QA, environnement GitHub qa-release réellement protégé. Ni token ni mot de passe ici/Git/APK.
4. Autoriser l'opération de cutover décrite au design (maintenance des seuls endpoints QA02 et arrêt/drain du writer incluant rotation refresh, backup intégral en copie, restauration sur nouveau volume, identité/auth/SCI vérifiés), aucun serveur production ou historique personnel.
5. Vérifier hostname et reçu live avant nouveau build ; autoriser la quantité/coût EAS dans le plan réellement constaté, sans achat/overage implicite. Le tarif Expo Free annonce15buildsAndroid et1KMAU, mais **ce n'est pas la preuve du quota de ce compte**.
6. Après résultat exact, approuver la première release contrôlée et le test OTA/rollback sur émulateur dédié ; publication aux appareils externes demeure une décision propre au candidat final. Aucune OTA production.

Cette fiche deviendra une décision unique courte avec SHA/fichiers/commandes/artefacts réellement prêts. Pas d'exécution payante ou de demande de secret prématurée. L'arrêt du compute ne supprime pas les données et peut laisser une facturation de disque ; destruction/fin de pilote à arbitrer séparément sans purge automatique.

## Sources primaires

- https://render.com/pricing — HTML complet et texte visible conservés hors dépôt : tarifs7/0,25/5Go/0,15.
- https://render.com/docs/web-services — hostname/TLS/health et service dédié.
- https://render.com/docs/free — veille/éphémère et limites gratuites.
- https://render.com/docs/disks — snapshots quotidiens7jours ; **ne pas les restaurer comme sauvegarde DB** ; online backup applicatif + copie hors service requis.
- https://render.com/docs/build-pipeline — limite de dépense des minutes seulement.
- https://render.com/docs/outbound-bandwidth — dépassements facturables.
- https://expo.dev/pricing et https://expo.dev/pricing.md — quotas/prix de service, pas statut réel du compte.

## Relevé effectif EAS ultérieur — 10novembre2026,12:23:46UTC

La commande officielle read-only `eas account:usage grimais --json --non-interactive`
a désormais répondu : **Free, Android5/15 utilisés (10restants), iOS0/15,
5/30builds au total**, cycle du1novembre au1décembre. Updates0/1000updaters,
0/100GiB de bande passante, dépassements et estimation facturée0cent.
Ce relevé de compte prime sur une approximation générique des quotas, sans
promesse de disponibilité future. Preuve nettoyée conservée hors dépôt dans
EAS_QUOTA_SANITIZED.json ; réponse brute privée0600, pas de coordonnées de paiement
ou URL de facturation publiées.

Le paquet externe pourra donc demander **un build Android inclus**, sans achat de
crédits ni changement de plan, puis update et rollback QA sur émulateur dédié
seulement. Le préflight doit relire les compteurs au moment de l'opération et
refuser si le quota manque ou qu'un dépassement serait requis. Aucune de ces
opérations n'est autorisée par la simple lecture du compte ou le GO BUILD du code.
Le hostname/cible hébergée reste inconnu ; Render reste proposition non connectée.
