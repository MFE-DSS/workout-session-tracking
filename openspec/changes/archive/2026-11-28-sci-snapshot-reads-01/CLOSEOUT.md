# SCI-SNAPSHOT-READS-01 — correction SQL bornée

28 novembre 2026. Code fusionné ; qualification opérationnelle HOLD ; lecteur DISABLED. CI canonique et livraison administrative de cette archive encore suivies séparément.

## Autorité et changement

GO opérateur : « ok gO pour le correctif SQL borné », reçu le 28 novembre. Parent `c8b413efa027467600654a445521ca8e564b4384`. Seul `sqlite_source.py` change en production ; deux fichiers de tests autorisés. Les lectures d’évaluation, d’autorité runtime et de présence des deux tables internes sont réutilisées dans une seule capture SQLite read-only, avec stockage borné, copies indépendantes et destruction après fermeture. Les échéances et la comptabilité des accès physiques restent appliquées. Aucun verdict SCI n’est mis en cache.

Aucun changement de requête propriétaire, sélection, DTO, source ou politique SCI/P07, writer, TIME-01, moteur V3, application mobile, budget ou environnement opérationnel.

## Brainstorming / Options / Risques / Choix retenu

La hausse de SQL4096 et un cache global ont été exclus. Choix : réutiliser uniquement les lectures immuables de la même transaction ; requalifier toujours l’autorité de chaque fait. Risques couverts : valeurs mutables, propriétaire différent, révision concurrente, absence devenue présence, nombreuses identités, échéance et capture fermée.

## RED → GREEN et tests locaux

Les trois refus RED des lectures répétées et le refus structurel 100V3 au plafond SQL4096 sont conservés. GREEN : 24 tests SQLite ; broad SCI/consommateurs 331 PASS / 4 SKIP Linux existants sur Mac ; HTTP 14 PASS. Tier SHARED_CODE, aucun full sweep local redondant. Ruff ciblé, budget global inchangé260≤548, Bandit, Gitleaks, protocole et OpenSpec strict passent.

Le parcours canonique inventory2 → évaluation → START → SET → FINISH conserve ses14faitsV3 et le mixte100. Le volume100V3 sur100séances est une construction structurelle explicitement étiquetée ; il ne prétend pas à100STARTs autorisés.

Les bases synthétiques du banc précédent ont été relues localement sans writer : 14V3/SQL282 ; mixte100/SQL557 ; 100V3 structurels/SQL3918 ; Legacy100/SQL904. Dix digests indépendants et empreintesDB concordent ; A/B/vide isolés, UNKNOWN conservé pour autorités absentes, préfixe ancien et texte horsplafond. Python3.14.7/Darwin : **preuve fonctionnelle locale, pas qualification Linux de l’image corrigée**.

Un premier échec du témoin hash provenait d’un checkpoint WAL différé d’un writer de fixture non fermé. La fermeture explicite des writers de test corrige ce harness ; preuve initiale conservée. Une invocation broad avec un ancien nom de test inexistant est également conservée ; aucune exécution vide n’est comptée comme succès.

## Revue et livraison

Revue indépendante du diff entier puis du delta de précision des tests : aucun Critical, Important ou Minor restant. Première CI9b90618 entièrement verte, mais SonarERROR pour trois remarques de tests. Assertions ensuite resserrées pour isoler l’appel refusé et vérifier la ressource ; produit inchangé,24tests repassés, nouvelle CI exigée.

PR [#459](https://github.com/MFE-DSS/workout-session-tracking/pull/459), HEAD `0e0008cede00c3f369b1c6c827603eb73e972820`. CI finale [46129030460](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/46129030460) : completed/success,11jobs ;9074backend PASS/3SKIP existants,140suites/1610mobiles etTypeScript PASS,77visuels PASS. Tests modifiés rejoués isolément etQA passants. Sonar final **OK**, couverture nouvelle100%,duplication0%,zéro nouvelle issue/bug/vulnérabilité. Les trois remarques initiales sont résolues par la précision des tests, sans changement administratif du gate.
Merge `7f05ba1a038d32de0d1568ecb3397e4489ba58da`, parentsc8b413ef/0e0008ce, arbre identique au HEAD vérifié. Quatre checks requis app15368 verts, PRCLEAN/MERGEABLE et aucun thread/revue bloquant avant fusion ; GOV-MERGE-01 appliqué sans bypass.
CI canonique [46130918222](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/46130918222) **en cours à la rédaction**. L’attestation WOULD_REUSE confirme l’arbre testé, mais le mode SHADOW laisse réellement tourner la suite complète. Le verdict final et le Sonar de branche seront relevés dans le reçu administratif vivant ; aucune réutilisation ni réussite canonique ne sont présumées.

## Verdicts et limites

Correction fonctionnelle et parité : PASS sur le HEAD PR vérifié ; CI canonique encore à résoudre à cet instant. SQL100V3 :3918/4096 sur les témoins locaux. SQL4096, VM2M, CPU2/3s, AS512Mio, supervisorwall3s, JSON et sortie inchangés.

**Image opérationnelle inchangée au source1f81d5b8 ; runtime corrigé exact HOLD ; lecteur DISABLED / NOT_QUALIFIED pour activation.** Le gain SQL n’atteste pas CPU, RSS ou wall de la future image. La confiance des futurs cheminsQA et le raccordement du lanceur restent distincts. S8707 reste OPEN, aucun finding administrativement modifié.

Aucun PREPARE_IMAGE, montage candidat distant, SSH, transfert, changementOVH, activationQA, donnée réelle, APK ou OTA dans ce scope. Sources, preuves, fixtures, historique des refus et autres worktrees conservés.

## Closeout et suite

Archive OpenSpec préparée sans modification de spec externe (`skip_specs:true`, optimisation interne). Les leases produit sont libérés après le merge code. Publication/CI/merge de cette archive, CI canonique code et nettoyage Git restent à terminer et à consigner par reçus vivants ; **CLOSED+CLEANED n’est pas encore revendiqué dans ce document**. Le ledger et les caches propres au worktree seront préservés avant son retrait ; aucun worktree tiers ni preuve unique supprimé.

Prochaine opération : autoriser séparément un unique paquet image exact au canonique final et sa qualification synthétique isolée. L’ancienne approbation46081408323 ne peut pas être réutilisée. Activation et DATA restent ultérieurs.
