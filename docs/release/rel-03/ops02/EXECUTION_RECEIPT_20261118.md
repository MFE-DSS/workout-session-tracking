# REL-03 OPS-02 — exécution du 18 novembre

**QA privé actif et testé ; public NOT_QUALIFIED ; Android NOT_READY/NOT_BUILT.**
Dernier postflight 13:44:36 UTC. REL-03 reste actif : ce reçu ne clôt pas ses
gates HTTPS, candidat Android, DATA ou appareil physique.

## Mandat, choix et révisions

Mandat opérateur : REL-03 OPS-02 RESUME, image corrigée déjà approuvée, paquet OPS
et réemploi du seul VPS existant autorisés. Le conflit du bridge a donné lieu à
l’[amendement borné](../../../../openspec/changes/rel-03-continuous-android-qa/INTERNAL_BRIDGE_AMENDMENT.md)
explicitement présenté, puis direction de poursuivre enregistrée avant apply.
Choix : conserver Internal/ICC/filtre, aucun port publié ; nginx QA utilisera
l’IP privée acquise et pinnée. Coût : remplacement d’endpoint/conteneur exige
nouvelle attestation. Aucun achat, reboot, changement UI/SCI/SDK/lock.

| Élément | Référence constatée |
|---|---|
| Backend/image | `b8fc63ffadba35028af9e1c92c2e48892f9fe403` |
| [Correctif #428](https://github.com/MFE-DSS/workout-session-tracking/pull/428) HEAD | `b212a7cf0cc6b73e23c822ca1099e5bf7379c34a` |
| Merge / collecteur hôte | `511ccb6fae624533b41eb3ecf2d5bb8d09940744` |
| [CI PR44308235009](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/44308235009) | completed/success,11jobs |
| [CI canonique44311837650](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/44311837650) | completed/success,11jobs |

Chaque CI a réellement exécuté **8853backend PASS/3ignorés,127suites/1449mobiles
+TypeScript,77visuels**. SHADOW seulement ; aucun remplacement des tests par
réutilisation. HEAD/merge ont le même arbre, merge gardé par expected_head_sha,
quatre checks protégés, base/revues/threads relus. Aucun bypass/force/squash,
run annulé ou relancé. Source produit conservée : BODY/NUT/MOB06/MOB07 et leurs
closeouts sont déjà ancêtres, aucune fonctionnalité recréée.

Local : ISOLATED,423broadQA et40ciblés PASS, témoins RED→GREEN, Ruff modifiés,
budget259≤548, protocole, OpenSpec28/28 et Gitleaks PASS. Revue indépendante
entière : trois Important corrigés en une passe ; pas de seconde revue prétendue.
Mineur différé : témoins négatifs isolés supplémentaires pour les trois gardes
de publication Docker, qui restent toutes imposées.

Sonar PR428 : **Quality Gate passed**,0nouvelle issue/0hotspot, nouvelle coverage
rapportée0,0% et duplication0,0%. Sonar canonique : **Quality Gate failed,
consultatif**, conditions Vulnerabilities Minor/Bugs Blocker/Smells Critical.
Huit alertes externes Bandit relues concernent cinq fichiers app identiques àb8fc
(B404/B603 packaging, six B110/B112). Pas de total Sonar/coverage canonique non
acquis inventé. Bandit outils conserve B108Medium sur `/tmp` préexistant et4Low,
0High ; aucune suppression, changement de seuil ou innocuité globale revendiquée.

## Image, état et activation réels

[Image44188461111](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/44188461111)
completed/success, sourceb8fc, approbation humaine MFE-DSS exacte. Artifact
14419314377 acquis indépendamment, custody/attempt/readback/déchiffrement vérifiés.
Archive75357184octets, SHA256
`76f7200d829793a752e33f89a1672eb2b242a12a7a43104c7eaa40e5193b1973`.
Config/image Docker réellement chargée :
`sha256:5ee90ab09696c4312cbe2a99654d5d2368d26f2050839858cca0ec801128334e`.
Linux/amd64,UID10001,Entrypoint/Cmd et rootfs ordonné concordants ; Python3.11.14,
FastAPI0.141.1,Starlette1.6.0,httpx0.28.1. Ancienne image389221f toujours refusée.

VPS existant : Ubuntu26.04.1/kernel7.0.0-43. Réseau/filtre, deux volumes et deux
unités QA dédiés ; aucun montage personnel. Base neuve migrée à
**program_builder_operations_01**,46tables/FK/intégrité vérifiés,2comptes
synthétiques neufs,106options d’exercices canoniques ; zéro fait à l’initialisation.
Bundle`22b066a0fb363b1bd435323269bad8a7fa47e4149f18b91e4b039e89d8352dfc`,
ACTIVE/génération1 et pins publiés existants. BODY/NUT/Library/Builder exacts.
ConfigSHA`24f9b58aed1455d5183c809fc65aa1250c395b23451a4c156a925686f84eec94`.

Service non privilégié/rootfsRO/cap-drop/no-new-privileges,1CPU/2Gio/128pids,
tmpfs64Mio,logs10Mio×3. Nouveau conteneur
`b81e1442c58a1f5f9a9ca4ec108246c7816a619fe7ace4add974b4e2be5f5f34`,
même image, même état/clefs/ancre, un writer et zéro port publié. Collecteur
immuable511ccb6, SHA256
`a76d97db0bc5c1c9a92721cd1b9de16ced06f10060f449e2ce032208d531d37d`.
Health Docker sain, version/health HTTP privés200. Un startup200 seul ne qualifie
pas le routage public. Les deux unités QA sont enabled après arrêt/reprise éprouvé.

## Smokes et récupération

HTTP privé réel,19intentions métier conservées avant envoi, aucun retry automatique :

- PASS loginA/B et ownership ; builder création/composition/validation/publication,
  programme1 ; Library/départ/Today/journal, même séance1 ; étranger/inconnu404.
- PASS série17,5kg saisis/10reps, clôture et historique détaillé LEGACY_V1 ;
  contexte/charge UNKNOWN, aucune conversion en masse externe totale. Une série
  de travail effectuée, deux échauffements non effectués, jamais trois faits.
- PASS BODY71,4→71,3 synthétiques, original/version, côté absent, retrait d’accord,
  gestion minimale sans nombres et effacement confirmé des deux versions ; reçu exact.
- PASS NUT jour/zone, énergie corrigée, zéro protéine distinct des macros absentes,
  cible personnelle synthétique2000 distincte du fait1800, complétude, reçus/A-B.
- PASS autorité courante, sourceb8fc/schema exact ; GET des reçus builder/BODY/NUT.
  Ce témoin n’est pas une injection réelle de perte de paquets.
- UNAVAILABLE dans cette campagne : V3septcalibrages, app installée/SQLite native,
  perte réseau réelle et physique. Aucun positif scientifique fabriqué.

Backup initial avant activation : snapshot/manifeste/ancre, trois exports AES-GCM,
copie Mac et restauration jetable,46tables/digests/ancre égaux ; continuité
`b606c892551ffd0b6941478c59e4eb19c5c305a83be2857c6b1264a87a395c5c`.
Deuxième export/restauration après smoke PASS ; continuité
`2e03a7a8e1df78301d1c9284f245f0ff095ce31fd1703d4ae8141d6246a7fed4`.
Aucune clé de chiffrement persistée sur l’hôte, copie promue ou DB downgradée.

Arrêt/reprise active PASS : QA seul inaccessible à l’arrêt, état conservé, même
conteneur/image relancés, health sain, ancien Bearer accepté et séance completed
relue. Nouvelle session d’authentification du test avant sa comparaison : digest
avant/après`d20e80e2dfde00a507b95ed5aec842f94fc36a48c4499a708d32d1895013c85b`.
Pas de reboot-hôte, rollback d’image ou restauration ancienne comme writer prétendu.
Pas de timer de sauvegarde périodique déclaré sain.

Échecs de sonde conservés/corrigés : transition systemd lue avant stabilisation
(activation réconciliée sans rejeu), syntaxe du diagnostic avant exécution,
assertion backup confondant lignes planifiées et faits (snapshot relu sans recréation),
clé publique d’audit initialement illisible. Cette dernière est maintenant
root644 sous `.ssh`root755, non modifiable par l’auditeur ; privés0600 et sshd
inchangés. SSH forcé refuse commande arbitraire et absence de preuve publique.

Isolation finale PASS : SSH/PostgreSQL hôte, API personnelle/autre réseau et
Internet bloqués depuis QA ; seul endpoint,Internal/ICC/filtre conservés.
Postflight13:44:36UTC : huit conteneurs personnels identiques/actifs, sept services
et Tailscale actifs, nginx/units personnels/mêmeboot inchangés. Checkout opérateur
et ses13entrées inchangés. Aucune donnée personnelle utilisée.

## Gate réellement ouvert et passation

**DNS A/AAAA qa.spignos.com absents au postflight.** L’automatisation OVH n’a pas
pu ouvrir la zone ; aucun RR, certificat ou vhost public QA changé. Action
opérateur bornée déjà demandée : un A `qa`→`51.91.79.44`, TTLpar défaut, aucun
AAAA ni autre RR modifié. Ensuite seulement appliquer les étapes autorisées
ACME/TLS/nginx et observer la génération réellement chargée/HTTPS/API/SCI/schema.
Ne pas inventer une cible stable ni qualifier QA à partir du seul smoke privé.

Profil futur `qa-continuous-android`,canalqa,dev.auren.releaseqa02,0.0.2/code3,
fingerprint : **prévu, pas construit**. Target canonique UNPROVISIONED conservé.
Source client/workflow doit contenir le protocole2.0.0 ; backend garde b8fc.
Certificat QA02 attendu seulement ; runtime/upgrade/binaire/installation non prouvés.
Après HTTPS qualifié : paquet candidat et GOAndroid distinct, puis un APK consolidé.
Aucune OTA automatique, acceptation physique ou DATA déduite des tests synthétiques.

Preuves privées persistantes `auren-review/rel03-ops02-20261116/resume-20261118/` :
ne pas publier ce dossier contenant secrets/copies privées. Pas de réinitialisation,
reset/stash/prune/force ni suppression de worktree. Worktree d’exploitation conservé.
Closeout du correctif uniquement ; aucun archivage COMPLETE de REL-03.

Suivi de publication du présent reçu : PR/HEAD/CI/merge à acquérir ; le reçu vivant
final les consignera sans réécrire cet instant documentaire.
