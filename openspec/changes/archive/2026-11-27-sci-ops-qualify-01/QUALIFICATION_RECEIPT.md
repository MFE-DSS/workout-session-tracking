# SCI-OPS-QUALIFY-01 — reçu d’exécution du paquet exact

27 novembre 2026 — Europe/Paris, relevé final de cette passe. **Image exacte construite et éprouvée ; lecteur NOT_QUALIFIED, activation QA NO, DISABLED conservé.** La campagne a trouvé un défaut de projection V3 reproductible. Le correctif proposé reste non appliqué.

## Cinq verdicts
| Contrôle | Verdict | Preuve et limite |
|---|---|---|
| CATALOGUE / SCI PARITY | PASS borné |1696fichiers embarqués/18pins égaux au Git approuvé ; catalogue intégral attesté puis projection sélective, rôles/identités/P07 inchangés. Ce PASS ne qualifie pas la réponse V3 finale.|
| EXACT DEPLOYMENT IMAGE | PASS |Build/acquisition/transport/load du même paquet, source et config digest concordants, sans overlay produit ou bundle.|
| OPERATIONAL PATH TRUST | HOLD pour QA |PASS sur la copie contrôlée UID/GID10001, parents/permissions/ACL/montages et refus non privilégiés ; futur profil/montage QA non qualifié. Root/hôte/Docker hors du modèle.|
| TARGET RUNTIME / RESOURCE LIMITS | HOLD |Linux natif exact éprouvé ; Legacy100 admis, mais vraie séance V3 clôturée refusée5/5 et mixte100 refusé2/2.|
| READER READY FOR QA ACTIVATION | NO |Défaut V3 bloquant ; raccordement du lanceur et vraie confiance QA restent distincts.|

## Paquet réellement acquis
- Canonique revérifié : `1ac401f44b8af9444a8521b30cd47b7201fd1c8e`. Aucun changement produit de cette passe.
- [PREPARE_IMAGE45990407820](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/45990407820), attempt1 : approbation humaine MFE-DSS effective avec `APPROVE_QA_IMAGE` et SHA exact ; prepare et prepare-qa-image success, release skipped par le mode choisi. L’ancien run refusé45977551087 reste conservé ; aucun re-run ou troisième dispatch.
- Image/config Docker : `sha256:6baa24c49404b2dd8ad74a3d5b4d6f9af3c83c6923a5711a1ae1bf79aebe5e8c`. Archive75 548 160octets, SHA256 `61d557a2520488e978cb30e74a4ab950572c16b3642120e7502887ec70487843`. Base résolue `sha256:c8271b1f627d0068857dce5b53e14a9558603b527e46f1f901722f935b786a39`. Docker save n’a émis aucun RepoDigest de distribution : il n’est pas inventé.
- Debian13.3/amd64 sur hôte natif Ubuntu26.04.1LTS/x86_64 ; **Python3.11.14 / SQLite3.46.1 / UID:GID10001:10001** mesurés. Lock, ajouts Dockerfile, freeze et pip check vérifiés. Entrypoint bootstrap et Cmd d’origine conservés.
- Conteneurs1CPU/2Gio, aucun swap supplémentaire,128PID, rootfs ro, cap-drop ALL, no-new-privileges, réseau none, aucun port publié, tmpfs64Mio. Stage root limité à ses volumes neufs/CHOWN. Sources et bundle issus de l’image seulement.

## Résultats effectifs
Legacy simple5/5 admis, CPU1,584–1,784s ; Legacy100faits2/2 admis, CPU1,668–1,685s, RSSmax71 254 016octets. Dix-huit réponses admises de la première matrice ont leur digest recalculé indépendamment,18/18PASS. Les cinq témoins V3 simplifiés initiaux sont des fixtures structurelles, pas une preuve du writer complet.

Le témoin de bout en bout utilise les **sept rencontres guidées inventory2 réelles**, évaluation/acknowledgment, START,14SET et FINISH canoniques : sept exercices,14/14séries,completed,non exclu. Une deuxième intention START est refusée par `first_session_already_created`. Les faits avant FINISH restent exclus ; ces résultats ne sont pas renommés succès V3 après clôture. Le complément Legacy synthétique forme un historique mixte de100faits.

Après FINISH : **V3 0/5 admis**, exit1, CPU1,786–1,903s. **Mixte100 0/2**, un exit1 et un SIGXCPU. Les diagnostics consomment464/825unités du budget SQLite et742 363/744 050octets, sous4096/2Mio ;258/526appels instrumentés à `OwnedReadCapture.rows`, hors PRAGMA/BEGIN et blobopen. Le compteur budgétaire inclut des lectures de colonnes : ce n’est pas un nombre de SELECT.

**Cause démontrée :** le contexte writer conserve `canonical_exercise_id` en plus des cinq propriétés publiques. Le lecteur les transmet toutes au DTO fermé. Chaque fixture complète produit14erreurs `extra_forbidden` à cet endroit. Sur une copie mémoire, la projection explicite des cinq propriétés passe schéma/invariants et digest normalisé ; le produit inchangé conserve son refus. Ce contre-factuel n’est ni une implémentation ni une qualification CPU d’un correctif.

