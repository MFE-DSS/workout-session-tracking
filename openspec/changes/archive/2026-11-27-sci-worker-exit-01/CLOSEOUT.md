# SCI-WORKER-EXIT-01 — livraison et qualification bornée

27 novembre 2026. **Code fusionné ; candidat Linux contrôlé PASS ; image opérationnelle NON REQUALIFIÉE ; lecteur DISABLED.** Les CI code PR et canonique sont réussies. La publication de cette archive, sa CI et le nettoyage Git restent à résoudre par les reçus finaux.

## Livraison

- Parent : `54f68f65bd4c69f986bc887d7e7fbbec98a8c67b`.
- PR code : [#456](https://github.com/MFE-DSS/workout-session-tracking/pull/456).
- HEAD livré : `741d9712559459a0a2f5a509cb4a615457f61600`.
- Merge : `3aef9d11348416135dcb6f68dd433b3bc1571e9f`, arbre identique au HEAD vérifié.
- CI PR : [46067424247](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/46067424247), **11 jobs success**, quatre contrôles protégés réussis. 9 064 tests backend PASS / 3 SKIP existants, 140 suites / 1 610 tests mobiles PASS et TypeScript PASS, 77 contrôles visuels PASS.
- CI canonique : [46069395764](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/46069395764), **completed/success, 11 jobs** ; mêmes 9 064 backend / 3 SKIP existants, 1 610 mobiles + TypeScript et 77 visuels effectivement exécutés.

## Changement et invariants

Seul `worker.py` change en production. La capture SQLite est fermée avant sortie, puis le DTO normalisé et son digest sont revérifiés ; l’encodage est borné, l’écriture doit être complète et le flush doit réussir avant le statut zéro. Le point d’entrée termine explicitement, sans le teardown général qui consommait le budget CPU après production du résultat. Les `finally` métier restent exécutés. Le superviseur n’est pas modifié et continue à refuser un statut d’échec même après réception d’un JSON complet.

Aucun changement de writer SET/FINISH, historique, TIME-01, DTO public, politique SCI/P07, allocation V3, SQLite métier, client mobile ou budget.

## Preuves RED → GREEN et revue

Quatre témoins RED sur l’ancien produit : teardown atexit, digest corrompu, DTO invalide et écriture courte. GREEN local final : **163 PASS / 4 SKIP exclusivement Linux**, ciblés et broad requis par le tier ISOLATED ; pas de full sweep local redondant. Ruff, budget inchangé 260 ≤ 548, Bandit, Gitleaks, protocole et OpenSpec strict réussis.

La revue indépendante fraîche du diff entier a relevé un Important de preuve : émettre `{}` avant un signal ne prouvait pas l’autorité du statut. Le test corrigé utilise un DTO complet concordant, un contrôle positif puis les mêmes octets avant SIGXCPU/SIGTERM/échec de flush. La suppression du seul contrôle de statut dans un mutant en mémoire produit deux échecs RED ; le superviseur réel passe. Le parcours natif `read_owned` prouve l’acquisition puis la libération du slot, la fermeture des pipes et le reap. Aucun Important restant ; aucun mineur différé. [Revue](INDEPENDENT_REVIEW.md).

## Qualification native effective

Code produit `13211bcb8f9bd2499af333577d725e914cf78986`, identique à celui livré après ajouts de tests/documents. Ancienne image support `sha256:6baa24c49404b2dd8ad74a3d5b4d6f9af3c83c6923a5711a1ae1bf79aebe5e8c`, avec source candidate montée en lecture seule : **ce n’est pas une image de déploiement reconstruite**.

Linux/amd64 natif, Debian 13.3, Python 3.11.14, SQLite 3.46.1, UID/GID 10001, 1 CPU / 2 Gio, 128 PID, réseau fermé, rootfs read-only, toutes capacités retirées et no-new-privileges. CPU enfant 2/3 s, AS 512 Mio, superviseur wall 3 s, SQL 4 096, VM SQL 2 millions et sortie 1 Mio inchangés.

| Cas | Succès / essais | CPU min–max | Moyenne / écart-type population |
|---|---:|---:|---:|
| Legacy nominal | 7/7 | 1,415620–1,681174 s | 1,523107 / 0,095795 s |
| Legacy 100 faits | 5/5 | 1,482917–1,636065 s | 1,550035 / 0,050194 s |
| V3 réel, 14 SET | 10/10 | 1,583213–1,786174 s | 1,706169 / 0,054109 s |
| Mixte 100 faits | 10/10 | 1,753630–1,913728 s | 1,836472 / 0,051722 s |

**32/32 exits zéro**, digests recalculés indépendamment et enfants reap. Six autres réponses UNKNOWN valides portent le total à **38 digests**. Pic RSS nominal : 74 989 568 octets. Les résultats restent PARTIAL quand requis ; aucune promotion artificielle à EXACT.

500/501 : quatre refus SIGXCPU préservés ; bundle effectif absent : deux refus exit1, sans fallback. Chaîne absente, préfixe ancien et texte surdimensionné restent UNKNOWN. Dépassement VM, AS, sortie et wall refusés ; nettoyage réel. Wall observé jusqu’à 3,002543 s pour un cap de 3 s : aucune promesse temps réel dur. Marge CPU mixte minimale observée : environ 86 ms, sans garantie sous toute charge.

Isolation A/B/vide, snapshot cohérent concurrent, intégrité et absence de mutation vérifiés. Les campagnes historiques V3 et mixte avaient chacune 4 admissions sur 7 et 3 refus SIGXCPU sur 7. Ces résultats et les erreurs de préparation/oracle restent conservés ; aucun refus n’est reclassé en succès. [Reçu complet](QUALIFICATION_RECEIPT.md).

## Sécurité et réserves

Sonar PR et canonique : **Quality Gate ERROR**, couverture nouvelle 95%, duplication 0%, nouveaux bugs et vulnérabilités 0. Finding **S5754 / CODE_SMELL / CRITICAL** sur `BaseException` au seul point d’entrée : interception délibérée pour choisir l’échec explicite même sur interruption pendant la finalisation, sans reprendre le teardown. Finding laissé OPEN ; aucun seuil, règle ni état d’issue modifié. Consultatif sous GOV-SONAR-01 ; aucune vulnérabilité exploitable établie par ce finding. **S8707** historique reste distinct, ouvert et non clos par cette livraison.

La confiance des 1 819 chemins/parents/permissions/ACL et les refus de remplacement sont qualifiés uniquement dans le banc. Ni futur montage QA ni administrateur root ne sont certifiés. L’image opérationnelle et ses chemins exacts restent à requalifier.

## Conservation et nettoyage

Les preuves privées, sources et bases synthétiques ont été exportées et empreintées dans `/Users/martinfeldmann/auren-review/sci-worker-exit-01-evidence-20261127/`. Aucun secret ni base n’est livré par la PR.

Nos 25 conteneurs et 4 volumes ont été supprimés après export. Les 10 conteneurs préexistants, leurs configurations, les volumes et services sont conservés. Les montages retournés dans un ordre différent ont été comparés par destination unique, sans suppression de champ ; les états bruts sont conservés. Aucune configuration existante modifiée.

Le seul cache SD1.5 autorisé a libéré 4 266 754 048 octets par le mécanisme officiel ; 25 211 232 256 octets libres immédiatement après. Aucune suppression des autres modèles, du cache Gradle ou des worktrees tiers.

## Prochaine opération

Préparer l’autorisation distincte d’une image exacte reconstruite depuis le canonique final, puis requalifier cette image, son profil et ses chemins opérationnels. Aucun nouveau PREPARE_IMAGE, déploiement, activation, données réelles, APK ou OTA n’est autorisé par le présent closeout.
