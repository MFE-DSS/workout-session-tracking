# REL-03 — code livré, opérations externes encore fermées

10 novembre 2026. **CODE_MERGED / BLOCKED_EXTERNAL / NON_DISTRIBUTABLE.**
Le change reste actif : aucune clôture opérationnelle ni archive COMPLETE.

## Référence réellement intégrée

PR [398](https://github.com/MFE-DSS/workout-session-tracking/pull/398),
HEAD `5f46d426328d5d70615f57737c42313961ee5f30`, merge
`d67f12a19839a7f6c91f88aa8bde3a4a3c6c6597`, base effective `a22dad5`.
La réservation documentaire MOB-06/Maltin arrivée sur la base est préservée.
Commit de merge avec garde du HEAD, quatre contrôles requis, sans thread/revue
bloquant ; UNSTABLE uniquement Sonar consultatif. Aucun déploiement, build cloud,
secret partagé, APK ou update externe n'a été produit par cette livraison.

Les outils de serveur/identité/backup, inventaire de release, profil Android QA,
observation native, preuves chiffrées et workflow manuel sont décrits dans
[README](README.md). Le dépôt produit est PUBLIC ; DB, secrets et preuves brutes
ne sont pas des artefacts publics. Le store privé reste UNPROVISIONED.

## CI et chemin réellement exécutés

- [PR 42845628797](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/42845628797) : 11 jobs réussis sur le HEAD final.
- [PR 42845512245](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/42845512245) : tentative 1 avec annulations lint/mobile/visuel, backend et QA réussis ; logs inspectés sans assertion échouée dans les jobs annulés. Un rerun des seuls jobs concernés, tentative 2, a réussi les 11 jobs. Ne pas présenter ces annulations comme des tests initialement verts.
- [Canonique 42852368435](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/42852368435) : completed/success, 11 jobs sur d67f12a. **8 401 backend passants / 3 ignorés ; 76 suites / 957 mobiles + TypeScript ; 77 visuels.**
- [Workflow manuel PREPARE 42852655171](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/42852655171) : prepare réussi, release skipped. L'artefact réel contient d67f12a, candidat `4cec240217232cab5c232d7e02384160887778fc56af8040a2f2f6be2d2e3214`, PREPARED, distributable=false, target/proof/runtime/artifact non acquis. Ni publication ni preuve d'installation.

Deux rouges réels antérieurs restent tracés : run42839224842, huit versions
d'actions Node20 refusées par actionlint CI1.17.1, corrigées avec les versions déjà
canoniques ; run42840016015, un test CLI hérite GITHUB_ACTIONS et appelle GitHub
sans jeton pytest, corrigé au seul test avec frontière read-only explicite et deux
modes. Aucun garde production supprimé. Le premier run finit cancelled après le
push correctif avec son lint réellement rouge. Une fermeture/réouverture unique
de PR a rétabli le déclenchement absent du HEAD final ; aucun bypass.

## Contrôles locaux et revue

Tier CI_INFRA. Sweep borné : 355/427 fichiers terminés, arrêt watchdog mémoire,
puis seulement les 72 restants terminés sous le même garde (pic 2 053 MiB sous
budget 2 300). Aucun -n auto, rerun des 355 ni abaissement du watchdog. Les modules
nouveaux sont couverts par leurs broad dédiés ; broad final affecté **339 PASS**,
puis **165 PASS** pour la frontière CLI/transport modifiée par le correctif CI.
Mobile 76 suites/957 et TypeScript ; Ruff neuf, budget260≤548, protocole, Bandit
ciblé et Gitleaks passants. Le vrai actionlint1.17.1 a été vérifié localement.

Revue globale indépendante puis une vague consolidée et une relecture ciblée :
C0/I2 → C0/I0. Ancre privée de continuité propriétaire et inventaire complet des
métadonnées EAS corrigés. M1 (validation initiale du ref Bash) et M2 (normalisation
permissive de futurs champs PREPARED) différés, refus aval strict et état non
distribuable conservés. Les deux correctifs CI ultérieurs sont vérifiés par tests
et CI ; aucune revue indépendante de leur SHA exact n'est inventée.

Hors jugement/qualification : capacité et UID/disque Render, TLS réel hébergé,
gel physique du writer/export, accès/coût/custodie/rotation du store privé,
configuration/quota/publication distants effectifs, APK installée/upgrade/OTA/
rollback et appareils physiques. Les choix de self-review effective, reviewer
DirectUser, republish connu et provisioning manuel sont des contraintes explicites,
pas des autorisations externes. Les 29 advisories npm restent visibles.

## Sonar exact

PR398 : ERROR consultatif, 28 MAJOR CODE_SMELL dans les tests (23 S9073, 1 S3415,
3 S8999, 1 S5778), zéro nouveau bug/vulnérabilité/hotspot, couverture app92,5%,
nouvelle non fournie. Analyse canonique `0c3292ec-10cc-4237-92af-7d0f57b56c50`,
10novembre16:26:01UTC, révision d67f12a : **ERROR, 8bugs / 555smells / 8 entrées
externes Bandit ouvertes / 0hotspot**, couverture92,5%, nouvelle92,50476969201418%.
Les huit entrées relues sont six B110/B112 de juin et deux B404/B603 packaging du
8novembre ; fichiers identiques à B9. Une neuvième entrée secrets historique est
déjà FALSE_POSITIVE, pas une vulnérabilité ouverte supplémentaire ni une décision
prise dans ce scope. Pas de déclaration globale d'innocuité. Évolution du profil
Python côté service enregistrée ; aucun seuil/statut/protection modifié ici.

## Sortie réelle

L'APK QA02 antérieure reste le seul binaire livré ; elle n'acquiert pas OTA par
ce merge. qa/qa existe sans groupe publié. Fingerprint Android et exports JS
réels ont été exercés localement, pas installés comme nouvelle APK.
[Décision externe unique](EXTERNAL_DECISION.md) avant infrastructure/cutover/build
et essais update/rollback. DATA, diffusion à un appareil externe et production
restent distincts. Le banc QA02 vivant, ses données synthétiques et les autres
worktrees/appareils sont préservés. Les preuves détaillées sont conservées hors
Git dans `/private/tmp/auren-rel-03-evidence/` et les notes de revue dans le worktree
REL-03, sans prétendre un cleanup tant que les opérations restent ouvertes.
