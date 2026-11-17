# REL-03 OPS-02 — livraison technique

17 novembre2026, Europe/Paris. **Code fusionné ; QA NOT_QUALIFIED, Android NOT_BUILT.** REL03 reste actif. Aucun VPS/DNS/TLS/secret/état distant, image cloud, APK ou OTA modifié par cette livraison.

## Révisions et CI

| Élément | Référence réelle |
|---|---|
| Parent | `348dc8c3fda4a0c9a74be54fe1e92f159e382142` |
| [Code423](https://github.com/MFE-DSS/workout-session-tracking/pull/423) HEAD final | `ff0b23f776593e0ede8b1ef4bc6dcc033b46b69c` |
| Merge | `c2e32e715ccb806ef3372fd362ada88f19bcfa42` |
| Arbre HEAD et merge identique | `c6b75570d63b94dea77c2fde58f21f46b08e338a` |
| [CI PR finale44098788218](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/44098788218) | completed/success,11jobs ; **8812backend PASS/3ignorés,127suites/1449mobiles + TypeScript,77visuels** réellement exécutés |
| [CI canonique code44102174477](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/44102174477) | En cours à la publication ; résultat à acquérir avant clôture du suivi |

Merge commit avec `expected_head_sha`, quatre checks protégés relus, aucun thread/revue bloquant, aucun bypass/force/squash. CI initiale44095240072 success sur2ac1a60 avant le correctif feuille : preuve historique, jamais substitut de la CI finale.

## Ce qui est livré

Garde de la même archive image : AES-GCM privé, fsync de l'intention avant upload unique, UNKNOWN sans replay, readback et restauration après acquisition indépendante du reçu GitHub. Réseau QA interne dédié, filtre hôte borné et ordre systemd. Vhost tardif `sites-enabled/zz-auren-qa-rel03.conf` pour préserver le serveur par défaut ; la recette nginx réelle reste opérationnelle. Initialisation exclusivement neuve par migrations/référentiels/services canoniques, deux comptes/devices synthétiques, catalogue builder non vide, zéro mesure/nutrition/fait exécuté et aucun consentement implicite.

Revue indépendante du changement entier et relectures des corrections favorables : fsync et catalogue vide corrigés RED→GREEN ; chemin nginx2RED→25gardesGREEN et169consommateursPASS. Les trois corrections du paquet (SHA post-CONFIGURED/CI, codec du backup initial, droits des deux volumes) ont été relues. Aucun Critical/Important restant identifié ; aucun avis ne vaut autorisation opérationnelle.

[Reçu local détaillé](DELIVERY_RECEIPT.md) : campagne globale458fichiers/8810PASS/3ignorés avant correction feuille ; arrêts mémoire et continuation explicites sous le même plafond1600Mio. Correction feuille ISOLATED :25gardes/169consommateurs, sans full sweep local redondant ; la CI finale8812 couvre la source corrigée. Ruff259≤548, protocole/actionlint/Gitleaks PASS, OpenSpec28/28. Aucun seuil ou baseline changé.

Sonar PR423 sur HEAD final : **ERROR consultatif**,5CODE_SMELL MAJOR (2S5778,3S9073),0nouveau bug/vulnérabilité/hotspot ; couverture92,2%, nouvelle non fournie. Extra Bandit outils : B108Medium sur la constante `/tmp` de la politique de tmpfs existante, ligne inchangée, sans création de fichier hôte ; nouveaux outils0Medium/High. CI obligatoire Bandit app/pip-audit runtime/Gitleaks passée. Ruff format reste consultatif,711fichiers signalés. Aucune déclaration globale d'innocuité.

## Workflow et candidat réels

[PREPARE44102306183](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/44102306183) surc2e32e7 : prepare success, prepare-qa-image/release skipped selon la branche non publiante. Artefact14336942121,876octets, ZIP SHA256 `81b492be6e7e59c5e4834d9fcce4eb82aa41c3641efca250260186f6e97acecb`, téléchargé et vérifié. Candidate digest `838327c68f38a3d50e1c268a7ae6e0a847f25041d953b8faf2437ba10becc502` ; sources native/JS c2e32e7, schéma program_builder_operations_01. Target/runtime/fingerprint/build/artifact absents : **distributable=false**.

Package attendu dev.auren.releaseqa02,0.0.2/code3 ; certificat QA02 seulement attendu, accès à la clé non réacquis et upgrade non éprouvé. L'ancestralité du floor produit683e883 et les empreintes de sept fichiers source/configuration sont conservées. Aucun app/SCI/migration/UI/SDK/lock changé ; anciennes fonctionnalités et réserves DA08 conservées.

## Opérations et conservation

Préflight SSH strict lecture seule17novembre13:23:26UTC : Ubuntu26.04.1/kernel7.0.0-43, sept services actifs, huit conteneurs identiques image/env/mounts/ports,6178Mio disponibles/43178Mio disque ; nginx-t, venv web/native imports/pip check et intégrité SQLite/FK passent, PG17/Tailscale actifs. Aucun nouveau reboot/upgrade. QA/vhost/certificat absents, domaine non qualifié. Backup workout FAILED/resources sur le chemin Python disparu ; timer actif ne vaut pas sauvegarde réussie, aucun repair dans ce scope.

[Paquet opérationnel unique](OPERATIONAL_DECISION.md) et [actions exactes](COMMANDS.md) **NON AUTORISÉS** : activation synthétique sur le VPS existant et désignation du second acteur humain GitHub exigé par la protection. Ensuite seulement : garde privée/configuration et sa CI propre, image réelle, service isolé, DNS/TLS, parcours propriétaires, backup/restore/rollback, qualification. APK/OTA/distribution et recette physique gardent leurs gates distinctes.

Worktree `/Users/martinfeldmann/auren-review/mob06-library-20261112`, autres checkouts/appareils/backups préservés. Preuves privées : `/Users/martinfeldmann/auren-review/rel03-ops02-20261116/`. Tests terminés et probe Docker jetable nettoyé ; aucun service QA local lancé. Pas d'archive COMPLETE ni de CLOSED+CLEANED global.

Suivis de publication : CI/Sonar canonique code, CI/livraison du présent closeout et propreté finale. Les reçus vivants finaux des PR résoudront ces items sans réécrire cet instant de publication.
