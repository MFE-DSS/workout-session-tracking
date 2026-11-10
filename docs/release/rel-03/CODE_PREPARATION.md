# REL-03 — code préparatoire, opérations externes ouvertes

10 novembre 2026. Base b9a334d22e6b75e9b83650eb1b2b833d4ed5d169.
**GO_BUILD_CONTROLLED / CODE_REVIEW_PENDING / NON_DISTRIBUTABLE / BLOCKED_EXTERNAL.**

Le GO opérateur « Autoriser le build contrôlé REL-03 » couvre les outils/tests,
configuration QA et livraison de code. Ce reçu ne ferme pas la pipeline opérationnelle.
Le HEAD fonctionnel lors de cette rédaction est4633ae6e5783c30ab6837ced916526270af71ac6 ;
les commits documentaires et le merge ultérieurs conserveront leurs identités propres.

## Réalisation et autorité

Serveur QA portable à façade mobile bornée, version/santé et liveness distinctes,
maintenance sans seed/activation automatique, vérification de toute SQLite et
backup/restauration en copie. La DB QA02 vivante, ses processus et son tunnel ne
sont pas transférés ni remplacés. Docker/Render sont des préparations, sans image
ou capacité512MiB prétendument qualifiée.

Nouveau profil qa-continuous-android0.0.2/code3, même package/signature attendue,
ExpoUpdates58.0.21 et expo-application58.1.2 sur Expo58.0.17/RN0.88 conservés.
Configuration officielle EAS qa→qa créée dans le scope autorisé ; aucun groupe
publié. L'APK QA02 reste Updatesdésactivé : nouveau binaire nécessaire. Empreinte
standard stable pour métadonnées JS et différente après permission native testée,
exports Android JS réellement réalisés ; ce ne sont pas des preuves d'OTA installée.

Workflow manual-dispatch seul, préparations NON_DISTRIBUTABLE sans credentials,
review candidate qa-release réelle et quatre checks HEAD exact avant publication.
Vrais reads GitHub/Render/TLS et SDK futurs derrière gates ; snapshots initiaux
et backup/export par release distincts. Source native/JS/backend et compatibilité
SQLite/inventaire sont séparées ; soumission EAS ne devient jamais installation.

Le dépôt produit est public, vérifié via l'API. Les preuves DB/auth ne peuvent pas
y circuler en clair. Producteur privé GitHub de ciphertext AES256GCM et import
protégé existent ; repo de preuves, clé séparée et tokens restent UNPROVISIONED.
Aucun upload, nouvelle clé/repo ou exécution externe de ce transport n'a eu lieu.
L'approbation unique lie candidat et empreinte attendue ; le job doit réellement
observer l'asset privé, déchiffrer et recomputer la preuve avant les gates SDK.

## Vérifications observées et limites

- Task1 :30ciblés+38broad, restaurationTOCTOU corrigée avec RED3 puis15DB+2serveur.
- Task2 :78backend avant correction,957mobiles/76suites+TypeScript ; six témoins
  OTA valides conservés après refus de18checksums invalides,69tests release passants.
- Task3 :202broad ; revue trouve première OTA nouveau runtime bloquée et backup
  par-release absent. Correctifs RED7/RED22 puis175tests, relecture ciblée sans
  Critical/Important résiduel ; état physique OPERATOR_ATTESTED toujours explicite.
- Task4 :35transport, broad276tests/45.44s, Ruff/budget260≤548/protocole/actionlint/
  Bandit passants ; revue fraîche sans Critical/Important/Minor. Les APIs externes
  sont simulées à leurs frontières, la cryptographie et les consommateurs locaux
  sont réellement exécutés. Aucun résultat de stockage distant n'en est déduit.
- Sweep root requis CI_INFRA : première passe355/427fichiers validés, arrêt du garde
  mémoire sur training_preferences à1925MiB pour budget1768. Reprise des72restants,
  un fichier/processus et garde inchangée, budget2300 après mémoire disponible3837.
  Résultat encore PENDING. Le nouveau fichier de transport, créé après l'inventaire
  du sweep, est couvert par le broad276 ; aucun full sweep répété par les agents.
- Revue globale la plus capable et CI GitHub du HEAD final encore PENDING à cet
  instant ; aucun succès PR/canonique/Sonar ou merge n'est anticipé.

Mineurs conservés : R2 normalisation de champs futurs PREPARED trop permissive
(non distribuable) ; M1 assertion Bash initiale non hex admise avant les gates SHA
réels. La revue globale les regrade ; ils ne sont pas effacés par les tests.
Dépendances npm :29advisories préexistants (3high/25moderate/1low), sans nouvelle
vulnérabilité ajoutée démontrée ou innocuité globale revendiquée. Sonar reste
consultatif, analyse réelle attendue. Aucun seuil, protection ou gate affaibli.

## Décisions techniques et coûts

