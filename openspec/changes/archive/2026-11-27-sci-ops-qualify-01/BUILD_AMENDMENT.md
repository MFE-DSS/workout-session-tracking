# SCI-OPS-QUALIFY-01 — amendement minimal du contexte V3

27 novembre2026 — Europe/Paris. **PROPOSÉ ; GO BUILD NON REÇU ; aucun correctif produit appliqué.**

## Défaut démontré sur le paquet exact
Source `1ac401f44b8af9444a8521b30cd47b7201fd1c8e`, image `sha256:6baa24c49404b2dd8ad74a3d5b4d6f9af3c83c6923a5711a1ae1bf79aebe5e8c`. Une séance synthétique issue des sept rencontres inventory2, de l’évaluation, du START, de quatorze SET et du FINISH canoniques est completed,14/14, non exclue. Aucune table métier n’est remplacée dans l’image.

Les cinq lectures V3 réelles échouent ; les deux lectures du mixte14V3+86Legacy aussi. La validation stricte localise quatorze `extra_forbidden` : `facts[i].context.canonical_exercise_id`. Le writer conserve six propriétés ; le DTO public autorise cinq propriétés et porte déjà l’identité dans `resolution.canonical_exercise_id`. Le lecteur transmet actuellement le contexte intégral.

Une copie mémoire projetée sur les cinq propriétés publiques passe le schéma, les invariants et le recalcul du digest. **Ce contre-factuel n’est ni un patch appliqué ni une qualification du futur CPU/worker.** Les refus originaux et les fixtures complètes sont conservés.

## Brainstorming / Options / Risques / Choix retenu
- Ajouter le sixième champ au DTO : rejeté ; élargit inutilement le contrat public.
- Modifier le writer ou les observations persistées : rejeté ; ne répare pas le lecteur et altère une autorité hors scope.
- Projeter explicitement à la frontière publique après preuve intégrale : retenu. Risque principal : masquer une identité contradictoire ou filtrer arbitrairement un champ inconnu. Les tests négatifs ci-dessous sont donc obligatoires.

## Périmètre exact demandé
1. `app/services/muscle_observed_load/provenance.py` : préserver le contexte stocké complet pour comparaison reçu/prescription, digests, provenance et contexte de charge ; vérifier l’identité canonique supplémentaire lorsqu’elle existe contre le mapping admis. Émettre ensuite exclusivement `context_ref`, `equipment_ref`, `realization_ref`, `side`, `load_semantics`. L’identité reste portée par la résolution.
2. `tests/test_muscle_observed_load_provenance.py` : témoins six champs réels, contexte historique cinq champs, contradiction d’identité, champ supplémentaire non admis, reçu/digest divergent et absence de conversion de masse.
3. Nouveau `tests/test_muscle_observed_load_writer_readback.py` : parcours synthétique des services canoniques inventory2 → évaluation → START → SET → FINISH → lecteur ; identités, opérations, unités, rôles et digest. Les aides de préparation restent dans les tests, pas dans le runtime.
4. Documents OpenSpec, revue et reçus propres à cet amendement. Aucun autre module produit n’est autorisé par ce scope proposé.

Un contexte historique à cinq propriétés déjà admis doit garder son comportement. Un champ inconnu ne doit pas être simplement supprimé. Toute contradiction conserve une qualification conservatrice selon les raisons existantes ; aucune promotion artificielle à EXACT. Aucun nouveau champ DTO, budget, politique SCI ou mapping P07.

## Exécution après GO seulement
- Revérifier canonique et leases ; conserver les témoins rouges existants.
- RED→GREEN sur le vrai contexte à six propriétés et les négatifs ; comparaisons indépendantes du digest depuis la réponse normalisée.
- `check_scope`, tests ciblés et broad consommateurs, sécurité, OpenSpec, revue indépendante du diff entier et CI protégée du HEAD exact. Pas de sweep local systématique hors tier applicable.
- Rejouer worker/superviseur réels : Legacy, V3 complète14faits et mixte100, propriétaires A/B/vide, états dégradés et refus adversariaux. Conserver CPU2/3s,AS512Mio,wall3s,SQL4096/VM2M et autres plafonds. L’essai mixte ayant atteint SIGXCPU reste une réserve mesurée ; aucun succès futur n’est présumé.
- Publier et merger sous GOV-MERGE-01 si les gates applicables passent, sans nouveau GO MERGE routinier. Une limite résiduelle maintient HOLD ; elle n’autorise pas une seconde optimisation implicite.

## Frontière opérationnelle
Le GO demandé ci-dessous couvre le code, les tests, la revue, la CI et sa livraison. Il ne couvre pas un nouveau PREPARE_IMAGE cloud à un SHA encore inconnu, un transfert de nouvelle image, un remplacement du QA ou une activation. Le paquet corrigé devra ensuite être reconstruit et qualifié comme image exacte sous son acte applicable ; le montage de source corrigé sur l’image actuelle ne vaudra pas preuve de déploiement. Le raccordement du lanceur QA et la confiance de son vrai profil/montage restent séparés.

Aucun writer, historique, TIME-01, SQLite, allocation V3, moteur de récupération, mobile, asset, secret existant, VPS actif, APK, OTA ou donnée réelle modifié. Lecteur toujours DISABLED. S8707 reste OPEN.

## Décision unique demandée
**« J’autorise l’amendement de projection du contexte V3 décrit dans ce BUILD_AMENDMENT.md du27novembre2026, ses trois fichiers de code/tests, les vérifications et sa livraison sous GOV-MERGE-01, sans activation ni opération de déploiement. »**

## Actualisation — GO reçu
Le statut PROPOSÉ en tête décrit l’instant de proposition. L’acte explicite du 27 novembre est enregistré dans AUTHORIZATION.md : le correctif exact est maintenant autorisé. Aucune extension du périmètre.
