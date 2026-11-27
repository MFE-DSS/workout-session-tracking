# Nouvelle intention autorisée — 27 novembre 2026

Réponse opérateur : « oui go j'autorise et avance sur ton critical path ». Autorisation enregistrée avec empreinte de IMAGE_RETRY_DELTA.md, puis nouvelle intention durable avant un seul POST. Le premier run45977551087 et son refus restent conservés ; aucun re-run de cette ancienne tentative.

## État réel
Source et canonique revérifiés : `1ac401f44b8af9444a8521b30cd47b7201fd1c8e`. Les quatre checks protégés passent ; workflow inchangé SHA256 `8c679b63f0321c38e5992989dc0bf2bf2391ab7c55cd9436921b2ac97301d74c`. Protection qa-release et garde privée relues, sans bypass.

Préconditions : Mac27 884 072 960octets libres ; VPS44 224 516 096octets libres et6 148 022 272octets de mémoire disponible. Seuils20Gio/20Gio/3Gio PASS à ce relevé, à revérifier avant acquisition/transfert. Aucune collision de ressources du banc.

Nouveau [run45990407820](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/45990407820), attempt1/source exacte : job prepare140476487500 completed/success ; prepare-qa-image140476572861 waiting ; release skipped comme prévu pour PREPARE_IMAGE. Dernière lecture11:29:02UTC : run waiting, approbations réelles vides. Aucun nouveau build effectif, image acquise ou transfert déclaré.

## Seule action humaine restante pour démarrer le build
Dans ce nouveau run : Review deployments → qa-release. Copier **toute la ligne**, puis Approve and deploy :

```text
APPROVE_QA_IMAGE 1ac401f44b8af9444a8521b30cd47b7201fd1c8e
```

Le fichier privé `execution-20261127/retry-02/APPROVAL_COMMENT.txt` contient uniquement cette ligne. Le GO de nouvelle intention ne vaut pas cette approbation humaine. L'agent ne la donne pas et n'émettra pas d'autre dispatch après une réponse perdue ou une attente.

## Travail indépendant préservé
Harness privé repris des campagnes existantes : syntaxe vérifiée, **pas encore exécuté sur l'image**. Le producteur de fixtures est adapté pour lire le bundle embarqué, sans le reconstruire ni le monter en remplacement, pour utiliser le GID réel à fournir après inspection et pour garder le profil de test root-owned/group-readable. Les autres cas/probes sont identifiés et empreintés ; qualification V3100faits et campagne complète restent à exécuter. Ce travail ne change aucun code produit ou autorité scientifique.

Preuves privées sous `sci-ops-qualify-01-evidence-20261127/execution-20261127/retry-02/` : autorisation, préflights, intention/réponse, run/jobs/approbations, commentaire exact et provenance du harness. Aucun service existant modifié. Image/chemins/runtime HOLD, lecteur DISABLED ; activation QA, APK/OTA, données réelles toujours exclus.