Maintenance/liveness explicite évite de semer une nouvelle DB sur volume neuf.
Source de build Render Git de confiance au commit approuvé, fermetureCOPY et
secrets exclus, remplace l'exigence locale d'archive seule ; image non reproductible
revendiquée. La policy effective de self-review GitHub est respectée, pas inventée.
Une seule revue humaine de déploiement candidate lie les digests exacts, distincte
du GO MERGE ; les preuves physiques restent des attestations de l'opérateur.
Le chiffrement et le store privé ajoutent une connexion/clé à configurer, en
contrepartie d'aucune DB en artefact public ni nouvel endpoint d'export QA public.
Les règles de fraîcheur utilisent préparation/capture/export/release réellement
liés plutôt qu'un TTL arbitraire. Les reçus historiques ne sont pas réécrits.

## Sortie restante

Après revue/CI/merge du code, une décision externe unique doit borner Render
(7.25USD/mois de base hors taxes/variables, capacité à mesurer), dépôt privé de
preuves/clé/tokens, environnement protégé et cutover synthétique complet. Puis
un build Android inclus sous quota relu, installation/upgrade, updateQA et rollback
sur client installé. Diffusion aux appareils externes, DATA et production restent
des autorisations distinctes. Le résultat opérationnel exigé par REL-03 n'est pas
COMPLETE et le change ne doit pas être archivé comme tel avant ces preuves.

## Actualisation avant PR — 10 novembre

Le suivi PENDING ci-dessus décrit son instant de publication. Le correctif final
fonctionnel est74481af5698ca45899a1510e189cc0b186ce1e66, parentf02acf4.
La revue globale indépendante puis sa seule relecture ciblée ont confirmé deux
Important corrigés et **Critical0/Important0** : ancre privée de tuples immuables
propriétaires vérifiée dans la DB active et toutes les copies de preuve ; inspection
complète des métadonnées EAS project/account et refus des overrides preview,
y compris tardifs. La relecture couvre les14fichiers du fix et les preuves de tests,
sans prétendre une seconde exécution indépendante ou une qualification externe.

Ancre : capture explicite en maintenance, jamais à l'activation ; digest lié à
configuration/cible/preuve chiffrée, tuples absents des reçus publics. Ajouts et
rotations auth/SCI restent possibles ; suppression/rebind des tuples ancrés ferme
l'admission et exige une décision DATA/maintenance future. Ce mécanisme ne prouve
pas une identité universellement infalsifiable. Pour EAS, les trois noms synchronisés
sont refusés s'ils sont liés uniquement à d'autres environnements ; choix conservateur,
pas affirmation que le SDK les modifierait toujours. Les autres secrets hors preview
restent intacts, leurs valeurs ne sont pas demandées.

Résultats locaux finaux : **339tests broad affectés passants/62.76s**, Ruff15fichiers,
format, budget260≤548, protocole, Bandit ciblé passants. RED initial12échecs/1témoin,
rejeu régression28échecs/2refus indépendants conservés, raffinement EAS12RED→13GREEN.
Le sweep root a réellement terminé les72fichiers restants :72/72PASS, exit0,
pic2053MiB<budget2300. Les427fichiers d'origine sont ainsi couverts entre les deux
passes, sans rerun des355premiers ; nouveaux tests couverts par leurs broad dédiés.
Aucune CI GitHub ou Sonar final n'est encore revendiquée à cet instant.

Rulings de sortie : M1/M2 différés conservés ; Render/Docker/montage/capacité/TLS,
arrêt du writer/export physique, store privé/droits/coût/custodie/rotation,
policy/quota/SDK distants réels, APK/installation/OTA/rollback et appareils physiques
restent non qualifiés. Les avis npm29 ne sont pas un audit d'innocuité. Les choix
self-review effectif/directUser/republish connu/hébergement manuel ne donnent aucune
permission supplémentaire. CI/base/Sonar/mergeabilité seront relus au HEAD exact.
Le change reste actif et **BLOCKED_EXTERNAL / NON_DISTRIBUTABLE** après livraison
du seul code ; aucun archivage COMPLETE ni déploiement implicite.

CI initiale PR398/run42839224842 : lint obligatoire rouge à actionlint sur huit
versions d'actions utilisant Node20 retiré. Le linter local1.7.12 ne signalait pas
ce contrôle présent dans la CI1.17.1 ; aucune réussite locale n'est substituée à
ce rouge réel. Patch minimal : versions déjà utilisées dans la CI canonique
checkout5/python6/node6/upload6/download7, sans autre changement de workflow.
Vérification avec le vrai linter1.17.1 téléchargé et checksum vérifié,164tests
pipeline/transport passants ; nouveau HEAD/CI réel requis avant merge.

CI suivante42840016015/HEAD77773c9 : lint/mobile/visuel passants, shard4
**1échec/1800PASS** sur test_prepare_cli_freezes_declared_proof_without_private_credentials.
Le test héritait GITHUB_ACTIONS=true et appelait réellement gh_get sans jeton du
job pytest ; l'échec n'est pas reclassé en annulation infra. Correctif uniquement
dans ce test : deux modes local/Actions explicites, frontière GitHub read-only
simulée, assertion du SHA canonique acquis et des deux appels attendus. Aucune
garde production, permission ou configuration CI n'est supprimée. Nouveau HEAD
et CI réelle requis. Le premier run42839224842 a fini cancelled après le push
correctif, avec lint réellement rouge ; aucune annulation manuelle ni faux PASS.
