# SCI-RUNTIME-03 — amendement produit exact proposé, non appliqué

26 novembre2026, Europe/Paris. Parent revérifié : `3d4c7577e5ffd39fb59de58d1aab3bded1936edb`.
**GO BUILD produit en attente.** Le GO `call_c7d26b9a63444e668003141b1b5c9d04` couvre le banc natif isolé, pas le correctif ci-dessous. Ce document remplace le brouillon Legacy seul, conservé dans les preuves privées.

## Défauts et coûts prouvés

1. Les imports dominent : environ1,22sCPU sur le nominal instrumenté. Le même catalogue411788octets, SHA256 `7d1ae5d3c05c4b76c540789e9e07d0c2c0d96c9a4aa03a28c0b4f964441981fd`, est parsé deux fois (environ0,29sCPU au total), pour Legacy et pour le bundleV3 synthétique contenant exactement ces mêmes octets. L'attestation des autorités de ces deux racines doit rester indépendante.
2. Le Linuxamd64 natif reproduit SIGXCPU vers2s sur le nominalV3, ainsi que sur500 séries. Le worker peut avoir écrit son JSON avant la mort ; le parent refuse correctement tout exit non nul. Le cache Legacy seul ne corrige pas la margeV3.
3. Digest de résultat V3 non stable : `projection.py` calcule son digest avant la normalisation stricte du DTO. Le champ admissible `/facts/0/setting/value` passe d'un entier à un float lors de cette validation. Le digest annoncé ne correspond alors plus à la représentation retournée. Témoin reproductible sur les sources intactes ; aucun writer ou fait historique n'est à réécrire.
4. **Limite distincte conforme au contrat** : les réponses500faits dépassent `max_tokens=65536` du parent même avec un enfant réussi. W500 est un plafond de scan, pas une garantie de500 faits servis. Le refusUNAVAILABLE reste attendu. Aucun changement de plafond ou de comportement à cette frontière n'est demandé.

## Scope exact proposé

Fichiers applicatifs :
- `app/services/muscle_observed_load/worker.py` : amorcer et transmettre un contexte de réutilisation pour ce seul job depuis la vue courante pleinement attestée ; conserver bootstrapORM et limites avant imports.
- `app/services/muscle_observed_load/provenance.py` : réutilisation du résultat de parsing seulement pour des **octets complets indépendamment attestés et strictement identiques**, même digest attendu, mêmes limites JSON et même implémentation attestée du parseur. Chaque racine/bundle vérifie toujours ses propres octets, manifestes, références, budgets et digests avant toute réutilisation.
- `app/services/muscle_observed_load/projection.py` : transmettre ce contexte à la vue du bundle après ses vérifications propres ; calculer `result_digest` sur le DTO normalisé effectivement retourné, avec le placeholder canonique initial, puis vérifier le résultat final stable. Ne changer aucun champ métier, état ou contrat de lecture.

Tests autorisés à demander : `tests/test_muscle_observed_load_worker.py`, `tests/test_muscle_observed_load_provenance.py`, `tests/test_muscle_observed_load_projection.py`. Documents, reçus et closeout du même change inclus. Aucun autre fichier produit ou CI sans amendement distinct.

## Frontière de confiance du cache demandée explicitement

