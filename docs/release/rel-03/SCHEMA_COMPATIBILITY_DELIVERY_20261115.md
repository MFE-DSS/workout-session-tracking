# REL03 — livraison de la correction de compatibilité,15novembre2026

**Correction de code livrée et vérifiée. REL03 opérationnel reste ACTIVE / NOT READY.** Ce reçu clôt les suivis CI/canonique/Sonar indiqués en attente dans le [reçu local](SCHEMA_COMPATIBILITY_RECEIPT_20261115.md) pour cette seule correction ; aucun change REL03 n'est archivé COMPLETE et aucune autorisation opérationnelle n'est ajoutée.

## Source et contrôles réels

[PR412](https://github.com/MFE-DSS/workout-session-tracking/pull/412), HEAD `12a4ee49dfb020a0422da9215c2545ac1df7a38f`, fusionnée par commit de merge `dc970d4d1b0352614cbdbbf1b694ff764f290829` sous GOV-MERGE-01. Les deux commits ont exactement le même arbre `84f8c39aaf9b3c2f8fc42db1d89fbdc21719e94d`. Revue indépendante : aucun défaut Critical/Important/actionable Minor ; empreinte du diff production/tests/candidat relu `2e2dd3bb70f70b91a57ca237074561cb564b5475e0e1c032322059ef6407475c`.

| Vérification | Résultat observé |
|---|---|
| [CI du HEAD de PR43726786137](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/43726786137) | success,11jobs ; backend8720passed/3skipped ; mobile1377tests/116suites et TypeScript ; visuel77passed |
| [CI canonique43728843207](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/43728843207), SHA `dc970d4d…` | completed/success,11jobs ; mêmes nombres backend/mobile/visuel, cinq shards et agrégateur QA réussis |
| Vérification locale du correctif | RED4régressions attendues ; GREEN264tests ciblés+93consommateurs ; tier ISOLATED, Ruff/protocole/OpenSpec27/27 ; Gitleaks0 ; Bandit4constats strictement préexistants,0nouveau |

Les pins database/release/candidat admettent désormais `nutrition_manual_01`. Une vraie migration Alembic remplace la fixture qui estampillait PLAN sur le schéma courant. Les copies synthétiques peuplées auth/PLAN/BODY/NUT conservent leurs lignes et digests via backup→copie export locale→restore neuf ; schémas anciens/falsifiés, intégrité/FK invalides et écrasement restent refusés. Cette copie locale ne prouve ni export externe chiffré ni garde hors service. Aucun app/model/migration/snapshot, runtime natif ou contrat UI modifié.

## Sonar réellement attribué

[Analyse de PR412](https://sonarcloud.io/dashboard?id=MFE-DSS_workout-session-tracking&pullRequest=412) sur le HEAD exact : **OK**,0issue/bug/vulnérabilité/hotspot, couverture92,3%.

Analyse canonique `8f8345d1-d299-4f13-ba69-adcf46688b4f`,15:33:31UTC, révision exacte `dc970d4d…` : **ERROR consultatif** sous GOV-SONAR-01,8bugs,8entrées VULNERABILITY importées de Bandit,638code smells,0hotspot ; couverture92,3%, nouvelle92,28909980545895%. Les16clés bug/sécurité sont les mêmes que sur la base `59a28dc6…` ; leurs fichiers sont identiques octet pour octet. Les règles Bandit sont B110/B112 et B404/B603. Cette attribution n'est pas une déclaration globale d'innocuité ; aucun seuil, statut d'issue ou protection n'a été modifié.

## PREPARE réel, sans distribution

[Workflow43728919113](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/43728919113), événement `workflow_dispatch` au SHA `dc970d4d…` : **success**, job `prepare` réussi, job `release` **skipped**. Artefact public de métadonnées `qa-prepared-candidate`, ID14167284428, ZIP SHA256 `44c7481518d75c462087cdc7a1d06d919a02e93f05a1d6c1b70425094cb74437`, téléchargé et vérifié.

Le paquet porte `canonical_sha`, `native_sha` et `js_sha` égaux au merge exact ; `server_schema=nutrition_manual_01`, `distributable=false`, cible/runtime/fingerprint/build-ID/artefact/proof nuls. Digest candidat `9344044a34c871419698019fb1580753c30b0abdb482b62b860b8cb1832775c5`. Son champ `action=BUILD_APK` décrit le futur candidat : l'opération exécutée est seulement **PREPARE**, aucun EAS Build/OTA. Ce reçu reste historique pour son SHA ; un futur HEAD exige une nouvelle préparation et ses preuves propres.

## Limite de clôture

Le présent closeout ajoute uniquement ce document sous `docs/release/rel-03/`. Sa CI de PR, son HEAD/merge et son nettoyage sont consignés dans les commentaires finaux des PR concernées. La CI canonique d'un push100%docs peut être légitimement absente par `paths-ignore: docs/**` ; aucun run ou nouvelle analyse Sonar n'est alors inventé.

L'hébergement stable, le support/sécurité de l'hôte, les preuves indépendantes OVH/fournisseur, l'origine QA exacte, la configuration contrôlée BODY/NUT/LIB, la conservation/continuité des données synthétiques, les secrets et protections de release, le cutover, l'APK installée/upgrade/OTA/rollback et la recette physique restent distincts et non réalisés ici. Aucun service OVH, DNS, DB vivante, secret, profil natif ou publication modifié. Le nettoyage peut retirer seulement les branches/worktree de cette correction après vérification d'absence de travail unique ; les anciens refs REL03 et les autres worktrees, dont MOB07, sont préservés.
