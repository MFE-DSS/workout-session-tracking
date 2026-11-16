# REL03 — raccordement image restant, avant application

16 novembre2026. **DESIGN PROPOSÉ, NON APPLIQUÉ.** Le scope technique accepté a livré `prepare_image` metadata-only et le codec local `stage_image/restore_image`. Il exclut l’upload/custodie et conserve une approbation distincte de préparation cloud. Le mandat OPS demande de finir l’adaptateur seulement s’il est permis : le protocole de garde réelle et ses credentials ne sont pas encore admis. Aucun callback d’upload implicite ajouté sous couvert du GO précédent.

## Plus petit raccordement proposé

Réutiliser le dépôt **privé** déjà prévu pour les preuves, séparément des paquets DB et de leurs caps. Le dépôt public AUREN n’accueille jamais les octets image, même chiffrés. Pas de registry/fournisseur supplémentaire ni upload automatique après merge. Le dépôt privé est UNPROVISIONED aujourd’hui.

Fichiers du delta proposé : `tools/qa_delivery/image_receipts.py`, son test dédié, `.github/workflows/qa-release.yml`, configuration de garde publique ne contenant que repository/état et docs/change REL03. Aucun app/SCI/migration/SDK/UI. Avant apply, revoir/amender le scope metadata-only en gardant l’autorisation technique acquise distincte de cette nouvelle liaison externe.

1. Dans le job `prepare-qa-image` déjà protégé et approuvé au SHA exact, produire une fois l’archive propre, puis chiffrer **cette même archive** avant sa destruction. Aucun build secondaire présenté comme identique au premier.
2. Vérifier par GET authentifié le repository.private et le release ID exact existant. Lire clé AES privée32octets/token uniquement depuis références protégées approuvées, jamais argv/log/artefact public. Pas de création repo/release/secret par le producteur.
3. Uploader un seul fichier ciphertext à nom dérivé du SHA/run/attempt, avec nouvelle destination. Taille image≤2Gio ; imposer en plus le plafond réel du provider sur **ciphertext=plaintext+45octets**, donc refuser si l’enveloppe dépasse le plafond sans augmenter les caps DB. La [documentation GitHub Releases](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases) exige un fichier strictement inférieur à2Gio : avec45octets d’enveloppe, plaintext au plus2Gio−46octets. Ce plafond doit être testé dans le delta et revérifié avant upload ; le codec local plus large ne constitue pas une permission provider.
4. Relire l’asset réel, calculer son checksum et conserver repository/release/assetID/taille/digest. En cas de POST sans réponse : état UNKNOWN, aucun upload/retry automatique ; résolution par lecture de cette tentative avant autre envoi. Un simple nom d’asset n’est pas un reçu de succès.
5. Publier uniquement la metadata du build dans l’artefact Actions public. Son acquisition indépendante vérifie run/job/attempt/SHA/CI et les références de garde privée. Aucun secret ou ciphertext dans l’artefact public.
6. Le mainteneur autorisé télécharge les mêmes octets en privé, vérifie checksum puis AES-GCM, refuse destination existante et tout plaintext final non authentifié ; Docker load seulement après GO distant. Vérifier config imageID, plateforme et Entrypoint/Cmd exacts après load. Ne pas extraire une archive Docker en tant que fichier tar arbitraire dans l’hôte.

## Tests et gate du delta

RED→GREEN : dépôt public/autre repo, mauvais run/SHA/attempt, image différente, limite d’enveloppe, fichier spécial/symlink, mauvaise clé/tag/checksum, destination existante, upload interrompu/réponse perdue, redirection avec fuite du Bearer, ancien reçu et double envoi. Test local streaming du vrai codec ; intégration du producteur avec garde simulée source-labellée. `check_scope` effectif CI_INFRA si workflow modifié : sweep local borné et CI réelle exact HEAD, revue indépendante, merge GOV‑MERGE‑01. Aucune publication réelle durant les tests.

L’exécution cloud, provisioning privé, secrets, upload/transfert et Docker load exigent le GO opérationnel après les preuves/commandes concrètes. L’ancien reçu metadata-only ne fournit pas les octets disparus. Aucun code préparatoire de ce delta, image réelle, asset privé ou frais n’est déclaré livré ici.
