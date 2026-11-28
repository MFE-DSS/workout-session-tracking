# SCI-OPS-QUALIFY-01 — reçu de l'image exacte

28 novembre 2026, Europe/Paris. **Qualification globale HOLD ; lecteur DISABLED.**

## Identité et autorité

GO opérateur : paquet image et qualification isolée, enregistré le 28 novembre. Un seul PREPARE_IMAGE, [run 46081408323](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/46081408323), tentative 1, approuvé effectivement par MFE-DSS sur `qa-release`, puis success. Aucune auto-approbation ni deuxième dispatch.

- Source : `1f81d5b82498f0a166e59b875e12db3dec56fceb` ; quatre checks obligatoires du code source success.
- Image/config OCI : `sha256:433cda53a2eb1a7d99cd6f124c889b34093a96071ed26a53cbc8211191a35671`.
- Archive : 75 550 720 octets, SHA256 `19cc94fbbf6ee038a3af3d165aa66fdf5c4b44c981e6f3d7e8066c5a6e550823` ; garde chiffrée, acquisition et transport SSH vérifiés. Docker save ne fournit pas de RepoDigest de distribution : aucun n'est inventé.
- Base : `sha256:c8271b1f627d0068857dce5b53e14a9558603b527e46f1f901722f935b786a39` ; Debian 13.3 / Linux amd64 / Python **3.11.14** / SQLite **3.46.1** ; UID/GID 10001.
- 1 696 fichiers embarqués attestés ; archive Git et Dockerfile liés au reçu GitHub. Les 29 versions du lock sont respectées ; les 36 distributions installées sont inventoriées, `pip check` passe. `greenlet 3.5.6`, dépendance Linux supplémentaire absente du lock, reste une réserve de reproductibilité des futurs builds, pas une équivalence implicite entre images.

## Brainstorming / Options / Risques / Choix retenu

Réutiliser l'ancien runtime avec un overlay n'aurait pas qualifié le paquet livré. Le choix exécuté est l'image nouvellement construite, sans aucun montage remplaçant le produit ou le bundle. Seuls harness, profil et bases synthétiques sont montés séparément. Risque testé : la forme de l'historique, et pas seulement son nombre de faits, peut épuiser un budget fixe.

## Résultats effectifs

| Campagne sur l'image embarquée | Résultat |
|---|---|
| Legacy nominal | 5/5 ; CPU 1,324–1,482 s |
| Legacy 100 faits | 2/2 ; CPU 1,484–1,546 s |
| V3 canonique complet, 14 SET | 5/5 ; CPU 1,573–1,654 s |
| Mixte 100, dont 14 V3 canoniques | 3/3 ; CPU 1,750–1,786 s |
| 100 V3 sur 100 séances, fixture structurelle construite | 0/2 ; exit 1, plafond SQL 4096 atteint |
| 500/501 séries | 4/4 refusées, SIGXCPU conservé |
| Bundle effectif absent | 2/2 refusées, aucun fallback |
| Préfixe ancien, autorité V3 absente, texte hors plafond | UNKNOWN conservé, 2 essais par cas |
| HTTP A/B/vide, 2 lectures chacun | propriétaires 1/2/3 isolés ; 14/1/0 faits ; EMPTY distinct |
| Deux GET simultanés | un 200 et un 503, pas de queue supplémentaire |
| Auth absente / chemin injecté | 401 / 422 |
| Snapshot avec writer séparé | 9 avant, 9 pendant, 88 à la capture suivante ; intégrité OK |

Les fixtures V3 complètes ont été régénérées via les services embarqués inventory2 → évaluation → START → SET → FINISH : sept profils qualifiés, sept exercices, quatorze faits. Le second START de contrôle est explicitement refusé. Le volume 100 V3 est une construction de test, et non cent démarrages autorisés par le produit.

30 digests de réponses recalculés indépendamment, tous valides ; rôles, identités, P07, contexte public, reçus et unités contrôlés. Aucun réglage machine/PER_IMPLEMENT converti en masse totale. Les réponses observées restent PARTIAL ou UNKNOWN selon leurs preuves ; aucune promotion en EXACT.

