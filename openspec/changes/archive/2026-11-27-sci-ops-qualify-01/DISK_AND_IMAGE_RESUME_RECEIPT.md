# Reçu effectif — disque et image, 27 novembre 2026

**Nettoyage borné exécuté ; seuil Mac PASS. Image non construite : première tentative arrêtée par sa garde d'approbation. Aucun second dispatch, aucune acquisition ou écriture distante.**

## Disque
Les28entrées ont été relues avec identités, propriétaires, device/inode, dates, parcours canonique, descendants, liens et références de processus/cwd/fichiers ouverts. Les arguments/environnements bruts n'ont pas été affichés ni conservés par cette campagne. Contrôle avant suppression répété, suppression par liste exacte et parent dirfd, sans suivre les liens.

20entrées supprimées :18caches npx admissibles, cache pip et npm `_cacache`. Huit conservées : les sept répertoires uv et le npx `fd45a72a545557e9` contenant des fichiers hardlinkés. Aucune suppression uv directe. La commande officielle uv cache clean permet le ciblage par paquet ; aucune opération n'a été établie comme strictement confinée aux sept répertoires inventoriés. Le seuil étant atteint sans uv, aucune purge plus large n'a été tentée.

Espace réellement observé à l’entrée/sortie du nettoyage :21 685 485 568 →24 132 624 384octets, soit20,196 →22,475Gio. **Gain net de libre :2 447 138 816octets, environ2,279Gio**. Il s'agit du delta global sur l'intervalle ; les activités concurrentes peuvent y contribuer, ce n'est pas une attribution exclusive aux blocs des caches supprimés. Seuil20Gio PASS, manque0octet. Aucun worktree, node_modules partagé, preuve, archive, DB, secret, simulateur ou conteneur supprimé.

## Image : cause du refus, pas un défaut produit corrigé
Run45977551087/source1ac401f complet/attempt1 : approbation humaine réelle, mais texte limité au SHA. Le préfixe obligatoire APPROVE_QA_IMAGE manque. Job140433119125/étape d'approbation : `qa_image_preparation_refused`, exit1 ; arrêt avant Docker pull/build. Aucun artefact et aucun asset privé de cette tentative. La comparaison exacte est conservée.

Rejeu local source-labellé : refus du commentaire réel, acceptation si seul son préfixe est corrigé ; attempt2 refusé. Aucun changement GitHub ou code ne découle de ce témoin. [Seul delta opérationnel restant](IMAGE_RETRY_DELTA.md) : nouvelle intention exacte soumise à autorisation, puis approbation complète du nouveau run. Ne pas cliquer Re-run pour contourner la garde.

## Cinq verdicts
| Contrôle | Résultat effectif |
|---|---|
| Catalogue / parité SCI | Acquis SCI03 conservés, nouvelle image HOLD |
| Image exacte de déploiement | HOLD — aucune image construite/acquise, aucun digest OCI inventé |
| Confiance des chemins opérationnels | HOLD — aucun nouveau montage runtime créé |
| Runtime / limites Linux/amd64 | HOLD — aucun test sur nouvelle image exécuté |
| Lecteur prêt pour activation QA | HOLD ; lecteur DISABLED, QA existant non remplacé |

Les315tests préparatoires antérieurs et la qualification SCI03 ne sont pas renommés qualification du paquet. Aucune optimisation CPU, modification SCI/DTO/SQL/TIME-01/client, APK ou OTA.

## Préservation effectivement relue
Deux lectures SSH strictes, sans mutation : dix conteneurs identiques en ID/image/config/hostconfig/état, après normalisation du seul ordre de la liste des montages (aucun champ supprimé). Volumes et états QA/workout/varro/nginx/docker identiques. Seuils VPS20Gio libres/3Gio mémoire disponibles toujours PASS. Relevé Mac après cette comparaison :20,369Gio libres, seuil encore PASS ; à relire avant acquisition, sans garantie de stabilité face aux autres activités du poste.

## Suivi privé séparé et conservation
Un dossier privé de suivi de l'incident de relevé existe hors Git : propriétaire fournisseur non encore identifié, consommateurs potentiels et journaux candidats distingués des usages API prouvés, rotation contrôlée proposée sans révocation ni changement de secret. Aucune valeur de clé n'est recopiée dans ce dossier ou les preuves SCI.

Preuves effectives dans `sci-ops-qualify-01-evidence-20261127/execution-20261127/` : autorisation de suppression, préflight28entrées, résultat20suppression/8conservation, run/approbation/étapes/log de refus, absence d'artefacts/asset et rejeu local de garde. L'original de l'échec reste intact. Ce reçu ne clôt pas SCI-OPS-QUALIFY-01.
