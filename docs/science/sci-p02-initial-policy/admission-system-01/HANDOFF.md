# SCI-P02-INITIAL-POLICY-ADMISSION — handoff science → PLAN

7 novembre 2026. **PROPOSED / NOT_ADMITTED / NOT_SERVED / READY_NOT_PRODUCED.** Auteur du dossier distinct du reviewer d'admission encore requis. Ce document ne promeut aucune référence dans un registre.

## Ce qui existe réellement

BodyTrainingBlueprint v1 et FirstPlanRecommendation v1 ; `initial-policy-producer/2.0.0` isolé, contrat de recherche `initial-plan-evaluation/1.0.0` et résultat `initial-plan-evaluation-result/1.0.0`, politique `0.3.0-proposed`. Digests/versions/SHA exacts et 12 sorties rejouées dans [REPORT](REPORT.md). L'enveloppe n'est ni endpoint ni transport FirstPlanClient, snapshot serveur possédé, preuve d'authentification/consentement ou commande de création de séance. Toute réponse réelle actuelle reste sans candidate_plan et sans READY.

Inputs minimums consommés : objective, population_scope, sessions_per_week, session_budgets_minutes, limitations. Taille/poids/expérience facultatifs/UNKNOWN ; priorités = souhaits. Pas d'inventaire obligatoire ; confirmations d'exercices contextuelles possibles. `BodyMeasurement/body_profile` garde son unique chronologie, aucune acquisition corporelle ajoutée ici.

## Ce que cette préparation propose

Verdict du système **NOT_ADMITTED**, C1/C2 conventions bornées proposées, C3 procédure/correction à admettre, C4 sept réalisations conditionnelles exactes proposées, C5 contrat successeur soumis à choix, C6 sortie C collecte. [Design](../../../../openspec/changes/science-initial-policy-admission/design.md), [tests futurs](TEST_SPEC.md), [temps](TIME_PROTOCOL.md). Aucun contrat successeur exporté, aucune correction appliquée. Les textes antérieurs, registres et artefacts historiques restent intacts.

Chaque gate porte PROPOSED_FOR_SCIENTIFIC_REVIEW. Le design §D5 rend reviewable un premier build isolé possible : trois corrections + registre séparé initialement vide + seul consommateur d'admission isolé et fixtures de refus. Son succès peut légitimement conserver NOT_ADMITTED. Le binding exécutable et une fixture READY sont une étape ultérieure conditionnée par preuve réelle, pas une promesse du build négatif.

## Conditions de reprise PLAN

PLAN peut préparer ses acquisitions/snapshot propriétaire/adaptateur/transport/idempotence, mais doit attendre une **admission effective versionnée** avant branche READY. Il reçoit alors : versions exactes contrat/policy/engine, decision/admission refs signées, digest de bundle/science, références de preuve et limites applicables, deux fingerprints complets, règle de révocation/invalidation et fixture réellement générée/validée. Une conformité JSON ou valeur APPROVED seule doit être refusée.

La sémantique SCI v1 ne contient pas tous les états runtime de D : expliciter leur mapping, ne pas transformer POLICY_UNAVAILABLE en une donnée manquante utilisateur ou TIME_UNCERTAIN seulement pour simplifier l'écran. Une enveloppe v2 non servie ne passe pas automatiquement FirstPlanClient v1 ; la compatibilité/version et l'adaptateur sont des travaux PLAN après contrat SCI revu. SCI possède les exigences scientifiques, PLAN l'implémentation de leur consommation : aucun writer concurrent des mêmes contrats.

Pour une prescription bootstrap future, charge inconnue ne bloque pas par principe si le protocole initial et **son temps** sont admis ; elle ne peut pas être rendue exécutable par étapes fictives. Réglages non massiques et unilatéraux non appairés nécessitent représentation et autorité effectives. Le vrai READY requiert l'ensemble des gates ; aucune fixture artificiellement autoritaire n'ouvre la chaîne.

Après handoff réel, la création de séance possédée/idempotente et sa relecture après réponse perdue appartiennent à `blueprint-first-session-runtime`, avec reprise prioritaire d'une séance existante. MISSION historique reste un domaine séparé, sans fallback SCI. RELEASE n'a pas de recette positive premier-plan avant ce runtime réel ; aucun appareil/build accepté par ce dossier.

**Blocker de mapping PLAN identifié dans le code historique :** `session_builder.instantiate_session` importe par défaut deux séries préparatoires au premier exercice, puis `max(1, warmup_sets-1)` aux autres. Passer zéro ne supprime pas toutes les rows. Ne pas importer cette constante 2/1 comme règle SCI ni confondre warmup rows, familiarisation, calibration et séries de travail prescrites. PLAN doit définir le mapping après admission, puis vérifier les rows réellement créées. Le POST mobile historique ne valide pas un plan SCI et ne porte pas de clé d'idempotence ; il n'est pas le handoff admis. Aucun patch de ce builder/endpoint ici.

## Décisions / preuves encore requises

| Manque | Responsable | Effet |
|---|---|---|
| Revue de cohérence du verdict réalisée ; validation opérationnelle positive du bootstrap encore requise | Reviewer scientifique distinct de l'auteur ; responsable du protocole pour sa validation réelle | La revue fraîche confirme NOT_ADMITTED sans Important ; aucune admission positive du bootstrap/bundle par ce seul dossier |
| Choix explicite projection v1 calculée/convention admise ou contrat successeur proposé | Opérateur + science + architecte PLAN | Pas d'assouplissement READY v1 ; build consumer bloqué sur version définitive |
| Route temps A/B/C, protocole applicable, cibles/statistique et moyens réels | Responsable scientifique/statistique + opérateur/exploitation ; DATA pour traitement des observations | C6 reste non acquis ; aucun délai/durée personnelle inventé |
| GO BUILD fonctionnel borné après revue proposal/spec/design | Opérateur | Corrections/tests/DTO/binding non appliqués ici |
| Preuve positive et admission effective exacte | Science/reviewer indépendant | Pas READY ; grand budget, historique isolé ou build réussi insuffisants |

Il n'est pas requis de redécider le socle MOB03, refaire la recherche musculaire, résoudre les quatre pull retenus inutilisés ou imposer poids/taille/inventaire. Le parent `science-initial-plan-policy` reste ouvert ; cet enfant seul mène la prochaine admission. Une future livraison s'intègre sous GOV-MERGE-01 avec contrôles réels du HEAD final, sans nouveau GO MERGE ponctuel ni GO DEPLOY implicite.
