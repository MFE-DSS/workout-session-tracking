# RELEASE-QA-02 — clôture du build, recette physique ouverte

Le build contrôlé produit un APK autonome réellement signé et téléchargeable. L'acceptation physique reste à retourner par le bêta-testeur ; l'opérateur n'a pas d'Android. Le change n'est pas archivé comme une recette complète et les processus de test restent disponibles temporairement.

## Livraison attestée

[PR #396](https://github.com/MFE-DSS/workout-session-tracking/pull/396), HEAD `ace70a70b4a721e5d4b4236bc52e4b4d60c8859d`, merge gardé `c7db051af39f7f9e14c1009f1e46cfde46bb650d`. Quatre checks requis verts, zéro revue/thread bloquant. GOV-MERGE-01, commit de merge sans bypass.

Le binaire reste construit au commit `5ed4e0e2ad8e8d80c43dc4049a30dad7f37f5c61`. Les reçus documentaires et les merges ne changent pas ce SHA embarqué. [Reçu APK](ARTIFACT_RECEIPT.json) : EAS `1c56f099-734b-4bf9-87f5-189fef95ccc5`, package `dev.auren.releaseqa02`, 0.0.1 (2), 106 411 230 octets. SHA256 : `75a1920a0b3143a2fae87d42d24fb8c3e9850063b8f2af00a60f850aaab46c99`. Signature v2 et métadonnées compilées vérifiées ; module `ExpoTopicSubscriptionModule` présent et vraie app lancée sans Expo Go / Metro. Source/config/lock inchangés depuis ce build.

[CI PR 42795457891](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/42795457891) completed/success, onze jobs : **8 091 tests backend passants / 3 ignorés**, **74 suites / 930 tests mobiles + TypeScript**, **77 tests visuels** réellement exécutés. CI canonique sur c7db051 en suivi au moment de cette publication ; fusion du reçu uniquement après sa réussite. Sonar PR #396 ERROR consultatif : quatre CODE_SMELL MAJOR S9073 dans les assertions composites du nouveau test de passerelle, zéro nouveau bug/vulnérabilité/hotspot ; couverture app 92,5 %, nouvelle non fournie. Aucun seuil/statut modifié. Les résultats canoniques exacts seront dans le reçu vivant final.

## Résultats et limites

[Résultats par flux](QA_RESULTS.md) distingue HTTP, émulateur et physique. Signup/login/token, Back/clavier décimal, saisie hors ligne→kill/reprise→ack, A/B/A, clôture et journal typé ont été exercés sur la vraie APK en émulateur Android 16 / API 36. Le parcours sept rencontres/V3/ack/commande est une preuve HTTP réelle sur témoignages synthétiques ; il n'est pas rebaptisé preuve physique/native intégrale.

Quatre erreurs de clôture SQLite sous acquisition concurrente sont conservées avant la réconciliation de la même commande de clôture persistée ; séance 2 ensuite completed et journal relu. Aucun faux PASS initial ou patch produit pour effacer ce résultat. Le message de capacités indisponibles et le slug après reprise hors ligne restent jusqu'au redémarrage à froid ; nouvelle permission de travail non présumée. Le premier timeout HTTP de 35 s est conservé séparément des cohortes réussies.

Une autre séance 3 synthétique ouverte est disponible au testeur, le compte neuf reste vide. Identifiants attribués séparément hors dépôt/APK, email réel refusé par la passerelle. Les valeurs ne demandent aucun exercice physique et ne deviennent pas des preuves personnelles. Progrès/Nutrition, bibliothèque historique native complète et certification TalkBack/grands caractères sont hors preuve intégrée.

## Qualité et conservation

Revues indépendantes code et artefact sans Critical/Important. Revue artefact : 2 704 fichiers versionnés de l'archive identiques à la source, zéro écart ; pas de revendication de build cloud reproductible. Source SDK/lock/UI/SCI et baselines conservés. npm : 29 advisories et 13 alignements restent divulgués, sans waiver ou audit CVE global induit. Ruff format reste consultatif : 679 fichiers signalés, y compris les nouveaux outils/tests ; le lint obligatoire réussit. Pas de reformatage massif ni gate affaibli.

Backend fonctionnel B8, vraie base QA migrée, bundle privé 22b066a… / inventaire 2 / génération 3. HTTPS temporaire sur poste opérateur ; pas de serveur partagé/production ou Store/OTA changé. La route identité porte un reçu de démarrage ; les routes métier gardent les gates courants. Un changement de hostname impose un rebuild.

Émulateur dédié arrêté normalement. Backend/passerelle/tunnel et worktree conservés pour le créneau distant ; aucun cleanup forcé ni autre worktree altéré. Checkout opérateur 61ca08c et empreinte de statut da808515… préservés. Pour arrêter : vérifier d'abord PID/commande/ports, fermer le seul tunnel puis les processus possédés, conserver SQLite/bundle/reçus. Aucune suppression ou migration inverse.

[Checklist unique](TESTER_CHECKLIST.md). Retour physique PASS/FAIL/UNAVAILABLE, modèle/OS/version installée requis avant acceptation pilote. DATA, qualité/dépendances avant exposition sensible et autorisation distincte de production restent ouverts. Le suivi des résultats après publication documentaire est porté par les reçus vivants des PR ; aucun succès de CI/nettoyage futur n'est anticipé ici.
