# SCI-RUNTIME-03 — exécution du GO produit

Parent3d4c7577,26novembre2026. Spec : BUILD_AMENDMENT.md et acte opérateur enregistré dans AUTHORIZATION.json. Six fichiers seulement ; documents de preuve/livraison inclus. Pas de nouveau budget ni activation.

## Brainstorming / Options / Risques / Choix retenu
Le GO retient la suppression du parsing redondant et le digest du DTO final. Les imports partagés ne sont pas refactorisés. Contexte frais dans le worker, gabarits privés/copieurs de vues, identité propriétaire/profil et invalidation lors d'un changement d'autorité ; sources identiques attestées séparément. Une source valide différente suit son parsing propre. Toutes les vérifications de bundle après compose_effective restent en place. Les copies ont un coût à qualifier, sans déduire un PASS du prototype.

## Task 1: Correctif testé des six fichiers

Interfaces : worker crée le contexte après parse du job, depuis la vue admise ; SourceView courant et bundle reçoivent ce contexte, mais leurs autorités restent vérifiées indépendamment. Les changements propriétaire/profil refusent le partage ; une nouvelle génération invalide les gabarits. DTO normalisé puis digest, vérification indépendante avant retour.

1. Ajouter tests réels : deux lectures du même catalogue courant/bundle attesté, vues indépendantes, digest corrompu/source différente valide, propriétaire/profil/génération, digest entier/float après DTO. Attendu : RED explicite contre le parent.
2. Implémenter seulement worker/provenance/projection, sans autre import SCI consommateur ou contrat modifié. Attendu : GREEN des régressions ; parité et refus existants conservés.
3. check_scope, Ruff/budget/protocole/OpenSpec, reader/API et broad SCI ciblés. Attendu : contrôles prescrits passants, pas de sweep local total non requis.

## Task 2: Qualification et livraison du HEAD réel

1. Nouvelle copie native avec image5ee90ab et sources/pins du HEAD livré ; conteneurs/volumes neufs, réseau fermé, UID10001/caps0/1CPU/2Gio, plafonds enfant inchangés. Attendu : mesures nominalesLegacy/V3/100faits, refus500/501/ressources, SQL/snapshot/owner/slots/reaping/digests ; aucun service existant modifié.
2. Revue indépendante du diff entier, correctifs bornésRED→GREEN et requalification si nécessaire. Attendu : aucun Important ouvert.
3. Commit/push/PR, CI protégée du HEAD exact, merge gardé GOV-MERGE-01 si toutes gates satisfaites, CI canonique. Attendu : SHA et reçus exacts ; Sonar réel consigné.
4. Archive/closeout/nettoyage borné après ancestralité et préservation des preuves. Attendu : CLOSED+CLEANED du code, service toujoursdisabled, confiance opérationnelle distincteHOLD si non qualifiée.

## Review Focus

Le cache ne doit ni contourner une attestation de source, ni admettre une autorité grâce à un hit ; caches et vues ne doivent pas fuiter entre jobs, propriétaires, profils, générations. Lire les contrôles après compose_effective et vérifier le cache-miss d'une source historique valide différente. Vérifier le digest sur les types réellement retournés, indépendamment du helper de calcul. Distinguer succès de processus, succès de validation parent et refus de budget attendus. Ne pas transférer la qualification du banc à un futur déploiement.