HTTP réel du lecteur sur la fixture writer terminée : A503×2 ; B200×2 avec son propre fait ; vide200×2 ; sans Bearer401 ; paramètre de chemin injecté422. Empreinte de DB inchangée par GET, enfants reapés, slots récupérés. Une campagne intermédiaire avec jetons synthétiques expirés a été conservée puis rejouée avec de nouvelles sessions synthétiques canoniques, sans changer l’authentification ni son expiration.

Complément de revue : sur la vraie fixture V3 avec binding valide, un chemin de bundle effectif volontairement absent entraîne **deux refus globaux du worker** (`muscle_observed_load_unavailable`,exit1,reap confirmé), sans DTO de faits admis. Ce témoin ne vaut pas UNKNOWN local ni succès V3. Le prédicat initial qui attendait UNKNOWN et les erreurs de préparation des permissions sont conservés ; aucune capacité supplémentaire ou correction produit n’a été ajoutée.

Autres témoins : préfixe ancien→UNKNOWN sans résultat récent inventé ; marqueur V3 sans binding→UNKNOWN sans fallback Legacy ;500/501faits refusés par limites parent/enfant ; VM SQL2M atteinte/refusée ; JSON/profondeur/tokens/sources refusés ; AS512Mio refuse600Mio ; CPU2/3s effectif ; sortie1 048 577octets refusée ; collecte à échéance3s observée à3,0015–3,0019s après création du processus, avec kill/reap ; les mesures nominales commencent, elles, avant Popen. Aucune garantie temps réel déduite de la seule configuration. Snapshot WAL synthétique stable9→9pendant writer→88à la capture suivante.

Le clone100séancesV3 atteint4096unités SQL mais ne peut pas être produit par le writer mono-owner actuel. Il reste un **stress non nominal**, sans justifier une correction SQL. Aucun budget augmenté, test ignoré ou timestamp historique réécrit.

## Sécurité, revue et vérifications
Finding Sonar `AaIXJeDDSfdp1gNdbPO0`,S8707 : **OPEN/MAJOR**, relu en direct, aucun statut modifié. Vérification de1819chemins/parents sans anomalie de mode/propriétaire/ACL/symlink dans le banc ; essais write/rename/substitution refusés. Le profil de campagne est explicitement une fixture synthétique, pas une admission opérationnelle ; ses octets bruts et leur digest sont préservés.

Revue indépendante : aucun Critical ; **Important ouvert** sur le pont contexte/DTO, décrit dans [l’amendement unique](BUILD_AMENDMENT.md). Les insuffisances de fixtures et de sondes ont été distinguées et traitées dans la campagne.

Scope ISOLATED par metadata OpenSpec. Préparation locale inchangée :315tests REL-03 ciblés/broad PASS sur Mac/Python3.11.14, Ruff260≤548, protocole/OpenSpec strict ; pas de Python produit neuf à linter, pas de full sweep. Ces résultats ne remplacent pas les essais Linux ci-dessus. [CI source45896913157](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/45896913157) : quatre checks obligatoires success ; Sonar consultatif failure conservé. Aucun nouveau HEAD correctif/PR/CI/merge n’existe dans cette passe.

Le bootstrap de l’image livré a aussi été exécuté avec son Entrypoint/Cmd réels : liveness200/data_ready=false, route503maintenance en l’absence de marqueur, aucun des trois paramètres SCI transmis par le lanceur fermé. Cette observation est distincte des503du défaut V3 dans le service HTTP du banc.

## Conservation et nettoyage effectifs
Nettoyage cache antérieur autorisé :20entrées npm/npx/pip supprimées,7uv et1npx à hardlinks conservées. Variation d’espace libre observée pendant cette opération :+2,279Gio, sans attribution exclusive face aux activités concurrentes du Mac.

Banc : **36conteneurs arrêtés et6volumes neufs supprimés** (31/3 pour la campagne principale, puis5/3 pour le complément catalogue absent) par IDs/labels exacts après conservation/empreintes ; aucun prune. Les10conteneurs préexistants, leurs identités/configurations/montages, les volumes préexistants et les états des services sont identiques avant/après. Archives claires d’image redondantes retirées du VPS et du Mac ; image exacte chargée et garde chiffrée conservées. Mac **21.617Gio libres**, VPS **41.069Gio libres** et mémoire disponible≥3Gio : seuilsPASS. Le répertoire privé de reçus distant est conservé.

Preuves complètes privées : `/Users/martinfeldmann/auren-review/sci-ops-qualify-01-evidence-20261127/execution-20261127/retry-02/`. Exports de fixtures, profil brut, reçus, logs, sources de sondes et empreintes restent hors Git ; aucune clé ou valeur d’accès dans ce reçu. Suivi privé de l’incident de clé séparé, sans rotation/révocation arbitraire. Worktree et documents non committés préservés pour la décision suivante ; scope non déclaré CLOSED.

## Prochaine opération unique
**Autoriser le [correctif borné du contexte V3](BUILD_AMENDMENT.md).** Une fois livré, il faudra requalifier son image exacte sous l’autorisation applicable.

Le futur SCI-ACTIVATE-01 devra ensuite traiter le schéma fermé du lanceur, ses trois paramètres SCI, le profil attesté lié au reçu réel, le montage de confiance et le rollback vers image/config/activation précédentes. Ce paquet d’activation n’est pas exécutable tant que le lecteur reste HOLD. Aucun flag, remplacement QA, DNS/TLS, APK, OTA ou traitement réel n’a été effectué.