- Un enfant, un job, un propriétaire ; rien dans HTTP ou un état global durable, aucun partage entre processus/requêtes/comptes.
- Autorisation demandée pour le seul partage de parsing entre catalogue courant et catalogue de bundle lorsque les **sources sont identiques par leurs octets/digest et limites**. Ne jamais partager leurs conclusions d'autorité. Une source différente, un digest divergent ou des limites différentes interdisent la réutilisation.
- Maximum deux entrées de parsing par job ; si plein, effectuer l'admission ordinaire sans mise en cache, sous les plafonds existants. Aucun élargissement de ReadLimits.
- Le dictionnaire de `CatalogueProjection` n'est pas profondément immuable. Garder le gabarit privé au contexte, ne pas l'exposer à un consommateur modifiable : fournir des copies indépendantes bornées aux vues. Tests de non-mutation du gabarit et d'indépendance des vues requis. Le coût mémoire/copie doit être remesuré sur le vrai code.
- Chaque nouveau job/source/profil recrée l'admission. CatalogueB valide, différent deA mais conforme à son propre pin : cache miss et parsing ordinaire, avec son résultat historique de référence. OctetsB différents de leur propre pin : refus existant. Une différence de source valide ne devient jamais un refus artificiel.
- Le contexte est fourni au parsing interne du bundle (`compose_effective`), après ses vérifications préalables d'octets/pins, pas seulement après le retour de `bundle`. Toutes les vérifications finales de liaison/extension/effective science restent obligatoires APRÈS ce parsing, même lors d'un hit ; un cache ne représente jamais une autorité admise.
- Aucun code de bundle historique exécuté ; seules ses données/empreintes sont consommées.

## Expériences conservées, pas code produit

Banc autorisé : image config `sha256:5ee90ab09696c4312cbe2a99654d5d2368d26f2050839858cca0ec801128334e`, sourceGit3d4c757 montéeRO, Linuxamd64 natif, Debian13.3/Python3.11.14/SQLite3.46.1, conteneur1CPU/2Gio, UID10001/caps0, CPU2/3s/AS512Mio/wall3s inchangés.

Le prototype privé qui réutilise le parsing d'octets identiques après chaque attestation et recalcule le digest après DTO donne3/3 succèsV3 :1,602–1,795sCPU, digest de sortie recalculé correct, champs métier identiques. Le code intact du même lot donne un SIGXCPU et trois digests V3 incorrects. Le gabarit partagé du prototype reste identique avant/après. **Ce prototype n'est pas l'implémentation finale à copies indépendantes** et ne vaut ni qualification produit ni CI. Les mesures à500faits restent des refus attendus ; aucun passage artificiel àEXACT.

Les comparaisons retirent seulement `read_id` et son digest dérivé, avec `as_of` fixé. La vérification séparée du digest est maintenant exécutée avant toute normalisation ; sa défaillance canoniqueV3 est conservée, pas cachée par la parité. Les limites lexicales et le DTO du parent sont testés séparément du succès enfant.

## RED/GREEN et livraison après GO

1. RED sur double parsing et digest V3 non stable (entier/float admissibles). Conserver les témoignages natifs précédents.
2. Appliquer uniquement ce scope ; GREEN parsing unique lorsque les octets attestés sont identiques, sources divergentes non réutilisées, template non muté/vues indépendantes, jobs/comptes séparés, digest conforme au DTO final. Aucune politiqueSCI modifiée.
3. Tests reader/API/SCI ciblés et broad, sécurité/protocole/OpenSpec selon `check_scope`, aucune hausse de budget ni full sweep local non requis.
4. Requalifier le **HEAD produit réel**, son archiveGit, ses pins et son nouveau profil dans le banc natif déjà autorisé avec les mêmes protections. Répéter Legacy/V3 nominaux et100faits admis par le parent ;500/501, chaîne manquante, préfixe ancien, limitesJSON/SQL/CPU/output, propriétaire/snapshot/zero-write/cleanup. Refus attendus classés comme tels. Une marge insuffisante ou une preuve manquante conserveHOLD.
5. Revue indépendante, CI protégée du HEAD exact, merge sous GOV-MERGE-01, CI canonique et closeout uniquement après satisfaction des gates. Pas de GO merge routinier supplémentaire.

## Frontières maintenues

Pas de modification du catalogue, des sources/politiquesSCI/P07, de l'allocation, writers, TIME-01, SQL, DTO/schema, auth, dépendances, CI, mobile ou plafonds. Pas d'activationQA, service existant, données réelles, APK, OTA, déploiement ou image reconstruite. Le lecteur reste disabled. Une qualification source-overlay ne s'étend pas à une future image ou configuration opérationnelle.

**Décision unique demandée : autoriser ce correctif SCI-RUNTIME-03 (réutilisation confinée et digest final), ses tests, la requalification native aux mêmes conditions et sa livraison gouvernée.**