Budgets inchangés : CPU 2/3 s, AS 512 Mio, wall superviseur 3 s, SQL 4096, VM 2 millions, JSON et sortie inchangés. RSS enfant nominal maximal via getrusage : 74 706 944 octets ; VmHWM échantillonné maximal : 74 784 768 octets. Wall nominal maximal 1,867 s, création du processus incluse. Les témoins AS/CPU, SQL/VM, JSON, sources, sortie, timeout, signal, reap et slots passent. Le délai configuré n'est pas présenté comme une garantie universelle de latence.

## Blocage mesuré, sans correction anticipée

Le scénario 100 V3 est refusé après 67 graphes/opérations : budget SQL 4096, VM 58 000, entrée DB 283 754 octets. Le catalogue est parsé **une fois**. Une sonde séparée attribue exactement le refus à `BudgetExceeded(statements)` ; ses timings instrumentés ne remplacent pas les témoins nominaux. Des lectures d'évaluation/autorité identiques sont répétées dans la même capture. [Amendement minimal proposé](SQL_CAPTURE_AMENDMENT_20261128.md), GO BUILD en attente ; aucun plafond ni code produit n'a été modifié.

## Sécurité, limites et préservation

Permissions, ancêtres, ACL, liens, montages et digests contrôlés sur les trois volumes du banc ; écritures/remplacements non privilégiés refusés, y compris UID hôte 65534. La racine du profil est root-owned et read-only ; son digest attendu provient de la garde de qualification, pas de HTTP. Un clone privé soumis à remplacement concurrent produit 39 admissions par descripteur et 41 refus ; six lectures runtime admises correspondent toutes aux octets attendus, et le digest divergent témoin est refusé. Aucun contenu divergent admis ni thread restant ; cette sonde n'est pas un témoin de temps nominal. Root/Docker/administrateur hôte restent hors du modèle. Ces preuves ne certifient pas un futur montage QA actif.

Sonar `pythonsecurity:S8707`, issue `AaIXJeDDSfdp1gNdbPO0`, relu OPEN et non modifié. Aucun jugement global de sécurité. Le bootstrap réel sans activation reste en maintenance ; le lanceur ne transmet pas de configuration SCI ambiante et son enfant garde le lecteur désactivé.

Deux défauts de sondes sont conservés : expiration de l'observateur initial de préparation, puis diagnostic root tentant de relire le répertoire après transfert UID10001. Le même producteur a été observé, puis ses postconditions vérifiées sous UID10001, sans replay des writers ni élévation de privilèges. Les réconciliations d'export et de nettoyage restent également dans les preuves privées ; aucun échec initial n'est effacé.

14 fichiers de fixtures, 26 fichiers de harness et les reçus/profils non secrets exportés et vérifiés avant nettoyage. 22 conteneurs arrêtés et 3 volumes propres au scope supprimés sans force/prune, y compris le témoin concurrent complémentaire. Les identités, images, montages, états et compteurs de redémarrage des 10 conteneurs préexistants sont inchangés ; leurs 21 volumes et images sont préservés. L'image exacte et les preuves privées sont conservées. Aucun service QA/personnel, secret, DNS, donnée réelle, APK ou OTA modifié.

## Verdicts séparés

1. CATALOGUE / SCI PARITY : **PASS**.
2. EXACT DEPLOYMENT IMAGE — identité et contenu : **PASS**.
3. OPERATIONAL PATH TRUST — copie contrôlée : **PASS**, futur QA **HOLD**.
4. TARGET RUNTIME / RESOURCE LIMITS — matrice complète : **HOLD**, scénario 100 V3 au plafond SQL.
5. READER READY FOR QA ACTIVATION : **NO**.

Prochaine décision : GO BUILD de l'amendement de lectures répétées, distinct de toute activation. Le raccordement du lanceur et SCI-ACTIVATE-01 restent ultérieurs ; aucune activation automatique, DATA ou release n'est admise.
