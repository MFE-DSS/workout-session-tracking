# Delta unique à autoriser — nouvelle intention d'image après refus de garde

27 novembre 2026 — **PROPOSÉ, NON EXÉCUTÉ.** Ce document ne déclenche rien et ne modifie aucune règle.

## Cause établie
Run existant45977551087, attempt1, source `1ac401f44b8af9444a8521b30cd47b7201fd1c8e` : approbation réelle MFE-DSS retrouvée pour qa-release, mais commentaire égal au seul SHA. La garde exige `APPROVE_QA_IMAGE <SHA>`.

Job140433119125, étape « Require image approval; preserve the same image in private encrypted custody » : `qa_image_preparation_refused`, exit1 à10:22:15UTC. Le code appelle la garde avant Docker pull/build. Aucun artefact Actions et aucun asset privé correspondant au nom exact de cette tentative n'ont été retrouvés.

Rejeu local du code canonique, sur les réponses GitHub acquises et avec status=in_progress correspondant à l'étape exécutée : commentaire réel refusé ; seul ajout du préfixe attendu accepté. Ce témoin local ne modifie aucune approbation réelle. Le témoin attempt2 est lui aussi refusé : un re-run du job n'est pas une réparation valide.

## Delta demandé
Autoriser **une nouvelle intention**, une seule tentative PREPARE_IMAGE, au même SHA exact et avec le workflow existant inchangé. Recontrôler canonique, quatre checks, protections, ressources et garde. Conserver le premier échec intégralement ; enregistrer une nouvelle intention durable avant un seul POST, puis retrouver le nouveau run sans replay automatique.

L'opérateur doit ensuite approuver **ce nouveau run**, avec exactement :

```text
APPROVE_QA_IMAGE 1ac401f44b8af9444a8521b30cd47b7201fd1c8e
```

L'agent ne s'auto-approuve pas, ne réutilise pas l'ancienne approbation et ne remplace pas la comparaison exacte par une règle permissive. Aucun changement de code/CI nécessaire ou proposé.

Les GO acquisition privée/transfert/banc isolé déjà reçus restent acquis, sous leurs préconditions. Le Mac a passé le seuil après nettoyage borné ; le seuil sera relu avant toute acquisition et le VPS avant transfert. Aucun nouveau service, fournisseur, secret ou budget. QA existant, flags, données réelles, APK/OTA toujours exclus.

## Pourquoi cette décision est nécessaire
Le mandat DISK AND IMAGE RESUME impose « Aucun second dispatch ». La première intention est consommée et ne produit pas d'image. Le présent amendement demande expressément la seule exception requise ; aucune action dépendante n'est anticipée.

## Formulation
« J'autorise une nouvelle intention PREPARE_IMAGE, une seule tentative au SHA1ac401f44b8af9444a8521b30cd47b7201fd1c8e, après le refus de garde du run45977551087. Conserver les règles et l'approbation humaine exacte du nouveau run ; poursuivre ensuite le GO opérationnel existant. »
