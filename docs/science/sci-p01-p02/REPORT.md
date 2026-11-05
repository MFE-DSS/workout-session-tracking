# Rapport SCI-P01 / SCI-P02 — contrats isolés

5 novembre 2026. Branche `spec/sci-p01-p02-blueprint-first-plan`, base 90da846. Réalisation autorisée après revue du design : « Valider les contrats et tests isolés ». Pas de moteur servi, de nouvelle règle de prescription, d'UI ou de migration.

## Brainstorming / Options / Risques / Choix retenu

Envelopper directement le planificateur historique masquerait ses baselines et l'absence de temps utilisateur. Réécrire l'orchestration serait hors périmètre. Choix retenu : audit + DTO/JSON Schemas/fixtures/tests isolés, en distinguant disponibilité de données, de politique et de compatibilité. Les artefacts ne sont importés par aucun module app/. Le module ne choisit pas d'exercice ni ne génère une prescription ; il valide la forme et la cohérence d'un échange proposé.

## Audit et décisions

18 gabarits,107 fiches scientifiques/84 identités canoniques, taxonomies11/15 zones et deux familles de générateurs repérées. La chaîne hebdomadaire est réellement servie sur le web ; elle reste inchangée. Probes purs : cadence 1/2/3/4 avec familles inconnues →24/48/72/96 séries physiques, statuts historiques partial. Baselines par zone total 148, distinct des séries physiques. Aucun de ces nombres ne devient une dose recommandée.

Le manifeste est identique au blob reçu dans la PR mobile #353 à 2ba9fd4, absent de la base canonique ; copie explicitement tracée. Les sources d'ancrage incluent ACSM 2026, dose-réponse volume/fréquence, split/full-body, effort et repos. Les limites de lecture (notamment texte intégral ACSM inaccessible) sont explicites ; aucune revue systématique complète ou validation prédictive anthropométrique revendiquée.

Revue de construction : trois clarifications réglées dans le design (politique nullable/priorité de statuts ; profil d'inputs séparé de la dose ; impossibilité démontrée distincte de l'inconnu). Les décisions restantes avant un moteur sont dans HANDOFF.md ; elles n'empêchent pas le paquet isolé demandé.

## Validation locale

check_scope : ISOLATED ; pas de full sweep local. Premiers tests rouges sur absence du module, puis sur fausses compatibilités, sources de conflits identiques, prior de population présenté comme fait personnel, date future, moteur absent, exposition inconnue/exacte et durée sans modèle. Corrections ciblées puis tests verts.

À cette passe : **43 tests de contrat**, inclus dans **341 tests ciblés et de voisinage passants** (44,02 s), avec deux avertissements de dépréciation de dépendances. Ruff nouveau code propre ; budget **264 ≤ 548** ; protocole et OpenSpec strict **5/5** passants. Les trois JSON Schemas correspondent à l'export des DTO et les huit fixtures se valident avec les références du dépôt. Les tests READY utilisent seulement une autorité synthétique, aucune politique réelle promue.

La revue indépendante finale a relevé deux problèmes importants, sans critique ni mineur : une confirmation disponible pouvait masquer un refus dans le même contexte ; la provenance de l'équipement et des confirmations était insuffisamment contrainte. Huit cas de régression ont d'abord échoué (35 autres passants), puis les deux corrections ont été appliquées en une passe. La vérification finale de 341 tests inclut ces huit cas. Une contradiction ne devient plus une compatibilité confirmée ; une disponibilité connue exige une source personnelle/contextuelle explicite.

Le diff hors manifeste est sans erreur d’espacement. Les doubles espaces du manifeste sont ses sauts de ligne Markdown d’origine, conservés pour maintenir une copie byte-identique à la source opérateur. Les empreintes du manifest ont été vérifiées.

Publication et CI du HEAD final encore à consigner avant livraison. Aucun test mobile/visuel nouveau requis localement puisqu'aucune surface ni consommateur produit ne change ; la CI existante reste applicable selon son déclenchement.

## État servi et limites

Les contrats sont proposés et vérifiables, non servis. Pas de snapshot Blueprint persistant, de premier plan produit, d'estimation de durée validée ou de fixture READY issue d'un vrai moteur. Le module n'authentifie pas et ne certifie pas la vérité scientifique des données qu'un producteur de confiance lui fournit. Aucune mutation de app/, clients/, data/, schémas backend partagés, DB ou tokens.

Le handoff donne versions, champs, inconnus, table de dépendances, producteurs/consommateurs, compatibilité et breaking changes. Les prochaines tâches nécessitent un change scientifique/API dédié ; aucun GO BUILD de moteur ou déploiement ne se déduit du présent paquet.
